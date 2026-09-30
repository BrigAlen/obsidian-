---
type: topic
domain: backend
stage: 8
section: "8.1"
order: 5
status: todo
level: senior
notion_id: 3ea33104867981f88d7cefc97436250e
tags: [domain/backend, stage/8, level/senior, topic/design, topic/patterns, topic/behavioral, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Поведенческие паттерны: Strategy, Chain of Responsibility, Command, Observer, Template Method, Mediator

↑ [[BE 8.1 Принципы и паттерны проектирования в C♯|8.1 Принципы и паттерны проектирования в C♯]] · ← [[BE 8.1.4 Структурные паттерны — Adapter, Decorator, Facade, Proxy, Composite|Предыдущая]] · → [[BE 8.1.6 Паттерны доступа к данным — Repository, Unit of Work, Specification|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: senior</span></div>
<!-- meta:end -->







> [!info] Зачем это на собесе
> Самые применимые паттерны: Strategy, Observer, Mediator, Chain — встречаются в ASP.NET Core и MediatR.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

| Паттерн | Суть | Где встречается |
|---|---|---|
| Strategy | взаимозаменяемые алгоритмы за интерфейсом | расчёт скидок, способы оплаты, `IComparer` |
| Chain of Responsibility | запрос проходит по цепочке обработчиков | middleware ASP.NET Core, `DelegatingHandler` |
| Command | запрос как объект: можно очередить, логировать, отменять | CQRS-команды, `ICommand` |
| Observer | подписчики получают уведомления | события C#, `IObservable<T>`, доменные события |
| Template Method | скелет алгоритма в базовом классе, шаги переопределяются | `BackgroundService`, базовые обработчики |
| Mediator | объекты общаются через посредника | MediatR |
| State | поведение зависит от состояния | конечные автоматы заказа |
| Iterator | обход коллекции | `IEnumerable`, `yield` |
| Visitor | операция над структурой без её изменения | обход AST, `ExpressionVisitor` |
| Memento | сохранение состояния для отката | undo |

```csharp
// Strategy + DI: набор стратегий, выбор по условию
public interface IShipping { bool Supports(string code); decimal Cost(Order o); }
public class ShippingCalculator(IEnumerable<IShipping> all)
{
    public decimal Cost(Order o, string code) => all.First(s => s.Supports(code)).Cost(o);
}

// Chain of Responsibility: пайплайн шагов обработки
public delegate Task Step(OrderContext ctx, Func<Task> next);
Step[] pipeline = [Validate, Reserve, Charge];

// Mediator: обработчик команды
public record CreateOrder(Guid CustomerId) : IRequest<Guid>;
public class CreateOrderHandler : IRequestHandler<CreateOrder, Guid> { /* ... */ }
var id = await mediator.Send(new CreateOrder(customerId));

// Observer: доменное событие
public event Func<OrderPaid, Task>? OrderPaid;
```

## Нюансы и подводные камни

- Observer с событиями C#: утечки памяти при неотписанных подписчиках (сильные ссылки).
- Mediator скрывает зависимости между компонентами; в больших системах затрудняет навигацию по коду.
- Strategy с `if/else` в фабрике сводит пользу к нулю: выбирайте через DI/ключи.
- Command объекты должны быть сериализуемыми, если уходят в очередь.

## Практика

1. Замените цепочку `if/else` расчёта доставки на стратегии.
2. Реализуйте свой мини-pipeline обработки заказа (Chain).
3. Сделайте конечный автомат статуса заказа (State).

## Вопросы с ответами

> [!question]- Где в ASP.NET Core используется Chain of Responsibility?
> В конвейере middleware.

> [!question]- Strategy или State?
> Strategy выбирает алгоритм снаружи; State меняет поведение объекта по его внутреннему состоянию.

> [!question]- Что делает Mediator?
> Централизует взаимодействие компонентов, чтобы они не знали друг о друге.

## Связанные темы

- [[N:3ea33104867981d99fb3d9af9f9dec4f]]
- [[N:3ea3310486798124917af0db2e701077]]
