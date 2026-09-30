---
type: topic
domain: db
stage: 3
section: "3.1"
order: 9
status: todo
level: middle
notion_id: 3ea33104867981b59c36d89eb5aeeb13
tags: [domain/db, stage/3, level/middle, topic/clickhouse, topic/queries, topic/optimization, topic/dictionaries, priority/should]
reviewed:
next_review:
priority: should
time: 4
---

# Запросы и оптимизация: агрегации, JOIN, FINAL, словари

↑ [[DB 3.1 ClickHouse|3.1 ClickHouse]] · ← [[DB 3.1.8 UPDATE и DELETE в ClickHouse — mutations, lightweight delete|Предыдущая]] · → [[DB 3.1.10 Интеграции — Kafka engine, телеметрия OTel в ClickHouse, Grafana|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~4 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> Как писать быстрые запросы в ClickHouse и какие типичные ошибки замедляют их.

## Правила быстрых запросов

1. **Фильтруйте по префиксу ключа сортировки** и по партиции.
2. **Выбирайте только нужные столбцы** (никогда `SELECT *` на больших таблицах).
3. Ограничивайте диапазон времени.
4. Фильтруйте **до** JOIN и агрегации.
5. Используйте предагрегаты (MV, проекции) для повторяющихся дашбордов.
6. Проверяйте, сколько данных читается: `read_rows`, `read_bytes` в `system.query_log`.

```sql
SELECT event_type, count() AS c, uniq(user_id) AS users, quantile(0.95)(value) AS p95
FROM events
WHERE tenant_id = 7 AND ts >= now() - INTERVAL 1 DAY
GROUP BY event_type
ORDER BY c DESC LIMIT 20;
```

## PREWHERE

Фильтр читает сначала только столбцы условия, потом остальные для подходящих строк. Оптимизатор включает `PREWHERE` автоматически (`optimize_move_to_prewhere`), можно указать вручную для селективных условий.

## Агрегации

- приближённые функции быстрее и экономнее: `uniq`, `uniqCombined`, `uniqHLL12`, `quantileTDigest`, `quantile`, `topK` (вместо точных `uniqExact`, `quantileExact`);
- `-If`, `-Array`, `-State`, `-Merge` комбинаторы: `sumIf(x, cond)`, `countIf`;
- `GROUP BY ... WITH TOTALS / ROLLUP / CUBE`;
- `LIMIT BY`: топ-N в группе: `... ORDER BY c DESC LIMIT 3 BY tenant_id`;
- `argMax(value, ts)` — значение при максимальном `ts`.

## Оконные функции

Поддерживаются (`row_number`, `lag`, `sum() OVER`), но менее оптимальны, чем агрегаты.

## JOIN

Исторически ClickHouse не оптимален для больших JOIN. Правила:

- **правая таблица загружается в память** (для hash join): она должна быть меньшей;
- фильтруйте и агрегируйте до соединения;
- алгоритмы: `hash`, `parallel_hash`, `grace_hash`, `partial_merge`, `full_sorting_merge` (`join_algorithm`);
- `GLOBAL JOIN` / `GLOBAL IN` в распределённых запросах: правая таблица выполняется один раз и рассылается на шарды;
- виды: `INNER`, `LEFT`, `RIGHT`, `FULL`, `CROSS`, `ANY`, `ASOF` (по времени), `SEMI/ANTI`;
- лучше **денормализовать** и использовать словари, чем делать много JOIN.

```sql
SELECT e.user_id, u.country, count()
FROM events AS e
ANY LEFT JOIN users AS u ON e.user_id = u.id
WHERE e.ts >= today() - 7
GROUP BY e.user_id, u.country;
```

## FINAL

Схлопывает дубликаты в ReplacingMergeTree/Collapsing при чтении. Дорого, но оптимизирован (параллельно, `do_not_merge_across_partitions_select_final`). Альтернативы: `argMax` + `GROUP BY`, предагрегат, `LIMIT 1 BY key`.

## Словари (dictionaries)

Справочники в памяти для быстрого поиска по ключу без JOIN.

```sql
CREATE DICTIONARY country_dict (code String, name String)
PRIMARY KEY code
SOURCE(POSTGRESQL(host 'pg' port 5432 user 'ro' password '...' db 'app' table 'countries'))
LAYOUT(FLAT()) LIFETIME(MIN 300 MAX 600);

SELECT dictGet('country_dict', 'name', country_code) AS country, count() FROM events GROUP BY country;
```

Источники: PostgreSQL, MySQL, HTTP, файл, ClickHouse. Layout: `flat`, `hashed`, `cache`, `range_hashed`, `ip_trie`.

## Диагностика

```sql
EXPLAIN indexes = 1 SELECT ...;                                -- какие партиции/гранулы читаются
EXPLAIN PIPELINE SELECT ...;
SELECT query_duration_ms, read_rows, formatReadableSize(read_bytes), memory_usage, query
FROM system.query_log WHERE type = 'QueryFinish' ORDER BY query_duration_ms DESC LIMIT 10;
```

Ограничения: `max_memory_usage`, `max_execution_time`, `max_rows_to_read`, `max_bytes_before_external_group_by`.

## Типичные ошибки

- `SELECT *`;
- запрос без фильтра по ключу/времени;
- большой JOIN на правой таблице, не помещающейся в память;
- `uniqExact`/`quantileExact` без необходимости;
- обращение к `Map`/JSON при частых ключах (см. материализованные столбцы);
- слишком частые `FINAL` на больших таблицах.

## Вопросы с ответами

> [!question]- Как оптимизировать медленный запрос в ClickHouse?
> Посмотреть `system.query_log` (сколько прочитано), `EXPLAIN indexes = 1`, убедиться, что условие использует префикс ключа и партицию, убрать лишние столбцы, использовать предагрегаты и приближённые функции.

> [!question]- Почему в ClickHouse советуют избегать больших JOIN?
> Правая таблица строится в памяти, распределённые соединения требуют пересылки данных. Лучше денормализация, словари и предагрегация.

> [!question]- Что такое PREWHERE?
> Оптимизация: сначала читаются только столбцы условия и отбираются строки, затем остальные столбцы только для подходящих строк.
