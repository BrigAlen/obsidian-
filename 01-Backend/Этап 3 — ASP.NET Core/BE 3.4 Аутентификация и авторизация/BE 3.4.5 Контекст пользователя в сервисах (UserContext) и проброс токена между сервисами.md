---
type: topic
domain: backend
stage: 3
section: "3.4"
order: 5
status: todo
level: middle
notion_id: 3ea33104867981729109f1a011466c28
tags: [domain/backend, stage/3, level/middle, topic/aspnet, topic/security, topic/microservices, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Контекст пользователя в сервисах (UserContext) и проброс токена между сервисами

↑ [[BE 3.4 Аутентификация и авторизация|3.4 Аутентификация и авторизация]] · ← [[BE 3.4.4 Политики, роли, claims-based и resource-based авторизация|Предыдущая]] · → [[BE 3.4.6 Хранение паролей, ASP.NET Core Identity, API-ключи|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->




























































> [!info] Зачем это на собесе
> Практика микросервисов: как сервис узнаёт «текущего пользователя» и как вызвать другой сервис от его имени.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

Не тащите `HttpContext` в бизнес-логику. Оберните доступ к пользователю интерфейсом.

```csharp
public interface IUserContext { Guid UserId { get; } bool IsAdmin { get; } }

public class HttpUserContext(IHttpContextAccessor accessor) : IUserContext
{
    private ClaimsPrincipal User => accessor.HttpContext?.User ?? throw new InvalidOperationException();
    public Guid UserId => Guid.Parse(User.FindFirstValue("sub")!);
    public bool IsAdmin => User.IsInRole("admin");
}

builder.Services.AddHttpContextAccessor();
builder.Services.AddScoped<IUserContext, HttpUserContext>();
```

В тестах подставляется fake; в фоновых задачах — «системный» контекст.

### Проброс токена между сервисами

| Вариант | Смысл | Когда |
|---|---|---|
| Пробросить входящий Bearer (delegation) | вызываем от имени пользователя | внутренние вызовы с проверкой прав по пользователю |
| Token Exchange (RFC 8693) | обмен токена на токен для другого aud | безопасная делегация |
| Client Credentials | сервис действует от своего имени | системные операции |

```csharp
builder.Services.AddHttpClient<IBillingClient, BillingClient>()
    .AddHeaderPropagation(o => o.Headers.Add("Authorization"));
```

## Нюансы и подводные камни

- `IHttpContextAccessor` недоступен вне запроса (фоновые задачи, очередь): передавайте пользователя явно в сообщении.
- Не доверяйте заголовкам вида `X-User-Id`, пришедшим от клиента; только от gateway после проверки токена.
- Пробрасывайте `aud` осознанно: токен для API A не должен подходить API B.
- Логируйте `sub`, но не токен.

## Практика

1. Внедрите `IUserContext` в сервис и напишите unit-тест с fake.
2. Настройте проброс `Authorization` и `X-Correlation-Id` между двумя сервисами.
3. Реализуйте Token Exchange в Keycloak.

## Вопросы с ответами

> [!question]- Как получить текущего пользователя в сервисе?
> Через абстракцию над `IHttpContextAccessor`/`ClaimsPrincipal`, зарегистрированную как scoped.

> [!question]- Пробросить токен или использовать service-токен?
> Если права зависят от пользователя — пробросить/обменять его токен; для системных задач — Client Credentials.

> [!question]- Как передать пользователя в асинхронной обработке?
> Положить идентификатор пользователя в сообщение и восстановить контекст в обработчике.

## Связанные темы

- [[N:3ea33104867981459090e4d09574ee38]]
- [[N:3ea33104867981bfb755f29c6b1cd640]]
