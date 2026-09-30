---
type: topic
domain: devops
stage: 7
order: 8
status: todo
level: middle+
tags: [domain/devops, stage/7, level/middle+, priority/should]
reviewed: 
next_review: 
priority: should
time: 9
---

# Алертинг: Alertmanager, правила алертов, маршрутизация, борьба с шумом

↑ [[DO Этап 7 · Observability и эксплуатация|Этап 7 · Observability и эксплуатация]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~9 мин чтения</span><span class="chip">Уровень: middle+</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> Плохой алертинг хуже отсутствия: усталость от шума, пропущенные критичные события. Спрашивают маршрутизацию и борьбу с шумом.

## Принципы хорошего алерта

- **требует действия человека** прямо сейчас (actionable) — иначе это не page, а тикет/дашборд;
- **симптомы важнее причин**: алертить на влияние на пользователя (ошибки, латентность, недоступность), причины (CPU, диск) — на предельные риски с запасом времени;
- **срочность соответствует серьёзности**: page — ночью разбудить можно; ticket — в рабочее время;
- **минимум ложных срабатываний** (precision) при высокой полноте (recall) для критичного;
- **понятное описание**: что сломалось, влияние, куда смотреть, runbook;
- **владелец** у каждого алерта; регулярный пересмотр.

## Prometheus + Alertmanager

```text
Prometheus (rules: expr + for) ──firing alerts──▶ Alertmanager (группировка, дедупликация, маршрутизация, подавление, silences) ──▶ receivers
```

**Правила алертов**:

```yaml
groups:
  - name: api.rules
    rules:
      - alert: ApiHighErrorRatio
        expr: sum(rate(http_requests_total{job="api",status=~"5.."}[5m])) / sum(rate(http_requests_total{job="api"}[5m])) > 0.05
        for: 10m                                   # должно выполняться непрерывно 10 минут
        keep_firing_for: 5m                        # держать firing после восстановления (против «мерцания»)
        labels: { severity: critical, team: backend, service: api }
        annotations:
          summary: "API: доля 5xx {{ $value | humanizePercentage }}"
          description: "За последние 5 мин > 5% ответов с ошибкой сервера."
          dashboard: "https://grafana/d/api-red"
          runbook_url: "https://wiki/runbooks/api-5xx"

      - alert: DiskWillFillIn24h
        expr: predict_linear(node_filesystem_avail_bytes{fstype!~"tmpfs|overlay"}[6h], 24*3600) < 0
        for: 30m
        labels: { severity: warning, team: infra }
        annotations: { summary: "Диск {{ $labels.instance }}:{{ $labels.mountpoint }} заполнится в течение суток" }

      - alert: TargetDown
        expr: up == 0
        for: 5m
        labels: { severity: critical }
```

Свойства: **`for`** (устойчивость: защита от всплесков), **метки** (`severity`, `team`, `service`, `env`) для маршрутизации, **аннотации** для людей (шаблоны Go: `{{ $labels.x }}`, `{{ $value }}`), `keep_firing_for`, recording rules для тяжёлых выражений, **`absent()`/`up`** для «нет данных», алерты на «Watchdog» (dead man’s switch: всегда firing; его пропажа означает сбой конвейера алертинга).

## Маршрутизация в Alertmanager

```yaml
route:
  receiver: default-ticket
  group_by: [alertname, service, env]
  group_wait: 30s          # ждать, чтобы собрать алерты в группу до первой отправки
  group_interval: 5m       # интервал для новых алертов в уже отправленной группе
  repeat_interval: 4h      # повтор, если алерт всё ещё firing
  routes:
    - matchers: [severity="critical"]
      receiver: oncall-pager
      continue: false
      routes:
        - matchers: [team="data"]
          receiver: data-oncall
    - matchers: [severity="warning"]
      receiver: team-chat
      mute_time_intervals: [nights]
    - matchers: [alertname="Watchdog"]
      receiver: deadmanssnitch
      repeat_interval: 1m

inhibit_rules:
  - source_matchers: [severity="critical", alertname="NodeDown"]
    target_matchers: [severity=~"warning|critical"]
    equal: [instance]                              # если узел упал, подавить остальные алерты этого узла
  - source_matchers: [alertname="ClusterDown"]
    target_matchers: [severity=~"warning|critical"]
    equal: [cluster]

time_intervals:
  - name: nights
    time_intervals: [{ times: [{ start_time: "22:00", end_time: "08:00" }], location: Europe/Moscow }]

receivers:
  - name: oncall-pager
    pagerduty_configs: [{ routing_key_file: /etc/alertmanager/pd-key }]
  - name: team-chat
    telegram_configs: [{ bot_token_file: /etc/alertmanager/tg-token, chat_id: -100123456, parse_mode: HTML, message: '{{ template "telegram.message" . }}' }]
  - name: default-ticket
    webhook_configs: [{ url: http://jira-bridge/alerts, send_resolved: true }]
```

- **Группировка** (`group_by`): один «шторм» из 100 алертов → одно уведомление; **дедупликация**; **ингибирование** (подавление производных алертов при наличии корневого); **silences** (временное отключение, например на время работ, с автором и причиной); **mute_time_intervals/active_time_intervals** (тихие часы для warning); **эскалация** и дежурные графики вне Alertmanager (PagerDuty/OnCall).
- Получатели: Telegram, Slack, email, PagerDuty, Opsgenie, webhook (интеграции с Jira, ChatOps); шаблоны сообщений со ссылками на дашборд, runbook и кнопки.
- **HA**: кластер Alertmanager (gossip, `--cluster.peer`), Prometheus шлёт всем экземплярам; не использовать балансировщик между Prometheus и Alertmanager.

## Борьба с шумом

| Проблема | Решение |
|---|---|
| Мерцающие алерты | `for:`, `keep_firing_for`, сглаживание окном, гистерезис |
| Алерт на каждую причину | алерты на симптомы и SLO burn rate, ингибирование |
| Десятки одинаковых | группировка по сервису, агрегированные выражения |
| Ночные страницы не по делу | разделить page/ticket; warning → только рабочее время |
| Алерты без действия | удалить или превратить в дашборд/метрику |
| Нет владельца | обязательные метки `team`/`owner` |
| «Привычка игнорировать» | пересмотр правил на ретро; метрики: число алертов на дежурного, доля полезных (actionable), время до реакции |
| Плановые работы | silences, maintenance windows |
| Каскад при падении зависимости | ингибирование, зависимостные алерты |
| Единичные ошибки при низком трафике | пороги по абсолютному числу + доле; ограничение минимального трафика (`and sum(rate(...)) > 1`) |
| Статические пороги не подходят | SLO/burn rate, сравнение с базовой линией (`offset 1w`), аномалии (осторожно), `predict_linear` |

**Алерты на основе SLO (burn rate)** — лучший способ снизить шум и связать с влиянием (см. тему про SLO).

## Качество правил

- тестирование: `promtool check rules`, **`promtool test rules`** (юнит-тесты правил с синтетическими рядами), линтеры (`pint`), проверка в CI, ревью правил;
- **документирование**: у каждого алерта — описание, runbook, дашборд, эскалация;
- **версионирование** правил в Git (PrometheusRule CRD, Helm), автоматическая выкатка;
- **регулярные ревью**: ретро по алертам (какие разбудили впустую, какие пропущены); удаление неиспользуемых;
- метрики алертинга: **precision/recall**, `ALERTS{alertstate="firing"}`, `alertmanager_notifications_failed_total`, время доставки;
- **Watchdog** и внешний мониторинг (Uptime Kuma, Healthchecks.io, Cronitor) — наблюдать за самим мониторингом;
- защита: секреты токенов, шаблоны без чувствительных данных, доступ к silences ограничить.

## Типовой набор алертов

| Категория | Примеры |
|---|---|
| **Доступность** | `probe_success == 0` (blackbox), `up == 0`, SLO burn rate |
| **Ошибки и задержки** | доля 5xx, p95/p99 latency, растущие очереди |
| **Насыщение** | память > 90%, диск (прогноз), CPU throttling, пул соединений БД, inode |
| **Kubernetes** | CrashLoopBackOff, NotReady ноды, Pending поды, PVC заполняется, HPA на максимуме |
| **Сертификаты/домены** | срок < 14 дней |
| **Бэкапы** | нет успешного бэкапа > 26 ч, ошибки архивации WAL |
| **Репликация/очереди** | лаг репликации, отставание consumer'ов Kafka |
| **Безопасность** | всплеск 401/403, необычные входы, срабатывания WAF/Falco |
| **Мониторинг** | Watchdog, `scrape_samples_post_metric_relabeling`, отказы отправки уведомлений |
| **Стоимость** | аномальный расход облака |

## Практики реагирования

- в уведомлении: что, где, влияние, с какого момента, ссылка на runbook/дашборд/логи; кнопки acknowledge/silence;
- **acknowledge** и эскалация, если никто не среагировал (PagerDuty policies);
- автоматизация первичной диагностики (бот прикладывает графики, последние деплои, похожие инциденты);
- связь с инцидент-менеджментом (автосоздание инцидента и канала для критичных);
- корректное закрытие: `send_resolved`, проверка восстановления.

## Вопросы с ответами

> [!question]- Как бороться с усталостью от алертов?
> Алертить на симптомы и SLO burn rate, убрать неактуальные и неcрочные (в тикеты/дашборды), добавить `for`, группировку и ингибирование, назначить владельцев, регулярно пересматривать правила по метрикам шума.

> [!question]- Что делают group_by, group_wait и inhibit_rules?
> `group_by` объединяет алерты в одно уведомление по меткам, `group_wait` задерживает первую отправку, чтобы собрать группу, `inhibit_rules` подавляют производные алерты при наличии корневого (например, все алерты упавшего узла).

> [!question]- Зачем Watchdog-алерт?
> Он всегда в состоянии firing; если внешний приёмник перестал его получать, значит, сломан сам конвейер мониторинга и алертинга.
