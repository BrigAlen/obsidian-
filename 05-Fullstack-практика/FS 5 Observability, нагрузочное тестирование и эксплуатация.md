---
type: topic
domain: fullstack
stage: 0
order: 5
notion_id: e5df04d244b64f3799529d9666e3c2c6
status: todo
level: middle+
tags: [domain/fullstack, kind/project, level/middle+, priority/should]
priority: should
time: 7
---

# Observability, нагрузочное тестирование и эксплуатация

↑ [[FS Fullstack-практика]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~7 мин чтения</span><span class="chip">Уровень: middle+</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> Без наблюдаемости невозможно эксплуатировать сервис. Важно показать цепочку: метрики, логи, трассы, SLO, алерты и нагрузочные тесты.

## Цель

Сделать проект Clinic наблюдаемым и проверенным под нагрузкой: собирать метрики, логи и трассировки, построить дашборды и алерты по SLO, провести нагрузочное тестирование, найти узкие места и подготовить runbook'и эксплуатации.

## Три столпа и корреляция

```text
.NET API / Worker / SPA (OTel) ──OTLP──▶ OTel Collector ─┬─▶ Prometheus (метрики)  ─┐
nginx/Ingress, контейнеры ───────────────────────────────┼─▶ Loki (логи)          ─┼▶ Grafana ─▶ Alertmanager ─▶ Telegram/PagerDuty
PostgreSQL/Redis/Keycloak (exporters) ───────────────────┴─▶ Tempo (трассы)       ─┘
```

Связка по **`trace_id`**: лог → трейс, метрика → exemplar → трейс, трейс → логи.

## Инструментация приложения

**.NET (OpenTelemetry)**:

```csharp
builder.Services.AddOpenTelemetry()
  .ConfigureResource(r => r.AddService("clinic-api", serviceVersion: Version).AddAttributes([new("deployment.environment", env)]))
  .WithTracing(t => t.AddAspNetCoreInstrumentation().AddHttpClientInstrumentation().AddNpgsql().AddRedisInstrumentation().AddSource("Clinic")
      .SetSampler(new ParentBasedSampler(new TraceIdRatioBasedSampler(0.1))).AddOtlpExporter())
  .WithMetrics(m => m.AddAspNetCoreInstrumentation().AddRuntimeInstrumentation().AddMeter("Clinic").AddOtlpExporter());
builder.Logging.AddOpenTelemetry(o => { o.IncludeScopes = true; o.AddOtlpExporter(); });
```

**Бизнес-метрики**: `appointments_booked_total{result="success|conflict"}`, `slot_booking_duration_seconds`, `outbox_pending_messages`, `notifications_sent_total{channel,status}`, `active_patients`.

**Структурированные логи** (JSON, Serilog/OTel): `trace_id`, `span_id`, уровень, `user_id` (псевдонимизированный), без ПДн и токенов; шаблоны сообщений без интерполяции.

**Frontend**: OTel JS (web vitals, ошибки, `traceparent` в запросах), Sentry для JS-ошибок и release health; **RUM-метрики** LCP/INP/CLS.

**Инфраструктура**: node_exporter, cAdvisor/kube-state-metrics, postgres_exporter, redis_exporter, nginx-exporter/Ingress метрики, blackbox (доступность и TLS).

## Дашборды

1. **Service overview (RED)**: RPS, доля ошибок, p50/p95/p99, по `route`; статус SLO и остаток error budget.
2. **Бизнес**: записи по времени, конфликты слотов, отмены, конверсия воронки.
3. **Зависимости**: PostgreSQL (соединения, блокировки, медленные запросы, репликация), Redis (hit ratio), очередь outbox (лаг), внешние провайдеры уведомлений.
4. **Ресурсы (USE)**: CPU/память/GC/пул потоков .NET, троттлинг, диски, сеть.
5. **Frontend**: Web Vitals, JS-ошибки, crash-free sessions.
6. **Релизы**: аннотации деплоев, сравнение версий (canary).

Принципы: обзор → детали, общие переменные (`$env`, `$service`), ссылки на логи/трассы/runbook, provisioning как код.

## SLO и алерты

```promql
# SLI доступности API (не 5xx)
sum(rate(http_server_request_duration_seconds_count{service="clinic-api",http_response_status_code!~"5.."}[5m]))
/ sum(rate(http_server_request_duration_seconds_count{service="clinic-api"}[5m]))
```

- **SLO 99.9%/30 дней**, алерты по **burn rate** (быстрое: 14.4× за 1 ч и 5 мин — page; медленное: 3× за 1 сут — ticket);
- латентность: доля запросов < 500 мс ≥ 95%;
- причинные алерты с запасом (диск заполнится за 24 ч, лаг outbox > 1 мин, пул соединений БД > 80%, реплика отстаёт, срок TLS < 14 дней, `up == 0`, CrashLoopBackOff);
- маршрутизация (`severity`, `team`), ингибирование, `for:`, ссылки на runbook, **Watchdog**;
- тесты правил (`promtool test rules`).

## Нагрузочное тестирование

**Цели**: проверить SLO, найти пределы и узкие места, оценить ёмкость, убедиться в устойчивости (конкурентное бронирование, пики, деградация).

Типы: **smoke** (минимальная нагрузка), **load** (ожидаемая), **stress** (до отказа), **spike** (резкий скачок), **soak** (длительная, утечки), сценарии **конкурентности** (тысячи запросов на ограниченные слоты).

```js
// k6: сценарий утреннего пика записи
import http from 'k6/http'
import { check, sleep } from 'k6'
import { uuidv4 } from 'https://jslib.k6.io/k6-utils/1.4.0/index.js'

export const options = {
  scenarios: {
    morning_peak: { executor: 'ramping-arrival-rate', startRate: 10, timeUnit: '1s', preAllocatedVUs: 200, maxVUs: 600,
      stages: [{ target: 100, duration: '2m' }, { target: 200, duration: '5m' }, { target: 0, duration: '1m' }] },
  },
  thresholds: { http_req_failed: ['rate<0.01'], 'http_req_duration{name:book}': ['p(95)<500'], 'http_req_duration{name:catalog}': ['p(95)<300'] },
}

export default function () {
  const headers = { Authorization: `Bearer ${__ENV.TOKEN}`, 'Idempotency-Key': uuidv4(), 'Content-Type': 'application/json' }
  const cat = http.get(`${__ENV.BASE}/api/v1/doctors?limit=20`, { headers, tags: { name: 'catalog' } })
  check(cat, { 'каталог 200': r => r.status === 200 })
  const slot = 1 + Math.floor(Math.random() * 5000)
  const res = http.post(`${__ENV.BASE}/api/v1/appointments`, JSON.stringify({ slotId: slot }), { headers, tags: { name: 'book' } })
  check(res, { 'запись 201 или 409': r => [201, 409].includes(r.status) })
  sleep(1)
}
```

Практики: **реалистичные данные и распределения**, окружение, близкое к проду (staging), **прогрев**, изоляция нагрузочного генератора, **метрики во время теста** (Grafana) и **связка с трассами**, фиксированные пороги (thresholds) → тест падает при нарушении, запуск в CI по расписанию (nightly) и перед релизами, хранение результатов (k6 → Prometheus remote write/Grafana Cloud), сравнение с базовой линией.

**Анализ**: где насыщение — CPU API, пул соединений БД, блокировки на слотах, медленный запрос без индекса, GC, лимиты ingress; **как искать**: flame graph (`dotnet-trace`, Pyroscope), `pg_stat_statements`, `EXPLAIN (ANALYZE, BUFFERS)`, трассы медленных запросов, `wait_event`.

Типичные находки и решения: отсутствующий индекс/N+1 → индекс, `Include`/проекции; горячие строки слотов → оптимизация транзакции (короткая, условное UPDATE), очередь запросов; пул соединений → PgBouncer, лимиты; кэш каталога → Redis с TTL/jitter; синхронная отправка уведомлений → outbox/worker; неверные requests/limits → тюнинг; HPA на метрике RPS/очереди; rate limiting на edge.

**Ёмкость**: из теста получаем «N RPS на под/ядро», объём БД на запись, прогноз роста → план масштабирования и стоимость (FinOps).

## Эксплуатация

- **Runbook'и**: высокая доля 5xx, рост латентности, конфликт слотов аномально высок, очередь outbox растёт, недоступна БД/Redis/Keycloak, заполнение диска, истёк сертификат, откат релиза;
- **On-call**: ротация, эскалации, шаблон инцидента, канал, статус-страница;
- **Бэкапы и восстановление**: PostgreSQL (PITR), проверка восстановления по расписанию, отчёт RPO/RTO;
- **Регулярные процессы**: ревью алертов, SLO-ревью (ежемесячно), capacity review, обновления и патчи, ревью расходов;
- **Безопасность эксплуатации**: доступы по ролям, аудит, секреты, ретенция логов/ПДн.

## Что делаем

- [ ] OTel-инструментация API/Worker/SPA, бизнес-метрики, структурированные логи с `trace_id`;
- [ ] Развернуть Prometheus/Loki/Tempo/Grafana (kube-prometheus-stack) + OTel Collector, экспортёры;
- [ ] Дашборды (RED/USE/бизнес/релизы), provisioning как код;
- [ ] SLO-алерты (burn rate) и причинные алерты, маршрутизация, runbook-ссылки, тесты правил;
- [ ] k6-сценарии (smoke/load/stress/spike/soak + конкурентность слотов) с порогами;
- [ ] Запуск нагрузки, анализ узких мест, оптимизации и повторный замер (до/после);
- [ ] Runbooks и процесс on-call; проверка восстановления из бэкапа;
- [ ] Отчёт о ёмкости и план масштабирования.

## Результат / артефакты

- дашборды и правила алертов в репозитории; конфигурация OTel/Prometheus/Loki/Grafana (IaC);
- скрипты k6, отчёт нагрузочного тестирования (до/после оптимизаций, графики, выводы);
- набор runbook'ов, шаблон постмортема, график дежурств;
- документ по SLO и бюджету ошибок; отчёт по ёмкости и стоимости.

## Что рассказать на собесе

- как связаны метрики, логи и трассы и как за минуты найти причину ошибки пользователя по `trace_id`;
- как выбирали SLI/SLO и почему алертите по burn rate, а не по каждому всплеску;
- как проводили нагрузочное тестирование, что нашли (конкретное узкое место) и как измерили эффект оптимизации;
- как определяете ёмкость и когда масштабировать;
- как организованы дежурства, runbook'и и регулярные ревью алертов.
