---
type: topic
domain: backend
stage: 8
section: "8.3"
order: 7
status: todo
level: senior
notion_id: 3ea331048679819b81a4e0efefe0785e
tags: [domain/backend, stage/8, level/senior, topic/distributed-systems, topic/locks, topic/consensus, priority/should]
reviewed:
next_review:
priority: should
time: 3
---

# Распределённые блокировки, лидерство, часы

↑ [[BE 8.3 Микросервисы и распределённые системы|8.3 Микросервисы и распределённые системы]] · ← [[BE 8.3.6 Eventual consistency, CAP и PACELC|Предыдущая]] · → [[BE 8.3.8 Общий код между сервисами — shared kernel, NuGet-пакеты, базовые образы|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: senior</span></div>
<!-- meta:end -->























> [!info] Зачем это на собесе
> «Как выполнить задачу только в одном инстансе» — практический вопрос, за которым скрыты тонкости распределённых систем.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

**Распределённая блокировка** — взаимное исключение между процессами на разных узлах.

| Способ | Особенности |
|---|---|
| PostgreSQL advisory lock (`pg_advisory_lock`) | просто, если БД уже есть, освобождается при потере соединения |
| Redis (`SET key val NX PX 30000`) | быстро; риски при отказе мастера; Redlock спорный |
| etcd / ZooKeeper / Consul | лидерство, сессии, строгая согласованность (консенсус Raft/Zab) |
| Kubernetes Lease | leader election для контроллеров |
| Строка в БД с `SELECT ... FOR UPDATE SKIP LOCKED` | очереди задач, «захват» работы |

```csharp
// Redis: захват с TTL и уникальным токеном
var token = Guid.NewGuid().ToString();
if (await db.StringSetAsync("lock:report", token, TimeSpan.FromSeconds(30), When.NotExists))
{
    try { await RunJobAsync(ct); }
    finally { await db.ScriptEvaluateAsync("if redis.call('get',KEYS[1])==ARGV[1] then return redis.call('del',KEYS[1]) else return 0 end", [ "lock:report" ], [ token ]); }
}
```

**Fencing token** — монотонно растущий номер вместе с блокировкой; ресурс отклоняет запросы со старым токеном. Без него «зависший» процесс после истечения TTL может испортить данные.

**Leader election** — выбор одного лидера среди реплик (для фоновых задач, планировщика). Консенсус: Raft, Paxos.

**Часы**: физические часы расходятся (NTP, drift), скачут; на них нельзя строить порядок событий и истечение блокировок. Альтернативы: логические часы (Lamport), векторные часы, монотонные счётчики, TrueTime (Spanner).

## Нюансы и подводные камни

- Пауза процесса (GC, swap) дольше TTL блокировки: два «владельца» одновременно.
- Блокировка не заменяет идемпотентность — делайте операции безопасными к повтору.
- Избегайте блокировок: очередь с единственным потребителем на ключ, партиционирование по ключу (Kafka).
- Redis-лок на одном узле теряется при перезапуске и failover.
- Сложные лидерские схемы проще делегировать инфраструктуре (Kubernetes, planner).

## Практика

1. Реализуйте advisory lock в PostgreSQL для периодической задачи.
2. Опишите сценарий с паузой GC и решите fencing token.
3. Замените блокировку на партиционирование сообщений по ключу.

## Вопросы с ответами

> [!question]- Почему распределённые блокировки сложны?
> Возможны сетевые задержки, паузы процессов и расхождения часов: владелец может считать, что блокировка у него, когда она уже истекла.

> [!question]- Что такое fencing token?
> Растущий номер, выдаваемый с блокировкой; хранилище отвергает операции с устаревшим номером.

## Связанные темы

- [[N:3ea331048679814b8cded192367036e3]]
- [[N:3ea3310486798108a3caf17276ee36aa]]
