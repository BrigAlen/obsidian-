---
type: topic
domain: backend
stage: 3
section: "3.4"
order: 1
status: todo
level: middle
notion_id: 3ea331048679811a91f1da415f818e6a
tags: [domain/backend, stage/3, level/middle, topic/aspnet, topic/security, topic/auth, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Аутентификация и авторизация в ASP.NET Core: схемы, handlers

↑ [[BE 3.4 Аутентификация и авторизация|3.4 Аутентификация и авторизация]] · → [[BE 3.4.2 JWT Bearer — валидация токена, claims, срок жизни|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->














































> [!info] Зачем это на собесе
> Первым уточняют разницу authN и authZ и как в ASP.NET Core устроены схемы.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

- **Аутентификация (authN)** — «кто вы»: результат — `ClaimsPrincipal`.
- **Авторизация (authZ)** — «что вам можно»: решение по политике/роли.

```csharp
builder.Services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
    .AddJwtBearer(o => { /* параметры */ })
    .AddCookie("cookie");
builder.Services.AddAuthorization();

app.UseAuthentication();   // строит HttpContext.User
app.UseAuthorization();    // проверяет требования endpoint
```

| Понятие | Что это |
|---|---|
| Scheme | именованная конфигурация способа аутентификации (Bearer, Cookie, API key) |
| Handler | реализация схемы: `AuthenticateAsync`, `ChallengeAsync` (401), `ForbidAsync` (403) |
| ClaimsPrincipal | пользователь = набор `ClaimsIdentity` с `Claim` |
| Default scheme | схема, используемая по умолчанию |

### Свой handler (пример API-ключа)

```csharp
public class ApiKeyHandler(IOptionsMonitor<AuthenticationSchemeOptions> o, ILoggerFactory l, UrlEncoder e, IKeyStore keys)
    : AuthenticationHandler<AuthenticationSchemeOptions>(o, l, e)
{
    protected override async Task<AuthenticateResult> HandleAuthenticateAsync()
    {
        if (!Request.Headers.TryGetValue("X-Api-Key", out var key) || !await keys.IsValidAsync(key!))
            return AuthenticateResult.Fail("invalid key");
        var id = new ClaimsIdentity([new Claim(ClaimTypes.Name, "service")], Scheme.Name);
        return AuthenticateResult.Success(new AuthenticationTicket(new ClaimsPrincipal(id), Scheme.Name));
    }
}
```

Endpoint защищают `[Authorize]`/`RequireAuthorization()`, анонимный доступ — `[AllowAnonymous]`.

## Нюансы и подводные камни

- Порядок: `UseAuthentication` строго перед `UseAuthorization`.
- Несколько схем: указывайте `AuthenticationSchemes` в политике.
- 401 без токена и 403 при нехватке прав — разные ответы handler-а.
- Fallback policy (`RequireAuthenticatedUser`) защищает всё по умолчанию.

## Практика

1. Защитите API двумя схемами: JWT и API key.
2. Настройте fallback policy и отметьте открытые endpoint-ы `AllowAnonymous`.
3. Выведите `User.Claims` в отладочном endpoint.

## Вопросы с ответами

> [!question]- Разница authN и authZ?
> AuthN устанавливает личность, authZ решает, разрешено ли ей действие.

> [!question]- Что такое ClaimsPrincipal?
> Модель пользователя в .NET: набор identity, каждая с claims (утверждениями).

> [!question]- Зачем несколько схем?
> Поддержка разных клиентов: браузер (cookie), мобильные/сервисы (Bearer), интеграции (API key).

## Связанные темы

- [[N:3ea33104867981f7801ef26a713b2fd5]]
- [[N:3ea33104867981459090e4d09574ee38]]
