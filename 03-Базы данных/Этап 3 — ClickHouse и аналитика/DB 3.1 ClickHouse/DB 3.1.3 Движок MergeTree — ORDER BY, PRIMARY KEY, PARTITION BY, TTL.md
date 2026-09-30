---
type: topic
domain: db
stage: 3
section: "3.1"
order: 3
status: todo
level: middle
notion_id: 3ea3310486798186b03bf228a7668007
tags: [domain/db, stage/3, level/middle, topic/clickhouse, topic/mergetree, topic/ttl, priority/should]
reviewed:
next_review:
priority: should
time: 4
---

# Движок MergeTree: ORDER BY, PRIMARY KEY, PARTITION BY, TTL

↑ [[DB 3.1 ClickHouse|3.1 ClickHouse]] · ← [[DB 3.1.2 Архитектура ClickHouse — парты, гранулы, sparse index, сжатие|Предыдущая]] · → [[DB 3.1.4 Семейство MergeTree — Replacing, Summing, Aggregating, Collapsing|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~4 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> Правильный DDL — 80% успеха в ClickHouse. Спрашивают, чем ORDER BY отличается от PRIMARY KEY и как выбирать партиционирование.

## Пример

```sql
CREATE TABLE events
(
    event_date  Date,
    event_time  DateTime,
    tenant_id   UInt32,
    user_id     UInt64,
    event_type  LowCardinality(String),
    properties  String,
    value       Float64
)
ENGINE = MergeTree
PARTITION BY toYYYYMM(event_date)
ORDER BY (tenant_id, event_type, event_time)
PRIMARY KEY (tenant_id, event_type)          -- необязательно: префикс ORDER BY
TTL event_time + INTERVAL 90 DAY DELETE
SETTINGS index_granularity = 8192;
```

## ORDER BY и PRIMARY KEY

- **`ORDER BY`** определяет **физическую сортировку** данных в парте и (по умолчанию) первичный индекс;
- **`PRIMARY KEY`** — то, что попадает в **разреженный индекс**; должен быть **префиксом** `ORDER BY`. Позволяет держать индекс короче, чем сортировка;
- если `PRIMARY KEY` не задан, он равен `ORDER BY`.

Как выбирать ключ сортировки:

1. Столбцы, по которым чаще всего фильтруют (в условиях `WHERE`).
2. Порядок: от **низкой кардинальности к высокой** (сжатие лучше, индекс эффективнее). Время часто идёт последним или после низкокардинальных.
3. Не слишком много столбцов (обычно 2–4).
4. Учитывать дедупликацию в `ReplacingMergeTree` (ключ сортировки = ключ идентичности).

## PARTITION BY

Логическое разбиение на партиции (каталоги партов). Нужно для **управления данными** (удаление, перенос, TTL по партиции), а не как главный инструмент ускорения.

- обычно по месяцу `toYYYYMM(date)` или дню для больших объёмов;
- **слишком много партиций** (тысячи) — плохо: много мелких партов, слияния между партициями невозможны;
- цель: десятки–сотни партиций; ориентир — партиция не менее нескольких ГБ;
- операции: `ALTER TABLE ... DROP PARTITION '202601'`, `DETACH`, `ATTACH`, `MOVE PARTITION`.

## TTL

Автоматическое удаление или перенос данных:

```sql
TTL event_time + INTERVAL 30 DAY DELETE,
    event_time + INTERVAL 7 DAY TO VOLUME 'cold',       -- на медленный диск
    event_time + INTERVAL 1 DAY GROUP BY tenant_id, toStartOfHour(event_time) SET value = sum(value)   -- агрегация старых данных
```

TTL применяется при слияниях (`merge_with_ttl_timeout`); можно на уровне столбца (сброс значения к умолчанию). Для строгой очистки: `ALTER TABLE ... MATERIALIZE TTL`.

## Хранение: диски и политики

`storage_policy` — многодисковые тома (hot/cold), объектное хранилище (S3) через диск.

## Другие настройки

- `SAMPLE BY` — выборка (`SAMPLE 0.1`);
- `index_granularity`, `min_bytes_for_wide_part`;
- `ttl_only_drop_parts = 1` — удалять целые парты по TTL.

## Типичные ошибки

- `PARTITION BY` по высококардинальному полю (например, `user_id`);
- ключ сортировки не соответствует фильтрам;
- время первым столбцом при фильтрации по тенанту (данные разных тенантов перемешаны);
- ожидание уникальности от `PRIMARY KEY`.

## Вопросы с ответами

> [!question]- Чем ORDER BY отличается от PRIMARY KEY?
> ORDER BY задаёт порядок хранения данных, PRIMARY KEY — что попадает в разреженный индекс. PRIMARY KEY должен быть префиксом ORDER BY; по умолчанию они совпадают.

> [!question]- Зачем PARTITION BY, если запросы ускоряет ключ сортировки?
> Партиции нужны для жизненного цикла данных: быстро удалять, переносить, архивировать по времени. Отбор партиций также помогает, но основной инструмент ускорения — ключ сортировки.

> [!question]- Как хранить только последние 90 дней?
> `TTL event_time + INTERVAL 90 DAY DELETE` (и `ttl_only_drop_parts`), либо удаление старых партиций.
