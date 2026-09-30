---
type: topic
domain: backend
stage: 7
section: "7.1"
order: 4
status: todo
level: senior
notion_id: 3ea33104867981aead48c78238ef618a
tags: [domain/backend, stage/7, level/senior, topic/dotnet, topic/performance, topic/caching, priority/should]
reviewed:
next_review:
priority: should
time: 3
---

# Кэширование: IMemoryCache, IDistributedCache, HybridCache, output caching

↑ [[BE 7.1 Производительность .NET и кэширование|7.1 Производительность .NET и кэширование]] · ← [[BE 7.1.3 Аллокации и зеро-аллокационный код|Предыдущая]] · → [[BE 7.1.5 Стратегии кэша и инвалидация, cache stampede|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: senior</span></div>
<!-- meta:end -->



















> [!info] Зачем это на собесе
> Кэш — самый частый способ ускорения и самый частый источник багов: инвалидация, устаревание, stampede.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

| Тип | Где хранится | Когда |
|---|---|---|
| `IMemoryCache` | память процесса | быстро, но у каждой реплики свой кэш |
| `IDistributedCache` (Redis, SQL) | внешнее хранилище | общий кэш реплик, сериализация, сетевая задержка |
| `HybridCache` (.NET 9) | L1 память + L2 распределённый | защита от stampede, теги, сериализация из коробки |
| Output caching | готовые HTTP-ответы (см. [[N:3ea331048679818ea678cc3a866d67e2]]) | публичные идемпотентные GET |
| HTTP-кэш (CDN, браузер) | вне приложения | статика и публичные данные |

```csharp
builder.Services.AddHybridCache(o => o.DefaultEntryOptions = new() { Expiration = TimeSpan.FromMinutes(5), LocalCacheExpiration = TimeSpan.FromMinutes(1) });

public async Task<ProductDto> GetAsync(int id, CancellationToken ct) =>
    await cache.GetOrCreateAsync($"product:{id}",
        async token => await repo.LoadAsync(id, token),         // вызывается один раз при промахе, остальные ждут
        tags: ["products"], cancellationToken: ct);

await cache.RemoveByTagAsync("products", ct);                   // инвалидация
```

Что кэшировать: дорогие вычисления, редко меняющиеся справочники, ответы внешних API. Что не кэшировать: персональные данные без ключа пользователя, быстро меняющиеся критичные данные.

## Нюансы и подводные камни

- Ключ должен включать все параметры, влияющие на результат (пользователь, язык, версия).
- Время жизни и инвалидация: кэш без стратегии инвалидации даёт устаревшие данные.
- `IMemoryCache.GetOrCreateAsync` не защищает от параллельных вызовов фабрики.
- Ограничивайте размер (`SizeLimit`), иначе память растёт.
- Кэш не должен быть единственным источником: система обязана работать при его недоступности.
- Сериализация в Redis: версионирование формата при обновлении приложения.

## Практика

1. Добавьте `HybridCache` к справочнику и измерьте нагрузку на БД.
2. Реализуйте инвалидацию по тегам при изменении данных.
3. Проверьте работу при остановке Redis.

## Вопросы с ответами

> [!question]- IMemoryCache или Redis?
> Память процесса быстрее, но не общая; Redis нужен для общего кэша реплик и больших объёмов.

> [!question]- Что даёт HybridCache?
> Двухуровневый кэш с защитой от stampede и тегированной инвалидацией.

## Связанные темы

- [[N:3ea33104867981fb8c07fdd4f935833b]]
- [[N:3ea33104867981ec936ae21e56f183b5]]
