---
type: topic
domain: backend
stage: 5
section: "5.4"
order: 3
status: todo
level: middle
notion_id: 3ea33104867981b59f88f3e0f044e0fc
tags: [domain/backend, stage/5, level/middle, topic/messaging, topic/kafka, topic/reliability, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Kafka: producer, acks, идемпотентность, порядок сообщений

↑ [[BE 5.4 Очереди и брокеры — Kafka, RabbitMQ|5.4 Очереди и брокеры: Kafka, RabbitMQ]] · ← [[BE 5.4.2 Kafka — топики, партиции, offset, consumer groups|Предыдущая]] · → [[BE 5.4.4 Kafka в .NET — Confluent.Kafka, сериализация, Schema Registry|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->


















> [!info] Зачем это на собесе
> Как не потерять и не продублировать сообщение при отправке.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

| Параметр | Смысл |
|---|---|
| `acks=0` | не ждать подтверждения (возможна потеря) |
| `acks=1` | подтверждает лидер (потеря при падении лидера до репликации) |
| `acks=all` | подтверждают все in-sync реплики (надёжно) |
| `min.insync.replicas` | минимум реплик для успешной записи |
| `enable.idempotence=true` | брокер отбрасывает дубли ретраев продюсера (сессия + sequence) |
| `retries`, `delivery.timeout.ms` | повторы и общий срок доставки |
| `linger.ms`, `batch.size`, `compression.type` | батчинг и пропускная способность |
| `max.in.flight.requests.per.connection` | параллельные неподтверждённые запросы (≤5 при идемпотентности сохраняют порядок) |

Надёжная конфигурация: `acks=all` + `enable.idempotence=true` + `min.insync.replicas=2` при `replication.factor=3`.

```csharp
var config = new ProducerConfig
{
    BootstrapServers = "kafka:9092",
    Acks = Acks.All,
    EnableIdempotence = true,
    LingerMs = 5,
    CompressionType = CompressionType.Zstd,
};
using var producer = new ProducerBuilder<string, string>(config).Build();
var result = await producer.ProduceAsync("orders", new Message<string, string> { Key = orderId, Value = json }, ct);
```

### Транзакции

Транзакционный продюсер атомарно пишет в несколько топиков/партиций и коммитит offset потребителя (**exactly-once** в связке consume-transform-produce внутри Kafka).

## Нюансы и подводные камни

- Идемпотентность продюсера защищает только от дублей в рамках одной сессии продюсера, а не от повторной публикации из приложения.
- Порядок при ретраях теряется без идемпотентности и с большим `max.in.flight`.
- Ключ определяет партицию; смена ключа ломает порядок.
- Всегда обрабатывайте результат `ProduceAsync` (ошибка не молчит).
- Слишком большие сообщения (по умолчанию ~1 МБ): передавайте ссылку на объект в хранилище.

## Практика

1. Сымитируйте падение брокера при `acks=1` и `acks=all`.
2. Включите идемпотентность и проверьте отсутствие дублей при ретраях.
3. Настройте компрессию и батчинг, замерьте throughput.

## Вопросы с ответами

> [!question]- Какие настройки нужны для «не потерять сообщение»?
> `acks=all`, `min.insync.replicas>=2`, `replication.factor>=3`, идемпотентный продюсер.

> [!question]- Что делает enable.idempotence?
> Брокер дедуплицирует повторные отправки одной записи по producer id и sequence number.

> [!question]- Как сохранить порядок событий сущности?
> Использовать ключ сущности (одна партиция) и не ломать порядок ретраями.

## Связанные темы

- [[N:3ea3310486798108ad25de6f5fe24ad2]]
- [[N:3ea3310486798150bf0bdb0160fa893a]]
