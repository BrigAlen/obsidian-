---
type: topic
domain: devops
stage: 7
order: 3
status: todo
level: middle+
tags: [domain/devops, stage/7, level/middle+, priority/should]
reviewed: 
next_review: 
priority: should
time: 6
---

# Grafana: дашборды, источники (Prometheus, ClickHouse, Loki), алерты

↑ [[DO Этап 7 · Observability и эксплуатация|Этап 7 · Observability и эксплуатация]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~6 мин чтения</span><span class="chip">Уровень: middle+</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> Grafana — витрина данных мониторинга. Нужны дашборды «по делу», источники данных, алерты и provisioning как код.

## Возможности

Визуализация метрик, логов и трейсов из разных источников в одном интерфейсе, дашборды, алерты, аннотации, explore, совместное использование и разграничение доступа.

### Источники данных (data sources)

| Источник | Для чего |
|---|---|
| **Prometheus / VictoriaMetrics / Mimir / Thanos** | метрики (PromQL) |
| **Loki** | логи (LogQL) |
| **Tempo / Jaeger** | трассировки |
| **ClickHouse** (плагин) | аналитика, логи/трейсы OTel, бизнес-данные (SQL) |
| **PostgreSQL / MySQL / MSSQL** | бизнес-метрики из БД |
| **Elasticsearch / OpenSearch** | логи и поиск |
| **CloudWatch, Azure Monitor, Google Cloud** | облачные метрики |
| **InfluxDB, Graphite, Zabbix** | другие TSDB |
| **Pyroscope** | профили |

Настройка: URL, авторизация, **права только на чтение** (отдельный пользователь/токен с минимальными правами), таймауты, `Default`.

## Дашборды

Панели (Time series, Stat, Gauge, Bar, Table, Heatmap, Logs, Traces, State timeline) + строки + **переменные** (`$env`, `$service`, `$instance`, `$__interval`, `$__rate_interval`) + аннотации (релизы, инциденты).

```promql
# панель: RPS по сервису, выбранный $service
sum by (route) (rate(http_server_request_duration_seconds_count{service="$service"}[$__rate_interval]))
# p95
histogram_quantile(0.95, sum by (le) (rate(http_server_request_duration_seconds_bucket{service="$service"}[$__rate_interval])))
```

Переменные: Query (`label_values(up, instance)`), Custom, Interval, Datasource, Constant, Text; **Multi-value/All**, зависимость между переменными (цепочка env → service → pod).

**Хороший дашборд**: отвечает на вопрос (не «всё подряд»), сверху — обобщение (SLO, золотые сигналы, **RED/USE**), ниже — детали; единицы и пороги; одинаковые оси и цвета; ссылки (drill-down на логи/трейсы/runbook); не более 15–20 панелей; осмысленные названия и описания; уровни: **обзор** → **сервис** → **инстанс/под**.

Готовые дашборды: Node Exporter Full (ID 1860), Kubernetes (15757…), PostgreSQL (9628), Nginx, ClickHouse, Loki, cAdvisor; импорт по ID (`Dashboards → Import`) с последующей адаптацией.

## Логи и трейсы в Grafana

**Explore** и панели Logs: запросы LogQL (Loki), ClickHouse SQL; **связь**: derived fields по `trace_id` → открыть трейс в Tempo; из трейса — логи по `trace_id`; метрики → примеры (**exemplars**) ведут на трейсы; «Correlations».

```text
{namespace="clinic", app="api"} |= "error" | json | level="error" | line_format "{{.message}} trace={{.trace_id}}"
sum by (app) (rate({namespace="clinic"} |= "error" [5m]))
```

## Alerting (Grafana Alerting)

Правила по любым источникам: выражение → условие → `for` → метки → контактные точки.

- **Alert rules** (запросы + Reduce/Math/Threshold), состояния Normal/Pending/Firing/NoData/Error;
- **Notification policies**: маршрутизация по меткам (`severity`, `team`), группировка, повторы, mute timings (окна тишины);
- **Contact points**: Telegram, Slack, email, PagerDuty, Opsgenie, webhook;
- **Silences**, шаблоны сообщений с ссылками на дашборд и runbook;
- **Multi-dimensional alerts**: одно правило создаёт экземпляры на каждую серию;
- в смешанных окружениях часто: **Prometheus rules + Alertmanager** для инфраструктуры и Grafana alerts для источников без PromQL (ClickHouse, SQL, облака).

Принципы: алертить на **симптомы** (влияние на пользователя) и критичные причины, с `for:` и понятным действием, ссылкой на runbook; избегать шума.

## Provisioning как код

Дашборды, источники данных, алерты — **в Git**, а не кликами.

```yaml
# provisioning/datasources/ds.yaml
apiVersion: 1
datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    jsonData: { timeInterval: 30s, exemplarTraceIdDestinations: [{ name: trace_id, datasourceUid: tempo }] }
  - name: ClickHouse
    type: grafana-clickhouse-datasource
    jsonData: { host: clickhouse, port: 9000, username: grafana_ro, defaultDatabase: otel }
    secureJsonData: { password: "${CLICKHOUSE_PASSWORD}" }
  - { name: Loki, type: loki, url: "http://loki:3100", uid: loki }
```

```yaml
# provisioning/dashboards/dash.yaml
apiVersion: 1
providers:
  - { name: clinic, folder: Clinic, type: file, options: { path: /var/lib/grafana/dashboards }, allowUiUpdates: false }
```

Способы хранения дашбордов: JSON в репозитории, **grafonnet/Jsonnet**, **Grafana Terraform provider**, **Grafana Operator** (Kubernetes CRD), Helm (`kube-prometheus-stack` — sidecar загружает ConfigMap с меткой `grafana_dashboard: "1"`). Экспорт JSON — «Share → Export → for sharing externally».

## Доступ и безопасность

- **аутентификация**: локальная, **OIDC/SSO (Keycloak)**, LDAP; отключить анонимный доступ и регистрацию; **роли** (Admin/Editor/Viewer), **организации** и **команды**, папки с правами; service accounts и API-токены для автоматизации;
- секреты источников хранить в `secureJsonData`/переменных окружения;
- за reverse proxy с TLS (`root_url`, `serve_from_sub_path`); заголовки безопасности; ограничение iframe/публичных снапшотов;
- SQL-источники: пользователь read-only, ограничения на тяжёлые запросы (таймауты, лимиты);
- персональные данные в панелях логов — маскирование, ограничение доступа.

## Эксплуатация

- **хранение**: БД Grafana (SQLite по умолчанию; для HA — PostgreSQL/MySQL), бэкапы;
- **HA**: несколько инстансов + внешняя БД + общий LB;
- версии: обновления, плагины фиксировать (`GF_INSTALL_PLUGINS`);
- мониторинг самой Grafana (`/metrics`);
- производительность: лёгкие запросы, `$__interval`, лимит точек, кэширование, recording rules в Prometheus для тяжёлых панелей, `min interval`;
- **стандартизация**: папки по командам, общие шаблоны дашбордов, соглашения об именах, владельцы, описание, теги; регулярный аудит неиспользуемых дашбордов.

## Dashboards as code: подход «сервис из коробки»

Шаблон дашборда сервиса (RED + ресурсы + логи + трейсы) создаётся автоматически для каждого нового сервиса (Jsonnet/Helm) — единый стандарт и быстрый старт.

## Вопросы с ответами

> [!question]- Зачем provisioning дашбордов и источников?
> Конфигурация хранится в Git, воспроизводима, проходит ревью и одинакова во всех окружениях; нет расхождений из-за ручных правок в UI.

> [!question]- Как в Grafana связать метрики, логи и трейсы?
> Общие метки и `trace_id`: derived fields в Loki ведут на трейс в Tempo, из трейса — обратно к логам; exemplars в метриках ссылаются на конкретные трейсы.

> [!question]- Когда использовать Grafana Alerting, а когда Prometheus rules?
> Prometheus/Alertmanager — для метрик Prometheus (версионируемые правила, высокая надёжность); Grafana Alerting — для алертов по разным источникам (ClickHouse, SQL, логи) и единой маршрутизации.
