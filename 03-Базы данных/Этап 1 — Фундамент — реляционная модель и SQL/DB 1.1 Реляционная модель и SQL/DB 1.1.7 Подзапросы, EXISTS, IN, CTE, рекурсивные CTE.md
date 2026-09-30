---
type: topic
domain: db
stage: 1
section: "1.1"
order: 7
status: todo
level: junior
notion_id: 3ea33104867981258c1afa7f45408497
tags: [domain/db, stage/1, level/junior, topic/sql, topic/subquery, topic/cte, priority/must]
reviewed:
next_review:
priority: must
time: 4
---

# Подзапросы, EXISTS, IN, CTE, рекурсивные CTE

↑ [[DB 1.1 Реляционная модель и SQL|1.1 Реляционная модель и SQL]] · ← [[DB 1.1.6 GROUP BY, HAVING, агрегатные функции|Предыдущая]] · → [[DB 1.1.8 Оконные функции — ROW_NUMBER, RANK, LAG, накопительные суммы|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~4 мин чтения</span><span class="chip">Уровень: junior</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> Умение структурировать сложные запросы и выбирать между IN, EXISTS и JOIN.

## Виды подзапросов

| Вид | Пример |
|---|---|
| Скалярный | `(SELECT max(total) FROM orders)` — одно значение |
| В `FROM` (derived table) | `FROM (SELECT ...) t` |
| С `IN` | `WHERE id IN (SELECT customer_id FROM orders)` |
| `EXISTS` | `WHERE EXISTS (SELECT 1 FROM orders o WHERE o.customer_id = c.id)` |
| Коррелированный | ссылается на внешний запрос, выполняется логически для каждой строки |
| С `ANY` / `ALL` | `total > ALL (SELECT ...)` |

## IN, EXISTS, JOIN

```sql
-- клиенты, у которых есть заказы
SELECT * FROM customers c WHERE EXISTS (SELECT 1 FROM orders o WHERE o.customer_id = c.id);

-- клиенты без заказов
SELECT * FROM customers c WHERE NOT EXISTS (SELECT 1 FROM orders o WHERE o.customer_id = c.id);
```

- `EXISTS` останавливается на первой найденной строке, не размножает строки;
- `NOT IN` **опасен с NULL**: если подзапрос возвращает хотя бы один NULL, результат пуст (`x NOT IN (1, NULL)` даёт UNKNOWN). Используйте `NOT EXISTS`;
- современные планировщики часто превращают `IN`/`EXISTS` в semi-join, различий по скорости обычно нет.

## CTE (WITH)

Именованный подзапрос, повышает читаемость.

```sql
WITH paid AS (
  SELECT customer_id, sum(total) AS revenue
  FROM orders WHERE status = 'paid' GROUP BY customer_id
),
top AS (
  SELECT * FROM paid ORDER BY revenue DESC LIMIT 10
)
SELECT c.email, t.revenue FROM top t JOIN customers c ON c.id = t.customer_id;
```

С PostgreSQL 12 нерекурсивные CTE без побочных эффектов **встраиваются** (inline), как подзапросы; управлять: `WITH x AS MATERIALIZED (...)` или `NOT MATERIALIZED`.

## Рекурсивные CTE

Для иерархий и графов.

```sql
WITH RECURSIVE tree AS (
  SELECT id, parent_id, name, 1 AS depth, ARRAY[id] AS path
  FROM categories WHERE parent_id IS NULL             -- якорь
  UNION ALL
  SELECT c.id, c.parent_id, c.name, t.depth + 1, t.path || c.id
  FROM categories c
  JOIN tree t ON c.parent_id = t.id                   -- рекурсивный шаг
  WHERE NOT c.id = ANY(t.path)                        -- защита от циклов
)
SELECT * FROM tree ORDER BY path;

-- числовой ряд
WITH RECURSIVE n(i) AS (SELECT 1 UNION ALL SELECT i + 1 FROM n WHERE i < 10) SELECT * FROM n;
```

Применение: дерево категорий, оргструктура, маршруты, BOM (состав изделия). Обязательно условие остановки и защита от циклов.

## Модифицирующие CTE

```sql
WITH deleted AS (
  DELETE FROM orders_queue WHERE created_at < now() - interval '30 days' RETURNING *
)
INSERT INTO orders_archive SELECT * FROM deleted;
```

## LATERAL

Подзапрос видит столбцы предыдущих элементов `FROM`: топ-N на группу, разворачивание функций.

## Вопросы с ответами

> [!question]- Почему NOT IN может вернуть пустой результат?
> Если в списке есть NULL, сравнение с ним даёт UNKNOWN, и условие никогда не истинно. Используйте `NOT EXISTS`.

> [!question]- Что такое рекурсивный CTE и как он устроен?
> Якорный запрос даёт начальные строки, рекурсивная часть соединяет предыдущий результат с таблицей, пока новые строки появляются. Нужна защита от бесконечной рекурсии.

> [!question]- Всегда ли CTE материализуется?
> Нет. Начиная с PostgreSQL 12 простой CTE встраивается в запрос, если он используется один раз и не имеет побочных эффектов.
