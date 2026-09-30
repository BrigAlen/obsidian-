---
type: topic
domain: db
stage: 2
section: "2.1"
order: 11
status: todo
level: middle
notion_id: 3ea3310486798140bcecf113f066d667
tags: [domain/db, stage/2, level/middle, topic/postgresql, topic/plpgsql, topic/triggers, topic/views, priority/must]
reviewed:
next_review:
priority: must
time: 5
---

# Функции, триггеры, представления, materialized views

↑ [[DB 2.1 PostgreSQL — индексы, транзакции, оптимизация|2.1 PostgreSQL: индексы, транзакции, оптимизация]] · ← [[DB 2.1.10 Оптимизация запросов и пул соединений (PgBouncer)|Предыдущая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~5 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> Логика в БД — спорная тема: нужно знать возможности и цену.

## Представления (VIEW)

Сохранённый запрос; данных не хранит, при обращении подставляется в запрос.

```sql
CREATE VIEW v_active_customers AS
SELECT c.id, c.email, count(o.id) AS orders
FROM customers c LEFT JOIN orders o ON o.customer_id = c.id AND o.status = 'paid'
WHERE c.deleted_at IS NULL GROUP BY c.id;
```

Применения: упрощение запросов, слой совместимости, ограничение доступа к столбцам (`security_barrier`, `security_invoker`), простые представления обновляемы.

## Materialized view

Хранит результат запроса физически; обновляется вручную/по расписанию.

```sql
CREATE MATERIALIZED VIEW mv_daily_revenue AS
SELECT date_trunc('day', created_at) AS day, sum(total) AS revenue
FROM orders WHERE status = 'paid' GROUP BY 1;

CREATE UNIQUE INDEX ON mv_daily_revenue (day);
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_daily_revenue;   -- без блокировки чтения, нужен уникальный индекс
```

Плюсы: быстрые тяжёлые отчёты. Минусы: устаревание данных, стоимость обновления (полное пересчитывание). Для инкрементальных агрегатов — вручную (триггеры, джобы) или расширения.

## Функции (PL/pgSQL и другие)

```sql
CREATE OR REPLACE FUNCTION order_total(p_order bigint) RETURNS numeric
LANGUAGE sql STABLE AS $$
  SELECT coalesce(sum(price * qty), 0) FROM order_items WHERE order_id = p_order
$$;

CREATE FUNCTION transfer(p_from bigint, p_to bigint, p_amount numeric) RETURNS void
LANGUAGE plpgsql AS $$
BEGIN
  IF p_amount <= 0 THEN RAISE EXCEPTION 'amount must be positive'; END IF;
  UPDATE accounts SET balance = balance - p_amount WHERE id = p_from AND balance >= p_amount;
  IF NOT FOUND THEN RAISE EXCEPTION 'insufficient funds'; END IF;
  UPDATE accounts SET balance = balance + p_amount WHERE id = p_to;
END $$;
```

- **волатильность**: `IMMUTABLE` (одинаковый результат, можно в индексе), `STABLE` (в пределах оператора), `VOLATILE` (по умолчанию); неверная пометка ломает планировщик;
- **PROCEDURE** (`CALL`) — может управлять транзакциями;
- функции-таблицы: `RETURNS TABLE(...)`, `SETOF`;
- языки: SQL, PL/pgSQL, PL/Python, PL/V8 и др.;
- `SECURITY DEFINER` — выполняется с правами владельца (осторожно с `search_path`).

## Триггеры

Код, вызываемый при `INSERT/UPDATE/DELETE`.

```sql
CREATE FUNCTION set_updated_at() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN NEW.updated_at = now(); RETURN NEW; END $$;

CREATE TRIGGER trg_orders_updated BEFORE UPDATE ON orders
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- аудит
CREATE TRIGGER trg_orders_audit AFTER INSERT OR UPDATE OR DELETE ON orders
FOR EACH ROW EXECUTE FUNCTION audit_changes();
```

Виды: `BEFORE` / `AFTER` / `INSTEAD OF` (для представлений), `FOR EACH ROW` / `FOR EACH STATEMENT`, `WHEN (условие)`, с переходными таблицами (`REFERENCING NEW TABLE`).

Применения: `updated_at`, аудит, поддержка производных данных, ограничения сложнее `CHECK`.

**Минусы**: скрытая логика, сложнее отладка и тесты, снижают скорость массовых операций, каскады триггеров, трудно версионировать. Используйте осознанно; бизнес-логику чаще держат в приложении.

## Генерируемые столбцы

```sql
ALTER TABLE items ADD COLUMN total numeric GENERATED ALWAYS AS (price * qty) STORED;
```

## Уведомления

`LISTEN/NOTIFY`: лёгкий pub/sub внутри БД; не гарантирует доставку, не работает с transaction pooling.

## Правила и расширения

Rules — устаревший механизм (используйте триггеры/представления). Расширения (`CREATE EXTENSION`): `pg_stat_statements`, `pg_trgm`, `uuid-ossp`, `postgis`, `pg_cron`, `pgcrypto`.

## Где держать логику

| В БД | В приложении |
|---|---|
| целостность (`CHECK`, FK), аудит, производные столбцы, пакетная обработка данных рядом с ними | бизнес-правила, интеграции, тестируемая и версионируемая логика |

## Вопросы с ответами

> [!question]- Чем materialized view отличается от обычного?
> Хранит результат физически и требует обновления (`REFRESH`), зато читается быстро; обычное представление выполняет запрос при каждом обращении.

> [!question]- Плюсы и минусы триггеров?
> Плюсы: гарантированное выполнение на уровне БД (аудит, инварианты). Минусы: скрытое поведение, сложность тестирования и отладки, снижение производительности массовых операций.

> [!question]- Зачем пометки IMMUTABLE/STABLE?
> Планировщик использует их для оптимизаций (кэширование, индексы по выражениям). Неправильная пометка приводит к неверным результатам.
