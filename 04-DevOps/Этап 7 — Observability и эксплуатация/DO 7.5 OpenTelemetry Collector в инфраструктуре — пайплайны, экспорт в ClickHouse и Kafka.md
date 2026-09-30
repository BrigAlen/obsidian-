---
type: topic
domain: devops
stage: 7
order: 5
status: todo
level: middle+
tags: [domain/devops, stage/7, level/middle+, priority/should]
reviewed: 
next_review: 
priority: should
time: 9
---

# OpenTelemetry Collector в инфраструктуре: пайплайны, экспорт в ClickHouse и Kafka

↑ [[DO Этап 7 · Observability и эксплуатация|Этап 7 · Observability и эксплуатация]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~9 мин чтения</span><span class="chip">Уровень: middle+</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> OTel Collector — центральный узел телеметрии: приём, обработка и маршрутизация метрик, логов и трейсов; связка с ClickHouse и Kafka.

## OpenTelemetry

Открытый стандарт и набор инструментов (CNCF) для **метрик, логов и трассировок**: спецификация, SDK, инструментация, протокол **OTLP** (gRPC `:4317`, HTTP `:4318`), семантические соглашения (`service.name`, `http.route`, `db.system`). Вендор-нейтрален: можно сменить бэкенд без изменения кода.

## Collector

Независимый процесс: **receivers → processors → exporters**, соединяются в **pipelines** для каждого сигнала.

```text
Приложения (OTel SDK, OTLP) ─┐
Prometheus scrape ───────────┼─▶ [Receivers] → [Processors] → [Exporters] ─▶ Tempo / Prometheus(remote write) / Loki / ClickHouse / Kafka / SaaS
Файлы логов, syslog ─────────┘                 (batch, filter, attributes, tail_sampling)
```

Зачем Collector, а не прямой экспорт из приложения: **развязка** (приложение не знает бэкенд), буферизация и повторы, единая обработка (обогащение, фильтрация, маскирование, семплирование), маршрутизация в несколько бэкендов, снижение нагрузки на приложения, централизованное управление ключами/аутентификацией, сбор из не-OTel источников.

Дистрибутивы: **otelcol** (core), **otelcol-contrib** (много компонентов), свои сборки (**ocb** — OpenTelemetry Collector Builder), Grafana Alloy, vendor-дистрибутивы.

## Конфигурация

```yaml
receivers:
  otlp:
    protocols: { grpc: { endpoint: 0.0.0.0:4317 }, http: { endpoint: 0.0.0.0:4318 } }
  prometheus:                                   # сбор метрик как Prometheus
    config: { scrape_configs: [{ job_name: node, scrape_interval: 30s, static_configs: [{ targets: ["localhost:9100"] }] }] }
  filelog:                                      # логи из файлов (nginx, контейнеров)
    include: [/var/log/nginx/access.json]
    operators: [{ type: json_parser, timestamp: { parse_from: attributes.time, layout: "%Y-%m-%dT%H:%M:%S%z" } }]
  hostmetrics: { collection_interval: 30s, scrapers: { cpu: {}, memory: {}, disk: {}, filesystem: {}, network: {} } }

processors:
  memory_limiter: { check_interval: 1s, limit_percentage: 80, spike_limit_percentage: 20 }     # ПЕРВЫМ в цепочке
  resourcedetection: { detectors: [env, system, docker, k8snode] }
  k8sattributes: { extract: { metadata: [k8s.namespace.name, k8s.pod.name, k8s.deployment.name] } }
  attributes/scrub:
    actions: [{ key: http.request.header.authorization, action: delete }, { key: user.email, action: hash }]
  filter/drop_health:
    error_mode: ignore
    traces: { span: ['attributes["http.route"] == "/health"'] }
  tail_sampling:                                 # хранить все ошибки и медленные, остальное 10%
    decision_wait: 10s
    policies:
      - { name: errors,  type: status_code, status_code: { status_codes: [ERROR] } }
      - { name: slow,    type: latency, latency: { threshold_ms: 1000 } }
      - { name: sample,  type: probabilistic, probabilistic: { sampling_percentage: 10 } }
  batch: { timeout: 5s, send_batch_size: 8192 }                                              # ПОСЛЕДНИМ

exporters:
  clickhouse:
    endpoint: tcp://clickhouse:9000?dial_timeout=10s
    database: otel
    username: otel_writer
    password: ${env:CH_PASSWORD}
    ttl: 72h
    create_schema: true
    timeout: 5s
    retry_on_failure: { enabled: true, initial_interval: 5s, max_interval: 30s, max_elapsed_time: 300s }
    sending_queue: { enabled: true, queue_size: 2000 }
  kafka:
    brokers: [kafka:9092]
    topic: otel-traces
    encoding: otlp_proto
    producer: { compression: zstd }
  prometheusremotewrite: { endpoint: http://mimir:9009/api/v1/push }
  otlp/tempo: { endpoint: tempo:4317, tls: { insecure: true } }
  debug: { verbosity: basic }

extensions:
  health_check: { endpoint: 0.0.0.0:13133 }
  pprof: { endpoint: localhost:1777 }

service:
  extensions: [health_check]
  pipelines:
    traces:  { receivers: [otlp], processors: [memory_limiter, k8sattributes, filter/drop_health, tail_sampling, batch], exporters: [clickhouse, otlp/tempo] }
    metrics: { receivers: [otlp, prometheus, hostmetrics], processors: [memory_limiter, resourcedetection, batch], exporters: [prometheusremotewrite, clickhouse] }
    logs:    { receivers: [otlp, filelog], processors: [memory_limiter, k8sattributes, attributes/scrub, batch], exporters: [clickhouse] }
  telemetry: { logs: { level: info }, metrics: { address: 0.0.0.0:8888 } }
```

Важные процессоры: `memory_limiter` (защита от OOM), `batch` (эффективная отправка), `resource`/`resourcedetection`/`k8sattributes` (обогащение), `attributes`/`transform` (OTTL: изменение/удаление/хэширование), `filter`, `tail_sampling`, `probabilistic_sampler`, `groupbytrace`, `routing`, `redaction`.

## Схемы развёртывания

| Схема | Описание | Применение |
|---|---|---|
| **Agent** (sidecar/DaemonSet на каждом узле) | локальный Collector рядом с приложением | быстрый приём, обогащение метаданными узла, логи файлов, hostmetrics |
| **Gateway** (центральный кластер за LB) | общий слой обработки | tail sampling, маршрутизация, политики, ограничение доступа к бэкенду, масштабирование |
| **Agent → Gateway** (две ступени) | типовая промышленная схема | |
| **С очередью (Kafka)** между | буфер, устойчивость к сбоям бэкенда, реплей | высокие объёмы, требования к надёжности |

**Tail sampling** требует, чтобы все спаны одного трейса попали на один экземпляр (балансировка по `trace_id`: `loadbalancing` exporter), поэтому размещается в Gateway.

## Экспорт в ClickHouse

Официальный `clickhouseexporter` создаёт таблицы `otel_logs`, `otel_traces`, `otel_metrics_*` (sum/gauge/histogram/…): партиционирование по дню, ключи сортировки по сервису и времени, `Map(LowCardinality(String), String)` для атрибутов, TTL, bloom-фильтры по `TraceId`.

```sql
SELECT ServiceName, count() AS spans, quantile(0.95)(Duration) / 1e6 AS p95_ms
FROM otel.otel_traces WHERE Timestamp >= now() - INTERVAL 1 HOUR AND StatusCode = 'Error'
GROUP BY ServiceName ORDER BY spans DESC;
```

Визуализация: Grafana (плагин ClickHouse), **SigNoz**, **HyperDX / ClickStack**, **Uptrace**. Советы: пакетная вставка (batch процессор + `sending_queue`), TTL для экономии места, отдельный пользователь на запись, схема/миграции управляются осознанно (`create_schema: false` в проде), мониторинг частей (parts) и слияний.

## Экспорт в Kafka

Буфер и шина: Collector-агенты пишут в Kafka (`kafka` exporter, топики по сигналам), другой Collector (Gateway) читает (`kafka` receiver) и пишет в бэкенды. Плюсы: развязка, переживает недоступность ClickHouse/Loki, возможность повторной обработки, несколько потребителей, сглаживание пиков. Минусы: дополнительная инфраструктура и задержка. Кодирование `otlp_proto`, сжатие `zstd/snappy`, партиции по `trace_id`/ключу.

## Автоинструментация и SDK

- **.NET**: `OpenTelemetry.Extensions.Hosting`, `AddAspNetCoreInstrumentation`, `AddHttpClientInstrumentation`, `AddNpgsql`, `AddSource("Clinic")`, экспортёр OTLP (`OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4317`, `OTEL_SERVICE_NAME`, `OTEL_RESOURCE_ATTRIBUTES=deployment.environment=prod,service.version=1.4.2`); **zero-code** автоинструментация (переменные окружения, CLR profiler);
- **Kubernetes Operator**: `Instrumentation` CRD + аннотация `instrumentation.opentelemetry.io/inject-dotnet: "true"`; `OpenTelemetryCollector` CRD (режимы deployment/daemonset/sidecar/statefulset), Target Allocator для Prometheus;
- **Frontend**: OTel JS для браузера (RUM), `traceparent` в запросах;
- **контекст**: W3C Trace Context (`traceparent`) + Baggage через HTTP/gRPC/очереди (Kafka headers) — сквозные трейсы.

## Надёжность и производительность Collector

- `memory_limiter` + `batch`, лимиты ресурсов контейнера, `sending_queue` с персистентностью (`file_storage` extension) для переживания рестартов;
- горизонтальное масштабирование Gateway (stateless, кроме tail sampling);
- мониторинг Collector: метрики `otelcol_receiver_accepted_spans`, `otelcol_exporter_send_failed_*`, `otelcol_exporter_queue_size`, `otelcol_processor_*_dropped`; **health_check**, `zpages`;
- конфигурация через Ansible/Helm/Operator, валидация (`otelcol validate --config`), версия Collector совместима с SDK;
- безопасность: TLS/mTLS на OTLP, аутентификация (`bearertokenauth`, OIDC), изоляция сети, удаление секретов/ПДн процессорами, права ClickHouse-пользователя.

## Вопросы с ответами

> [!question]- Зачем нужен Collector, если SDK может экспортировать напрямую?
> Collector развязывает приложения и бэкенды, буферизует и повторяет отправку, централизует обработку (обогащение, фильтрация, семплирование, маскирование), позволяет маршрутизировать в несколько систем и менять бэкенд без изменения кода.

> [!question]- Что такое tail sampling и какие у него требования?
> Решение о сохранении трейса принимается после получения всех его спанов (например, хранить все с ошибками и медленные). Требует, чтобы спаны одного трейса попали на один экземпляр, поэтому размещается в Gateway с балансировкой по `trace_id`.

> [!question]- Зачем Kafka между Collector и хранилищем?
> Буфер и развязка: при недоступности ClickHouse данные не теряются, возможен реплей и несколько потребителей, сглаживаются пики нагрузки.
