---
type: topic
domain: devops
stage: 7
order: 1
status: todo
level: middle+
tags: [domain/devops, stage/7, level/middle+, priority/should]
reviewed: 
next_review: 
priority: should
time: 7
---

# Метрики: Prometheus, типы метрик, PromQL

↑ [[DO Этап 7 · Observability и эксплуатация|Этап 7 · Observability и эксплуатация]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~7 мин чтения</span><span class="chip">Уровень: middle+</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> Prometheus — стандарт метрик. Нужно знать pull-модель, типы метрик и уверенно писать PromQL.

## Наблюдаемость: три столпа

**Метрики** (числа во времени: «что происходит»), **логи** (события: «что именно случилось»), **трассировки** (путь запроса: «где и почему медленно»). Плюс события, профили. Метрики дёшевы и подходят для алертов и дашбордов.

## Prometheus

Система мониторинга и TSDB (time-series database): **pull-модель** — сервер сам опрашивает цели по HTTP (`/metrics`) с интервалом (scrape_interval, 15–60 с).

```text
Targets (/metrics) ◀─scrape─ Prometheus ─┬─▶ Alertmanager ─▶ Telegram/Slack/PagerDuty/email
(exporters, приложения)      (TSDB, PromQL, rules)  └─▶ Grafana (запросы)
Service discovery: static, file_sd, Kubernetes, Consul, DNS, EC2
```

```yaml
# prometheus.yml
global: { scrape_interval: 30s, evaluation_interval: 30s, external_labels: { cluster: prod } }
rule_files: [/etc/prometheus/rules/*.yml]
alerting: { alertmanagers: [{ static_configs: [{ targets: ["alertmanager:9093"] }] }] }
scrape_configs:
  - job_name: node
    static_configs: [{ targets: ["10.0.1.11:9100", "10.0.1.12:9100"], labels: { env: prod } }]
  - job_name: api
    metrics_path: /metrics
    kubernetes_sd_configs: [{ role: pod }]
    relabel_configs:
      - { source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape], regex: "true", action: keep }
```

Pull vs push: pull упрощает обнаружение недоступных целей (`up == 0`) и управление; для краткоживущих задач — **Pushgateway** (только для batch-джобов), удалённая запись (`remote_write`) для агентов (Grafana Agent/Alloy, vmagent, OTel Collector).

Модель данных: **серия** = имя метрики + набор **меток (labels)** + (timestamp, value).

```text
http_requests_total{method="GET", route="/api/orders", status="200", job="api", instance="10.0.1.5:8080"} 15234
```

## Типы метрик

| Тип | Описание | Пример | Как использовать |
|---|---|---|---|
| **Counter** | монотонно растёт (сброс при рестарте) | `http_requests_total`, `errors_total` | `rate()`, `increase()` |
| **Gauge** | значение вверх/вниз | `memory_bytes`, `queue_length`, `temperature` | напрямую, `avg_over_time` |
| **Histogram** | распределение по **корзинам** (`_bucket{le=}`, `_sum`, `_count`) | `http_request_duration_seconds` | `histogram_quantile()`; агрегируется между инстансами |
| **Summary** | квантили на клиенте (`{quantile="0.99"}`) | | не агрегируется; реже используется |

Нативные (sparse) histograms — экономичнее. **Кардинальность**: каждая уникальная комбинация значений меток = отдельная серия; метки `user_id`, `url` с произвольными значениями, `request_id` **взрывают** память. Метки — ограниченные множества (метод, статус, route-шаблон, сервис).

## PromQL

**Селекторы**

```promql
http_requests_total                                   # мгновенный вектор
http_requests_total{job="api", status=~"5..", route!="/health"}   # =, !=, =~, !~ (regex)
http_requests_total[5m]                               # диапазонный вектор
http_requests_total offset 1h                         # сдвиг по времени
```

**Функции для counter**

```promql
rate(http_requests_total[5m])             # среднесекундная скорость за окно (по каждой серии)
increase(http_requests_total[1h])         # прирост за окно
irate(...)                                # мгновенная (по двум последним точкам) — для графиков «нервных» метрик
```

**Агрегации** (`sum`, `avg`, `min`, `max`, `count`, `topk`, `bottomk`, `quantile`) с `by` / `without`:

```promql
sum by (route) (rate(http_requests_total[5m]))
topk(5, sum by (pod) (rate(container_cpu_usage_seconds_total[5m])))
```

**Ошибки (доля)**

```promql
sum(rate(http_requests_total{status=~"5.."}[5m])) / sum(rate(http_requests_total[5m]))
```

**Квантили из histogram**

```promql
histogram_quantile(0.95, sum by (le, route) (rate(http_request_duration_seconds_bucket[5m])))
```

**Gauge**

```promql
avg_over_time(queue_length[10m]); max_over_time(...); delta(memory_bytes[1h]); deriv(disk_used_bytes[1h]); predict_linear(node_filesystem_avail_bytes[6h], 24*3600) < 0
```

**Операции с векторами**: арифметика и сравнение с сопоставлением меток (`on(...)`, `ignoring(...)`, `group_left`), `and`/`or`/`unless`, `absent()` (метрики нет), `up == 0`, `label_replace`, `clamp_min`, подзапросы `[30m:1m]`.

**Recording rules**: предрасчёт тяжёлых выражений: 

```yaml
groups:
  - name: api
    rules:
      - record: route:http_requests:rate5m
        expr: sum by (route) (rate(http_requests_total[5m]))
      - alert: HighErrorRatio
        expr: sum(rate(http_requests_total{status=~"5.."}[5m])) / sum(rate(http_requests_total[5m])) > 0.05
        for: 10m
        labels: { severity: critical }
        annotations: { summary: "Доля 5xx {{ $value | humanizePercentage }}", runbook_url: "https://wiki/rb/api-5xx" }
```

## Инструментация приложения

**.NET**: OpenTelemetry metrics + Prometheus exporter (`OpenTelemetry.Exporter.Prometheus.AspNetCore`) или `prometheus-net`; встроенные метрики рантайма (GC, пул потоков, HTTP-сервер: `http.server.request.duration`).

```csharp
builder.Services.AddOpenTelemetry().WithMetrics(m => m
    .AddAspNetCoreInstrumentation().AddRuntimeInstrumentation().AddMeter("Clinic.Orders")
    .AddPrometheusExporter());
app.MapPrometheusScrapingEndpoint();           // /metrics

var meter = new Meter("Clinic.Orders");
var created = meter.CreateCounter<long>("orders_created_total");
created.Add(1, new KeyValuePair<string, object?>("channel", "web"));
```

Что измерять: методы **RED** для сервисов (**R**ate, **E**rrors, **D**uration), **USE** для ресурсов (**U**tilization, **S**aturation, **E**rrors), **четыре золотых сигнала** (latency, traffic, errors, saturation), бизнес-метрики (заказы, платежи).

Именование: `snake_case`, единицы в имени (`_seconds`, `_bytes`), суффикс `_total` для counter, префикс по приложению.

## Хранение и масштабирование

- TSDB локально: блоки по 2 часа, WAL, retention (`--storage.tsdb.retention.time=15d`); память пропорциональна числу активных серий;
- один Prometheus не масштабируется горизонтально: **федерация**, **шардирование** по целям, **Thanos / Cortex / Mimir / VictoriaMetrics** (долговременное хранение, глобальный вид, HA, дедупликация);
- HA: два одинаковых Prometheus (external_labels `replica`), Alertmanager в кластере;
- контроль: `prometheus_tsdb_head_series`, `scrape_samples_scraped`, `topk(10, count by (__name__)({__name__=~".+"}))`; **`metric_relabel_configs`** для отбрасывания лишнего; `sample_limit`.

## Kubernetes

**Prometheus Operator / kube-prometheus-stack**: CRD `ServiceMonitor`, `PodMonitor`, `PrometheusRule`, `Probe`; автоматическое обнаружение; готовые дашборды и правила.

## Практики и подводные камни

- `rate()` требует окно ≥ 4 × scrape interval; не применять `rate` к gauge; `rate` от `sum` ошибочно (сначала `rate`, потом `sum`);
- `histogram_quantile` — оценка по корзинам: подбирайте границы под SLO; усреднение квантилей неверно;
- сброс counter при рестарте учитывается в `rate`; «дыры» (`up==0`) — алерт;
- `for:` в алертах (устойчивость) и **алерт на симптомы**;
- не хранить секреты в метках; защита `/metrics` (NetworkPolicy, аутентификация), не раскрывать внутренности наружу;
- **Staleness**: исчезнувшие серии помечаются устаревшими;
- **время**: синхронизация часов (NTP), UTC;
- документирование метрик, стандарты меток между сервисами.

## Вопросы с ответами

> [!question]- Pull или push: как работает Prometheus?
> Prometheus сам опрашивает цели по HTTP (pull), что упрощает обнаружение недоступных узлов (`up`) и централизованное управление; push через Pushgateway допустим лишь для краткоживущих задач.

> [!question]- Чем counter отличается от gauge и как работать с counter?
> Counter только растёт и сбрасывается при рестарте; его используют через `rate()`/`increase()`. Gauge меняется вверх и вниз и читается напрямую.

> [!question]- Что такое кардинальность и почему она опасна?
> Число уникальных комбинаций меток (серий). Высококардинальные метки (user_id, URL) раздувают память и замедляют Prometheus, поэтому метки ограничивают небольшими множествами.
