---
type: topic
domain: db
stage: 3
section: "3.1"
order: 11
status: todo
level: middle
notion_id: 3ea33104867981c3a827dfba080e13dc
tags: [domain/db, stage/3, level/middle, topic/clickhouse, topic/replication, topic/sharding, topic/keeper, priority/should]
reviewed:
next_review:
priority: should
time: 4
---

# Репликация и шардирование: ReplicatedMergeTree, Distributed, Keeper

↑ [[DB 3.1 ClickHouse|3.1 ClickHouse]] · ← [[DB 3.1.10 Интеграции — Kafka engine, телеметрия OTel в ClickHouse, Grafana|Предыдущая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~4 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> Кластерная топология ClickHouse: как обеспечить отказоустойчивость и горизонтальное масштабирование.

## Термины

- **Реплика** — копия данных шарда на другом сервере (отказоустойчивость, распределение чтения);
- **Шард** — часть данных (горизонтальное разделение для объёма и скорости);
- **Кластер** — набор шардов, у каждого одна или несколько реплик.

## Репликация: ReplicatedMergeTree

```sql
CREATE TABLE events ON CLUSTER main
(
    ts DateTime, tenant_id UInt32, event_type LowCardinality(String), value Float64
)
ENGINE = ReplicatedMergeTree('/clickhouse/tables/{shard}/events', '{replica}')
PARTITION BY toYYYYMM(ts)
ORDER BY (tenant_id, ts);
```

- координация через **ClickHouse Keeper** (совместимая с ZooKeeper замена на C++, протокол Raft) или ZooKeeper;
- в Keeper хранятся **метаданные** (список партов, очереди слияний и мутаций), сами данные передаются между репликами напрямую;
- репликация **асинхронная** и **мультимастер**: вставка в любую реплику, остальные подтягивают парты;
- `insert_quorum` — подтверждение записи на N реплик (строже, медленнее); `select_sequential_consistency` для чтения без отставания;
- реплики самовосстанавливаются: отстающая догоняет очередь;
- Keeper: кластер из **3 (или 5)** узлов, отдельные диски, низкая задержка сети; его падение — таблицы переходят в read-only.

## Шардирование и Distributed

```sql
CREATE TABLE events_dist ON CLUSTER main AS events
ENGINE = Distributed(main, default, events, cityHash64(tenant_id));
```

- **Distributed** — «виртуальная» таблица без данных; маршрутизирует запросы на шарды и объединяет результат; при вставке распределяет строки по **ключу шардирования** (`sharding_key`);
- ключ шардирования: равномерное распределение и локальность (например, по `tenant_id` — все данные клиента на одном шарде, ускоряет JOIN и группировки по нему);
- запись: в Distributed (асинхронно доставляется на шарды, буфер на диске) либо **напрямую в локальные таблицы** шардов (быстрее, надёжнее, но клиент сам выбирает шард);
- `internal_replication = true` для реплицируемых таблиц: запись в одну реплику, остальные копируют через репликацию;
- чтение: `prefer_localhost_replica`, `load_balancing` (random, nearest_hostname, in_order, round_robin).

## Распределённые запросы

Запрос разбивается на шарды, результаты объединяются на инициаторе. `GLOBAL IN/JOIN` — рассылка результата подзапроса; `distributed_product_mode`. Иногда предагрегация на шардах эффективнее (`GROUP BY` с `distributed_group_by_no_merge`).

## Конфигурация кластера

```xml
<remote_servers>
  <main>
    <shard>
      <internal_replication>true</internal_replication>
      <replica><host>ch-1a</host><port>9000</port></replica>
      <replica><host>ch-1b</host><port>9000</port></replica>
    </shard>
    <shard>
      <internal_replication>true</internal_replication>
      <replica><host>ch-2a</host><port>9000</port></replica>
      <replica><host>ch-2b</host><port>9000</port></replica>
    </shard>
  </main>
</remote_servers>
```

Макросы `{shard}`, `{replica}`, `{cluster}` в конфиге каждого узла. `ON CLUSTER` выполняет DDL на всех узлах (через очередь в Keeper).

## Типичная топология

- малые нагрузки: 1 шард × 2–3 реплики (отказоустойчивость);
- большие объёмы: N шардов × 2 реплики + 3 узла Keeper;
- облако ClickHouse Cloud: SharedMergeTree, хранилище в объектном хранилище, вычисления отделены.

## Эксплуатация

- **пересчёт шардов** (resharding) сложен: планируйте запас, используйте ключ с возможностью роста;
- мониторинг: `system.replicas` (`is_readonly`, `absolute_delay`, `queue_size`), `system.replication_queue`, `system.distribution_queue`;
- бэкапы: `BACKUP TABLE ... TO S3`, `clickhouse-backup`, снапшоты (`FREEZE`);
- обновления по одной реплике (rolling), проверка совместимости версий;
- защита от «расхождения» (`system.mutations`, `check table`).

## Вопросы с ответами

> [!question]- Чем шардирование отличается от репликации?
> Репликация создаёт копии одних и тех же данных для надёжности и чтения; шардирование делит данные между серверами для масштабирования объёма и производительности.

> [!question]- Что хранится в Keeper?
> Метаданные репликации: список партов, очереди операций (вставки, слияния, мутации), блоки дедупликации. Не сами данные.

> [!question]- Как выбрать ключ шардирования?
> Он должен равномерно распределять нагрузку и, по возможности, соответствовать основным запросам (например, `tenant_id`), чтобы запросы и JOIN оставались локальными в пределах шарда.
