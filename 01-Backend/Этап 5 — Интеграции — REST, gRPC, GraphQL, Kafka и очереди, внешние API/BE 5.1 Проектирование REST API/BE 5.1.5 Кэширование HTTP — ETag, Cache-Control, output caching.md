---
type: topic
domain: backend
stage: 5
section: "5.1"
order: 5
status: todo
level: middle
notion_id: 3ea331048679818ea678cc3a866d67e2
tags: [domain/backend, stage/5, level/middle, topic/api, topic/rest, topic/caching, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Кэширование HTTP: ETag, Cache-Control, output caching

↑ [[BE 5.1 Проектирование REST API|5.1 Проектирование REST API]] · ← [[BE 5.1.4 Версионирование и обратная совместимость|Предыдущая]] · → [[BE 5.1.6 Публичный API — документация, лимиты, ключи|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->
















> [!info] Зачем это на собесе
> Про производительность: как снять нагрузку с сервера и не отдавать устаревшие данные.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

| Заголовок | Смысл |
|---|---|
| `Cache-Control: max-age=60` | можно использовать без запроса 60 секунд |
| `Cache-Control: no-store` | не кэшировать (чувствительные данные) |
| `Cache-Control: private/public` | кэшировать только в браузере / и в общих кэшах |
| `ETag: "abc"` + `If-None-Match` | условный запрос: если не изменилось — `304 Not Modified` без тела |
| `Last-Modified` + `If-Modified-Since` | то же по времени |
| `Vary: Accept-Encoding, Authorization` | от каких заголовков зависит ответ |

```csharp
app.MapGet("/products/{id}", async (int id, HttpContext ctx, IProducts p) =>
{
    var product = await p.GetAsync(id);
    var etag = $"\"{product.Version}\"";
    if (ctx.Request.Headers.IfNoneMatch == etag) return Results.StatusCode(304);
    ctx.Response.Headers.ETag = etag;
    ctx.Response.Headers.CacheControl = "public,max-age=60";
    return Results.Ok(product);
});
```

### Серверные кэши ASP.NET Core

- **Output caching** (`AddOutputCache`, `.CacheOutput()`): кэш ответа на сервере с политиками, тегами и инвалидацией.
- **Response caching**: на основе заголовков, для HTTP-кэшей.
- **`IMemoryCache` / `IDistributedCache` / `HybridCache` (.NET 9)**: кэш данных, а не ответов.

```csharp
builder.Services.AddOutputCache(o => o.AddPolicy("products", b => b.Expire(TimeSpan.FromMinutes(1)).Tag("products")));
app.MapGet("/products", ...).CacheOutput("products");
await cache.EvictByTagAsync("products", ct);   // инвалидация при изменении
```

## Нюансы и подводные камни

- Кэшировать персонализированные ответы в общем кэше нельзя (`private` или `Vary: Authorization`).
- Инвалидация — самая сложная часть: тегируйте и очищайте по событиям.
- Cache stampede: много запросов одновременно при истечении; используйте блокировку/`HybridCache`.
- Оптимистичная конкуренция через ETag + `If-Match` совмещает кэш и версионирование.
- Не кэшируйте ошибки и 5xx надолго.

## Практика

1. Добавьте ETag и проверьте 304 в DevTools.
2. Включите Output cache с тегами и инвалидацией.
3. Реализуйте защиту от stampede через `HybridCache`.

## Вопросы с ответами

> [!question]- Как работает ETag?
> Клиент отправляет `If-None-Match` с прошлым ETag; если ресурс не менялся, сервер отвечает 304 без тела.

> [!question]- Чем output cache отличается от IMemoryCache?
> Output cache кэширует готовый HTTP-ответ, `IMemoryCache` — произвольные данные.

> [!question]- Что такое cache stampede?
> Одновременное обновление истекшего ключа множеством запросов, создающее пик нагрузки.

## Связанные темы

- [[N:3ea33104867981a78f21d0e71de5ad83]]
- [[N:3ea33104867981c99bb0c8415f3e7528]]
