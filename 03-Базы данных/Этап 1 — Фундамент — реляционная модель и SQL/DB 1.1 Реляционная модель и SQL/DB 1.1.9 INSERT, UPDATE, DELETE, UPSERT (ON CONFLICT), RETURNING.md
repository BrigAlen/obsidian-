---
type: topic
domain: db
stage: 1
section: "1.1"
order: 9
status: todo
level: junior
notion_id: 3ea33104867981ebb6c8cd77f1bd5905
tags: [domain/db, stage/1, level/junior, topic/sql, topic/dml, topic/upsert, priority/must]
reviewed:
next_review:
priority: must
time: 4
---

# INSERT, UPDATE, DELETE, UPSERT (ON CONFLICT), RETURNING

↑ [[DB 1.1 Реляционная модель и SQL|1.1 Реляционная модель и SQL]] · ← [[DB 1.1.8 Оконные функции — ROW_NUMBER, RANK, LAG, накопительные суммы|Предыдущая]] · → [[DB 1.1.10 NULL и трёхзначная логика|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~4 мин чтения</span><span class="chip">Уровень: junior</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> Идемпотентные операции, upsert и пакетные обновления — практика реального backend.

## INSERT

```sql
INSERT INTO customers (email, name) VALUES ('a@x.com', 'Анна');

INSERT INTO customers (email, name)
VALUES ('b@x.com', 'Борис'), ('c@x.com', 'Вера')     -- несколько строк одним запросом
RETURNING id, email;

INSERT INTO archive SELECT * FROM orders WHERE created_at < now() - interval '1 year';
```

Пакетная вставка одним запросом гораздо быстрее, чем по одной строке; для больших загрузок — `COPY`.

## UPDATE

```sql
UPDATE orders SET status = 'paid', paid_at = now() WHERE id = 42 RETURNING *;

-- обновление по данным другой таблицы
UPDATE orders o
SET    total = s.sum_total
FROM   (SELECT order_id, sum(price * qty) AS sum_total FROM order_items GROUP BY order_id) s
WHERE  s.order_id = o.id;
```

**Всегда проверяйте `WHERE`**; для рискованных операций используйте транзакцию и предварительный `SELECT` с тем же условием.

## DELETE и TRUNCATE

```sql
DELETE FROM sessions WHERE expires_at < now() RETURNING id;
TRUNCATE TABLE staging RESTART IDENTITY;      -- быстро, не вызывает построчные триггеры DELETE
```

`DELETE` оставляет мёртвые версии строк (нужна автоочистка), `TRUNCATE` освобождает место мгновенно, но берёт сильную блокировку и в PostgreSQL транзакционен.

## UPSERT

```sql
INSERT INTO product_stock (product_id, qty)
VALUES (1, 10)
ON CONFLICT (product_id)
DO UPDATE SET qty = product_stock.qty + EXCLUDED.qty
RETURNING *;

INSERT INTO tags (name) VALUES ('sql') ON CONFLICT (name) DO NOTHING;
```

- `ON CONFLICT` требует уникальный индекс/ограничение на указанных столбцах;
- `EXCLUDED` — строка, которую пытались вставить;
- атомарен и безопасен при гонках (в отличие от «SELECT, затем INSERT»);
- `MERGE` (PostgreSQL 15+) — стандартный SQL для более сложных сценариев.

## RETURNING

Возвращает изменённые строки без отдельного SELECT: получить сгенерированный `id`, значения по умолчанию, старые/новые значения (PostgreSQL 18).

## Идемпотентность и очереди

```sql
-- захват задачи из очереди несколькими воркерами
UPDATE jobs SET status = 'running', started_at = now()
WHERE id = (
  SELECT id FROM jobs WHERE status = 'queued'
  ORDER BY id LIMIT 1
  FOR UPDATE SKIP LOCKED
)
RETURNING *;
```

## Нюансы

- частичные обновления одной строки конкурируют за блокировку: держите транзакции короткими;
- массовые `UPDATE`/`DELETE` разбивайте на батчи (по 1–10 тыс.), чтобы не раздувать WAL и не держать блокировки;
- `UPDATE` без изменений всё равно создаёт новую версию строки, добавляйте `WHERE col IS DISTINCT FROM new`.

## Вопросы с ответами

> [!question]- Как сделать вставку, безопасную к повторам?
> `INSERT ... ON CONFLICT DO NOTHING` (или `DO UPDATE`) по уникальному ключу идемпотентности.

> [!question]- Чем DELETE отличается от TRUNCATE?
> DELETE удаляет построчно (с WHERE, триггерами, оставляет мёртвые версии); TRUNCATE очищает таблицу целиком быстро с эксклюзивной блокировкой.

> [!question]- Зачем RETURNING?
> Получить результат модификации (id, значения по умолчанию) за один вызов, без гонки между INSERT и SELECT.
