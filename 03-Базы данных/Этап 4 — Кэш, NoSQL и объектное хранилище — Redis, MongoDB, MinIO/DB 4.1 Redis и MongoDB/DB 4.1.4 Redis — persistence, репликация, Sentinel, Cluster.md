---
type: topic
domain: db
stage: 4
section: "4.1"
order: 4
status: todo
level: middle
notion_id: 3ea3310486798180a206e947414bd7f7
tags: [domain/db, stage/4, level/middle, topic/redis, topic/persistence, topic/replication, topic/sentinel, topic/cluster, priority/should]
reviewed:
next_review:
priority: should
time: 3
---

# Redis: persistence, репликация, Sentinel, Cluster

↑ [[DB 4.1 Redis и MongoDB|4.1 Redis и MongoDB]] · ← [[DB 4.1.3 Redis — pub-sub, streams, распределённые блокировки, rate limiting|Предыдущая]] · → [[DB 4.1.5 MongoDB — документная модель, индексы, агрегации (обзорно)|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> Redis хранит данные в памяти, значит, нужно понимать сохранность, отказоустойчивость и масштабирование.

## Персистентность

| Способ | Как работает | Плюсы | Минусы |
|---|---|---|---|
| **RDB** | периодические снимки (`save 900 1`, `BGSAVE`) через `fork` | компактно, быстрый старт, удобные бэкапы | потеря данных с последнего снимка |
| **AOF** | журнал всех записей (`appendonly yes`), fsync: `always` / `everysec` / `no` | потери до 1 секунды (`everysec`) | больше размер, медленнее восстановление |
| **RDB + AOF** | комбинация (Multi-Part AOF в 7.x) | баланс | |
| **Нет** | чистый кэш | максимум скорости | всё теряется при перезапуске |

- `fork` при снапшоте копирует страницы памяти (copy-on-write): нужен запас памяти;
- для кэша — персистентность часто отключают, для хранилища состояния — AOF `everysec` + RDB;
- Redis — **не замена основной БД** без осознанных требований к надёжности.

## Репликация

Асинхронная master → replica (`REPLICAOF host port`, `replicaof` в конфиге).

- реплики нужны для отказоустойчивости и чтения (может быть устаревшим);
- частичная ресинхронизация (`PSYNC`), backlog репликации;
- `min-replicas-to-write`, `WAIT` — ограничение риска потери записи;
- возможна потеря последних записей при падении мастера (асинхронность).

## Sentinel

Мониторит мастера и реплики, выполняет **автоматический failover**.

```text
1 master + 2 replicas + 3 sentinel (кворум 2)
```

Функции: мониторинг, уведомления, выбор новой реплики, конфигурация для клиентов. Клиент спрашивает у Sentinel адрес текущего мастера (`ServiceName` в StackExchange.Redis). Не масштабирует запись: данные по-прежнему на одном мастере.

Проблемы: split-brain при сетевых разделениях (`min-replicas-to-write`, кворум), лаг репликации.

## Redis Cluster

Горизонтальное **шардирование** и отказоустойчивость.

- пространство из **16384 хэш-слотов**; ключ → слот: `CRC16(key) mod 16384`; слоты распределены между мастерами;
- у каждого мастера реплики; автоматический failover;
- клиент узнаёт топологию, ответы `MOVED` / `ASK` при перенаправлении;
- **multi-key операции** (`MGET`, транзакции, Lua) возможны только для ключей в одном слоте: используйте **hash tags** `{user:42}:cart`, `{user:42}:profile`;
- нет нескольких БД (только `db 0`);
- минимум 3 мастера.

## Сравнение

| Топология | Масштабирует | Автоfailover | Когда |
|---|---|---|---|
| Один узел | нет | нет | dev, кэш |
| Master + replicas | чтение | нет (вручную) | простая |
| Sentinel | чтение | да | HA при данных до объёма одного узла |
| Cluster | запись и объём | да | большие данные и нагрузка |

Управляемые: AWS ElastiCache, Azure Cache, Google Memorystore, Redis Cloud. Совместимые: **Valkey** (форк под Linux Foundation), KeyDB, Dragonfly.

## Эксплуатация

- `maxmemory` и политика вытеснения обязательны;
- отключить Transparent Huge Pages, `vm.overcommit_memory = 1`;
- мониторинг: `INFO` (memory, persistence, replication, stats), `SLOWLOG`, `LATENCY`, `MEMORY USAGE`, big keys (`--bigkeys`);
- защита: `requirepass`/ACL, TLS, не открывать порт наружу, отключать опасные команды (`FLUSHALL`, `CONFIG`);
- бэкапы: RDB на внешнее хранилище, проверка восстановления.

## Вопросы с ответами

> [!question]- В чём разница между RDB и AOF?
> RDB — периодические снимки (компактно, возможна потеря последних изменений). AOF — журнал операций (потеря до секунды при `everysec`, больше размер).

> [!question]- Что делает Sentinel и чем он отличается от Cluster?
> Sentinel обеспечивает автоматический failover для схемы «один мастер + реплики», но не масштабирует запись. Cluster шардирует данные по слотам и масштабирует объём и запись.

> [!question]- Зачем hash tags в Redis Cluster?
> Чтобы ключи, участвующие в одной операции, попали в один слот: `{user:42}:cart` и `{user:42}:profile`.
