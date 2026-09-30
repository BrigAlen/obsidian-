---
type: topic
domain: backend
stage: 5
section: "5.4"
order: 8
status: todo
level: middle
notion_id: 3ea331048679819a8d47e8140fca5d08
tags: [domain/backend, stage/5, level/middle, topic/messaging, topic/reliability, topic/patterns, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Transactional Outbox и Inbox, идемпотентные консьюмеры

↑ [[BE 5.4 Очереди и брокеры — Kafka, RabbitMQ|5.4 Очереди и брокеры: Kafka, RabbitMQ]] · ← [[BE 5.4.7 Гарантии доставки — at-most-once, at-least-once, exactly-once|Предыдущая]] · → [[BE 5.4.9 Dead letter queue, retry, poison messages|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->















> [!info] Зачем это на собесе
> Стандартный паттерн надёжной публикации событий: «сохранили в БД, но не отправили» — как избежать.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

**Проблема dual write**: сервис сохраняет заказ в БД и публикует событие в брокер — это две системы без общей транзакции. Падение между шагами → заказ есть, события нет (или наоборот).

**Transactional Outbox**: событие записывается в таблицу `outbox` **в той же транзакции**, что и бизнес-данные. Отдельный процесс (relay) читает таблицу и публикует в брокер, помечая отправленное.

```mermaid
sequenceDiagram
  participant S as Сервис
  participant DB as БД
  participant R as Relay
  participant K as Kafka
  S->>DB: BEGIN; insert order; insert outbox; COMMIT
  R->>DB: выбрать неотправленные
  R->>K: publish
  R->>DB: пометить отправленными
```

```csharp
await using var tx = await db.Database.BeginTransactionAsync(ct);
db.Orders.Add(order);
db.Outbox.Add(new OutboxMessage(Guid.NewGuid(), "OrderCreated", JsonSerializer.Serialize(evt)));
await db.SaveChangesAsync(ct);
await tx.CommitAsync(ct);
```

Relay: фоновый сервис с запросом `select ... for update skip locked` либо CDC (Debezium читает WAL и публикует в Kafka).

**Inbox** — зеркальный паттерн на стороне потребителя: таблица обработанных `message_id` + эффект в одной транзакции (см. [[N:3ea3310486798136adb0e4fbd93dd754]]).

| Вариант relay | Плюсы | Минусы |
|---|---|---|
| Polling + skip locked | просто | задержка, нагрузка на БД |
| CDC (Debezium) | почти в реальном времени, без запросов | инфраструктура |
| MassTransit/Wolverine outbox | готовое решение | зависимость от библиотеки |

## Нюансы и подводные камни

- Relay даёт at-least-once: дубли возможны, потребители обязаны быть идемпотентными.
- Порядок событий одного агрегата: сортируйте по sequence/времени создания.
- Очищайте обработанные записи (архив/TTL), иначе таблица разрастается.
- Несколько инстансов relay должны не мешать друг другу (`skip locked`).
- Не публикуйте в брокер внутри транзакции БД: сначала коммит.

## Практика

1. Реализуйте outbox и relay на `skip locked`.
2. Сымитируйте падение после коммита и убедитесь, что событие уходит позже.
3. Добавьте Inbox в потребителе.

## Вопросы с ответами

> [!question]- Какую проблему решает Outbox?
> Гарантирует, что событие будет опубликовано тогда и только тогда, когда транзакция с бизнес-данными зафиксирована.

> [!question]- Даёт ли Outbox exactly-once?
> Нет, это at-least-once; нужна идемпотентность потребителя (Inbox).

> [!question]- Polling или CDC?
> Polling проще и достаточен на средней нагрузке; CDC — минимальная задержка и нагрузка при высоких объёмах.

## Связанные темы

- [[N:3ea3310486798136adb0e4fbd93dd754]]
- [[N:3ea33104867981dca042d2475ad3bdfc]]
