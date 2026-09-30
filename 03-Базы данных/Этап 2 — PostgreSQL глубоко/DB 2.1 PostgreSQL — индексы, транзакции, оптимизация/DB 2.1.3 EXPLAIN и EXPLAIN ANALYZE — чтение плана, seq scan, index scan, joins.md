---
type: topic
domain: db
stage: 2
section: "2.1"
order: 3
status: todo
level: middle
notion_id: 3ea33104867981be8473c115b0d1470d
tags: [domain/db, stage/2, level/middle, topic/postgresql, topic/explain, topic/optimization, priority/must]
reviewed:
next_review:
priority: must
time: 4
---

# EXPLAIN и EXPLAIN ANALYZE: чтение плана, seq scan, index scan, joins

↑ [[DB 2.1 PostgreSQL — индексы, транзакции, оптимизация|2.1 PostgreSQL: индексы, транзакции, оптимизация]] · ← [[DB 2.1.2 Индексы — B-tree, Hash, GIN, GiST, BRIN, составные, частичные, covering|Предыдущая]] · → [[DB 2.1.4 Транзакции и ACID|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~4 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> «Запрос тормозит: что делаете?» — ответ начинается с EXPLAIN. Нужно уметь читать план.

## Команды

```sql
EXPLAIN SELECT ...;                                  -- план и оценки, без выполнения
EXPLAIN (ANALYZE, BUFFERS, VERBOSE) SELECT ...;      -- реальное выполнение + статистика буферов
EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) ...;
```

**Осторожно**: `ANALYZE` действительно выполняет запрос (включая `INSERT/UPDATE/DELETE`): оборачивайте в транзакцию с `ROLLBACK`.

## Как читать

```text
Nested Loop  (cost=0.43..120.5 rows=10 width=64) (actual time=0.03..0.9 rows=12 loops=1)
  -> Index Scan using idx_customers_pk on customers c  (cost=0.29..8.3 rows=1 ...)
       Index Cond: (id = 42)
  -> Index Scan using idx_orders_customer on orders o  (cost=0.14..90 rows=10 ...)
       Index Cond: (customer_id = c.id)
Planning Time: 0.2 ms
Execution Time: 1.1 ms
```

- **cost=startup..total**: условные единицы, оценка планировщика;
- **rows**: оценка числа строк; `actual rows` — реальное;
- **loops**: сколько раз выполнялся узел (умножайте actual time и rows на loops);
- читать план **снизу вверх, изнутри наружу**.

## Основные узлы

| Узел | Смысл |
|---|---|
| **Seq Scan** | полное чтение таблицы |
| **Index Scan** | по индексу + чтение строк из таблицы |
| **Index Only Scan** | только индекс |
| **Bitmap Index/Heap Scan** | набор страниц по индексу, для средней селективности и `OR` |
| **Nested Loop** | для каждой строки внешнего — поиск во внутреннем |
| **Hash Join** | строит хэш-таблицу меньшей стороны |
| **Merge Join** | слияние отсортированных входов |
| **Sort** / **Incremental Sort** | сортировка (может уходить на диск) |
| **HashAggregate** / **GroupAggregate** | агрегирование |
| **Gather** | параллельные воркеры |

## Что искать

1. **Расхождение оценок и реальности** (`rows=10` против `actual rows=1000000`): устаревшая статистика, коррелирующие столбцы → `ANALYZE`, расширенная статистика `CREATE STATISTICS`.
2. **Seq Scan на большой таблице** с селективным условием → нет индекса или он не подходит.
3. **Rows Removed by Filter** очень большой → условие фильтрует поздно, нужен индекс.
4. **Sort Method: external merge Disk** → мало `work_mem`.
5. **Nested Loop с большим числом loops** во внутреннем Seq Scan.
6. **Buffers: shared read** высоко → чтения с диска, кэш не помогает.
7. **Hash Batches > 1** → хэш не помещается в `work_mem`.
8. **Heap Fetches** в Index Only Scan высоки → нужен VACUUM.
9. Большое **Planning Time** (много партиций, сложные запросы).

## Пример оптимизации

```sql
-- было: Seq Scan по 5 млн строк, 800 мс
EXPLAIN ANALYZE SELECT * FROM orders WHERE customer_id = 42 AND status = 'new' ORDER BY created_at DESC LIMIT 20;

-- решение
CREATE INDEX CONCURRENTLY idx_orders_cust_status_created ON orders (customer_id, status, created_at DESC);
-- стало: Index Scan, 0.3 мс, без Sort
```

## Инструменты

`pg_stat_statements` (найти дорогие запросы), `auto_explain` (планы медленных запросов в лог), визуализаторы (explain.dalibo.com, explain.depesz.com), `pgMustard`.

## Вопросы с ответами

> [!question]- Чем EXPLAIN отличается от EXPLAIN ANALYZE?
> EXPLAIN показывает оценочный план без выполнения, ANALYZE выполняет запрос и показывает реальное время и число строк.

> [!question]- Почему планировщик выбрал Seq Scan при наличии индекса?
> Селективность низкая (нужна большая доля строк), таблица мала, статистика устарела, индекс не подходит условию (функция, тип, порядок), либо оценка стоимости выше.

> [!question]- Что делать, если оценка rows сильно расходится с реальностью?
> Выполнить `ANALYZE`, увеличить `default_statistics_target` для столбцов, создать расширенную статистику для коррелирующих столбцов.
