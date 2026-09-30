---
type: topic
domain: db
stage: 1
section: "1.1"
order: 5
status: todo
level: junior
notion_id: 3ea33104867981bf8b23fa952e9bc832
tags: [domain/db, stage/1, level/junior, topic/sql, topic/join, priority/must]
reviewed:
next_review:
priority: must
time: 4
---

# JOIN: inner, left, right, full, cross, self

↑ [[DB 1.1 Реляционная модель и SQL|1.1 Реляционная модель и SQL]] · ← [[DB 1.1.4 SELECT, WHERE, ORDER BY, LIMIT|Предыдущая]] · → [[DB 1.1.6 GROUP BY, HAVING, агрегатные функции|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~4 мин чтения</span><span class="chip">Уровень: junior</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> JOIN — самая частая тема SQL-собеседований; спрашивают виды и типичные ловушки.

## Виды

| JOIN | Результат |
|---|---|
| `INNER JOIN` | только строки с совпадением в обеих таблицах |
| `LEFT JOIN` | все из левой + совпавшие из правой (иначе NULL) |
| `RIGHT JOIN` | зеркально левому (используют редко, меняйте порядок таблиц) |
| `FULL JOIN` | все из обеих таблиц |
| `CROSS JOIN` | декартово произведение (`n × m`) |
| `SELF JOIN` | таблица соединяется сама с собой |
| `LATERAL` | подзапрос может ссылаться на предыдущие таблицы |

```sql
-- клиенты и число их заказов, включая клиентов без заказов
SELECT c.id, c.email, count(o.id) AS orders_count
FROM customers c
LEFT JOIN orders o ON o.customer_id = c.id
GROUP BY c.id, c.email;

-- клиенты без заказов (anti-join)
SELECT c.* FROM customers c
LEFT JOIN orders o ON o.customer_id = c.id
WHERE o.id IS NULL;

-- self join: сотрудник и его руководитель
SELECT e.name AS employee, m.name AS manager
FROM employees e LEFT JOIN employees m ON m.id = e.manager_id;

-- комбинации размеров и цветов
SELECT s.name, c.name FROM sizes s CROSS JOIN colors c;

-- LATERAL: три последних заказа каждого клиента
SELECT c.id, o.*
FROM customers c
CROSS JOIN LATERAL (
  SELECT * FROM orders WHERE customer_id = c.id ORDER BY created_at DESC LIMIT 3
) o;
```

## Типичные ловушки

- **условие в WHERE вместо ON** для LEFT JOIN превращает его в INNER:

```sql
-- неверно: отфильтрует клиентов без оплаченных заказов
LEFT JOIN orders o ON o.customer_id = c.id WHERE o.status = 'paid'
-- верно: условие в ON
LEFT JOIN orders o ON o.customer_id = c.id AND o.status = 'paid'
```

- **дублирование строк** при связи 1:N: `SUM` по родительскому полю удваивается; агрегируйте до JOIN или используйте подзапрос;
- **NULL в ключах** не соединяются (`NULL = NULL` даёт NULL);
- `USING (id)` и `NATURAL JOIN`: второй опасен (соединяет по всем одноимённым столбцам).

## Алгоритмы соединения (как это исполняется)

| Алгоритм | Когда хорош |
|---|---|
| **Nested Loop** | мало строк во внешней таблице, есть индекс во внутренней |
| **Hash Join** | большие таблицы без индекса, равенство |
| **Merge Join** | оба входа отсортированы (по индексу), большие объёмы |

Планировщик выбирает сам; смотрите в `EXPLAIN`.

## Производительность

- индекс на столбцах соединения (особенно внешние ключи);
- соединяйте по типам одного вида (не `int` с `text`);
- уменьшайте вход фильтрацией до соединения;
- порядок таблиц в `INNER JOIN` планировщик меняет сам.

## Вопросы с ответами

> [!question]- Чем LEFT JOIN отличается от INNER JOIN?
> INNER возвращает только совпавшие пары. LEFT сохраняет все строки левой таблицы, подставляя NULL, если пары нет.

> [!question]- Как найти записи без связанных?
> `LEFT JOIN ... WHERE right.id IS NULL` или `NOT EXISTS (SELECT 1 ...)`.

> [!question]- Почему после LEFT JOIN сумма получилась завышенной?
> Связь 1:N размножила строки левой таблицы. Агрегировать надо на нужном уровне: сначала свернуть правую таблицу подзапросом или CTE.
