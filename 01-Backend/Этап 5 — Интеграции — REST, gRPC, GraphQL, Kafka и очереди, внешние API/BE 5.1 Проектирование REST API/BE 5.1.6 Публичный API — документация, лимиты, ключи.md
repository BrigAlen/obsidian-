---
type: topic
domain: backend
stage: 5
section: "5.1"
order: 6
status: todo
level: middle
notion_id: 3ea33104867981c99bb0c8415f3e7528
tags: [domain/backend, stage/5, level/middle, topic/api, topic/rest, topic/security, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Публичный API: документация, лимиты, ключи

↑ [[BE 5.1 Проектирование REST API|5.1 Проектирование REST API]] · ← [[BE 5.1.5 Кэширование HTTP — ETag, Cache-Control, output caching|Предыдущая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->

































> [!info] Зачем это на собесе
> Что нужно, чтобы API могли безопасно использовать внешние разработчики.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

| Аспект | Практика |
|---|---|
| Документация | OpenAPI + примеры, гайд быстрого старта, changelog, коды ошибок |
| Аутентификация | API-ключи для простых сценариев, OAuth 2.0 для доступа от имени пользователя |
| Лимиты | rate limit по ключу/плану, заголовки `X-RateLimit-*`/`Retry-After`, ответ 429 |
| Квоты и тарифы | суточные/месячные лимиты, биллинг |
| Безопасность | HTTPS, минимальные права ключей (scopes), ротация, IP allowlist |
| Наблюдаемость | логирование по ключам, метрики использования, алерты на аномалии |
| Песочница | тестовое окружение с фиктивными данными |
| SDK | генерация клиентов из OpenAPI |
| Вебхуки | подписи и повторы (см. [[N:3ea331048679818db18de06d285c2054]]) |

```csharp
builder.Services.AddRateLimiter(o => o.AddPolicy("by-key", ctx =>
    RateLimitPartition.GetTokenBucketLimiter(ctx.Request.Headers["X-Api-Key"].ToString(),
        _ => new TokenBucketRateLimiterOptions { TokenLimit = 100, TokensPerPeriod = 10, ReplenishmentPeriod = TimeSpan.FromSeconds(1) })));
```

## Нюансы и подводные камни

- Ключ храните хэшированным, показывайте только один раз.
- Прозрачные, стабильные ошибки и коды — часть контракта.
- Вводите лимиты с самого начала: снять ограничения проще, чем добавить.
- Разделяйте публичный и внутренний API, не выставляйте внутренние endpoint-ы.
- Планируйте депрекацию и версионирование до первых клиентов.

## Практика

1. Добавьте API-ключи с scopes и лимитами по плану.
2. Опубликуйте OpenAPI в Scalar/Swagger UI с примерами.
3. Соберите дашборд использования по ключам.

## Вопросы с ответами

> [!question]- API-ключ или OAuth?
> Ключ — для доступа приложения; OAuth — когда нужен доступ от имени пользователя с ограниченными правами.

> [!question]- Как сообщить клиенту о лимите?
> Ответом 429 с заголовком `Retry-After` и информацией об остатке квоты.

## Связанные темы

- [[N:3ea331048679818ea678cc3a866d67e2]]
- [[N:3ea33104867981f3b15bfe79b76ee3cc]]
