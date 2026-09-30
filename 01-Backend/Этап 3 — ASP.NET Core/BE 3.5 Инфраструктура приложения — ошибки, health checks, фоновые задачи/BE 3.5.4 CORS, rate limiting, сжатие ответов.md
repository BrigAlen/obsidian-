---
type: topic
domain: backend
stage: 3
section: "3.5"
order: 4
status: todo
level: middle
notion_id: 3ea3310486798119982ad4f3f641704d
tags: [domain/backend, stage/3, level/middle, topic/aspnet, topic/security, topic/performance, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# CORS, rate limiting, сжатие ответов

↑ [[BE 3.5 Инфраструктура приложения — ошибки, health checks, фоновые задачи|3.5 Инфраструктура приложения: ошибки, health checks, фоновые задачи]] · ← [[BE 3.5.3 Фоновые задачи — IHostedService, BackgroundService, Worker, Hangfire и Quartz|Предыдущая]] · → [[BE 3.5.5 Graceful shutdown и жизненный цикл приложения|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->
















































> [!info] Зачем это на собесе
> CORS — вечная боль frontend-бэкенд интеграции; rate limiting — защита от перегрузки.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

### CORS

Браузерная политика: страница с origin A может обращаться к origin B, только если B разрешил это заголовками `Access-Control-Allow-*`. Сервер не блокирует запрос — блокирует браузер.

```csharp
builder.Services.AddCors(o => o.AddPolicy("web", p => p
    .WithOrigins("https://app.example.com")
    .WithMethods("GET", "POST", "PUT", "DELETE")
    .WithHeaders("Authorization", "Content-Type")
    .AllowCredentials()));
app.UseCors("web");
```

Preflight — `OPTIONS` перед «небезопасным» запросом; ответ можно кэшировать (`SetPreflightMaxAge`).

### Rate limiting

```csharp
builder.Services.AddRateLimiter(o =>
{
    o.RejectionStatusCode = 429;
    o.AddFixedWindowLimiter("api", w => { w.PermitLimit = 100; w.Window = TimeSpan.FromMinutes(1); });
    o.AddPolicy("per-user", ctx => RateLimitPartition.GetTokenBucketLimiter(
        ctx.User.Identity?.Name ?? ctx.Connection.RemoteIpAddress?.ToString() ?? "anon",
        _ => new TokenBucketRateLimiterOptions { TokenLimit = 20, TokensPerPeriod = 10, ReplenishmentPeriod = TimeSpan.FromSeconds(1) }));
});
app.UseRateLimiter();
```

| Алгоритм | Особенность |
|---|---|
| Fixed window | просто, всплески на границе окна |
| Sliding window | плавнее |
| Token bucket | допускает всплески |
| Concurrency | ограничивает параллельные запросы |

### Сжатие

`AddResponseCompression` (Brotli/Gzip) для текстовых ответов. Обычно делается на proxy/CDN.

## Нюансы и подводные камни

- `AllowAnyOrigin` вместе с `AllowCredentials` запрещён спецификацией.
- CORS не заменяет авторизацию: запросы без браузера его игнорируют.
- Встроенный rate limiter локален для инстанса; для кластера нужен общий счётчик (Redis) или лимиты на gateway.
- Сжатие HTTPS-ответов с секретами → BREACH; будьте осторожны.

## Практика

1. Настройте CORS для SPA и проверьте preflight в DevTools.
2. Добавьте лимит на endpoint логина.
3. Сравните размеры ответа с Brotli и без.

## Вопросы с ответами

> [!question]- Что такое CORS и кто его проверяет?
> Механизм браузера, ограничивающий кросс-доменные запросы; сервер лишь сообщает разрешения заголовками.

> [!question]- Зачем preflight?
> Браузер заранее спрашивает разрешение для «непростых» запросов (метод, заголовки, credentials).

> [!question]- Чем token bucket отличается от fixed window?
> Bucket допускает короткие всплески при контроле среднего темпа; fixed window имеет резкие границы окна.

## Связанные темы

- [[N:3ea33104867981b28ed6dcb331e6f3c6]]
- [[N:3ea331048679819b82adf7f42ef440d8]]
