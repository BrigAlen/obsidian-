---
type: topic
domain: backend
stage: 5
section: "5.3"
order: 3
status: todo
level: middle
notion_id: 3ea331048679815caa34c14a7c942c60
tags: [domain/backend, stage/5, level/middle, topic/api, topic/graphql, topic/performance, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Проблема N+1 и DataLoader

↑ [[BE 5.3 GraphQL на бэкенде и Federation|5.3 GraphQL на бэкенде и Federation]] · ← [[BE 5.3.2 Hot Chocolate — queries, mutations, фильтрация, пагинация|Предыдущая]] · → [[BE 5.3.4 Federation и gateway — Hot Chocolate Fusion|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->














> [!info] Зачем это на собесе
> Главный вопрос по GraphQL-производительности; DataLoader — стандартный ответ.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

Запрос `orders { customer { name } }`: resolver `customer` вызывается для каждого заказа — 1 запрос на список + N запросов за клиентами.

**DataLoader** собирает все ключи, запрошенные в рамках одного «тика» выполнения, и выполняет **один пакетный запрос**; результат кэшируется в рамках запроса.

```csharp
public class CustomerByIdDataLoader(IBatchScheduler scheduler, IDbContextFactory<AppDbContext> factory, DataLoaderOptions? options = null)
    : BatchDataLoader<Guid, Customer>(scheduler, options ?? new DataLoaderOptions())
{
    protected override async Task<IReadOnlyDictionary<Guid, Customer>> LoadBatchAsync(IReadOnlyList<Guid> keys, CancellationToken ct)
    {
        await using var db = await factory.CreateDbContextAsync(ct);
        return await db.Customers.Where(c => keys.Contains(c.Id)).ToDictionaryAsync(c => c.Id, ct);
    }
}

public async Task<Customer> GetCustomer([Parent] Order o, CustomerByIdDataLoader loader, CancellationToken ct)
    => await loader.LoadAsync(o.CustomerId, ct);
```

Итог: 2 запроса вместо N+1: `orders` и `customers where id in (...)`.

| Вид | Смысл |
|---|---|
| `BatchDataLoader` | один ключ → одно значение |
| `GroupedDataLoader` | один ключ → коллекция (заказы клиента) |
| `CacheDataLoader` | кэш без пакетирования |

## Нюансы и подводные камни

- DbContext не потокобезопасен: используйте `IDbContextFactory` в DataLoader.
- Слишком большие `IN` — ограничивайте размер батча.
- При `UseProjection` часть N+1 решается самим EF, DataLoader нужен для связей между сервисами и не-EF источников.
- DataLoader кэширует в рамках запроса; не путайте с межзапросным кэшем.

## Практика

1. Включите логирование SQL и увидите N+1, затем внедрите DataLoader.
2. Сделайте `GroupedDataLoader` для заказов клиента.
3. Сравните число запросов до и после.

## Вопросы с ответами

> [!question]- Как DataLoader решает N+1?
> Накапливает ключи за тик выполнения и загружает их одним пакетным запросом.

> [!question]- DataLoader или Include?
> Include/проекции — внутри одного источника EF; DataLoader — универсально, в том числе для других сервисов.

## Связанные темы

- [[N:3ea33104867981bf90d1f3ec3e986fe2]]
- [[N:3ea331048679810ab845d7cf86845ccc]]
