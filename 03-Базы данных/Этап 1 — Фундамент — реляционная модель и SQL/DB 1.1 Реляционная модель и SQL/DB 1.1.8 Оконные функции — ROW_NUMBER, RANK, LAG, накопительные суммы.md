---
type: topic
domain: db
stage: 1
section: "1.1"
order: 8
status: todo
level: junior
notion_id: 3ea33104867981228662fe5e85834bbb
tags: [domain/db, stage/1, level/junior, topic/sql, topic/window-functions, priority/must]
reviewed:
next_review:
priority: must
time: 4
---

# Оконные функции: ROW_NUMBER, RANK, LAG, накопительные суммы

↑ [[DB 1.1 Реляционная модель и SQL|1.1 Реляционная модель и SQL]] · ← [[DB 1.1.7 Подзапросы, EXISTS, IN, CTE, рекурсивные CTE|Предыдущая]] · → [[DB 1.1.9 INSERT, UPDATE, DELETE, UPSERT (ON CONFLICT), RETURNING|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~4 мин чтения</span><span class="chip">Уровень: junior</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> Топ-N по группе, накопительные итоги, сравнение с предыдущей строкой — самые частые задачи уровня middle.

## Идея

Оконная функция считает значение **по набору строк, связанных с текущей**, не схлопывая строки, в отличие от `GROUP BY`.

```sql
функция() OVER (
  PARTITION BY ...     -- группы
  ORDER BY ...         -- порядок в группе
  ROWS BETWEEN ...     -- рамка
)
```

## Ранжирование

| Функция | Поведение при равных значениях |
|---|---|
| `ROW_NUMBER()` | уникальные номера 1, 2, 3, 4 |
| `RANK()` | одинаковый ранг, пропуск: 1, 2, 2, 4 |
| `DENSE_RANK()` | без пропусков: 1, 2, 2, 3 |
| `NTILE(n)` | разбиение на n корзин |
| `PERCENT_RANK()`, `CUME_DIST()` | относительное положение |

```sql
-- топ-3 заказа каждого клиента
SELECT * FROM (
  SELECT o.*, row_number() OVER (PARTITION BY customer_id ORDER BY total DESC) AS rn
  FROM orders o
) t WHERE rn <= 3;

-- удаление дубликатов, оставляя один
DELETE FROM users WHERE id IN (
  SELECT id FROM (
    SELECT id, row_number() OVER (PARTITION BY email ORDER BY id) AS rn FROM users
  ) t WHERE rn > 1
);
```

## Смещение

```sql
SELECT date, revenue,
       lag(revenue)  OVER (ORDER BY date)                   AS prev_day,
       lead(revenue) OVER (ORDER BY date)                   AS next_day,
       revenue - lag(revenue) OVER (ORDER BY date)          AS delta,
       first_value(revenue) OVER (PARTITION BY month ORDER BY date) AS first_in_month
FROM daily_revenue;
```

## Накопительные и скользящие

```sql
SELECT date, revenue,
       sum(revenue) OVER (ORDER BY date)                                        AS running_total,
       avg(revenue) OVER (ORDER BY date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS moving_avg_7d,
       revenue::numeric / sum(revenue) OVER ()                                  AS share
FROM daily_revenue;
```

## Рамки (frame)

- `ROWS` — по числу строк, `RANGE` — по значению (равные ORDER BY-значения попадают вместе), `GROUPS`;
- по умолчанию при наличии `ORDER BY`: `RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW` (нарастающий итог);
- для `last_value` нужна рамка до `UNBOUNDED FOLLOWING`, иначе результат неожидан.

## Полезные шаблоны

- **сессии/пробелы (gaps and islands)**: `id - row_number() OVER (ORDER BY id)` как ключ группы непрерывных значений;
- **последняя запись на сущность**: `row_number() ... = 1`;
- **разница с предыдущим**: `lag`;
- **процентили и медиана** — агрегаты `percentile_cont`.

## Ограничения

Оконные функции нельзя использовать в `WHERE`, `GROUP BY`, `HAVING`: оборачивайте в подзапрос или CTE. Именованное окно: `WINDOW w AS (PARTITION BY ... ORDER BY ...)`.

## Вопросы с ответами

> [!question]- Чем RANK отличается от DENSE_RANK и ROW_NUMBER?
> ROW_NUMBER нумерует строки без повторов; RANK при равенстве даёт одинаковый ранг и пропускает следующие; DENSE_RANK одинаковый ранг без пропусков.

> [!question]- Как найти топ-N в каждой группе?
> `row_number() OVER (PARTITION BY group ORDER BY metric DESC)` во вложенном запросе и фильтр `rn <= N`.

> [!question]- Почему нельзя фильтровать по оконной функции в WHERE?
> `WHERE` выполняется раньше вычисления оконных функций. Используйте подзапрос, CTE или `QUALIFY` (в БД, где он есть).
