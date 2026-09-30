---
type: section
domain: backend
stage: 5
section: "5.4"
order: 4
status: todo
level: middle
notion_id: 3ea33104867981d6b37bde0cb5e2ceea
tags: [domain/backend, stage/5, kind/section]
---

# 5.4 Очереди и брокеры: Kafka, RabbitMQ

↑ [[BE Этап 5 · Интеграции — REST, gRPC, GraphQL, Kafka и очереди, внешние API|Этап 5]]

Асинхронный обмен: Kafka и RabbitMQ, гарантии доставки, outbox/inbox, DLQ и MassTransit.

## Темы
<!-- toc:start -->
**Итого:** 11 тем · ~40 мин · готово 0 из 11

<div class="bar"><span style="width:0%"></span></div>

| # | Тема | Приоритет | Чтение | Статус |
|---|---|---|---|---|
| 1 | [[BE 5.4.1 Зачем асинхронный обмен — очереди, pub-sub, события\|Зачем асинхронный обмен: очереди, pub∕sub, события]] | <span class="badge must">Обязательно</span> | 3 мин | <span class="badge todo">Не начато</span> |
| 2 | [[BE 5.4.2 Kafka — топики, партиции, offset, consumer groups\|Kafka: топики, партиции, offset, consumer groups]] | <span class="badge must">Обязательно</span> | 3 мин | <span class="badge todo">Не начато</span> |
| 3 | [[BE 5.4.3 Kafka — producer, acks, идемпотентность, порядок сообщений\|Kafka: producer, acks, идемпотентность, порядок сообщений]] | <span class="badge must">Обязательно</span> | 3 мин | <span class="badge todo">Не начато</span> |
| 4 | [[BE 5.4.4 Kafka в .NET — Confluent.Kafka, сериализация, Schema Registry\|Kafka в .NET: Confluent.Kafka, сериализация, Schema Registry]] | <span class="badge must">Обязательно</span> | 4 мин | <span class="badge todo">Не начато</span> |
| 5 | [[BE 5.4.5 RabbitMQ — exchanges, queues, routing, ack\|RabbitMQ: exchanges, queues, routing, ack]] | <span class="badge must">Обязательно</span> | 3 мин | <span class="badge todo">Не начато</span> |
| 6 | [[BE 5.4.6 Kafka или RabbitMQ — когда что\|Kafka или RabbitMQ: когда что]] | <span class="badge must">Обязательно</span> | 3 мин | <span class="badge todo">Не начато</span> |
| 7 | [[BE 5.4.7 Гарантии доставки — at-most-once, at-least-once, exactly-once\|Гарантии доставки: at-most-once, at-least-once, exactly-once]] | <span class="badge must">Обязательно</span> | 3 мин | <span class="badge todo">Не начато</span> |
| 8 | [[BE 5.4.8 Transactional Outbox и Inbox, идемпотентные консьюмеры\|Transactional Outbox и Inbox, идемпотентные консьюмеры]] | <span class="badge must">Обязательно</span> | 3 мин | <span class="badge todo">Не начато</span> |
| 9 | [[BE 5.4.9 Dead letter queue, retry, poison messages\|Dead letter queue, retry, poison messages]] | <span class="badge must">Обязательно</span> | 3 мин | <span class="badge todo">Не начато</span> |
| 10 | [[BE 5.4.10 MassTransit и абстракции над брокерами\|MassTransit и абстракции над брокерами]] | <span class="badge must">Обязательно</span> | 3 мин | <span class="badge todo">Не начато</span> |
| 11 | [[BE 5.4.11 Альтернативы Kafka и RabbitMQ — NATS JetStream, Redpanda, Pulsar и облачные очереди\|Альтернативы Kafka и RabbitMQ: NATS JetStream, Redpanda, Pulsar и облачные очереди]] | <span class="badge should">Желательно</span> | 9 мин | <span class="badge todo">Не начато</span> |
<!-- toc:end -->

## Чек-лист раздела
- [ ] Прочитал все темы
- [ ] Могу объяснить каждую тему за 2 минуты вслух
