---
type: topic
domain: db
stage: 2
section: "2.1"
order: 6
status: todo
level: middle
notion_id: 3ea33104867981149c6bd3ba02dc824b
tags: [domain/db, stage/2, level/middle, topic/postgresql, topic/mvcc, topic/vacuum, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# MVCC, VACUUM, bloat

↑ [[DB 2.1 PostgreSQL — индексы, транзакции, оптимизация|2.1 PostgreSQL: индексы, транзакции, оптимизация]] · ← [[DB 2.1.5 Уровни изоляции и аномалии — dirty read, non-repeatable, phantom, serialization|Предыдущая]] · → [[DB 2.1.7 Блокировки — row, table, advisory, SELECT FOR UPDATE, deadlocks|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> Ключ к пониманию «почему таблица раздулась», «что делает autovacuum» и почему читатели не блокируют писателей.

## MVCC

**Multi-Version Concurrency Control**: изменение строки создаёт **новую версию**, старая остаётся, пока она нужна другим транзакциям.

- `UPDATE` = пометить старую версию удалённой + вставить новую (в другое место);
- `DELETE` = пометить версию удалённой;
- у каждой версии `xmin` (создавшая транзакция) и `xmax` (удалившая);
- **снимок (snapshot)** определяет, какие версии видимы;
- читатели не блокируют писателей и наоборот.

```sql
SELECT xmin, xmax, ctid, * FROM orders LIMIT 3;
```

## Мёртвые версии и bloat

Старые версии (**dead tuples**), которые никому не нужны, занимают место и замедляют сканирование. Накопление = **bloat** (раздувание таблиц и индексов).

Причины: массовые `UPDATE`/`DELETE`, длинные транзакции, отставший VACUUM, висящие prepared-транзакции, реплики с `hot_standby_feedback`, слоты репликации.

## VACUUM

| Команда | Действие |
|---|---|
| `VACUUM` | помечает место мёртвых версий как свободное для повторного использования, обновляет карты FSM и VM; **не блокирует** чтение/запись; не возвращает место ОС (кроме хвоста) |
| `VACUUM FULL` | полностью перезаписывает таблицу, уменьшает файл; **эксклюзивная блокировка**, использовать редко |
| `ANALYZE` | обновляет статистику планировщика |
| `VACUUM FREEZE` | замораживание xid для защиты от wraparound |

Вместо `VACUUM FULL` на боевых системах: `pg_repack`, `pg_squeeze`, `REINDEX CONCURRENTLY`.

## Autovacuum

Автоматический процесс. Запускается, когда число мёртвых строк превышает порог:

`autovacuum_vacuum_threshold + autovacuum_vacuum_scale_factor × n_live_tup` (по умолчанию 50 + 20% таблицы).

Для больших таблиц 20% слишком много: настраивайте на таблицу.

```sql
ALTER TABLE events SET (autovacuum_vacuum_scale_factor = 0.02, autovacuum_analyze_scale_factor = 0.01);
```

Параметры: `autovacuum_max_workers`, `autovacuum_vacuum_cost_limit` (скорость), `autovacuum_naptime`.

## HOT-обновления

Если обновление не меняет индексированные столбцы и в странице есть место, новая версия остаётся на той же странице без обновления индексов (**Heap-Only Tuple**). Помогает `fillfactor` < 100 для часто обновляемых таблиц.

## Wraparound

`xid` 32-битный; без заморозки БД дойдёт до защитной остановки. Мониторинг `age(relfrozenxid)`, настройка `autovacuum_freeze_max_age`.

## Диагностика

```sql
SELECT relname, n_live_tup, n_dead_tup, last_autovacuum, last_autoanalyze
FROM pg_stat_user_tables ORDER BY n_dead_tup DESC LIMIT 10;

SELECT pid, xact_start, state, query FROM pg_stat_activity
WHERE state <> 'idle' ORDER BY xact_start;       -- длинные транзакции
```

Оценка bloat: расширение `pgstattuple`, запросы из `check_postgres`.

## Практика

- избегайте долгих транзакций и «idle in transaction» (`idle_in_transaction_session_timeout`);
- очередь/логи на таблице с интенсивными обновлениями: партиционирование и удаление партиций вместо `DELETE`;
- `fillfactor` 80–90 для «горячих» таблиц;
- мониторьте bloat, время последнего autovacuum, xid age.

## Вопросы с ответами

> [!question]- Почему UPDATE в PostgreSQL создаёт мёртвые строки?
> Из-за MVCC: обновление вставляет новую версию, а старая остаётся для транзакций со старыми снимками, пока VACUUM не освободит её.

> [!question]- Чем VACUUM отличается от VACUUM FULL?
> Обычный VACUUM освобождает место внутри файла для повторного использования без блокировок. FULL пересоздаёт таблицу, уменьшая файл, но блокирует её.

> [!question]- Почему таблица растёт, хотя autovacuum работает?
> Длинные транзакции или слоты репликации не дают удалить мёртвые версии; порог autovacuum слишком высок для большой таблицы; работа не успевает из-за лимитов стоимости.
