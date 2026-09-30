---
type: topic
domain: backend
stage: 3
section: "3.4"
order: 4
status: todo
level: middle
notion_id: 3ea33104867981459090e4d09574ee38
tags: [domain/backend, stage/3, level/middle, topic/aspnet, topic/security, topic/authorization, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Политики, роли, claims-based и resource-based авторизация

↑ [[BE 3.4 Аутентификация и авторизация|3.4 Аутентификация и авторизация]] · ← [[BE 3.4.3 OAuth 2.0, OpenID Connect и Keycloak на бэкенде|Предыдущая]] · → [[BE 3.4.5 Контекст пользователя в сервисах (UserContext) и проброс токена между сервисами|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->





















> [!info] Зачем это на собесе
> Проверяется умение выбрать модель доступа: роли, claims, политики или проверка по ресурсу.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

| Модель | Пример | Когда |
|---|---|---|
| Role-based | `[Authorize(Roles = "Admin")]` | простые системы |
| Claims-based | `RequireClaim("department", "sales")` | атрибуты пользователя |
| Policy-based | `RequireAssertion`, свои requirements | сложные правила |
| Resource-based | «может ли user изменить **этот** документ» | владение, ACL |

```csharp
builder.Services.AddAuthorizationBuilder()
    .AddPolicy("Adult", p => p.RequireClaim("age").RequireAssertion(c => int.Parse(c.User.FindFirstValue("age")!) >= 18))
    .AddPolicy("CanEditOrders", p => p.Requirements.Add(new EditOrdersRequirement()));

app.MapDelete("/orders/{id}", Delete).RequireAuthorization("CanEditOrders");
```

### Resource-based

```csharp
public class OrderOwnerHandler : AuthorizationHandler<OwnerRequirement, Order>
{
    protected override Task HandleRequirementAsync(AuthorizationHandlerContext ctx, OwnerRequirement req, Order order)
    {
        if (order.OwnerId == ctx.User.FindFirstValue(ClaimTypes.NameIdentifier)) ctx.Succeed(req);
        return Task.CompletedTask;
    }
}

var result = await authz.AuthorizeAsync(User, order, new OwnerRequirement());
if (!result.Succeeded) return Forbid();
```

Ресурс нужно сначала загрузить, поэтому проверка выполняется в коде, а не атрибутом.

## Нюансы и подводные камни

- IDOR: проверяйте доступ к объекту, а не только роль (`/orders/123` чужого пользователя).
- Множество requirement-ов в одной политике — AND; несколько handlers одного requirement — OR.
- Фильтруйте выборки по владельцу на уровне запроса (`Where(o => o.OwnerId == userId)`).
- Проверки прав только на UI не защищают API.

## Практика

1. Реализуйте политику «владелец или админ».
2. Добавьте resource-based handler для заказов и тест на попытку доступа к чужому.
3. Настройте fallback policy для всего API.

## Вопросы с ответами

> [!question]- Роль или политика?
> Роль — грубая группа; политика инкапсулирует правило (роль, claims, ресурс) и гибче.

> [!question]- Что такое IDOR?
> Небезопасный прямой доступ к объектам: пользователь меняет идентификатор и получает чужие данные; лечится проверкой владения на сервере.

> [!question]- Когда нужна resource-based авторизация?
> Когда решение зависит от конкретного объекта, а не только от пользователя.

## Связанные темы

- [[N:3ea33104867981eab521e5a0dd217b96]]
- [[N:3ea33104867981729109f1a011466c28]]
