---
type: topic
domain: db
stage: 4
section: "4.1"
order: 2
status: todo
level: middle
notion_id: 3ea331048679818eb54ee4baf033537a
tags: [domain/db, stage/4, level/middle, topic/redis, topic/cache, topic/eviction, priority/should]
reviewed:
next_review:
priority: should
time: 4
---

# Redis как кэш: TTL, eviction, стратегии cache-aside, write-through

↑ [[DB 4.1 Redis и MongoDB|4.1 Redis и MongoDB]] · ← [[DB 4.1.1 Redis — структуры данных и команды|Предыдущая]] · → [[DB 4.1.3 Redis — pub-sub, streams, распределённые блокировки, rate limiting|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~4 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> Кэширование — главный сценарий Redis. Спрашивают стратегии, инвалидацию и проблемы кэша (stampede, penetration).

## Стратегии

| Стратегия | Схема | Плюсы / минусы |
|---|---|---|
| **Cache-aside** (lazy loading) | приложение читает кэш; при промахе идёт в БД и кладёт в кэш | просто, кэшируется только нужное; первое обращение медленное, возможна устарелость |
| **Read-through** | кэш сам загружает данные из БД | приложение проще; нужна интеграция |
| **Write-through** | запись идёт в кэш и синхронно в БД | согласованность; выше задержка записи |
| **Write-behind** | запись в кэш, в БД — асинхронно пачками | быстро; риск потери при сбое |
| **Refresh-ahead** | обновление до истечения TTL | нет холодных промахов; сложнее |

```csharp
public async Task<Product?> GetAsync(long id)
{
    var key = $"product:{id}";
    var cached = await _db.StringGetAsync(key);
    if (cached.HasValue) return JsonSerializer.Deserialize<Product>(cached!);

    var product = await _repo.FindAsync(id);
    if (product is not null)
        await _db.StringSetAsync(key, JsonSerializer.Serialize(product), TimeSpan.FromMinutes(10) + TimeSpan.FromSeconds(Random.Shared.Next(60)));
    return product;
}

public async Task UpdateAsync(Product p)
{
    await _repo.SaveAsync(p);
    await _db.KeyDeleteAsync($"product:{p.Id}");   // инвалидация
}
```

Инвалидация: **удалять** ключ при изменении (проще и безопаснее, чем обновлять значение в кэше).

## TTL

Всегда задавайте срок жизни: защита от вечно устаревших данных и переполнения. **Добавляйте разброс (jitter)**, чтобы ключи не истекали одновременно.

## Политики вытеснения (maxmemory-policy)

При достижении `maxmemory` Redis вытесняет ключи:

| Политика | Поведение |
|---|---|
| `noeviction` | ошибка при записи (по умолчанию) |
| `allkeys-lru` | вытеснить наименее недавно использованные из всех |
| `allkeys-lfu` | наименее часто используемые |
| `volatile-lru` / `volatile-lfu` / `volatile-ttl` | только ключи с TTL |
| `allkeys-random`, `volatile-random` | случайные |

Для чистого кэша — `allkeys-lru` или `allkeys-lfu`. LRU/LFU приближённые (выборка ключей).

## Проблемы кэша

| Проблема | Описание | Решения |
|---|---|---|
| **Cache stampede** (dog-pile) | ключ истёк, тысячи запросов одновременно идут в БД | блокировка на загрузку (single flight), jitter TTL, refresh-ahead, stale-while-revalidate |
| **Cache penetration** | запросы несуществующих ключей всегда мимо кэша | кэшировать «пустой» результат с коротким TTL, Bloom-фильтр |
| **Cache avalanche** | массовое одновременное истечение или падение кэша | jitter, репликация, деградация, лимиты на БД |
| **Hot key** | один ключ с огромной нагрузкой | локальный кэш (L1), репликация ключа, шардирование по суффиксу |
| **Big key** | огромное значение | разбивать, сжимать |
| **Устаревшие данные** | расхождение с БД | инвалидация, короткий TTL, событийное обновление |

Двухуровневый кэш: L1 в памяти процесса (`IMemoryCache`) + L2 Redis; инвалидация L1 через pub/sub. В .NET: `IDistributedCache`, `HybridCache` (single-flight и L1/L2 из коробки).

## Что кэшировать

Читаемое часто и редко изменяемое, дорогое в вычислении, справочники, результаты внешних вызовов, сессии, агрегаты. Не кэшируйте то, что требует строгой консистентности в реальном времени.

## Ключи и сериализация

Версионирование в ключе: `product:v2:42` (смена формата без ручной очистки); компактные форматы (MessagePack, protobuf) вместо JSON для больших объёмов; сжатие.

## Метрики

Hit ratio (`keyspace_hits`, `keyspace_misses`), evictions, использование памяти, задержки (`SLOWLOG`, `LATENCY`).

## Вопросы с ответами

> [!question]- Что такое cache-aside?
> Приложение сначала обращается к кэшу, при промахе читает БД и сохраняет результат в кэш; при изменении данных запись в БД и удаление ключа из кэша.

> [!question]- Как защититься от cache stampede?
> Блокировка на перезагрузку ключа (только один запрос идёт в БД), jitter TTL, предварительное обновление, отдача слегка устаревшего значения во время обновления.

> [!question]- Почему при инвалидации лучше удалять ключ, а не обновлять?
> Удаление проще и избегает гонок, при которых старое значение перезаписывает новое; следующий запрос загрузит актуальные данные.
