---
type: topic
domain: db
stage: 2
section: "2.1"
order: 10
status: todo
level: middle
notion_id: 3ea33104867981f5839fe292190f2cac
tags: [domain/db, stage/2, level/middle, topic/postgresql, topic/optimization, topic/pgbouncer, priority/must]
reviewed:
next_review:
priority: must
time: 4
---

# Оптимизация запросов и пул соединений (PgBouncer)

↑ [[DB 2.1 PostgreSQL — индексы, транзакции, оптимизация|2.1 PostgreSQL: индексы, транзакции, оптимизация]] · ← [[DB 2.1.9 Партиционирование таблиц|Предыдущая]] · → [[DB 2.1.11 Функции, триггеры, представления, materialized views|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~4 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> Практический навык: методичный поиск узкого места и пул соединений под нагрузкой.

## Процесс оптимизации

1. **Найти** дорогие запросы: `pg_stat_statements` (по `total_exec_time`, `mean_exec_time`, `calls`), логи (`log_min_duration_statement`), APM.
2. **Проанализировать** `EXPLAIN (ANALYZE, BUFFERS)`.
3. **Гипотеза**: индекс, переписывание запроса, статистика, схема.
4. **Изменить** и **измерить** повторно на реалистичных данных.
5. **Зафиксировать** (миграция индекса, тест, мониторинг).

```sql
SELECT calls, round(total_exec_time::numeric, 0) AS total_ms, round(mean_exec_time::numeric, 2) AS mean_ms,
       rows, left(query, 80) AS q
FROM pg_stat_statements ORDER BY total_exec_time DESC LIMIT 10;
```

## Типичные приёмы

| Проблема | Решение |
|---|---|
| Seq Scan по большой таблице | подходящий индекс (составной, частичный) |
| N+1 запросов из приложения | JOIN / `WHERE id = ANY($1)` / пакетная загрузка |
| Большой `OFFSET` | keyset-пагинация |
| `SELECT *` | нужные столбцы, covering-индекс |
| `count(*)` по большой таблице | оценка (`reltuples`), кэш счётчиков, приблизительные значения |
| `OR` по разным столбцам | `UNION ALL`, отдельные индексы |
| Функция в условии | функциональный индекс или переписать |
| Коррелированный подзапрос | JOIN / `LATERAL` / окно |
| Сортировка на диске | индекс под `ORDER BY`, `work_mem` |
| Медленная вставка | пакетная вставка, `COPY`, отключить лишние индексы на время загрузки |
| Тяжёлый отчёт | materialized view, реплика, ClickHouse |

## Настройки под нагрузку

`shared_buffers`, `work_mem` (осторожно), `effective_cache_size`, `random_page_cost` (для SSD ~1.1), `max_parallel_workers_per_gather`, `jit` (для OLTP часто выключают), `default_statistics_target`.

## Пул соединений

Проблема: процесс на соединение → сотни клиентов превращаются в перегрузку по памяти и переключению контекста. Оптимально держать серверных соединений порядка `cores × 2..4`.

**PgBouncer** — лёгкий пулер.

| Режим | Соединение возвращается в пул | Особенности |
|---|---|---|
| **session** | после закрытия клиентской сессии | совместим со всем, меньше выигрыш |
| **transaction** | после завершения транзакции | максимальное мультиплексирование |
| **statement** | после каждого оператора | нет многооператорных транзакций |

Ограничения transaction-режима: нельзя полагаться на состояние сессии (`SET`, `LISTEN/NOTIFY`, advisory-lock на сессию, временные таблицы, prepared statements — есть поддержка в новых версиях `max_prepared_statements`).

```ini
[databases]
app = host=pg1 port=5432 dbname=app

[pgbouncer]
pool_mode = transaction
default_pool_size = 20
max_client_conn = 2000
server_idle_timeout = 600
auth_type = scram-sha-256
```

Также: **Pgpool-II** (балансировка, кэш), **Odyssey**, Supavisor. Пул на стороне приложения (Npgsql, HikariCP) тоже нужен: он уменьшает накладные на установку соединений; но при множестве экземпляров сервиса суммарное число соединений требует внешнего пулера.

## В .NET

Npgsql: строка подключения с `Maximum Pool Size`, `Minimum Pool Size`, `Connection Idle Lifetime`; при PgBouncer transaction mode — `No Reset On Close=true` и осторожность с prepared statements (`Max Auto Prepare`).

## Диагностика соединений

```sql
SELECT state, count(*) FROM pg_stat_activity GROUP BY 1;
SHOW max_connections;
```

Много `idle in transaction` — утечка или долгие транзакции в приложении.

## Вопросы с ответами

> [!question]- С чего начать оптимизацию медленной системы?
> Найти реально дорогие запросы по `pg_stat_statements` (суммарное время, частота), затем `EXPLAIN ANALYZE`, а не оптимизировать наугад.

> [!question]- Зачем PgBouncer при наличии пула в приложении?
> Пул приложения ограничивает соединения одного экземпляра. При десятках экземпляров, серверлесс и микросервисах суммарное число соединений велико; PgBouncer держит малое число серверных соединений.

> [!question]- Какие ограничения у transaction pooling?
> Нельзя использовать состояние сессии: session-level `SET`, advisory-locks на сессию, `LISTEN`, временные таблицы; prepared statements требуют поддержки в версии пулера.
