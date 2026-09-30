---
type: topic
domain: db
stage: 2
section: "2.1"
order: 7
status: todo
level: middle
notion_id: 3ea3310486798150a3fbf78c0564a6d6
tags: [domain/db, stage/2, level/middle, topic/postgresql, topic/locks, topic/deadlock, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Блокировки: row, table, advisory, SELECT FOR UPDATE, deadlocks

↑ [[DB 2.1 PostgreSQL — индексы, транзакции, оптимизация|2.1 PostgreSQL: индексы, транзакции, оптимизация]] · ← [[DB 2.1.6 MVCC, VACUUM, bloat|Предыдущая]] · → [[DB 2.1.8 JSONB, массивы, полнотекстовый поиск|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> Конкуренция за данные — типичная боль высоконагруженных систем. Спрашивают виды блокировок и способы избежать deadlock.

## Блокировки строк

| Режим | Команда | Блокирует |
|---|---|---|
| `FOR UPDATE` | `SELECT ... FOR UPDATE` | обновление, удаление, другой FOR UPDATE / SHARE |
| `FOR NO KEY UPDATE` | обычный `UPDATE` (не меняющий ключ) | |
| `FOR SHARE` | | изменения строки, разрешает другой SHARE |
| `FOR KEY SHARE` | берётся при проверке FK | удаление и изменение ключа |

Модификаторы: `NOWAIT` (сразу ошибка), `SKIP LOCKED` (пропустить занятые), `OF table`.

```sql
-- очередь задач без ожидания друг друга
SELECT * FROM jobs WHERE status = 'queued'
ORDER BY id FOR UPDATE SKIP LOCKED LIMIT 10;
```

Читатели (`SELECT` без FOR) **не блокируются**.

## Блокировки таблиц

| Режим | Кто берёт | Конфликтует с |
|---|---|---|
| `ACCESS SHARE` | `SELECT` | только `ACCESS EXCLUSIVE` |
| `ROW EXCLUSIVE` | `INSERT/UPDATE/DELETE` | `SHARE` и выше |
| `SHARE UPDATE EXCLUSIVE` | `VACUUM`, `CREATE INDEX CONCURRENTLY` | себя, SHARE и выше |
| `SHARE` | `CREATE INDEX` (не CONCURRENTLY) | пишущие |
| `ACCESS EXCLUSIVE` | `DROP`, `TRUNCATE`, `VACUUM FULL`, большинство `ALTER TABLE` | **всё**, даже SELECT |

**Опасность**: `ALTER TABLE` берёт ACCESS EXCLUSIVE и ждёт в очереди; пока он ждёт, **все новые запросы к таблице встают за ним**. Решения: `SET lock_timeout = '2s'`, короткие миграции, повтор при неудаче.

## Advisory locks

Блокировки по произвольному ключу на уровне приложения: не привязаны к данным.

```sql
SELECT pg_advisory_lock(42);              -- на сессию
SELECT pg_try_advisory_xact_lock(42);     -- на транзакцию, не ждёт
```

Применение: единственный воркер задачи (cron), сериализация операции над сущностью, миграции.

## Deadlock

Две транзакции удерживают ресурсы и ждут друг друга.

```text
T1: UPDATE accounts SET ... WHERE id = 1;   T2: UPDATE accounts SET ... WHERE id = 2;
T1: UPDATE accounts SET ... WHERE id = 2;   T2: UPDATE accounts SET ... WHERE id = 1;   -- deadlock
```

PostgreSQL обнаруживает цикл (после `deadlock_timeout`, 1 с) и **прерывает одну транзакцию** (`40P01`).

Как избежать:

- **единый порядок** захвата ресурсов (сортировать id);
- короткие транзакции, меньше строк за раз;
- `SELECT ... FOR UPDATE` с упорядочиванием;
- индексы для внешних ключей (иначе больше блокировок);
- retry при ошибке.

## Диагностика

```sql
SELECT pid, pg_blocking_pids(pid) AS blocked_by, state, wait_event_type, wait_event, query
FROM pg_stat_activity WHERE cardinality(pg_blocking_pids(pid)) > 0;

SELECT * FROM pg_locks WHERE NOT granted;
```

Настройки: `lock_timeout`, `statement_timeout`, `idle_in_transaction_session_timeout`, `log_lock_waits = on`.

## Оптимистичная и пессимистичная блокировка

- **пессимистичная**: `SELECT FOR UPDATE`, подходит при высокой конкуренции за строку;
- **оптимистичная**: столбец `version`/`xmin`, проверка при `UPDATE ... WHERE version = ?`, подходит при редких конфликтах; конфликт = повтор.

## Вопросы с ответами

> [!question]- Блокирует ли SELECT запись?
> Обычный SELECT не блокирует ни читателей, ни писателей благодаря MVCC. `SELECT FOR UPDATE` блокирует строки.

> [!question]- Что делает SKIP LOCKED?
> Пропускает уже заблокированные другими транзакциями строки: удобно для очередей задач с несколькими воркерами.

> [!question]- Как безопасно выполнить ALTER TABLE на нагруженной таблице?
> Установить `lock_timeout`, выполнять короткими шагами, использовать безблокировочные варианты (`CONCURRENTLY`, `NOT VALID` + `VALIDATE`), повторять при неудаче в менее загруженное время.
