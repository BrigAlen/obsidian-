---
type: topic
domain: backend
stage: 5
section: "5.7"
order: 4
status: todo
level: middle
notion_id: 3ea3310486798180b86aeb7a4f28a1d4
tags: [domain/backend, stage/5, level/middle, topic/testing, topic/kafka, topic/messaging, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Тестирование консьюмеров Kafka и очередей

↑ [[BE 5.7 Тестирование интеграций|5.7 Тестирование интеграций]] · ← [[BE 5.7.3 Тестирование gRPC-сервисов|Предыдущая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->


























> [!info] Зачем это на собесе
> Асинхронный код тестировать сложнее: как не получить flaky-тесты и проверить идемпотентность.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

Разделяйте **обработчик** (логика) и **инфраструктуру** (клиент брокера).

| Уровень | Что проверять | Как |
|---|---|---|
| Unit | логика обработчика сообщений | вызвать `Handle(message)` с fake-зависимостями |
| Integration | обработка через настоящий брокер | Testcontainers (Kafka/RabbitMQ) |
| Библиотека | MassTransit | `AddMassTransitTestHarness`, `harness.Consumed.Any<T>()` |
| Контракт | формат сообщений | схемы/Schema Registry |

```csharp
[Fact]
public async Task Consumer_is_idempotent_on_duplicate_message()
{
    var handler = new OrderPaidHandler(db, clock);
    var msg = new OrderPaid(orderId, messageId: Guid.NewGuid());

    await handler.HandleAsync(msg);
    await handler.HandleAsync(msg);    // дубль

    Assert.Equal(1, await db.Payments.CountAsync(p => p.OrderId == orderId));
}
```

Интеграционный тест с Kafka:

```csharp
await using var kafka = new KafkaBuilder().WithImage("confluentinc/cp-kafka:7.6.0").Build();
await kafka.StartAsync();
await producer.ProduceAsync("orders", new Message<string, string> { Key = id, Value = json });

// ждём результата с таймаутом, а не Task.Delay
await Eventually.AssertAsync(async () => Assert.True(await db.Orders.AnyAsync(o => o.Id == id && o.Status == Status.Paid)),
                            timeout: TimeSpan.FromSeconds(15));
```

Сценарии, которые нужно проверять:

- Дубль сообщения и повторная доставка.
- Сообщение не по порядку.
- Невалидное сообщение → DLQ, поток не блокируется.
- Временная ошибка → ретрай с задержкой.
- Остановка потребителя: offset коммитится после обработки.

## Нюансы и подводные камни

- `Task.Delay(…)` в тестах даёт flaky: используйте опрос с таймаутом (`Eventually`).
- Каждому тесту — уникальный топик/группа, чтобы не мешали друг другу.
- Kafka в контейнере стартует медленно: один контейнер на коллекцию тестов.
- Не проверяйте внутреннюю механику клиентской библиотеки: проверяйте результат обработки.

## Практика

1. Напишите unit-тест идемпотентности обработчика.
2. Поднимите Kafka через Testcontainers и проверьте end-to-end обработку.
3. Проверьте попадание «ядовитого» сообщения в DLQ.

## Вопросы с ответами

> [!question]- Как избежать flaky-тестов с брокером?
> Опрашивать состояние с таймаутом вместо фиксированных задержек, использовать уникальные топики и один контейнер на набор тестов.

> [!question]- Что обязательно проверить в потребителе?
> Идемпотентность, обработку невалидных и повторных сообщений, корректный коммит offset.

## Связанные темы

- [[N:3ea3310486798122a480fdb4a13a418d]]
- [[N:3ea33104867981dca042d2475ad3bdfc]]
