---
type: topic
domain: backend
stage: 5
section: "5.4"
order: 4
status: todo
level: middle
notion_id: 3ea3310486798150bf0bdb0160fa893a
tags: [domain/backend, stage/5, level/middle, topic/messaging, topic/kafka, topic/dotnet, priority/must]
reviewed:
next_review:
priority: must
time: 4
---

# Kafka в .NET: Confluent.Kafka, сериализация, Schema Registry

↑ [[BE 5.4 Очереди и брокеры — Kafka, RabbitMQ|5.4 Очереди и брокеры: Kafka, RabbitMQ]] · ← [[BE 5.4.3 Kafka — producer, acks, идемпотентность, порядок сообщений|Предыдущая]] · → [[BE 5.4.5 RabbitMQ — exchanges, queues, routing, ack|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~4 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->









































> [!info] Зачем это на собесе
> Как правильно написать потребителя: коммит offset, обработка ошибок, схемы сообщений.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

Клиент `Confluent.Kafka` — обёртка над librdkafka.

```csharp
public class OrdersConsumer(IServiceScopeFactory scopes, ILogger<OrdersConsumer> log) : BackgroundService
{
    protected override Task ExecuteAsync(CancellationToken ct) => Task.Run(async () =>
    {
        var cfg = new ConsumerConfig
        {
            BootstrapServers = "kafka:9092",
            GroupId = "billing",
            EnableAutoCommit = false,               // коммитим вручную после обработки
            AutoOffsetReset = AutoOffsetReset.Earliest,
        };
        using var consumer = new ConsumerBuilder<string, string>(cfg).Build();
        consumer.Subscribe("orders");
        try
        {
            while (!ct.IsCancellationRequested)
            {
                var cr = consumer.Consume(ct);
                using var scope = scopes.CreateScope();
                await scope.ServiceProvider.GetRequiredService<IOrderHandler>().HandleAsync(cr.Message.Value, ct);
                consumer.Commit(cr);                // at-least-once
            }
        }
        catch (OperationCanceledException) { }
        finally { consumer.Close(); }               // корректный выход из группы
    }, ct);
}
```

### Сериализация и Schema Registry

| Формат | Плюсы |
|---|---|
| JSON | просто, читаемо, нет контроля схемы |
| Avro / Protobuf + Schema Registry | компактно, схема хранится в реестре, проверка совместимости |

Schema Registry задаёт режимы совместимости (BACKWARD, FORWARD, FULL): изменение схемы, нарушающее правила, будет отклонено при регистрации.

## Нюансы и подводные камни

- `Consume` блокирует поток: запускайте в отдельной задаче/потоке.
- Автокоммит до окончания обработки приводит к потере сообщения при падении.
- Долгая обработка → выход из группы по `max.poll.interval.ms` и rebalance.
- Всегда `Close()` при остановке, иначе группа ждёт таймаут сессии.
- Не обрабатывайте параллельно сообщения одной партиции без учёта порядка.

## Практика

1. Напишите потребителя с ручным коммитом и корректной остановкой.
2. Добавьте Schema Registry и Avro/Protobuf.
3. Сымитируйте падение обработчика и проверьте повторную обработку.

## Вопросы с ответами

> [!question]- Почему отключают автокоммит?
> Чтобы коммитить offset только после успешной обработки и не терять сообщения.

> [!question]- Зачем Schema Registry?
> Централизованное хранение схем и проверка совместимости при их эволюции.

> [!question]- Что будет при долгой обработке?
> Потребитель может быть исключён из группы (`max.poll.interval.ms`), начнётся rebalance и сообщение обработается повторно.

## Связанные темы

- [[N:3ea33104867981b59f88f3e0f044e0fc]]
- [[N:3ea33104867981bea3c6e8b07804ac82]]
