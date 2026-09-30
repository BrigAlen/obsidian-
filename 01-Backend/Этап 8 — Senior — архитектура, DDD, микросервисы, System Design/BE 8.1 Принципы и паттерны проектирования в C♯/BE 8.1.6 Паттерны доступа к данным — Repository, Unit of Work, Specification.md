---
type: topic
domain: backend
stage: 8
section: "8.1"
order: 6
status: todo
level: senior
notion_id: 3ea3310486798124917af0db2e701077
tags: [domain/backend, stage/8, level/senior, topic/design, topic/patterns, topic/data-access, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Паттерны доступа к данным: Repository, Unit of Work, Specification

↑ [[BE 8.1 Принципы и паттерны проектирования в C♯|8.1 Принципы и паттерны проектирования в C♯]] · ← [[BE 8.1.5 Поведенческие паттерны — Strategy, Chain of Responsibility, Command, Observer, Template Method, Mediator|Предыдущая]] · → [[BE 8.1.7 Result pattern и обработка ошибок без исключений|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: senior</span></div>
<!-- meta:end -->



















> [!info] Зачем это на собесе
> Часть вопроса «нужен ли Repository поверх EF» (см. [[N:3ea33104867981048155ce6c5ea28bef]]); здесь сами паттерны.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

| Паттерн | Суть |
|---|---|
| Repository | коллекция-подобный интерфейс к агрегатам; скрывает хранилище |
| Unit of Work | отслеживает изменения и сохраняет их одной транзакцией |
| Specification | объект-условие запроса, комбинируется (`And`, `Or`) |
| Query Object / Read model | отдельные запросы для чтения (CQRS) |
| Data Mapper vs Active Record | отделять ли сущность от хранения |
| Identity Map | один объект на ключ в рамках сессии |

```csharp
public abstract class Specification<T>
{
    public abstract Expression<Func<T, bool>> Criteria { get; }
    public Specification<T> And(Specification<T> other) => new AndSpec<T>(this, other);
}
public class PaidOrders : Specification<Order> { public override Expression<Func<Order, bool>> Criteria => o => o.Status == Status.Paid; }
public class OrdersOfCustomer(Guid id) : Specification<Order> { public override Expression<Func<Order, bool>> Criteria => o => o.CustomerId == id; }

public Task<List<Order>> ListAsync(Specification<Order> spec, CancellationToken ct) => db.Orders.Where(spec.Criteria).ToListAsync(ct);
```

Repository агрегата: `GetAsync(id)`, `Add(order)`; Unit of Work — `SaveChangesAsync` в конце use case. В DDD репозитории — на агрегат, а не на таблицу.

## Нюансы и подводные камни

- Generic-репозиторий с `IQueryable` протекает: детали запросов уходят в вызывающий код.
- Specification на `Expression` должна транслироваться в SQL, иначе клиентское вычисление.
- Репозиторий для чтения (списки, отчёты) лучше заменить запросами напрямую к БД.
- Транзакционные границы — на уровне use case.

## Практика

1. Реализуйте Specification для фильтров заказов и скомбинируйте их.
2. Сравните объём кода: DbContext напрямую и репозиторий.
3. Сделайте отдельный read-запрос для списка вместо репозитория.

## Вопросы с ответами

> [!question]- Что такое Unit of Work?
> Паттерн, накапливающий изменения и сохраняющий их атомарно; в EF Core это `DbContext`.

> [!question]- Когда Specification оправдана?
> При множестве повторно используемых комбинируемых условий выборки.

## Связанные темы

- [[N:3ea33104867981f88d7cefc97436250e]]
- [[N:3ea33104867981a8bdded452aaea7f32]]
