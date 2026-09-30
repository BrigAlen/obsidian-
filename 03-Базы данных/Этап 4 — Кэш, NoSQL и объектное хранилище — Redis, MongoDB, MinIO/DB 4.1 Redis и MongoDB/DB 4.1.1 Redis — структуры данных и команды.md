---
type: topic
domain: db
stage: 4
section: "4.1"
order: 1
status: todo
level: middle
notion_id: 3ea33104867981b0a5d7f52b55b2a7d1
tags: [domain/db, stage/4, level/middle, topic/redis, topic/data-structures, priority/should]
reviewed:
next_review:
priority: should
time: 3
---

# Redis: структуры данных и команды

↑ [[DB 4.1 Redis и MongoDB|4.1 Redis и MongoDB]] · → [[DB 4.1.2 Redis как кэш — TTL, eviction, стратегии cache-aside, write-through|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> Redis — не «просто кэш»: спрашивают структуры данных и то, какую задачу решает каждая.

## Что такое Redis

Хранилище «ключ–значение» **в оперативной памяти** с богатыми структурами данных. Однопоточное выполнение команд (ввод-вывод в новых версиях многопоточный): операции **атомарны**, задержки — доли миллисекунды. Порт 6379, протокол RESP.

## Структуры данных

| Тип | Команды | Применение |
|---|---|---|
| **String** | `SET`, `GET`, `INCR`, `SETEX`, `SETNX`, `MGET` | кэш, счётчики, токены, блокировки |
| **Hash** | `HSET`, `HGET`, `HGETALL`, `HINCRBY` | объекты (профиль, сессия) |
| **List** | `LPUSH`, `RPOP`, `BLPOP`, `LRANGE` | очереди, последние N событий |
| **Set** | `SADD`, `SISMEMBER`, `SINTER`, `SUNION` | теги, уникальные значения, «кто онлайн» |
| **Sorted Set** | `ZADD`, `ZRANGE`, `ZRANGEBYSCORE`, `ZINCRBY`, `ZRANK` | рейтинги, приоритетные очереди, задержанные задачи |
| **Stream** | `XADD`, `XREADGROUP`, `XACK` | журнал событий, очереди |
| **Bitmap** | `SETBIT`, `BITCOUNT` | флаги активности |
| **HyperLogLog** | `PFADD`, `PFCOUNT` | приближённые уникальные (0.81% ошибки, 12 КБ) |
| **Geo** | `GEOADD`, `GEOSEARCH` | поиск рядом |
| **JSON, Search, TimeSeries, Bloom** | модули Redis Stack | документы, поиск, временные ряды |

## Примеры

```text
SET user:42:name "Анна" EX 3600          # со сроком жизни
INCR page:home:views                     # атомарный счётчик
HSET user:42 name "Анна" city "Москва" plan "pro"
HGETALL user:42
LPUSH queue:emails "job1"; BRPOP queue:emails 5
SADD online:2026-09-30 42 43; SCARD online:2026-09-30
ZADD leaderboard 1500 "anna" 1320 "boris"
ZREVRANGE leaderboard 0 9 WITHSCORES     # топ-10
PFADD visitors:2026-09-30 "u1" "u2"; PFCOUNT visitors:2026-09-30
```

## Ключи

- имена с префиксами: `app:entity:id:field` (`shop:cart:42`);
- **не используйте `KEYS *`** на проде (блокирует): применяйте `SCAN` с курсором;
- срок жизни: `EXPIRE key sec`, `TTL key`, `PERSIST`;
- удаление больших ключей: `UNLINK` (асинхронно) вместо `DEL`.

## Транзакции и скрипты

- `MULTI` / `EXEC`: пакет команд выполняется последовательно без вмешательства (без отката при ошибке команды); `WATCH` для оптимистичной блокировки;
- **Lua-скрипты** (`EVAL`) и **Functions**: атомарное выполнение произвольной логики на сервере;
- **pipelining**: отправка нескольких команд без ожидания ответов (меньше задержек сети).

## Сложность и большие структуры

Команды имеют сложность O(1), O(log n), O(n): следите за O(n) на больших коллекциях (`HGETALL` на огромном хэше, `SMEMBERS`, `LRANGE 0 -1`). Большие ключи (big keys) блокируют сервер и создают перекосы.

## Использование из .NET

`StackExchange.Redis`: `ConnectionMultiplexer` (один на приложение), `IDatabase`, асинхронные методы, `IServer.Keys` (SCAN), `ISubscriber`.

```csharp
var mux = await ConnectionMultiplexer.ConnectAsync("redis:6379");
var db = mux.GetDatabase();
await db.StringSetAsync("user:42:name", "Анна", TimeSpan.FromHours(1));
var name = await db.StringGetAsync("user:42:name");
await db.HashSetAsync("user:42", [new("name", "Анна"), new("plan", "pro")]);
long views = await db.StringIncrementAsync("page:home:views");
```

## Вопросы с ответами

> [!question]- Почему Redis быстрый?
> Данные в памяти, простые структуры, эффективная однопоточная модель без блокировок между потоками, мультиплексирование соединений (epoll), pipelining.

> [!question]- Чем плох KEYS *?
> Это O(N) и блокирует единственный поток обработки команд; на больших базах вызывает простои. Используйте `SCAN`.

> [!question]- Какую структуру выбрать для рейтинга?
> Sorted Set: `ZADD` / `ZINCRBY` для обновления, `ZREVRANGE` для топа, `ZRANK` для места пользователя, все за O(log n).
