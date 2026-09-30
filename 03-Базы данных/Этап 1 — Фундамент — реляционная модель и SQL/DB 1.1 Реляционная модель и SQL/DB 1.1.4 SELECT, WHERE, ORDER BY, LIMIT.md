---
type: topic
domain: db
stage: 1
section: "1.1"
order: 4
status: todo
level: junior
notion_id: 3ea33104867981a0886ee55eb1122371
tags: [domain/db, stage/1, level/junior, topic/sql, topic/select, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# SELECT, WHERE, ORDER BY, LIMIT

↑ [[DB 1.1 Реляционная модель и SQL|1.1 Реляционная модель и SQL]] · ← [[DB 1.1.3 Проектирование схемы — ER, типы данных, суррогатные ключи, UUID|Предыдущая]] · → [[DB 1.1.5 JOIN — inner, left, right, full, cross, self|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: junior</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> База любого SQL-собеседования: порядок выполнения запроса и работа с фильтрами.

## Синтаксис

```sql
SELECT DISTINCT c.email, o.total AS order_total
FROM   orders o
JOIN   customers c ON c.id = o.customer_id
WHERE  o.status = 'paid'
  AND  o.created_at >= now() - interval '30 days'
ORDER  BY o.total DESC, c.email
LIMIT  20 OFFSET 40;
```

## Логический порядок выполнения

1. `FROM` / `JOIN`
2. `WHERE`
3. `GROUP BY`
4. `HAVING`
5. `SELECT` (вычисление выражений, `DISTINCT`)
6. `ORDER BY`
7. `LIMIT` / `OFFSET`

Поэтому **алиас из `SELECT` нельзя использовать в `WHERE`**, но можно в `ORDER BY`.

## Фильтры в WHERE

| Оператор | Пример |
|---|---|
| сравнения | `=`, `<>`, `<`, `<=`, `>`, `>=` |
| диапазон | `BETWEEN 10 AND 20` (обе границы включаются) |
| набор | `status IN ('new', 'paid')` |
| шаблон | `name LIKE 'Ив%'`, `ILIKE` (без регистра) |
| регулярные | `~`, `~*` (PostgreSQL) |
| NULL | `IS NULL`, `IS NOT NULL`, `IS DISTINCT FROM` |
| логика | `AND`, `OR`, `NOT` (приоритет: `NOT` > `AND` > `OR`, ставьте скобки) |

## ORDER BY и LIMIT

- без `ORDER BY` порядок строк **не гарантирован**;
- `LIMIT` без `ORDER BY` возвращает произвольные строки;
- `NULLS FIRST` / `NULLS LAST`; по умолчанию в PostgreSQL NULL считаются наибольшими;
- `OFFSET` большого размера медленный (БД читает и отбрасывает строки): для пагинации используйте **keyset**:

```sql
SELECT * FROM orders
WHERE (created_at, id) < ($1, $2)
ORDER BY created_at DESC, id DESC
LIMIT 20;
```

## Полезные приёмы

```sql
SELECT DISTINCT ON (customer_id) customer_id, id, created_at   -- последний заказ клиента (PostgreSQL)
FROM orders ORDER BY customer_id, created_at DESC;

SELECT count(*) FILTER (WHERE status = 'paid') AS paid, count(*) AS total FROM orders;

SELECT id, CASE WHEN total >= 1000 THEN 'крупный' ELSE 'обычный' END AS kind FROM orders;

SELECT coalesce(nickname, name) FROM users;
```

## Оптимизация

- не используйте `SELECT *` в продакшн-коде: лишние данные, ломает covering-индексы;
- условие на индексированный столбец без функции: `WHERE created_at >= ...`, а не `WHERE date(created_at) = ...`;
- `LIKE '%abc'` не использует обычный B-tree, для поиска подстроки нужен `pg_trgm` + GIN.

## Вопросы с ответами

> [!question]- Почему алиас из SELECT нельзя использовать в WHERE?
> `WHERE` выполняется раньше `SELECT`; на этом шаге алиас ещё не существует. Используйте выражение целиком, подзапрос или CTE.

> [!question]- Как получить последние N записей на каждую группу?
> `DISTINCT ON`, оконная функция `ROW_NUMBER() OVER (PARTITION BY ... ORDER BY ...)` с фильтром `rn <= N` или `LATERAL` подзапрос.

> [!question]- Чем плох OFFSET на больших значениях?
> Приходится прочитать и отбросить все пропущенные строки; keyset-пагинация использует индекс и работает за постоянное время.
