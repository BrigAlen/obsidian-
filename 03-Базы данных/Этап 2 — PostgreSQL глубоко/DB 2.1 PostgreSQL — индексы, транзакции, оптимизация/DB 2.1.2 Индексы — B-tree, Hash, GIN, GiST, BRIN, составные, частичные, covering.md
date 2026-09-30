---
type: topic
domain: db
stage: 2
section: "2.1"
order: 2
status: todo
level: middle
notion_id: 3ea33104867981adbeefd8a4ab4b25cc
tags: [domain/db, stage/2, level/middle, topic/postgresql, topic/indexes, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Индексы: B-tree, Hash, GIN, GiST, BRIN, составные, частичные, covering

↑ [[DB 2.1 PostgreSQL — индексы, транзакции, оптимизация|2.1 PostgreSQL: индексы, транзакции, оптимизация]] · ← [[DB 2.1.1 Архитектура PostgreSQL — процессы, страницы, WAL, shared buffers|Предыдущая]] · → [[DB 2.1.3 EXPLAIN и EXPLAIN ANALYZE — чтение плана, seq scan, index scan, joins|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> Индексы — главный рычаг производительности. Нужно знать типы, порядок столбцов и когда индекс не работает.

## Зачем и цена

Индекс ускоряет чтение, но замедляет запись (каждый INSERT/UPDATE/DELETE обновляет индексы), занимает место и усложняет обслуживание. Индексируем то, что используется в `WHERE`, `JOIN`, `ORDER BY`, `GROUP BY`.

## Типы

| Тип | Подходит для | Операторы |
|---|---|---|
| **B-tree** (по умолчанию) | равенство, диапазон, сортировка, `LIKE 'abc%'` | `= < > BETWEEN`, `ORDER BY` |
| **Hash** | только равенство (после 10-й версии безопасен) | `=` |
| **GIN** | составные значения: `jsonb`, массивы, полнотекстовый поиск, `pg_trgm` | `@>`, `?`, `@@`, `LIKE '%x%'` (trgm) |
| **GiST** | геометрия, диапазоны, ближайшие соседи, полнотекст | `&&`, `<->` |
| **SP-GiST** | префиксные деревья, неравномерные данные | |
| **BRIN** | огромные таблицы с физической корреляцией (время) | компактный, диапазоны блоков |
| **Bloom** | много столбцов, равенство | расширение |

```sql
CREATE INDEX idx_orders_customer ON orders (customer_id);
CREATE INDEX idx_docs_data ON docs USING gin (data jsonb_path_ops);
CREATE INDEX idx_events_ts ON events USING brin (created_at);
CREATE INDEX idx_users_name_trgm ON users USING gin (name gin_trgm_ops);
```

## Составные индексы

Порядок столбцов важен: индекс `(a, b, c)` эффективен для условий по `a`, `a, b`, `a, b, c` (**левый префикс**), но не для `b` отдельно.

Правило: сначала столбцы с **равенством**, затем с диапазоном, затем для сортировки.

```sql
-- запрос: WHERE customer_id = ? AND status = ? ORDER BY created_at DESC
CREATE INDEX idx_orders_cust_status_created ON orders (customer_id, status, created_at DESC);
```

## Частичные индексы

Индексируют часть строк, компактнее и быстрее.

```sql
CREATE INDEX idx_orders_active ON orders (created_at) WHERE status = 'new';
CREATE UNIQUE INDEX uq_users_email_active ON users (lower(email)) WHERE deleted_at IS NULL;
```

## Индексы по выражению

```sql
CREATE INDEX idx_users_lower_email ON users (lower(email));   -- для WHERE lower(email) = ?
```

## Covering (INCLUDE) и Index Only Scan

```sql
CREATE INDEX idx_orders_cust_inc ON orders (customer_id) INCLUDE (total, status);
```

Все нужные столбцы лежат в индексе, таблица не читается (**Index Only Scan**). Работает, если карта видимости актуальна (нужен VACUUM).

## Когда индекс не используется

- функция над столбцом (`WHERE date(created_at) = ...`, `lower(col)` без функционального индекса);
- неявное приведение типов;
- `LIKE '%abc'` (нужен `pg_trgm`);
- низкая селективность (большая доля строк: seq scan дешевле);
- `OR` по разным столбцам (может помочь BitmapOr);
- устаревшая статистика (`ANALYZE`);
- нарушен порядок столбцов в составном индексе;
- маленькая таблица: последовательное чтение быстрее.

## Обслуживание

```sql
CREATE INDEX CONCURRENTLY idx ON t (col);      -- без блокировки записи (дольше, нельзя внутри транзакции)
REINDEX INDEX CONCURRENTLY idx;                -- перестроить раздутый индекс
DROP INDEX CONCURRENTLY idx;
```

Поиск неиспользуемых: `pg_stat_user_indexes.idx_scan = 0`. Дубли и избыточные (`(a)` при существующем `(a, b)`).

## Внешние ключи

Индексы на FK не создаются автоматически. Без индекса `JOIN` и каскадное удаление родителя делают seq scan дочерней таблицы.

## Вопросы с ответами

> [!question]- Индекс (a, b): будет ли он использоваться для WHERE b = 1?
> Обычно нет (или очень неэффективно): индекс упорядочен сначала по `a`. Нужен индекс с `b` первым либо отдельный.

> [!question]- Чем частичный индекс полезен?
> Меньше размер и стоимость записи, ускоряет типовые запросы к подмножеству (активные, не удалённые), позволяет уникальность на подмножестве.

> [!question]- Зачем CONCURRENTLY?
> Создание индекса без долгой блокировки записи в таблицу; цена — больше времени и невозможность выполнить в транзакции.
