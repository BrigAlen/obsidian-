---
type: topic
domain: db
stage: 2
section: "2.1"
order: 4
status: todo
level: middle
notion_id: 3ea331048679818bb5dee9698aa4864a
tags: [domain/db, stage/2, level/middle, topic/postgresql, topic/transactions, topic/acid, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Транзакции и ACID

↑ [[DB 2.1 PostgreSQL — индексы, транзакции, оптимизация|2.1 PostgreSQL: индексы, транзакции, оптимизация]] · ← [[DB 2.1.3 EXPLAIN и EXPLAIN ANALYZE — чтение плана, seq scan, index scan, joins|Предыдущая]] · → [[DB 2.1.5 Уровни изоляции и аномалии — dirty read, non-repeatable, phantom, serialization|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> Основа надёжности данных; спрашивают, что именно гарантирует каждая буква и как это реализовано.

## ACID

| Свойство | Смысл | Как обеспечивается |
|---|---|---|
| **Atomicity** | всё или ничего | откат транзакции, MVCC |
| **Consistency** | переход из корректного состояния в корректное | ограничения, триггеры, правила приложения |
| **Isolation** | параллельные транзакции не мешают друг другу | MVCC, блокировки, уровни изоляции |
| **Durability** | после COMMIT данные не теряются | WAL + fsync, репликация |

## Управление

```sql
BEGIN;
UPDATE accounts SET balance = balance - 100 WHERE id = 1;
UPDATE accounts SET balance = balance + 100 WHERE id = 2;
COMMIT;        -- или ROLLBACK;

SAVEPOINT sp1; ... ROLLBACK TO sp1; RELEASE sp1;   -- частичный откат
```

- любой отдельный оператор вне `BEGIN` выполняется в неявной транзакции (autocommit);
- в PostgreSQL **DDL транзакционен**: `CREATE TABLE`, `ALTER TABLE` можно откатить;
- после ошибки транзакция переходит в состояние aborted, пока не будет `ROLLBACK` (или откат к savepoint);
- внутри транзакции `now()` возвращает время начала, `clock_timestamp()` — текущее.

## Долговечность и скорость

`synchronous_commit = on` (по умолчанию) ждёт `fsync` WAL. `off` ускоряет, но при сбое можно потерять последние транзакции (без повреждения БД). `remote_write`, `remote_apply` — для синхронной репликации.

## Транзакции и приложение

- держите транзакции **короткими**: длинные блокируют VACUUM, держат блокировки, раздувают таблицы;
- не делайте сетевые вызовы (HTTP, очередь) внутри транзакции;
- обрабатывайте **retry** при serialization failure (`40001`) и deadlock (`40P01`);
- идемпотентность операций при повторах;
- в .NET: `TransactionScope`, `DbContext.Database.BeginTransaction`, `SaveChanges` сам создаёт транзакцию;
- распределённые транзакции (между сервисами): **saga**, outbox, а не 2PC.

## Двухфазный коммит

`PREPARE TRANSACTION` / `COMMIT PREPARED` — для координаторов (XA). Требует осторожности: подвисшие prepared-транзакции блокируют VACUUM.

## Идентификатор транзакции

`xid` 32-битный, с циклическим счётчиком: **wraparound** предотвращается `VACUUM FREEZE`. Мониторинг `age(datfrozenxid)`.

## Вопросы с ответами

> [!question]- Что значит атомарность в PostgreSQL?
> Все изменения транзакции применяются целиком или не применяются вообще: при ROLLBACK или сбое версии строк, созданные транзакцией, остаются невидимыми.

> [!question]- Можно ли откатить ALTER TABLE?
> В PostgreSQL да: DDL транзакционен (кроме некоторых команд, например `CREATE INDEX CONCURRENTLY`, `VACUUM`).

> [!question]- Почему длинные транзакции вредны?
> Держат блокировки, не позволяют VACUUM удалять мёртвые версии строк (раздувание), могут вызывать конфликты и задержки репликации.
