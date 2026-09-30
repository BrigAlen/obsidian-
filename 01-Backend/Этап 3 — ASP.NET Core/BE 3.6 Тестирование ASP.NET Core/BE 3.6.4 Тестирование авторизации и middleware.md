---
type: topic
domain: backend
stage: 3
section: "3.6"
order: 4
status: todo
level: middle
notion_id: 3ea3310486798199a2e6f67582af01e4
tags: [domain/backend, stage/3, level/middle, topic/aspnet, topic/testing, topic/security, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Тестирование авторизации и middleware

↑ [[BE 3.6 Тестирование ASP.NET Core|3.6 Тестирование ASP.NET Core]] · ← [[BE 3.6.3 Testcontainers — настоящие БД и брокеры в тестах|Предыдущая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->















































> [!info] Зачем это на собесе
> Как проверить, что защищённые endpoint-ы действительно закрыты, не поднимая Keycloak.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

Подмена аутентификации тестовой схемой:

```csharp
public class TestAuthHandler(IOptionsMonitor<AuthenticationSchemeOptions> o, ILoggerFactory l, UrlEncoder e)
    : AuthenticationHandler<AuthenticationSchemeOptions>(o, l, e)
{
    protected override Task<AuthenticateResult> HandleAuthenticateAsync()
    {
        if (!Request.Headers.TryGetValue("X-Test-User", out var user))
            return Task.FromResult(AuthenticateResult.NoResult());

        var claims = new[] { new Claim("sub", user!), new Claim(ClaimTypes.Role, Request.Headers["X-Test-Role"].FirstOrDefault() ?? "user") };
        var ticket = new AuthenticationTicket(new ClaimsPrincipal(new ClaimsIdentity(claims, "Test")), "Test");
        return Task.FromResult(AuthenticateResult.Success(ticket));
    }
}

builder.ConfigureTestServices(s =>
    s.AddAuthentication("Test").AddScheme<AuthenticationSchemeOptions, TestAuthHandler>("Test", _ => { }));
```

```csharp
[Fact] public async Task Anonymous_gets_401()
    => Assert.Equal(HttpStatusCode.Unauthorized, (await client.GetAsync("/orders")).StatusCode);

[Fact] public async Task User_cannot_read_foreign_order()
{
    client.DefaultRequestHeaders.Add("X-Test-User", "u1");
    Assert.Equal(HttpStatusCode.NotFound, (await client.GetAsync($"/orders/{foreignId}")).StatusCode);
}
```

Middleware тестируют либо через `TestServer` с минимальным конвейером, либо интеграционно через `WebApplicationFactory`.

## Нюансы и подводные камни

- Тестируйте матрицу: аноним, обычный пользователь, админ, владелец/не владелец.
- Проверяйте негативные пути: 401, 403, IDOR.
- Проверьте, что новые endpoint-ы не остались открытыми (fallback policy + тест, перебирающий все маршруты).
- Не отключайте авторизацию в тестах целиком — вы перестанете её проверять.

## Практика

1. Добавьте `TestAuthHandler` и тесты 401/403/200.
2. Напишите тест, который проходит по всем endpoint-ам и проверяет наличие политики авторизации.
3. Протестируйте свой middleware с `DefaultHttpContext`.

## Вопросы с ответами

> [!question]- Как тестировать защищённые endpoint-ы без реального IdP?
> Подменить схему аутентификации тестовым handler-ом, задающим claims.

> [!question]- Что обязательно проверить в тестах авторизации?
> Анонимный доступ (401), недостаточные права (403), доступ к чужим ресурсам (IDOR).

## Связанные темы

- [[N:3ea331048679810e9b74c450d13d065b]]
- [[N:3ea33104867981729109f1a011466c28]]
