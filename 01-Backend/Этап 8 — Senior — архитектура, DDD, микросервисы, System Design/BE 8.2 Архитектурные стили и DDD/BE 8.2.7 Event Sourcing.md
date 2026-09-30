---
type: topic
domain: backend
stage: 8
section: "8.2"
order: 7
status: todo
level: senior
notion_id: 3ea33104867981dcb475d2f8f1b52ab6
tags: [domain/backend, stage/8, level/senior, topic/architecture, topic/event-sourcing, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Event Sourcing

↑ [[BE 8.2 Архитектурные стили и DDD|8.2 Архитектурные стили и DDD]] · ← [[BE 8.2.6 DDD — тактический — entity, value object, aggregate, domain events|Предыдущая]] · → [[BE 8.2.8 Модульный монолит|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: senior</span></div>
<!-- meta:end -->







> [!info] Зачем это на собесе
> Спрашивают, когда это оправдано и какие сложности несёт.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

Вместо хранения текущего состояния сохраняется **последовательность событий**, изменивших его. Состояние — результат их проигрывания.

```text
OrderCreated → ItemAdded → ItemAdded → OrderPaid → OrderShipped
                                  ↓ replay
                           состояние Order = Shipped, items = 2
```

```csharp
public abstract record OrderEvent(Guid OrderId, DateTimeOffset At);
public record ItemAdded(Guid OrderId, DateTimeOffset At, Sku Sku, int Qty) : OrderEvent(OrderId, At);
public record OrderPaid(Guid OrderId, DateTimeOffset At) : OrderEvent(OrderId, At);

public class Order
{
    public Status Status { get; private set; }
    public static Order Rehydrate(IEnumerable<OrderEvent> history) { var o = new Order(); foreach (var e in history) o.Apply(e); return o; }
    private void Apply(OrderEvent e) { switch (e) { case OrderPaid: Status = Status.Paid; break; /* ... */ } }
}
```

| Плюсы | Минусы |
|---|---|
| полный аудит и история | сложность и порог входа |
| можно восстановить состояние на любой момент | эволюция схемы событий (версионирование, upcasting) |
| естественная основа для проекций и интеграции | eventual consistency проекций |
| отладка «что произошло» | запросы по текущему состоянию — через проекции |
| | удаление персональных данных (GDPR): шифрование ключами, crypto-shredding |

Техники: **snapshots** (ускорение загрузки), **проекции/read-модели**, оптимистичная блокировка по версии потока, хранилища: EventStoreDB, Marten (PostgreSQL), собственная таблица `events`.

Когда оправдан: строгий аудит (финансы), сложные доменные процессы с историей, потребность в темпоральных запросах. В остальных случаях — избыточен.

## Нюансы и подводные камни

- Изменение формата событий нельзя выполнить «миграцией на месте»: события неизменяемы.
- «Плохое» событие не удаляют, а компенсируют новым.
- Проекции нужно уметь перестраивать (replay).
- Не путайте с журналом изменений (audit log) — он проще и часто достаточен.
- Event Sourcing ≠ CQRS ≠ шина событий.

## Практика

1. Смоделируйте счёт/заказ через события и восстановите состояние.
2. Реализуйте проекцию текущих остатков и её перестроение.
3. Используйте Marten для потока событий в PostgreSQL.

## Вопросы с ответами

> [!question]- Зачем Event Sourcing?
> Полная история изменений, восстановление состояния на любой момент и удобная основа для проекций и интеграций.

> [!question]- Как менять схему событий?
> Версионированием и upcasting (преобразованием старых событий при чтении).

## Связанные темы

- [[N:3ea33104867981fdacffc2220726e99c]]
- [[N:3ea33104867981e4b04ddaf9890413ce]]
