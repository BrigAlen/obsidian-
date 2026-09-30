---
type: topic
domain: backend
stage: 5
section: "5.4"
order: 7
status: todo
level: middle
notion_id: 3ea3310486798136adb0e4fbd93dd754
tags: [domain/backend, stage/5, level/middle, topic/messaging, topic/reliability, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Гарантии доставки: at-most-once, at-least-once, exactly-once

↑ [[BE 5.4 Очереди и брокеры — Kafka, RabbitMQ|5.4 Очереди и брокеры: Kafka, RabbitMQ]] · ← [[BE 5.4.6 Kafka или RabbitMQ — когда что|Предыдущая]] · → [[BE 5.4.8 Transactional Outbox и Inbox, идемпотентные консьюмеры|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->












































> [!info] Зачем это на собесе
> «Что значит exactly-once?» — ловушка: на практике это at-least-once + идемпотентность.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

| Гарантия | Поведение | Как достигается | Риск |
|---|---|---|---|
| At-most-once | доставлено 0 или 1 раз | не повторять; коммит до обработки | потеря сообщений |
| At-least-once | доставлено ≥1 раз | повторять до подтверждения; коммит после обработки | дубли |
| Exactly-once | ровно 1 эффект | at-least-once + идемпотентная обработка/транзакции | сложность |

Распределённая система не может отличить «сообщение потеряно» от «ответ потерян», поэтому настоящая доставка «ровно один раз» на уровне сети невозможна. Достижим **эффект** «ровно один раз»: дубли приходят, но повторная обработка не меняет результат.

Способы получить exactly-once эффект:

- **Идемпотентный потребитель**: дедупликация по id сообщения (Inbox) или естественно идемпотентные операции (`upsert`, `set status = paid`).
- **Транзакции Kafka** (consume-transform-produce внутри Kafka).
- **Transactional outbox** для надёжной публикации (см. [[N:3ea331048679819a8d47e8140fca5d08]]).
- **Оптимистическая проверка версии** состояния.

```csharp
// Идемпотентная обработка: таблица обработанных сообщений в той же транзакции, что и эффект
await using var tx = await db.Database.BeginTransactionAsync(ct);
if (await db.Processed.AnyAsync(p => p.MessageId == msg.Id, ct)) return;   // дубль
await ApplyAsync(msg, ct);
db.Processed.Add(new Processed(msg.Id));
await db.SaveChangesAsync(ct);
await tx.CommitAsync(ct);
```

## Нюансы и подводные камни

- «Exactly-once» в Kafka работает в границах Kafka; внешние эффекты (email, платёж) требуют идемпотентности.
- Дедупликация по id нуждается в TTL и хранилище.
- Порядок и повторы: старое сообщение может прийти после нового — проверяйте версию.
- Побочные эффекты (письма) отправляйте через outbox или идемпотентный ключ провайдера.

## Практика

1. Реализуйте Inbox-таблицу и проверьте дубль.
2. Сымитируйте падение после обработки, но до коммита offset.
3. Сделайте обработчик естественно идемпотентным через upsert.

## Вопросы с ответами

> [!question]- Возможна ли доставка exactly-once?
> На уровне сети нет; достигается эффект exactly-once через at-least-once и идемпотентную обработку.

> [!question]- Почему at-least-once — выбор по умолчанию?
> Потеря данных обычно хуже дубля, а дубли снимаются идемпотентностью.

## Связанные темы

- [[N:3ea331048679819392dadf05bb41e310]]
- [[N:3ea331048679819a8d47e8140fca5d08]]
