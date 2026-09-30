---
type: topic
domain: db
stage: 1
section: "1.1"
order: 6
status: todo
level: junior
notion_id: 3ea33104867981c4ba7fd6eb160925b8
tags: [domain/db, stage/1, level/junior, topic/sql, topic/group-by, topic/aggregates, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# GROUP BY, HAVING, агрегатные функции

↑ [[DB 1.1 Реляционная модель и SQL|1.1 Реляционная модель и SQL]] · ← [[DB 1.1.5 JOIN — inner, left, right, full, cross, self|Предыдущая]] · → [[DB 1.1.7 Подзапросы, EXISTS, IN, CTE, рекурсивные CTE|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: junior</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> Аналитика по данным — типовая задача; частая ловушка — `WHERE` против `HAVING` и NULL в агрегатах.

## Агрегатные функции

| Функция | Замечания |
|---|---|
| `count(*)` | все строки |
| `count(col)` | не-NULL значения |
| `count(DISTINCT col)` | уникальные не-NULL значения |
| `sum`, `avg`, `min`, `max` | игнорируют NULL |
| `string_agg(col, ', ' ORDER BY col)` | конкатенация |
| `array_agg(col)`, `jsonb_agg(...)` | сбор в массив |
| `bool_and`, `bool_or` | логические |
| `percentile_cont(0.5) WITHIN GROUP (ORDER BY x)` | медиана |

```sql
SELECT customer_id,
       count(*)                         AS orders,
       sum(total)                       AS revenue,
       round(avg(total), 2)             AS avg_check,
       max(created_at)                  AS last_order,
       count(*) FILTER (WHERE status = 'cancelled') AS cancelled
FROM orders
WHERE created_at >= date '2026-01-01'
GROUP BY customer_id
HAVING sum(total) > 10000
ORDER BY revenue DESC;
```

## WHERE и HAVING

- `WHERE` фильтрует **строки до группировки**;
- `HAVING` фильтрует **группы после агрегации**.

Условие, не зависящее от агрегатов, должно быть в `WHERE`: эффективнее и может использовать индексы.

## Правило GROUP BY

Каждое выражение в `SELECT`, не обёрнутое агрегатом, должно быть в `GROUP BY` (или функционально зависеть от первичного ключа сгруппированной таблицы в PostgreSQL).

## Продвинутая группировка

```sql
SELECT region, product, sum(amount)
FROM sales
GROUP BY GROUPING SETS ((region, product), (region), ());   -- детализация и итоги

GROUP BY ROLLUP (year, month)       -- иерархические подытоги
GROUP BY CUBE (region, product)     -- все комбинации
```

## Группировка по времени

```sql
SELECT date_trunc('day', created_at) AS day, count(*)
FROM orders GROUP BY 1 ORDER BY 1;
```

Для непрерывного ряда с нулями: `generate_series` + `LEFT JOIN`.

## NULL и агрегаты

- `sum` пустого набора возвращает `NULL`, а не 0: `coalesce(sum(x), 0)`;
- `avg` игнорирует NULL: среднее по 3 значениям из 5;
- `count(*)` считает строки, `count(col)` — не-NULL.

## Вопросы с ответами

> [!question]- Чем WHERE отличается от HAVING?
> WHERE отбирает строки до группировки и не может содержать агрегаты; HAVING отбирает группы после агрегации.

> [!question]- Чем count(*) отличается от count(col)?
> `count(*)` считает все строки, `count(col)` пропускает NULL.

> [!question]- Как посчитать долю от общего?
> Оконная функция: `sum(x) / sum(sum(x)) OVER ()` или подзапрос с общей суммой.
