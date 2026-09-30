---
type: topic
domain: db
stage: 5
section: "5.1"
order: 3
status: todo
level: middle
notion_id: 3ea3310486798174a214fed6e6215815
tags: [domain/db, stage/5, level/middle, topic/goose, topic/clickhouse, topic/migrations, priority/should]
reviewed:
next_review:
priority: should
time: 5
---

# goose для ClickHouse

↑ [[DB 5.1 Миграции — EF Core, Flyway, goose|5.1 Миграции: EF Core, Flyway, goose]] · ← [[DB 5.1.2 Flyway — версионные и repeatable миграции, запуск в Docker|Предыдущая]] · → [[DB 5.1.4 Миграции EF Core в проде — bundles, скрипты, кто и когда применяет|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~5 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> Для аналитического стека нужна своя дисциплина миграций: ClickHouse не транзакционен, и DDL ведёт себя иначе.

## goose

Лёгкий инструмент миграций на Go: SQL-файлы (и Go-миграции), поддержка PostgreSQL, MySQL, SQLite, **ClickHouse** и др. История хранится в таблице `goose_db_version`.

```sh
goose -dir migrations clickhouse "tcp://default:pass@localhost:9000/analytics" up
goose -dir migrations clickhouse "..." status
goose -dir migrations clickhouse "..." down
goose create add_events_table sql
```

Формат файла:

```sql
-- migrations/20260930120000_add_events_table.sql

-- +goose Up
-- +goose StatementBegin
CREATE TABLE IF NOT EXISTS events
(
    ts         DateTime,
    tenant_id  UInt32,
    event_type LowCardinality(String),
    payload    String
)
ENGINE = MergeTree
PARTITION BY toYYYYMM(ts)
ORDER BY (tenant_id, ts);
-- +goose StatementEnd

-- +goose Down
-- +goose StatementBegin
DROP TABLE IF EXISTS events;
-- +goose StatementEnd
```

`StatementBegin/End` — для многострочных операторов.

## Особенности ClickHouse

- **нет транзакций для DDL**: миграция из нескольких операторов при ошибке остаётся применённой частично. Делайте **одну миграцию = один оператор** и пишите идемпотентные скрипты (`IF NOT EXISTS`, `IF EXISTS`);
- `ALTER` для MergeTree: добавление и удаление столбцов быстрые (метаданные), изменение типа и `MODIFY ORDER BY` ограничено (ключ сортировки нельзя просто переписать: создаётся новая таблица и данные переносятся);
- **ключ сортировки, партиционирование и движок неизменяемы**: изменение = новая таблица + `INSERT SELECT` + `EXCHANGE TABLES` / `RENAME`;
- кластер: `ON CLUSTER` для DDL на всех узлах; для реплицируемых таблиц через Keeper; в goose нужно указывать `ON CLUSTER` явно в SQL;
- материализованные представления: при изменении схемы источника нужно обновить MV (`ALTER TABLE ... MODIFY QUERY` в новых версиях или пересоздание);
- бэкфилл исторических данных делается отдельным `INSERT INTO ... SELECT` (может быть долгим и идти в фоне);
- в **таблицу истории** goose для кластера лучше указать реплицируемый движок, либо запускать миграции на одном узле через Distributed-DDL.

## Паттерн: смена ключа сортировки

```sql
-- 1. новая таблица
CREATE TABLE events_v2 AS events ENGINE = MergeTree ORDER BY (tenant_id, event_type, ts);
-- 2. перенос (можно по партициям)
INSERT INTO events_v2 SELECT * FROM events;
-- 3. атомарная подмена
EXCHANGE TABLES events AND events_v2;
-- 4. позднее удалить events_v2 (старая версия)
```

## Паттерн: добавление столбца

```sql
ALTER TABLE events ADD COLUMN IF NOT EXISTS browser LowCardinality(String) DEFAULT '' AFTER event_type;
```

Быстро (старые парты вычисляют значение по умолчанию на лету).

## Запуск в CI/CD и Docker

```sh
docker run --rm --network app -v "$PWD/migrations:/migrations:ro" ghcr.io/pressly/goose:latest \
  -dir /migrations clickhouse "tcp://migrator:${CH_PASSWORD}@clickhouse:9000/analytics" up
```

Или встроенный режим на Go (библиотека `goose.Up(db, dir)`), подходит для сервисов на Go; для .NET — контейнер goose отдельным шагом.

## Альтернативы

`clickhouse-migrations` (Node), `golang-migrate`, `Atlas` (declarative для ClickHouse), `dbmate`, Liquibase (плагин ClickHouse), EF Core не поддерживает ClickHouse.

## Практики

- версионируйте и DDL таблиц, и MV, и словари;
- тестируйте миграции на копии схемы в контейнере ClickHouse (Testcontainers);
- учитывайте **неблокирующую природу**: изменения применяются во время работы запросов;
- отдельный пользователь `migrator` с правами DDL, а приложения только на `INSERT`/`SELECT`;
- для `down` помните: `DROP TABLE` уничтожает данные, используйте осторожно и запрещайте на проде.

## Вопросы с ответами

> [!question]- Почему в ClickHouse советуют одну миграцию на один оператор?
> DDL не транзакционен: при ошибке на втором операторе первый уже применён. Мелкие идемпотентные миграции проще повторить и диагностировать.

> [!question]- Как изменить ключ сортировки таблицы MergeTree?
> Создать новую таблицу с нужным `ORDER BY`, перелить данные `INSERT SELECT`, подменить через `EXCHANGE TABLES` и удалить старую.

> [!question]- Как применять миграции в кластере ClickHouse?
> Использовать `ON CLUSTER` в DDL (через Keeper) и запускать goose от одного клиента; следить за консистентностью на всех репликах.
