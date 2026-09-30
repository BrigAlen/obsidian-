---
type: topic
domain: db
stage: 3
section: "3.1"
order: 7
status: todo
level: middle
notion_id: 3ea33104867981a68f9fd77903336c50
tags: [domain/db, stage/3, level/middle, topic/clickhouse, topic/materialized-views, topic/projections, priority/should]
reviewed:
next_review:
priority: should
time: 4
---

# Материализованные представления и проекции

↑ [[DB 3.1 ClickHouse|3.1 ClickHouse]] · ← [[DB 3.1.6 Вставка данных — батчи, async insert, почему нельзя по одной строке|Предыдущая]] · → [[DB 3.1.8 UPDATE и DELETE в ClickHouse — mutations, lightweight delete|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~4 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> Инкрементальная предагрегация — ключевой приём ускорения дашбордов в ClickHouse.

## Материализованное представление (MV)

В ClickHouse MV — это **триггер на вставку**: при каждом `INSERT` в исходную таблицу выполняется запрос над **вставленным блоком**, и результат пишется в целевую таблицу.

```sql
-- исходные события
CREATE TABLE events (ts DateTime, tenant_id UInt32, event_type LowCardinality(String), value Float64)
ENGINE = MergeTree ORDER BY (tenant_id, ts);

-- целевая таблица предагрегатов
CREATE TABLE events_hourly
(
    hour DateTime, tenant_id UInt32, event_type LowCardinality(String),
    cnt AggregateFunction(count), total AggregateFunction(sum, Float64)
)
ENGINE = AggregatingMergeTree ORDER BY (tenant_id, event_type, hour);

-- MV
CREATE MATERIALIZED VIEW events_hourly_mv TO events_hourly AS
SELECT toStartOfHour(ts) AS hour, tenant_id, event_type, countState() AS cnt, sumState(value) AS total
FROM events GROUP BY hour, tenant_id, event_type;

-- запрос
SELECT hour, countMerge(cnt), sumMerge(total) FROM events_hourly WHERE tenant_id = 7 GROUP BY hour ORDER BY hour;
```

Особенности:

- обрабатывает **только новые данные** (вставленный блок), историю не пересчитывает: для старых данных нужен бэкфилл `INSERT INTO events_hourly SELECT ...`;
- MV **не читает всю таблицу**, поэтому стоимость мала;
- `UPDATE/DELETE` в исходной таблице **не отражаются** в MV;
- MV можно цеплять цепочкой, использовать для маршрутизации данных (например, из Kafka в несколько таблиц), для трансформации и обогащения при вставке;
- ошибка в MV ломает вставку в исходную таблицу.

## Refreshable MV

Новый вид (`REFRESH EVERY 1 HOUR`): периодически пересчитывает запрос целиком, подходит для тяжёлых JOIN и отчётов.

```sql
CREATE MATERIALIZED VIEW top_users REFRESH EVERY 1 HOUR TO top_users_table AS
SELECT user_id, count() c FROM events GROUP BY user_id ORDER BY c DESC LIMIT 1000;
```

## Проекции (projections)

Скрытая дополнительная сортировка/агрегация **внутри той же таблицы**. Оптимизатор сам выбирает подходящую проекцию.

```sql
ALTER TABLE events ADD PROJECTION by_user (SELECT * ORDER BY user_id);
ALTER TABLE events ADD PROJECTION daily_agg (SELECT toDate(ts) d, event_type, count(), sum(value) GROUP BY d, event_type);
ALTER TABLE events MATERIALIZE PROJECTION by_user;   -- для существующих данных
```

Плюсы: прозрачно для запросов, обновляется вместе с данными и мутациями. Минусы: занимает место, замедляет вставку, ограничения (нет JOIN, ограниченная работа с `FINAL`).

## Как выбирать

| Задача | Инструмент |
|---|---|
| Быстрый доступ к другой сортировке (другой ключ) | проекция (или отдельная таблица + MV) |
| Предагрегация в реальном времени | MV + AggregatingMergeTree/SummingMergeTree |
| Тяжёлый периодический отчёт | refreshable MV |
| Обогащение/маршрутизация при вставке | MV |

## Практика

- целевая таблица с явным `TO`, удобнее управлять и мигрировать;
- ключ целевой таблицы под запросы к предагрегатам;
- храните сырые данные с TTL, а предагрегаты — дольше;
- следите за размером состояний `uniqState` (дорогие);
- согласованность: при ошибке MV вставка может частично примениться (не транзакционно между таблицами).

## Вопросы с ответами

> [!question]- Как MV в ClickHouse отличается от MV в PostgreSQL?
> В ClickHouse это триггер на вставку, инкрементально обрабатывающий новые блоки и записывающий в целевую таблицу; в PostgreSQL — снимок запроса, обновляемый командой REFRESH.

> [!question]- Пересчитаются ли данные MV при появлении старых строк?
> MV срабатывает на каждую вставку, в том числе «исторических» данных, но данные, вставленные до создания MV, нужно догрузить вручную.

> [!question]- Когда проекция лучше отдельной таблицы?
> Когда нужна дополнительная сортировка или агрегат без изменения приложения; прозрачность и согласованность с исходными данными. Отдельная таблица даёт больше гибкости.
