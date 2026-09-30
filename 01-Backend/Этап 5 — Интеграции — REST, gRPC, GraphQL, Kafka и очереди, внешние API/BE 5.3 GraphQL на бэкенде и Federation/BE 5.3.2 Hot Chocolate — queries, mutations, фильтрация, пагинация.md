---
type: topic
domain: backend
stage: 5
section: "5.3"
order: 2
status: todo
level: middle
notion_id: 3ea33104867981bf90d1f3ec3e986fe2
tags: [domain/backend, stage/5, level/middle, topic/api, topic/graphql, topic/hotchocolate, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Hot Chocolate: queries, mutations, фильтрация, пагинация

↑ [[BE 5.3 GraphQL на бэкенде и Federation|5.3 GraphQL на бэкенде и Federation]] · ← [[BE 5.3.1 GraphQL на сервере — схема, типы, resolvers|Предыдущая]] · → [[BE 5.3.3 Проблема N+1 и DataLoader|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->









> [!info] Зачем это на собесе
> Практическая реализация GraphQL на .NET: подход code-first и встроенные возможности.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

Hot Chocolate — основной GraphQL-сервер для .NET.

```csharp
builder.Services
    .AddGraphQLServer()
    .AddQueryType<Query>()
    .AddMutationType<Mutation>()
    .AddProjections().AddFiltering().AddSorting()
    .AddDataLoader<CustomerByIdDataLoader>()
    .ModifyRequestOptions(o => o.IncludeExceptionDetails = builder.Environment.IsDevelopment());
app.MapGraphQL();

public class Query
{
    [UsePaging(MaxPageSize = 50, IncludeTotalCount = true)]
    [UseProjection, UseFiltering, UseSorting]
    public IQueryable<Order> GetOrders(AppDbContext db) => db.Orders;   // EF: SQL строится по запросу клиента
}

public class Mutation
{
    public async Task<Order> CancelOrder(Guid id, [Service] IOrderService svc, CancellationToken ct)
        => await svc.CancelAsync(id, ct);
}
```

| Возможность | Что даёт |
|---|---|
| `UseProjection` | выбираются только запрошенные колонки |
| `UseFiltering/UseSorting` | `where`/`order` без ручного кода |
| `UsePaging` | Relay-курсоры (`edges`, `pageInfo`) |
| Mutation conventions | payload с `errors`, единый шаблон |
| Subscriptions | WebSocket, топики (in-memory/Redis) |
| Authorization | `[Authorize]` на полях |

## Нюансы и подводные камни

- `IQueryable` наружу + фильтрация = клиент может строить дорогие запросы: ограничивайте поля фильтрации.
- Ошибки бизнес-логики возвращайте типизированно (union/errors), не исключениями.
- Ограничьте `MaxPageSize`, глубину и стоимость (см. [[N:3ea3310486798105bb21fdc37191b769]]).
- Сопоставляйте DTO и схему, чтобы изменения БД не ломали контракт.
- Мутации выполняются последовательно, запросы — параллельно.

## Практика

1. Подключите Hot Chocolate к EF Core с проекциями и фильтрами.
2. Реализуйте мутацию с типизированными ошибками.
3. Настройте подписку на изменения заказа через Redis.

## Вопросы с ответами

> [!question]- Что делает UseProjection?
> Транслирует выбранные клиентом поля в `Select` EF, чтобы читать только нужные колонки.

> [!question]- Как возвращать ошибки мутаций?
> Через payload с полем ошибок (mutation conventions) вместо генерации исключений.

## Связанные темы

- [[N:3ea3310486798175b3a6d2f428a4a9d4]]
- [[N:3ea331048679815caa34c14a7c942c60]]
