---
type: topic
domain: db
stage: 4
section: "4.1"
order: 3
status: todo
level: middle
notion_id: 3ea33104867981548077f5f5fab9f75c
tags: [domain/db, stage/4, level/middle, topic/redis, topic/pubsub, topic/streams, topic/locks, topic/rate-limit, priority/should]
reviewed:
next_review:
priority: should
time: 4
---

# Redis: pub/sub, streams, распределённые блокировки, rate limiting

↑ [[DB 4.1 Redis и MongoDB|4.1 Redis и MongoDB]] · ← [[DB 4.1.2 Redis как кэш — TTL, eviction, стратегии cache-aside, write-through|Предыдущая]] · → [[DB 4.1.4 Redis — persistence, репликация, Sentinel, Cluster|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~4 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> Redis часто используют как «клей» между сервисами: уведомления, очереди, блокировки, ограничение частоты.

## Pub/Sub

```text
SUBSCRIBE news        # подписчик
PUBLISH news "hello"  # публикация
PSUBSCRIBE events:*   # по шаблону
```

- «выстрелил и забыл»: **нет хранения и подтверждений**; неподключённый подписчик пропускает сообщения;
- подходит для: инвалидации кэша между инстансами, уведомлений в реальном времени, SignalR-backplane;
- не подходит для надёжной доставки.

## Streams

Лог событий с хранением, группами потребителей и подтверждениями (аналог упрощённого Kafka).

```text
XADD orders * userId 42 total 1500 status new          # добавить событие
XGROUP CREATE orders workers $ MKSTREAM                # группа потребителей
XREADGROUP GROUP workers w1 COUNT 10 BLOCK 5000 STREAMS orders >
XACK orders workers 1690000000000-0                    # подтвердить обработку
XPENDING orders workers                                # необработанные
XAUTOCLAIM orders workers w2 60000 0                   # забрать зависшие
XTRIM orders MAXLEN ~ 100000                           # ограничение размера
```

- сообщения сохраняются, доставляются каждой **группе** один раз (между консьюмерами группы распределяются);
- подтверждение `XACK`, повторная обработка зависших (PEL);
- гарантия «как минимум один раз»: обработчики должны быть идемпотентными;
- сравнение с Kafka: проще и быстрее для небольших нагрузок, но данные в памяти, меньше экосистема и партиционирование; RabbitMQ — богаче маршрутизация.

## Списки как очереди

`LPUSH` + `BRPOP` — простая очередь; сообщение теряется, если обработчик упал после получения (надёжный вариант: `LMOVE`/`BLMOVE` в список «в работе»). В .NET: Hangfire, Streams или брокер.

## Распределённая блокировка

Задача: только один процесс выполняет критическую секцию (cron, миграция, ресурс).

```text
SET lock:report:2026-09-30 <уникальный_токен> NX PX 30000     # взять: только если нет, с TTL 30 с
# освободить только свой токен (атомарно, Lua):
if redis.call("get", KEYS[1]) == ARGV[1] then return redis.call("del", KEYS[1]) else return 0 end
```

Правила:

- всегда **TTL**, иначе при падении блокировка зависнет;
- освобождать **только свою** блокировку (сверка токена);
- если работа дольше TTL — продлевать (watchdog);
- **fencing token**: критичные операции проверяют монотонный токен на стороне ресурса, так как блокировка может истечь во время паузы процесса (GC, сеть);
- **Redlock** (несколько независимых узлов) — спорен в критичных случаях (см. дискуссию Kleppmann / Antirez); для корректности лучше использовать ограничения БД, идемпотентность, блокировки в БД (`advisory lock`);
- в .NET: `RedLock.net`, `DistributedLock`, `LockTake`/`LockRelease` в StackExchange.Redis.

## Rate limiting

**Фиксированное окно**

```text
INCR rl:user:42:2026-09-30T12:00        # + EXPIRE 60 при первом инкременте
если > лимита — отклонить
```

Простая, но пропускает всплески на границе окон.

**Скользящее окно (Sorted Set)**

```text
ZREMRANGEBYSCORE rl:user:42 0 (now-60000)
ZADD rl:user:42 now now-uuid
ZCARD rl:user:42     # текущее число запросов в окне
EXPIRE rl:user:42 60
```

**Token bucket / leaky bucket**: хранение числа токенов и времени пополнения в hash, вычисление в Lua-скрипте (атомарно). Готовые решения: Redis Cell (`CL.THROTTLE`), `AspNetCoreRateLimit`, встроенный `RateLimiter` .NET с Redis-хранилищем.

Атомарность обеспечивайте Lua-скриптами или транзакциями.

## Другие паттерны

- **Идемпотентность**: `SET key NX EX` для дедупликации запросов;
- **Сессии** и токены с TTL;
- **Задержанные задачи**: Sorted Set со временем выполнения как score;
- **Лидерство**: блокировка с продлением;
- **Счётчики и лидерборды**: `INCR`, `ZINCRBY`.

## Вопросы с ответами

> [!question]- Чем Pub/Sub отличается от Streams?
> Pub/Sub не хранит сообщения и не подтверждает доставку; Streams хранят события, поддерживают группы потребителей и подтверждения.

> [!question]- Как безопасно освободить распределённую блокировку?
> Проверить, что значение равно вашему токену, и удалить ключ одной атомарной операцией (Lua), иначе можно снять чужую блокировку.

> [!question]- Как реализовать rate limiting в Redis?
> Счётчик с TTL (фиксированное окно), Sorted Set (скользящее окно) или token bucket в Lua-скрипте; ключ включает пользователя или IP.
