---
type: topic
domain: db
stage: 5
section: "5.1"
order: 5
status: todo
level: middle
notion_id: 3ea3310486798164a86de34b0a2fb489
tags: [domain/db, stage/5, level/middle, topic/migrations, topic/zero-downtime, topic/expand-contract, topic/postgresql, priority/should]
reviewed:
next_review:
priority: should
time: 5
---

# Zero-downtime миграции: expand and contract, большие таблицы, индексы CONCURRENTLY

↑ [[DB 5.1 Миграции — EF Core, Flyway, goose|5.1 Миграции: EF Core, Flyway, goose]] · ← [[DB 5.1.4 Миграции EF Core в проде — bundles, скрипты, кто и когда применяет|Предыдущая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~5 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> Главный вопрос senior по эксплуатации: как менять схему под нагрузкой без остановки и блокировок.

## Почему миграции ломают прод

- `ALTER TABLE` берёт **`ACCESS EXCLUSIVE`** блокировку; пока она ждёт, **все новые запросы выстраиваются в очередь** за ней, и сервис «встаёт»;
- перезапись таблицы (изменение типа, `DEFAULT` в старых версиях) на больших объёмах занимает часы;
- несовместимость версий: новый код с старой схемой и наоборот при rolling update.

## Паттерн Expand and Contract (parallel change)

Изменение делится на совместимые шаги.

```text
1. EXPAND:   добавить новую структуру (колонка/таблица), код пишет в старую И новую
2. MIGRATE:  бэкфилл старых данных (порциями, в фоне)
3. SWITCH:   читать из новой; старая пока остаётся (обратная совместимость для отката)
4. CONTRACT: удалить старую структуру после того, как ни одна версия кода её не использует
```

**Пример: переименование колонки `full_name` → `name`**

1. Миграция: `ALTER TABLE users ADD COLUMN name text;`
2. Код v2: пишет в обе колонки, читает `coalesce(name, full_name)`.
3. Бэкфилл батчами: `UPDATE users SET name = full_name WHERE id BETWEEN ... AND name IS NULL;`
4. Код v3: использует только `name`.
5. Позже миграция: `ALTER TABLE users DROP COLUMN full_name;`

Никогда не делайте «rename» за один шаг при rolling update: одна версия приложения упадёт.

## Безопасные операции (PostgreSQL)

| Операция | Безопасный способ |
|---|---|
| Добавить столбец | `ADD COLUMN ... NULL` — мгновенно; `DEFAULT` константа — мгновенно с PostgreSQL 11 |
| Добавить `NOT NULL` | через `CHECK (col IS NOT NULL) NOT VALID` → `VALIDATE CONSTRAINT` → `SET NOT NULL` (PG12+ использует CHECK, без сканирования) |
| Внешний ключ | `ADD CONSTRAINT ... FOREIGN KEY ... NOT VALID`, затем `VALIDATE CONSTRAINT` (не блокирует запись) |
| Индекс | `CREATE INDEX CONCURRENTLY` (не в транзакции) |
| Уникальный ограничение | создать уникальный индекс `CONCURRENTLY`, затем `ADD CONSTRAINT ... UNIQUE USING INDEX` |
| Удалить индекс | `DROP INDEX CONCURRENTLY` |
| Изменить тип столбца | новый столбец + бэкфилл + переключение (не `ALTER TYPE`, который переписывает таблицу) |
| Удалить столбец | сначала перестать использовать в коде, затем `DROP COLUMN` (метаданные) |
| Партиционирование существующей таблицы | создать новую партиционированную, перенос батчами, подмена |

```sql
-- lock_timeout защищает от долгого ожидания блокировки и каскада очереди
SET lock_timeout = '3s';
SET statement_timeout = '15min';

ALTER TABLE orders ADD COLUMN currency char(3);
ALTER TABLE orders ADD CONSTRAINT orders_total_positive CHECK (total >= 0) NOT VALID;
ALTER TABLE orders VALIDATE CONSTRAINT orders_total_positive;   -- SHARE UPDATE EXCLUSIVE, не блокирует запись

CREATE INDEX CONCURRENTLY idx_orders_customer ON orders (customer_id);
-- если прервался: остаётся INVALID индекс — удалить и повторить
SELECT indexrelid::regclass FROM pg_index WHERE NOT indisvalid;
```

При неудаче из-за `lock_timeout` миграцию **повторяют** (retry с паузой), а не увеличивают таймаут.

## Бэкфилл больших таблиц

- **батчами** по 1000–10000 строк по первичному ключу, с паузами (`pg_sleep`), чтобы не раздувать WAL и не нагружать реплики (lag);
- отдельный фоновый job/скрипт, а не часть «миграции деплоя»;
- идемпотентный, возобновляемый (`WHERE new IS NULL`), с прогрессом и метриками;
- следить за `autovacuum`, репликацией, нагрузкой;
- до завершения бэкфилла код обязан уметь читать оба варианта.

```sql
-- порция
WITH batch AS (
  SELECT id FROM users WHERE name IS NULL ORDER BY id LIMIT 5000 FOR UPDATE SKIP LOCKED
)
UPDATE users u SET name = u.full_name FROM batch WHERE u.id = batch.id;
```

## Инструменты

`pg_repack` (перестроение без блокировок), `pgroll`, `reshape`, `gh-ost`/`pt-online-schema-change` (MySQL), Atlas lint (анализ опасных изменений), `squawk` (линтер миграций PostgreSQL), `strong_migrations` (Rails).

## Деплой и совместимость

```text
Migration N (expand, совместима со старым кодом) → deploy code (пишет в обе) → backfill → deploy code (читает новое) → Migration N+1 (contract)
```

- схема и код выкатываются **в разных релизах**; каждый релиз обратно совместим с предыдущим (две версии работают одновременно при rolling update, canary, blue/green);
- **feature flags** для переключения чтения/записи;
- **откат кода** должен быть возможен без отката схемы.

## Чек-лист перед миграцией

- [ ] какие блокировки берёт команда и насколько долго?
- [ ] есть `lock_timeout` и `statement_timeout`?
- [ ] совместима ли новая схема со старым кодом и наоборот?
- [ ] размер таблицы и время на копии прод-данных?
- [ ] `CONCURRENTLY` для индексов?
- [ ] план отката/roll-forward, бэкап?
- [ ] мониторинг: блокировки (`pg_stat_activity`), replication lag, ошибки приложения?
- [ ] окно и ответственные, коммуникация?

## Вопросы с ответами

> [!question]- Что такое expand and contract?
> Поэтапное изменение: сначала расширяем схему совместимым образом, переносим данные и переключаем код, и только потом удаляем старое. Так каждая версия приложения работает с обеими схемами, и простоя нет.

> [!question]- Почему ALTER TABLE опасен даже если выполняется мгновенно?
> Для взятия ACCESS EXCLUSIVE блокировки он ждёт завершения всех текущих транзакций с таблицей, а новые запросы встают за ним в очередь, вызывая каскадный простой. Нужен `lock_timeout` и повтор.

> [!question]- Как добавить NOT NULL в большую таблицу без блокировки?
> Добавить `CHECK (col IS NOT NULL) NOT VALID`, выполнить `VALIDATE CONSTRAINT` (не блокирует запись), затем `SET NOT NULL` (быстро при наличии валидного CHECK), после чего удалить CHECK.
