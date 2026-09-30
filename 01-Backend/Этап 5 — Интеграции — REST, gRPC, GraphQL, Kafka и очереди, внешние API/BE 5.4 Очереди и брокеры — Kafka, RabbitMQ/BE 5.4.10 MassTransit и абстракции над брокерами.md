---
type: topic
domain: backend
stage: 5
section: "5.4"
order: 10
status: todo
level: middle
notion_id: 3ea33104867981b7972aceb8b1dde4cf
tags: [domain/backend, stage/5, level/middle, topic/messaging, topic/dotnet, topic/masstransit, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# MassTransit и абстракции над брокерами

↑ [[BE 5.4 Очереди и брокеры — Kafka, RabbitMQ|5.4 Очереди и брокеры: Kafka, RabbitMQ]] · ← [[BE 5.4.9 Dead letter queue, retry, poison messages|Предыдущая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->







> [!info] Зачем это на собесе
> Какие готовые библиотеки используют вместо ручной работы с брокером и чем они хороши/плохи.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

MassTransit (и аналоги Wolverine, NServiceBus, Rebus, Brighter) — .NET-абстракция над брокерами (RabbitMQ, Kafka, Azure Service Bus, SQS, in-memory): сообщения, консьюмеры, retry, outbox, саги.

```csharp
builder.Services.AddMassTransit(x =>
{
    x.AddConsumer<OrderPaidConsumer>();
    x.AddEntityFrameworkOutbox<AppDbContext>(o => { o.UsePostgres(); o.UseBusOutbox(); });   // transactional outbox

    x.UsingRabbitMq((ctx, cfg) =>
    {
        cfg.Host("rabbit");
        cfg.UseMessageRetry(r => r.Exponential(5, TimeSpan.FromSeconds(1), TimeSpan.FromMinutes(1), TimeSpan.FromSeconds(5)));
        cfg.ConfigureEndpoints(ctx);
    });
});

public record OrderPaid(Guid OrderId);

public class OrderPaidConsumer : IConsumer<OrderPaid>
{
    public async Task Consume(ConsumeContext<OrderPaid> ctx) { /* ... */ }
}

await publishEndpoint.Publish(new OrderPaid(id), ct);
```

| Возможность | Что даёт |
|---|---|
| Retry, circuit breaker, rate limit | устойчивость без ручного кода |
| Outbox/Inbox | надёжная доставка и дедупликация |
| Sagas / state machines | долгие бизнес-процессы, оркестрация |
| Request/response, scheduling | надстройки поверх брокера |
| Тестовый harness | `AddMassTransitTestHarness` для тестов |

Плюсы: единый API, готовые паттерны. Минусы: абстракция скрывает специфику брокера (партиции Kafka ≠ очереди RabbitMQ), версия v9+ стала коммерческой (лицензия для организаций) — обратите внимание на условия и альтернативы (Wolverine, Rebus).

## Нюансы и подводные камни

- Универсальная абстракция не даёт использовать всё богатство брокера; знайте модель под капотом.
- Не проектируйте топологию «по умолчанию»: проверьте, какие exchange/очереди создаёт библиотека.
- Сообщения — контракты: версионируйте типы и пространства имён.
- Проверьте лицензирование библиотек до внедрения.

## Практика

1. Подключите MassTransit с RabbitMQ и outbox на EF Core.
2. Реализуйте сагу «заказ → оплата → доставка».
3. Напишите тест на consumer с `TestHarness`.

## Вопросы с ответами

> [!question]- Зачем MassTransit?
> Готовые retry, outbox, саги и единый API вместо ручной работы с клиентом брокера.

> [!question]- Какие минусы у таких библиотек?
> Скрытая топология, зависимость и лицензия; требуется знание брокера под капотом.

## Связанные темы

- [[N:3ea33104867981dca042d2475ad3bdfc]]
- [[N:3ea33104867981e6845fee5306c0eb22]]
