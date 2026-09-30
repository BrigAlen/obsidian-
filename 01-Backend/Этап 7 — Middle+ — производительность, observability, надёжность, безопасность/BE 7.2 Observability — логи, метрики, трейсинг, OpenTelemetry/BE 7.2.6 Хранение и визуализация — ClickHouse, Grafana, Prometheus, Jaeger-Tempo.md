---
type: topic
domain: backend
stage: 7
section: "7.2"
order: 6
status: todo
level: senior
notion_id: 3ea33104867981869027f9a72bdd9a33
tags: [domain/backend, stage/7, level/senior, topic/observability, topic/storage, topic/grafana, priority/should]
reviewed:
next_review:
priority: should
time: 3
---

# Хранение и визуализация: ClickHouse, Grafana, Prometheus, Jaeger/Tempo

↑ [[BE 7.2 Observability — логи, метрики, трейсинг, OpenTelemetry|7.2 Observability: логи, метрики, трейсинг, OpenTelemetry]] · ← [[BE 7.2.5 OTLP и OpenTelemetry Collector — receivers, processors, exporters|Предыдущая]] · → [[BE 7.2.7 Метрики и SLO — RED, USE, алерты|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: senior</span></div>
<!-- meta:end -->







> [!info] Зачем это на собесе
> Какие хранилища подходят под какие сигналы и как строят дашборды.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

| Сигнал | Хранилище | Визуализация |
|---|---|---|
| Метрики | Prometheus (pull), VictoriaMetrics, Mimir (долгое хранение) | Grafana |
| Логи | Loki (индексирует только метки), Elasticsearch/OpenSearch, ClickHouse | Grafana, Kibana |
| Трейсы | Tempo (объектное хранилище), Jaeger (Elasticsearch/Cassandra), ClickHouse | Grafana, Jaeger UI |
| Профили | Pyroscope, Parca | Grafana |

**Prometheus**: собирает метрики по HTTP (`/metrics`), язык запросов PromQL.

```promql
sum(rate(http_server_request_duration_seconds_count{status=~"5.."}[5m])) / sum(rate(http_server_request_duration_seconds_count[5m]))   # доля ошибок
histogram_quantile(0.95, sum by (le) (rate(http_server_request_duration_seconds_bucket[5m])))                                            # p95
```

**ClickHouse** как единое хранилище логов/трейсов/метрик (например, SigNoz, HyperDX, Uptrace): колоночное сжатие и быстрые агрегаты по огромным объёмам.

**Grafana**: дашборды, алерты, связь сигналов (переход от метрики к трейсу через exemplars, от лога к трейсу по `trace_id`).

Хорошие дашборды: по методу RED для сервисов и USE для ресурсов (см. [[N:3ea3310486798118bb10cd40be47fd97]]), ссылки на runbook.

## Нюансы и подводные камни

- Кардинальность меток в Prometheus — главная причина падений.
- Retention и стоимость хранения: горячие и холодные данные, агрегирование (recording rules).
- Дашборд без вывода — украшение: каждому графику нужен вопрос, на который он отвечает.
- Хранилище и агент сбора надо мониторить отдельно.

## Практика

1. Соберите стек Prometheus + Grafana + Tempo + Loki в Docker Compose.
2. Постройте RED-дашборд сервиса.
3. Настройте переход от метрики к трейсу и логу.

## Вопросы с ответами

> [!question]- Prometheus использует pull или push?
> Pull: опрашивает `/metrics` целей; для коротких задач применяется Pushgateway.

> [!question]- Почему ClickHouse подходит для телеметрии?
> Колоночное хранение и сжатие дают быстрые агрегаты и дешёвое хранение больших объёмов.

## Связанные темы

- [[N:3ea33104867981b2897cdf14acc698c7]]
- [[N:3ea3310486798118bb10cd40be47fd97]]
