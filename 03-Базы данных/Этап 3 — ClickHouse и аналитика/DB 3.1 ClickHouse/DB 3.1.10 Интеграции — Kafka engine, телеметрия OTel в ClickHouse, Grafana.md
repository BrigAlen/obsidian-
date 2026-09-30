---
type: topic
domain: db
stage: 3
section: "3.1"
order: 10
status: todo
level: middle
notion_id: 3ea331048679812882e8dbb8253d4486
tags: [domain/db, stage/3, level/middle, topic/clickhouse, topic/kafka, topic/opentelemetry, topic/grafana, priority/should]
reviewed:
next_review:
priority: should
time: 4
---

# Интеграции: Kafka engine, телеметрия OTel в ClickHouse, Grafana

↑ [[DB 3.1 ClickHouse|3.1 ClickHouse]] · ← [[DB 3.1.9 Запросы и оптимизация — агрегации, JOIN, FINAL, словари|Предыдущая]] · → [[DB 3.1.11 Репликация и шардирование — ReplicatedMergeTree, Distributed, Keeper|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~4 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> ClickHouse редко живёт сам: он получает данные из очередей и отдаёт в BI и observability.

## Kafka → ClickHouse

**Kafka Engine** — таблица-потребитель, читает топик; данные забираются материализованным представлением.

```sql
CREATE TABLE events_queue (ts DateTime, user_id UInt64, event_type String, value Float64)
ENGINE = Kafka
SETTINGS kafka_broker_list = 'kafka:9092', kafka_topic_list = 'events',
         kafka_group_name = 'ch-consumer', kafka_format = 'JSONEachRow',
         kafka_num_consumers = 2, kafka_max_block_size = 65536;

CREATE MATERIALIZED VIEW events_mv TO events AS
SELECT ts, user_id, event_type, value FROM events_queue;
```

Особенности: гарантия «как минимум один раз» (возможны дубли: используйте идемпотентность/ReplacingMergeTree), сложнее отладка, offset коммитятся после записи; ошибки разбора: `kafka_handle_error_mode = 'stream'`.

Альтернативы: **ClickPipes** (облако), **Kafka Connect ClickHouse Sink**, Vector, Redpanda Connect, Flink, самописный консьюмер, который пишет батчами (обычно надёжнее и проще эксплуатировать).

## CDC из PostgreSQL

Debezium → Kafka → ClickHouse (ReplacingMergeTree), **MaterializedPostgreSQL** (экспериментальный), ClickPipes for Postgres, PeerDB.

## Другие источники и приёмники

- табличные функции: `s3()`, `url()`, `file()`, `postgresql()`, `mysql()`, `remote()`;
- движки-интеграции: `PostgreSQL`, `MySQL`, `S3`, `Iceberg`, `Delta`;
- экспорт: `INSERT INTO FUNCTION s3(...)`, форматы Parquet/CSV.

## Observability: OpenTelemetry → ClickHouse

Логи, метрики и трейсы хранятся в ClickHouse (SigNoz, Uptrace, HyperDX, Qryn, ClickStack). Схема:

```text
Приложения (OTel SDK) → OTel Collector → ClickHouse exporter → таблицы otel_logs / otel_traces / otel_metrics_*
```

```yaml
exporters:
  clickhouse:
    endpoint: tcp://clickhouse:9000?dial_timeout=10s
    database: otel
    ttl: 72h
    create_schema: true
    timeout: 5s
    retry_on_failure: { enabled: true }
    sending_queue: { queue_size: 1000 }
```

Схема для логов и трейсов: ключ сортировки по `(ServiceName, Timestamp)`, `LowCardinality` для сервисов и уровней, `Map(LowCardinality(String), String)` для атрибутов, `TTL` по времени, bloom-фильтры для `TraceId`.

Плюсы: дёшево хранить большие объёмы, быстрый поиск и агрегации; SQL-доступ. Минусы: нужна собственная эксплуатация и UI.

## Grafana

Плагин **ClickHouse data source** (официальный). Возможности: SQL-редактор, макросы времени (`$__timeFilter(ts)`, `$__timeInterval(ts)`), переменные дашборда, режимы Table/Time series/Logs/Traces, алерты.

```sql
SELECT $__timeInterval(ts) AS time, event_type, count() AS c
FROM events
WHERE $__timeFilter(ts) AND tenant_id = ${tenant}
GROUP BY time, event_type ORDER BY time
```

Практика: запросы к предагрегатам (MV) для быстрых дашбордов; ограничение по времени и `LIMIT`; отдельный пользователь ClickHouse с ролью `readonly` и квотами для Grafana.

## Клиенты

.NET: `ClickHouse.Client`, Go: `clickhouse-go`, Python: `clickhouse-connect`, HTTP-интерфейс (порт 8123), native (9000), JDBC/ODBC.

## Безопасность

Пользователи, роли, `readonly`, профили настроек, квоты, лимиты запросов, TLS, IP-ограничения, отдельные пользователи для сервисов.

## Вопросы с ответами

> [!question]- Как надёжно загружать события из Kafka?
> Kafka Engine + MV или внешний консьюмер с батчами. Доставка «как минимум один раз», поэтому нужны дедупликация (ReplacingMergeTree) или идемпотентные вставки.

> [!question]- Почему ClickHouse хорош для логов и трейсов?
> Колоночное сжатие, быстрые агрегации, TTL, дешёвое хранение больших объёмов и SQL для анализа.

> [!question]- Как ускорить дашборды Grafana на ClickHouse?
> Предагрегаты в MV, ограничение диапазона, фильтры по ключу сортировки, отдельный readonly пользователь с лимитами.
