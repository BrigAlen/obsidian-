---
type: topic
domain: db
stage: 7
order: 3
notion_id: 0d18015e1e4741f19f933b023e07f4fa
status: todo
level: middle+
tags: [domain/db, stage/7, level/middle+, priority/nice]
reviewed: 
next_review: 
priority: nice
time: 7
---

# High Availability и failover: Patroni, etcd, read replicas

↑ [[DB Этап 7 · Эксплуатация и безопасность БД|Этап 7 · Эксплуатация и безопасность БД]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge nice">По желанию</span><span class="chip">~7 мин чтения</span><span class="chip">Уровень: middle+</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> Отказоустойчивость PostgreSQL — частая тема senior/DevOps-собеседований: как работает автоматический failover и как избежать split-brain.

## Цели

- **Доступность** (SLA 99.9–99.99%), минимальное **RTO** и **RPO ≈ 0** для критичных данных;
- автоматический failover без ручных действий;
- масштабирование чтения репликами.

Встроенной автоматической кластеризации в PostgreSQL нет: есть репликация (streaming), а управление переключением выполняют внешние инструменты.

## Инструменты HA для PostgreSQL

| Инструмент | Идея |
|---|---|
| **Patroni** | демон на каждом узле, хранит лидерство в DCS (etcd/Consul/ZooKeeper/Kubernetes API) |
| **repmgr** | управление репликацией и failover (с witness) |
| **pg_auto_failover** | монитор + узлы |
| **Stolon**, Crunchy PGO, CloudNativePG, Zalando Postgres Operator | операторы Kubernetes (многие на Patroni) |
| Управляемые: RDS/Aurora, Cloud SQL, Azure Flexible Server | HA встроена |

## Patroni

Архитектура:

```text
            ┌───────── etcd кластер (3 узла) — DCS, лидерский ключ с TTL ─────────┐
            │                                                                      │
   Patroni + PG (leader)        Patroni + PG (replica)        Patroni + PG (replica)
            │                                                                      │
       HAProxy / vip-manager / PgBouncer  ← клиенты видят «текущего лидера»
```

- Patroni на каждом узле управляет процессом PostgreSQL и регулярно обновляет **лидерский ключ** в DCS с TTL;
- при исчезновении лидера ключ истекает, реплики **голосуют**: побеждает наиболее актуальная реплика (по LSN, с ограничением `maximum_lag_on_failover`), её `promote`;
- старый лидер при возврате **демотируется** и подстраивается под нового (`pg_rewind`);
- конфигурация кластера (`postgresql.parameters`, `synchronous_mode`) хранится в DCS и применяется ко всем узлам;
- REST API (порт 8008): `/primary`, `/replica`, `/health`: используется HAProxy для маршрутизации.

```yaml
# patroni.yml (фрагмент)
scope: pg-main
name: pg1
etcd3: { hosts: etcd1:2379,etcd2:2379,etcd3:2379 }
restapi: { listen: 0.0.0.0:8008, connect_address: pg1:8008 }
bootstrap:
  dcs:
    ttl: 30
    loop_wait: 10
    retry_timeout: 10
    maximum_lag_on_failover: 1048576
    synchronous_mode: true
    postgresql:
      use_pg_rewind: true
      parameters: { wal_level: replica, hot_standby: "on", max_wal_senders: 10 }
postgresql:
  listen: 0.0.0.0:5432
  data_dir: /var/lib/postgresql/data
  authentication:
    replication: { username: replicator, password: "..." }
```

`patronictl list`, `patronictl switchover`, `patronictl failover`, `patronictl reinit`.

Маршрутизация:

```text
# haproxy.cfg
listen postgres_primary
  bind *:5000
  option httpchk GET /primary
  http-check expect status 200
  default-server inter 3s fall 3 rise 2 on-marked-down shutdown-sessions
  server pg1 pg1:5432 check port 8008
  server pg2 pg2:5432 check port 8008
  server pg3 pg3:5432 check port 8008
listen postgres_replicas
  bind *:5001
  option httpchk GET /replica
  ...
```

Порт 5000 — запись (лидер), 5001 — чтение (реплики). Альтернатива: VIP (`vip-manager`), DNS, multi-host строки подключения Npgsql (`Host=pg1,pg2,pg3;Target Session Attributes=primary`).

## etcd (DCS)

Распределённое хранилище ключ–значение на **Raft**: нужен **кворум** (majority) узлов. Кластер из **3 (или 5)** узлов; потеря большинства = кластер только читает, Patroni **останавливает запись на лидере** (демотирует), чтобы избежать split-brain.

Требования: отдельные быстрые диски (низкая fsync-задержка), стабильная сеть, мониторинг (`etcdctl endpoint health`), бэкапы, не размещать на нагруженных узлах БД без ресурсов.

## Синхронная репликация и потери данных

- `synchronous_mode: true` — Patroni управляет `synchronous_standby_names`: гарантирует, что при failover промотируется реплика с полным набором подтверждённых транзакций (RPO = 0);
- если синхронной реплики нет, запись блокируется (строгий режим) или разрешается с потерей гарантии (`synchronous_mode_strict` управляет).

## Split-brain и fencing

Два узла считают себя лидерами и принимают запись, данные расходятся. Защита:

- **DCS с кворумом**: лидерство только с действующим ключом;
- **watchdog** (softdog/аппаратный): перезагрузка узла, если Patroni завис;
- **fencing**: изоляция старого лидера (остановка PostgreSQL, отзыв VIP, STONITH);
- синхронная репликация;
- в приложении: соединения только через прокси, обрывать сессии при смене лидера (`on-marked-down shutdown-sessions`).

## Поведение приложения при failover

1. Разрыв соединений (30–60 секунд неработоспособности зависят от `ttl`, `loop_wait`).
2. Пул соединений (PgBouncer/Npgsql) должен **отбрасывать** мёртвые соединения и переподключаться.
3. Повторы **идемпотентных** операций с backoff; транзакции в процессе откатываются.
4. Таймауты подключения и команд короткие.
5. Учения: регулярно **switchover** и имитация сбоев (chaos).

## Read replicas

- реплики для чтения, отчётов, бэкапов; лаг мониторится; routing по приоритету (`Target Session Attributes=prefer-standby`);
- **каскадная репликация** и реплики в другом регионе;
- `hot_standby_feedback`, `max_standby_streaming_delay` настраиваются компромиссом между конфликтами и раздуванием;
- тег `nofailover` / `noloadbalance` для специальных реплик (аналитика, бэкап).

## Топология

| Вариант | Узлы | Комментарий |
|---|---|---|
| Минимум | 2 PG + witness/etcd | нужен третий голос для кворума |
| Стандарт | 3 PG (1 лидер + 2 реплики) + 3 etcd (можно на тех же узлах при малом масштабе) | типовой кластер |
| Multi-AZ/DC | узлы в 3 зонах | устойчивость к отказу зоны; учёт задержки для синхронной репликации |
| DR-регион | standby cluster | асинхронно, ручное/полуавтоматическое переключение |

## Мониторинг

`patroni_*` метрики (Prometheus), `pg_stat_replication`, лаг, состояние etcd, алерты: нет лидера, два лидера, лаг > N, слот без потребителя, `timeline` изменился.

## Kubernetes

Операторы: **CloudNativePG** (без Patroni, свой менеджер), Zalando, Crunchy. StatefulSet + PVC, PodDisruptionBudget, anti-affinity по зонам, сервисы `-rw`/`-ro`, бэкапы в S3 (Barman Cloud/pgBackRest), rolling-обновления с switchover.

## Вопросы с ответами

> [!question]- Как Patroni выбирает нового лидера?
> Лидерство держится ключом в DCS с TTL. При его истечении реплики соревнуются за ключ; допускаются только реплики с допустимым отставанием, выигрывает самая актуальная. Остальные перенастраиваются на нового лидера.

> [!question]- Зачем нужен кворум etcd и что будет без него?
> Consensus (Raft) исключает два лидера. Без кворума DCS недоступен, и Patroni демотирует лидера в режим только чтения, чтобы избежать split-brain: лучше потерять доступность записи, чем получить расхождение данных.

> [!question]- Как приложение должно переживать failover?
> Подключаться через прокси/multi-host строку, отбрасывать мёртвые соединения, повторять идемпотентные операции с backoff и короткими таймаутами; избегать длинных транзакций.
