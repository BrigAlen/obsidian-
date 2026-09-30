---
type: topic
domain: db
stage: 7
order: 4
notion_id: 09d910aa5ad141faae1979cdbf6c5df0
status: todo
level: middle+
tags: [domain/db, stage/7, level/middle+, priority/nice]
reviewed: 
next_review: 
priority: nice
time: 7
---

# Мониторинг PostgreSQL: pg_stat_activity, pg_stat_statements, логи и алерты

↑ [[DB Этап 7 · Эксплуатация и безопасность БД|Этап 7 · Эксплуатация и безопасность БД]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge nice">По желанию</span><span class="chip">~7 мин чтения</span><span class="chip">Уровень: middle+</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> Без мониторинга вы узнаёте о проблемах от пользователей. Спрашивают, какие метрики смотреть и как искать медленные запросы и блокировки.

## Источники данных

| Источник | Что даёт |
|---|---|
| **Статистические представления** `pg_stat_*` | состояние в реальном времени |
| **pg_stat_statements** | агрегаты по запросам (время, вызовы, блоки) |
| **Логи PostgreSQL** | медленные запросы, ошибки, блокировки, автоочистка |
| **Экспортёры** (`postgres_exporter`, `pgwatch`, `pgMonitor`) | метрики в Prometheus |
| **Метрики ОС/ресурсов** (node_exporter, cAdvisor) | CPU, память, диски, сеть |
| **Трассировка/APM** | запросы с точки зрения приложения (OpenTelemetry) |

## pg_stat_activity: что происходит сейчас

```sql
-- активные запросы, самые долгие сверху
SELECT pid, usename, application_name, state, wait_event_type, wait_event,
       now() - query_start AS duration, left(query, 100) AS query
FROM pg_stat_activity
WHERE state <> 'idle' AND pid <> pg_backend_pid()
ORDER BY duration DESC;

-- «idle in transaction» — утечка транзакций, блокирует VACUUM
SELECT pid, now() - xact_start AS xact_age, query FROM pg_stat_activity
WHERE state = 'idle in transaction' ORDER BY xact_age DESC;

-- кто кого блокирует
SELECT a.pid AS blocked, pg_blocking_pids(a.pid) AS blocked_by, a.query
FROM pg_stat_activity a WHERE cardinality(pg_blocking_pids(a.pid)) > 0;

-- соединения по состояниям
SELECT state, count(*) FROM pg_stat_activity GROUP BY state;

SELECT pg_cancel_backend(pid);      -- отменить запрос
SELECT pg_terminate_backend(pid);   -- закрыть соединение
```

`wait_event_type`: `Lock`, `IO`, `LWLock`, `Client` — где ожидание.

## pg_stat_statements: какие запросы дороги

Расширение (`shared_preload_libraries = 'pg_stat_statements'`, `CREATE EXTENSION`).

```sql
SELECT queryid, calls,
       round(total_exec_time::numeric, 0)   AS total_ms,
       round(mean_exec_time::numeric, 2)    AS mean_ms,
       round(stddev_exec_time::numeric, 2)  AS stddev_ms,
       rows, shared_blks_hit, shared_blks_read,
       round(100.0 * shared_blks_hit / nullif(shared_blks_hit + shared_blks_read, 0), 1) AS hit_pct,
       left(query, 80) AS query
FROM pg_stat_statements
ORDER BY total_exec_time DESC LIMIT 15;

SELECT pg_stat_statements_reset();
```

Сортировки: по `total_exec_time` (общая нагрузка), `mean_exec_time` (медленные), `calls` (частые), `shared_blks_read` (диск), `temp_blks_written` (сортировки на диск). Запросы нормализованы (параметры `$1`). Связь с планами — `auto_explain`.

## Ключевые метрики

| Группа | Метрики | Признак проблем |
|---|---|---|
| **Соединения** | `numbackends` / `max_connections`, idle in transaction | > 80% лимита, рост idle in tx |
| **Запросы** | время (p95, p99), TPS, медленные | рост задержек |
| **Кэш** | hit ratio `blks_hit / (blks_hit + blks_read)` | < 99% для OLTP |
| **Блокировки** | ожидающие, deadlocks (`pg_stat_database.deadlocks`) | рост |
| **Транзакции** | `xact_commit`, `xact_rollback`, долгие транзакции | доля rollback, возраст xact |
| **Репликация** | `replay_lag`, `pg_stat_replication`, слоты | лаг растёт, слот без потребителя |
| **VACUUM** | `n_dead_tup`, `last_autovacuum`, age(`relfrozenxid`) | раздувание, wraparound |
| **Объём** | размеры БД/таблиц/индексов, темп роста | рост, bloat |
| **Checkpoint/WAL** | `checkpoints_req` против `timed`, объём WAL | слишком частые |
| **Временные файлы** | `temp_files`, `temp_bytes` | нехватка `work_mem` |
| **Ресурсы** | CPU, iowait, latency диска, память, swap | насыщение |
| **Ошибки** | count ERROR/FATAL в логах | всплески |

```sql
SELECT relname, n_live_tup, n_dead_tup, last_autovacuum FROM pg_stat_user_tables ORDER BY n_dead_tup DESC LIMIT 10;
SELECT datname, round(100.0 * blks_hit / nullif(blks_hit + blks_read, 0), 2) AS hit_pct, deadlocks, temp_files, temp_bytes FROM pg_stat_database;
SELECT relname, seq_scan, idx_scan FROM pg_stat_user_tables WHERE seq_scan > 1000 ORDER BY seq_tup_read DESC LIMIT 10;
SELECT schemaname, relname, indexrelname, idx_scan FROM pg_stat_user_indexes WHERE idx_scan = 0;   -- неиспользуемые индексы
SELECT slot_name, active, pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(), restart_lsn)) AS retained FROM pg_replication_slots;
SELECT pg_size_pretty(pg_database_size(current_database()));
```

## Логи

```conf
log_min_duration_statement = 500          # логировать запросы > 500 мс
log_lock_waits = on                       # ожидание блокировки > deadlock_timeout
log_temp_files = 0                        # любые временные файлы
log_autovacuum_min_duration = 1000
log_checkpoints = on
log_connections = on
log_disconnections = on
log_line_prefix = '%m [%p] %q%u@%d %a '
log_error_verbosity = default
log_statement = 'ddl'
```

Анализ: **pgBadger** (отчёты), отправка в Loki/ELK/ClickHouse; `auto_explain` (планы медленных: `auto_explain.log_min_duration = '1s'`, `log_analyze = on`).

## Стек мониторинга

```text
postgres_exporter ──▶ Prometheus ──▶ Grafana (дашборды, алерты) ──▶ Alertmanager ──▶ Telegram/Slack/PagerDuty
node_exporter ─────▶ Prometheus
логи ─▶ Loki/ELK
```

Готовые дашборды Grafana для PostgreSQL (ID 9628, 455), коммерческие: pganalyze, Datadog, Percona PMM.

## Алерты (пример)

| Алерт | Условие |
|---|---|
| Недоступность | `pg_up == 0` |
| Много соединений | `> 80% max_connections` 5 мин |
| Лаг репликации | `replay_lag > 30 с` |
| Долгая транзакция | `xact_age > 10 мин` |
| Слот копит WAL | `retained > X ГБ` |
| Диск | свободно `< 15%`, прогноз заполнения < 24 ч |
| Deadlocks | рост |
| Wraparound | `age(datfrozenxid) > 1 млрд` |
| Autovacuum | нет запуска N часов, `n_dead_tup` высок |
| Ошибки бэкапа/архивации WAL | `pg_stat_archiver.failed_count` растёт |
| Кэш | `hit_pct < 95%` |

Принципы алертинга: **симптомы** (влияние на пользователя), а не только причины; уровни серьёзности; runbook в каждом алерте; минимум шума; SLO и burn rate.

## Диагностика «всё тормозит»

1. `pg_stat_activity`: сколько активных, чего ждут, долгие запросы, блокировки.
2. Ресурсы ОС: CPU, iowait, память/swap, диск.
3. `pg_stat_statements`: что изменилось, топ по времени.
4. Изменения: деплой, миграция, новый отчёт, рост данных.
5. `EXPLAIN (ANALYZE, BUFFERS)` ключевых запросов.
6. Autovacuum и bloat, статистика (`ANALYZE`).
7. Репликация, checkpoint, WAL.

## Вопросы с ответами

> [!question]- Как найти самые «дорогие» запросы?
> `pg_stat_statements`, сортировка по `total_exec_time` (влияние на систему), по `mean_exec_time` (медленные), по `calls`, `shared_blks_read` (диск) и `temp_blks_written`.

> [!question]- Что опасного в idle in transaction?
> Транзакция держит блокировки и снапшот, мешает VACUUM удалять мёртвые строки, приводит к раздуванию и блокировкам. Ограничивают `idle_in_transaction_session_timeout`.

> [!question]- Какие метрики PostgreSQL вы ставите на алерты?
> Доступность, долю занятых соединений, лаг репликации, долгие транзакции, свободное место и прогноз, рост WAL из-за слотов, deadlocks, возраст xid, ошибки архивации WAL и бэкапов, cache hit ratio.
