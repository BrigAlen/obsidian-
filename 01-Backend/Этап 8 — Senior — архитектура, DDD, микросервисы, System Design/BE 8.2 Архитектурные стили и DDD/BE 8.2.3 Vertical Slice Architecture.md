---
type: topic
domain: backend
stage: 8
section: "8.2"
order: 3
status: todo
level: senior
notion_id: 3ea3310486798122b6d0c40f6364b6bd
tags: [domain/backend, stage/8, level/senior, topic/architecture, topic/vertical-slice, priority/must]
reviewed:
next_review:
priority: must
time: 4
---

# Vertical Slice Architecture

↑ [[BE 8.2 Архитектурные стили и DDD|8.2 Архитектурные стили и DDD]] · ← [[BE 8.2.2 Clean Architecture, Onion, Hexagonal (Ports & Adapters)|Предыдущая]] · → [[BE 8.2.4 CQRS и MediatR|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~4 мин чтения</span><span class="chip">Уровень: senior</span></div>
<!-- meta:end -->










> [!info] Зачем это на собесе
> Современная альтернатива слоям: организация кода по фичам.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

Код группируется **по вертикальным срезам (фичам)**, а не по техническим слоям. Каждая фича содержит всё нужное: endpoint, валидацию, обработчик, запрос к данным.

```text
Features/
  Orders/
    CreateOrder/
      CreateOrder.cs          # Request, Validator, Handler, Endpoint — рядом
    GetOrder/
      GetOrder.cs
    CancelOrder/
      CancelOrder.cs
  Customers/
    ...
Common/                       # только действительно общее
```

```csharp
public static class CreateOrder
{
    public record Command(Guid CustomerId, List<Item> Items);
    public class Validator : AbstractValidator<Command> { /* ... */ }

    public class Handler(AppDbContext db, TimeProvider clock)
    {
        public async Task<Guid> Handle(Command c, CancellationToken ct)
        {
            var order = Order.Create(c.CustomerId, c.Items, clock.GetUtcNow());
            db.Orders.Add(order);
            await db.SaveChangesAsync(ct);
            return order.Id;
        }
    }

    public static void Map(IEndpointRouteBuilder app) =>
        app.MapPost("/orders", async (Command c, Handler h, CancellationToken ct) => Results.Created($"/orders/{await h.Handle(c, ct)}", null));
}
```

| Аспект | Слои | Vertical Slice |
|---|---|---|
| Изменение фичи | много файлов в разных папках | всё в одном месте |
| Общий код | слой сервисов, репозитории | минимально, выделяется по необходимости |
| Технологии на срез | единые для всех | можно разные (EF для записи, Dapper для чтения) |
| Риск | «толстые» слои | дублирование между срезами |

Подходит вместе с CQRS и MediatR/Wolverine; в каждом срезе допускается разная сложность.

## Нюансы и подводные камни

- Дублирование между срезами допустимо, пока не возникает общее правило — выносите в домен.
- Бизнес-инварианты нужно держать в доменной модели, иначе они разбредутся по срезам.
- Слишком много «общего» вновь создаёт слои.
- Требует договорённости о структуре папок и именовании.

## Практика

1. Перенесите два use case с раскладки по слоям на срезы.
2. Используйте Dapper для чтения в срезе списка и EF для записи.
3. Оцените, сколько файлов меняется при добавлении поля.

## Вопросы с ответами

> [!question]- Чем vertical slice отличается от слоистой?
> Группировка по фичам, а не по техническим слоям; минимум разделяемых абстракций между срезами.

> [!question]- Не приводит ли это к дублированию?
> Допустимое дублирование дешевле неверной общей абстракции; общее выносят после осознания.

## Связанные темы

- [[N:3ea331048679814f8a95f37f80928498]]
- [[N:3ea331048679812facbfd65b88f19fcb]]
