---
type: topic
domain: backend
stage: 7
section: "7.3"
order: 4
status: todo
level: senior
notion_id: 3ea33104867981c5a9dbc796f665fb11
tags: [domain/backend, stage/7, level/senior, topic/reliability, topic/idempotency, priority/should]
reviewed:
next_review:
priority: should
time: 3
---

# Идемпотентность операций и дедупликация

↑ [[BE 7.3 Надёжность и отказоустойчивость|7.3 Надёжность и отказоустойчивость]] · ← [[BE 7.3.3 Polly и Microsoft.Extensions.Resilience|Предыдущая]] · → [[BE 7.3.5 Rate limiting и backpressure|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: senior</span></div>
<!-- meta:end -->










































> [!info] Зачем это на собесе
> Идемпотентность — условие безопасных ретраев и at-least-once доставки.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

Операция **идемпотентна**, если повтор даёт тот же результат, что и одно выполнение.

Способы:

| Способ | Пример |
|---|---|
| Естественная идемпотентность | `PUT`, `DELETE`, `SET status = 'paid'`, upsert |
| Ключ идемпотентности | заголовок `Idempotency-Key` (см. [[N:3ea331048679816dbce2c367c9bda11e]]) |
| Дедупликация по ID сообщения | таблица Inbox обработанных сообщений |
| Условные обновления | `UPDATE ... WHERE version = @v` (оптимистичная блокировка) |
| Уникальные ограничения | unique-индекс на бизнес-ключ |
| Конечный автомат | переход состояния допустим один раз (`created → paid`) |

```sql
INSERT INTO payments (id, order_id, amount) VALUES (@id, @order, @amount)
ON CONFLICT (id) DO NOTHING;         -- повтор с тем же id ничего не меняет

UPDATE orders SET status = 'paid' WHERE id = @id AND status = 'created';   -- повторная оплата игнорируется
```

Идемпотентный потребитель:

```csharp
await using var tx = await db.Database.BeginTransactionAsync(ct);
if (await db.Processed.AnyAsync(x => x.MessageId == msg.Id, ct)) return;
await ApplyAsync(msg, ct);
db.Processed.Add(new Processed(msg.Id));
await db.SaveChangesAsync(ct); await tx.CommitAsync(ct);
```

## Нюансы и подводные камни

- Проверка «есть ли уже» и запись должны быть атомарными (unique + транзакция), иначе гонка.
- Внешние побочные эффекты (письмо, платёж провайдеру) — только с ключом идемпотентности провайдера или через outbox.
- Срок хранения ключей ограничен — определите окно дедупликации.
- Идемпотентный ответ должен возвращать тот же результат/статус.

## Практика

1. Сделайте оплату идемпотентной через unique-индекс и конечный автомат.
2. Реализуйте Inbox для потребителя очереди.
3. Проверьте гонку двумя одновременными запросами с одним ключом.

## Вопросы с ответами

> [!question]- Как сделать POST идемпотентным?
> Ключ идемпотентности от клиента и хранение результата по ключу с уникальным ограничением.

> [!question]- Почему проверки «сначала SELECT, потом INSERT» недостаточно?
> Между ними возможна гонка; нужен unique-индекс и обработка нарушения.

## Связанные темы

- [[N:3ea331048679811aa59dd143aea4d4c6]]
- [[N:3ea331048679813d96e3e4f7c0faab14]]
