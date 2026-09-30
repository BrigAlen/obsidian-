---
type: topic
domain: db
stage: 3
section: "3.1"
order: 4
status: todo
level: middle
notion_id: 3ea3310486798149aa0bf9415fcec570
tags: [domain/db, stage/3, level/middle, topic/clickhouse, topic/replacingmergetree, topic/aggregatingmergetree, priority/should]
reviewed:
next_review:
priority: should
time: 5
---

# Семейство MergeTree: Replacing, Summing, Aggregating, Collapsing

↑ [[DB 3.1 ClickHouse|3.1 ClickHouse]] · ← [[DB 3.1.3 Движок MergeTree — ORDER BY, PRIMARY KEY, PARTITION BY, TTL|Предыдущая]] · → [[DB 3.1.5 Типы данных и LowCardinality, Nullable, Array, Map|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~5 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> Специализированные движки решают дедупликацию и предагрегацию, но имеют важные нюансы: слияния происходят «когда-нибудь».

## Общий принцип

Все варианты — MergeTree с дополнительной логикой при **слиянии партов**: строки с одинаковым **ключом сортировки** (`ORDER BY`) схлопываются. Слияние происходит в фоне, поэтому **в любой момент могут существовать дубликаты**, и данные нужно читать с учётом этого.

## ReplacingMergeTree

Оставляет **последнюю версию** строки для ключа.

```sql
CREATE TABLE users_state
(
    user_id UInt64,
    name    String,
    updated_at DateTime,
    is_deleted UInt8 DEFAULT 0
)
ENGINE = ReplacingMergeTree(updated_at, is_deleted)
ORDER BY user_id;

-- корректное чтение до слияния
SELECT * FROM users_state FINAL WHERE user_id = 42;
-- или
SELECT argMax(name, updated_at) FROM users_state GROUP BY user_id;
```

Применение: снимки состояния из CDC, дедупликация повторно доставленных событий, «upsert». `FINAL` замедляет запрос (в новых версиях сильно оптимизирован), при удаляемых строках нужен `is_deleted`.

## SummingMergeTree

Суммирует числовые столбцы для строк с одним ключом.

```sql
CREATE TABLE daily_totals (day Date, tenant_id UInt32, requests UInt64, bytes UInt64)
ENGINE = SummingMergeTree ORDER BY (day, tenant_id);

SELECT day, tenant_id, sum(requests), sum(bytes) FROM daily_totals GROUP BY day, tenant_id;  -- всегда агрегируем при чтении
```

## AggregatingMergeTree

Хранит **промежуточные состояния агрегатов** (`AggregateFunction`). Основа материализованных представлений.

```sql
CREATE TABLE stats_agg
(
    day  Date,
    uniq_users AggregateFunction(uniq, UInt64),
    avg_value  AggregateFunction(avg, Float64),
    p95        AggregateFunction(quantile(0.95), Float64)
)
ENGINE = AggregatingMergeTree ORDER BY day;

-- запись через состояние
INSERT INTO stats_agg SELECT toDate(ts), uniqState(user_id), avgState(value), quantileState(0.95)(value) FROM events GROUP BY 1;

-- чтение через Merge
SELECT day, uniqMerge(uniq_users), avgMerge(avg_value), quantileMerge(0.95)(p95) FROM stats_agg GROUP BY day;
```

## CollapsingMergeTree и VersionedCollapsingMergeTree

Схлопывают пары «строка / отменяющая строка» по столбцу `sign` (+1 и −1): способ выразить обновление и удаление в append-only модели.

```sql
ENGINE = CollapsingMergeTree(sign) ORDER BY id
-- изменение: вставить старую строку с sign = -1 и новую с sign = +1
```

`VersionedCollapsingMergeTree` терпим к порядку вставки (учитывает версию). Сложнее в использовании, чем Replacing.

## Реплицируемые варианты

`ReplicatedMergeTree`, `ReplicatedReplacingMergeTree` и т. д. — тот же движок с репликацией через Keeper.

## Как выбирать

| Задача | Движок |
|---|---|
| Просто хранить события | MergeTree |
| Актуальное состояние сущности, дедупликация | ReplacingMergeTree |
| Простые суммы/счётчики по ключу | SummingMergeTree |
| Сложные предагрегаты (uniq, quantile) | AggregatingMergeTree (+ MV) |
| Обновления через отмену | Collapsing / VersionedCollapsing |

## Ловушки

- дедупликация **не мгновенная** и не глобальная (только внутри партиции, если ключ партиционирования отличается, схлопывания нет);
- нельзя полагаться на уникальность; читать надо с `FINAL`, `argMax` или агрегированием;
- ключ схлопывания — весь `ORDER BY`, а не `PRIMARY KEY`.

## Вопросы с ответами

> [!question]- Гарантирует ли ReplacingMergeTree уникальность?
> Нет. Дубликаты удаляются при фоновых слияниях, момент которых не определён; для актуального чтения применяют `FINAL` или `argMax`.

> [!question]- Для чего AggregatingMergeTree?
> Хранит промежуточные состояния агрегатов (`uniqState`, `quantileState`), позволяя инкрементально предагрегировать данные (в паре с материализованным представлением) и получать итог функциями `*Merge`.
