---
type: topic
domain: db
stage: 6
section: "6.1"
order: 5
status: todo
level: senior
notion_id: 3ea33104867981b0b918fb10e89e9d0d
tags: [domain/db, stage/6, level/senior, topic/cdc, topic/debezium, topic/kafka, topic/clickhouse, priority/should]
reviewed:
next_review:
priority: should
time: 7
---

# Change Data Capture: Debezium, логическая репликация, PostgreSQL → Kafka → ClickHouse

↑ [[DB 6.1 Масштабирование и надёжность данных|6.1 Масштабирование и надёжность данных]] · ← [[DB 6.1.4 Бэкапы и восстановление — pg_dump, PITR, RPO и RTO|Предыдущая]] · → [[DB 6.1.6 Выбор хранилища под задачу — polyglot persistence|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~7 мин чтения</span><span class="chip">Уровень: senior</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> CDC — стандартный способ строить аналитику и интеграции без двойной записи и нагрузки на основную БД.

## Что такое CDC

**Change Data Capture** — перехват изменений (INSERT/UPDATE/DELETE) в БД и передача их потребителям как поток событий.

Задачи: синхронизация с аналитическим хранилищем (ClickHouse), поиском (Elasticsearch), кэшем, микросервисами; миграции без простоя; аудит; материализованные представления в других системах.

## Подходы к получению изменений

| Подход | Описание | Минусы |
|---|---|---|
| **Polling** (по `updated_at`) | периодический запрос | пропускает удаления, нагрузка, задержка |
| **Триггеры** | запись изменений в таблицу аудита | замедляет основную нагрузку, сложность |
| **Dual write** (запись в два места из приложения) | приложение пишет в БД и в брокер | нет атомарности: расхождения при сбое |
| **Transactional Outbox** | событие записывается в таблицу `outbox` в той же транзакции; читатель публикует в брокер | своя таблица и публикатор |
| **Log-based CDC** | чтение журнала БД (WAL / binlog) | нужен коннектор, настройка БД |

Log-based CDC — предпочтительный: **низкая нагрузка, полный порядок, захват удалений, без изменений приложения**.

## PostgreSQL: логическое декодирование

- `wal_level = logical`;
- **replication slot** хранит позицию потребителя (WAL удерживается, пока слот не прочитан);
- **output plugin**: `pgoutput` (встроенный), `wal2json`;
- **publication** — набор таблиц;
- `REPLICA IDENTITY` (`DEFAULT` — PK; `FULL` — старые значения целиком) определяет, что попадёт в событие при UPDATE/DELETE.

**Опасность**: забытый или отставший слот копит WAL и **заполняет диск**. Мониторьте `pg_replication_slots` (`restart_lsn`, `wal_status`), задайте `max_slot_wal_keep_size`.

```sql
ALTER SYSTEM SET wal_level = 'logical';
CREATE PUBLICATION dbz_pub FOR TABLE public.orders, public.customers;
SELECT * FROM pg_create_logical_replication_slot('dbz_slot', 'pgoutput');
```

## Debezium

Платформа CDC на Kafka Connect: коннекторы для PostgreSQL, MySQL, SQL Server, MongoDB, Oracle.

```json
{
  "name": "pg-orders",
  "config": {
    "connector.class": "io.debezium.connector.postgresql.PostgresConnector",
    "database.hostname": "postgres", "database.port": "5432",
    "database.user": "debezium", "database.password": "${file:/secrets/db:password}",
    "database.dbname": "app",
    "topic.prefix": "app",
    "plugin.name": "pgoutput",
    "publication.name": "dbz_pub",
    "slot.name": "dbz_slot",
    "table.include.list": "public.orders,public.customers",
    "snapshot.mode": "initial",
    "tombstones.on.delete": "true",
    "transforms": "unwrap",
    "transforms.unwrap.type": "io.debezium.transforms.ExtractNewRecordState",
    "transforms.unwrap.add.fields": "op,source.ts_ms",
    "transforms.unwrap.delete.handling.mode": "rewrite"
  }
}
```

Топики: `app.public.orders`. Событие содержит `before`, `after`, `op` (`c`, `u`, `d`, `r` — snapshot), `source` (LSN, транзакция, время). Начальный **snapshot** выгружает существующие данные, затем идёт поток изменений.

Схемы: Avro/JSON Schema с **Schema Registry**; эволюция схем (совместимость).

## Цепочка PostgreSQL → Kafka → ClickHouse

```text
PostgreSQL ─(WAL)→ Debezium ─→ Kafka ─→ ClickHouse (Kafka engine / ClickPipes / Sink) ─→ Grafana/BI
```

В ClickHouse:

```sql
CREATE TABLE orders_queue (...)            -- Kafka engine, формат JSONEachRow/Avro
ENGINE = Kafka SETTINGS kafka_topic_list = 'app.public.orders', kafka_group_name = 'ch', kafka_format = 'JSONEachRow';

CREATE TABLE orders
(
    id UInt64, customer_id UInt64, total Decimal(12,2), status LowCardinality(String),
    updated_at DateTime64(3), _version UInt64, _deleted UInt8
)
ENGINE = ReplacingMergeTree(_version, _deleted) ORDER BY id;

CREATE MATERIALIZED VIEW orders_mv TO orders AS
SELECT id, customer_id, total, status, updated_at,
       source_ts_ms AS _version, if(__op = 'd', 1, 0) AS _deleted
FROM orders_queue;

-- чтение актуального состояния
SELECT * FROM orders FINAL WHERE _deleted = 0;
```

Схема: версия строки = LSN/время источника; `ReplacingMergeTree` оставляет последнюю; удаления помечаются флагом.

Альтернативы: **ClickPipes / PeerDB** (PostgreSQL → ClickHouse напрямую), `MaterializedPostgreSQL`, Airbyte, Flink CDC, Kafka Connect ClickHouse Sink.

## Гарантии и эксплуатация

- доставка **at-least-once** → потребители идемпотентны (upsert по ключу и версии);
- **порядок** гарантируется в пределах партиции Kafka: ключ события = PK строки;
- **DDL**: изменения схемы нужно планировать (Debezium обновляет схему, sink может упасть): добавляйте столбцы совместимо;
- **большие транзакции** и пакетные `UPDATE` создают всплески событий;
- **мониторинг**: lag коннектора (`MilliSecondsBehindSource`), размер слота, ошибки, lag консьюмеров;
- **повторный snapshot** при потере слота или смене конфигурации;
- **безопасность**: отдельный пользователь с `REPLICATION` и правами на чтение нужных таблиц; исключать PII (`column.exclude.list`) или маскировать;
- **Outbox + Debezium** (`EventRouter` SMT): надёжная публикация доменных событий без dual write.

## Когда не нужен

Небольшие данные и простые отчёты — достаточно реплики и материализованных представлений; периодический ETL-пакет проще в эксплуатации, если задержка в часах приемлема.

## Вопросы с ответами

> [!question]- Почему dual write плох?
> Нет общей транзакции между БД и брокером: при сбое между записями данные расходятся. Решения: CDC по журналу БД или transactional outbox.

> [!question]- Чем опасен replication slot в PostgreSQL?
> Пока слот не прочитан, WAL удерживается и копится; остановленный потребитель может заполнить диск основного сервера. Нужен мониторинг и `max_slot_wal_keep_size`.

> [!question]- Как обеспечить актуальное состояние в ClickHouse при UPDATE/DELETE в источнике?
> Писать версию и признак удаления в ReplacingMergeTree, читать с `FINAL` (или `argMax`), а потребителя делать идемпотентным (at-least-once).
