---
type: topic
domain: db
stage: 1
section: "1.1"
order: 11
status: todo
level: junior
notion_id: 3ea33104867981d5bc3ef00ef7d846a3
tags: [domain/db, stage/1, level/junior, topic/sql, topic/interview, topic/practice, priority/must]
reviewed:
next_review:
priority: must
time: 5
---

# Задачи на SQL с собеседований

↑ [[DB 1.1 Реляционная модель и SQL|1.1 Реляционная модель и SQL]] · ← [[DB 1.1.10 NULL и трёхзначная логика|Предыдущая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~5 мин чтения</span><span class="chip">Уровень: junior</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> Практический блок: типовые задачи, которые дают на живом кодинге. Решайте сначала сами, потом сверяйтесь.

## Тестовая схема

```sql
customers(id, name, email, city, created_at)
orders(id, customer_id, total, status, created_at)
order_items(order_id, product_id, qty, price)
products(id, name, category_id, price)
employees(id, name, salary, department_id, manager_id)
```

## Классика

**1. Второй по величине оклад**

```sql
SELECT max(salary) FROM employees WHERE salary < (SELECT max(salary) FROM employees);
-- устойчивый вариант с окном
SELECT DISTINCT salary FROM (
  SELECT salary, dense_rank() OVER (ORDER BY salary DESC) r FROM employees
) t WHERE r = 2;
```

**2. Дубликаты email**

```sql
SELECT email, count(*) FROM customers GROUP BY email HAVING count(*) > 1;
```

**3. Клиенты без заказов**

```sql
SELECT c.* FROM customers c WHERE NOT EXISTS (SELECT 1 FROM orders o WHERE o.customer_id = c.id);
```

**4. Топ-3 клиента по выручке в каждом городе**

```sql
SELECT * FROM (
  SELECT c.city, c.id, sum(o.total) AS revenue,
         row_number() OVER (PARTITION BY c.city ORDER BY sum(o.total) DESC) AS rn
  FROM customers c JOIN orders o ON o.customer_id = c.id
  GROUP BY c.city, c.id
) t WHERE rn <= 3;
```

**5. Сотрудники с зарплатой выше средней по отделу**

```sql
SELECT * FROM (
  SELECT e.*, avg(salary) OVER (PARTITION BY department_id) AS avg_dep FROM employees e
) t WHERE salary > avg_dep;
```

**6. Накопительная выручка по дням и рост к предыдущему дню**

```sql
SELECT day, revenue,
       sum(revenue) OVER (ORDER BY day) AS running,
       revenue - lag(revenue) OVER (ORDER BY day) AS delta
FROM (SELECT created_at::date AS day, sum(total) AS revenue FROM orders GROUP BY 1) d;
```

**7. Клиенты, сделавшие заказ в 3 месяца подряд (gaps and islands)**

```sql
WITH m AS (
  SELECT DISTINCT customer_id, date_trunc('month', created_at)::date AS month FROM orders
), g AS (
  SELECT customer_id, month,
         month - (row_number() OVER (PARTITION BY customer_id ORDER BY month) * interval '1 month') AS grp
  FROM m
)
SELECT customer_id FROM g GROUP BY customer_id, grp HAVING count(*) >= 3;
```

**8. Иерархия: все подчинённые руководителя (рекурсивный CTE)**

```sql
WITH RECURSIVE t AS (
  SELECT id, name, manager_id FROM employees WHERE id = 1
  UNION ALL
  SELECT e.id, e.name, e.manager_id FROM employees e JOIN t ON e.manager_id = t.id
) SELECT * FROM t;
```

**9. Конверсия воронки (просмотр → корзина → покупка)**

```sql
SELECT count(DISTINCT user_id) FILTER (WHERE event = 'view')     AS viewed,
       count(DISTINCT user_id) FILTER (WHERE event = 'cart')     AS carted,
       count(DISTINCT user_id) FILTER (WHERE event = 'purchase') AS bought
FROM events;
```

**10. Удалить дубликаты, оставив самую раннюю запись**

```sql
DELETE FROM customers c USING customers d
WHERE c.email = d.email AND c.id > d.id;
```

**11. Медиана**

```sql
SELECT percentile_cont(0.5) WITHIN GROUP (ORDER BY total) FROM orders;
```

**12. Пропущенные id в последовательности**

```sql
SELECT g.i FROM generate_series((SELECT min(id) FROM t), (SELECT max(id) FROM t)) g(i)
LEFT JOIN t ON t.id = g.i WHERE t.id IS NULL;
```

## Как отвечать

1. Уточните схему, дубликаты, NULL, ожидаемый объём.
2. Опишите идею словами (JOIN + агрегат, окно, антиджоин).
3. Напишите простое решение, затем оптимизацию.
4. Проверьте граничные случаи: пустые группы, равные значения, NULL.
5. Скажите про индексы и план запроса.

## Вопросы с ответами

> [!question]- Как быстро проверить корректность запроса?
> На малом наборе данных вручную посчитать ожидаемый результат, проверить крайние случаи (пусто, дубли, NULL) и сравнить с альтернативным способом решения.

> [!question]- Когда использовать оконную функцию, а когда GROUP BY?
> Если нужно сохранить детальные строки и добавить агрегат/ранг — окно. Если нужна одна строка на группу — GROUP BY.
