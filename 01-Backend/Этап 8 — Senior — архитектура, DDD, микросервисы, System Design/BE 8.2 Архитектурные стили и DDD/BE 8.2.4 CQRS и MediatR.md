---
type: topic
domain: backend
stage: 8
section: "8.2"
order: 4
status: todo
level: senior
notion_id: 3ea331048679812facbfd65b88f19fcb
tags: [domain/backend, stage/8, level/senior, topic/architecture, topic/cqrs, topic/mediatr, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# CQRS и MediatR

↑ [[BE 8.2 Архитектурные стили и DDD|8.2 Архитектурные стили и DDD]] · ← [[BE 8.2.3 Vertical Slice Architecture|Предыдущая]] · → [[BE 8.2.5 DDD — стратегический — bounded context, ubiquitous language, context map|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: senior</span></div>
<!-- meta:end -->



























> [!info] Зачем это на собесе
> CQRS упоминают везде; нужно различать CQRS как принцип и «тяжёлый» вариант с Event Sourcing и отдельными хранилищами.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

**CQRS (Command Query Responsibility Segregation)** — разделение модели записи (команды меняют состояние) и модели чтения (запросы возвращают данные).

| Уровень | Что | Когда |
|---|---|---|
| Простой | отдельные обработчики команд и запросов, одна БД | почти всегда полезен |
| Раздельные модели | запись — доменная модель, чтение — проекции/DTO (Dapper, view) | разные требования к чтению и записи |
| Раздельные хранилища | чтение из денормализованного хранилища (реплика, ClickHouse, Elasticsearch), синхронизация событиями | высокая нагрузка на чтение, eventual consistency |
| CQRS + Event Sourcing | запись — поток событий | особые требования к аудиту |

```csharp
public record CreateOrder(Guid CustomerId, List<ItemDto> Items) : IRequest<Guid>;          // команда
public record GetOrder(Guid Id) : IRequest<OrderDto?>;                                       // запрос

public class CreateOrderHandler(AppDbContext db) : IRequestHandler<CreateOrder, Guid> { /* меняет состояние */ }
public class GetOrderHandler(IDbConnection conn) : IRequestHandler<GetOrder, OrderDto?> { /* читает Dapper-ом */ }

builder.Services.AddMediatR(c => c.RegisterServicesFromAssemblyContaining<Program>());
builder.Services.AddTransient(typeof(IPipelineBehavior<,>), typeof(ValidationBehavior<,>));   // сквозная валидация

var id = await mediator.Send(new CreateOrder(customerId, items), ct);
```

**MediatR** — реализация паттерна Mediator: `Send` для запросов/команд, `Publish` для уведомлений, `IPipelineBehavior` для сквозных задач (валидация, логирование, транзакция). Альтернативы: Wolverine, свой мини-диспетчер, прямые вызовы обработчиков (Vertical Slice).

## Нюансы и подводные камни

- MediatR — не обязательная часть CQRS; в новых версиях лицензия изменилась (коммерческая для организаций), рассмотрите альтернативы.
- Разные хранилища читателей приводят к eventual consistency: клиент может не видеть свою запись сразу.
- Команда не должна возвращать данные для отображения (максимум идентификатор).
- Скрытая «магия» Mediator усложняет навигацию по коду.
- CQRS для простого CRUD — избыточен.

## Практика

1. Разделите один сервис на команды и запросы с MediatR.
2. Добавьте pipeline behavior валидации и логирования.
3. Реализуйте read-модель списка заказов через Dapper.

## Вопросы с ответами

> [!question]- Что такое CQRS?
> Разделение операций записи и чтения на разные модели/обработчики с независимой оптимизацией.

> [!question]- Обязательно ли CQRS требует Event Sourcing?
> Нет: это независимые паттерны, хотя часто используются вместе.

## Связанные темы

- [[N:3ea3310486798122b6d0c40f6364b6bd]]
- [[N:3ea331048679811b9ea3ddea76b7fa24]]
