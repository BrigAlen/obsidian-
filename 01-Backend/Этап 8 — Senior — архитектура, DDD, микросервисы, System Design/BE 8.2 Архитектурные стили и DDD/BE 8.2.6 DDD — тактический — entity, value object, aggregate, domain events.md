---
type: topic
domain: backend
stage: 8
section: "8.2"
order: 6
status: todo
level: senior
notion_id: 3ea33104867981fdacffc2220726e99c
tags: [domain/backend, stage/8, level/senior, topic/architecture, topic/ddd, priority/must]
reviewed:
next_review:
priority: must
time: 4
---

# DDD: тактический — entity, value object, aggregate, domain events

↑ [[BE 8.2 Архитектурные стили и DDD|8.2 Архитектурные стили и DDD]] · ← [[BE 8.2.5 DDD — стратегический — bounded context, ubiquitous language, context map|Предыдущая]] · → [[BE 8.2.7 Event Sourcing|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~4 мин чтения</span><span class="chip">Уровень: senior</span></div>
<!-- meta:end -->

































> [!info] Зачем это на собесе
> Практические строительные блоки DDD в C#: агрегат, инварианты, границы транзакции.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

| Блок | Смысл |
|---|---|
| Entity | объект с идентичностью, живущий во времени (`Order`) |
| Value Object | неизменяемый объект без идентичности, сравнивается по значению (`Money`, `Address`, `Email`) |
| Aggregate | кластер объектов с общими инвариантами и одним корнем (aggregate root) |
| Repository | загрузка/сохранение агрегата целиком |
| Domain Service | логика, не принадлежащая одной сущности |
| Domain Event | факт, произошедший в домене (`OrderPaid`) |
| Factory | сложное создание агрегата |

```csharp
public readonly record struct Money(decimal Amount, string Currency)
{
    public static Money Zero(string c) => new(0, c);
    public Money Add(Money o) => o.Currency == Currency ? this with { Amount = Amount + o.Amount } : throw new InvalidOperationException("currency mismatch");
}

public class Order                     // aggregate root
{
    private readonly List<OrderItem> _items = [];
    private readonly List<IDomainEvent> _events = [];
    public Guid Id { get; } = Guid.NewGuid();
    public Status Status { get; private set; } = Status.New;
    public IReadOnlyList<OrderItem> Items => _items;
    public IReadOnlyList<IDomainEvent> Events => _events;

    public void AddItem(Sku sku, int qty, Money price)
    {
        if (Status != Status.New) throw new DomainException("Нельзя менять оплаченный заказ");   // инвариант защищён корнем
        if (qty <= 0) throw new DomainException("Количество должно быть положительным");
        _items.Add(new OrderItem(sku, qty, price));
    }

    public void Pay()
    {
        if (_items.Count == 0) throw new DomainException("Пустой заказ");
        Status = Status.Paid;
        _events.Add(new OrderPaid(Id));
    }
}
```

Правила агрегата:

- Изменения только через корень; снаружи нет прямого доступа к внутренним сущностям.
- Транзакция = один агрегат; между агрегатами — ссылки по идентификатору и eventual consistency (доменные события).
- Агрегат небольшой: маленькие агрегаты лучше масштабируются и меньше конфликтуют.

Доменные события публикуются после сохранения (через outbox) и запускают реакции в других агрегатах/контекстах.

## Нюансы и подводные камни

- Анемичная модель: публичные сеттеры и логика в сервисах.
- Гигантские агрегаты (заказ + клиент + товары) — блокировки и медленная загрузка.
- Value Object как `record` удобен; EF Core умеет owned types/ComplexProperty.
- Исключения для нарушения инварианта vs Result — определите единый стиль.
- Не тащите «DDD-лайт» ради терминов без пользы.

## Практика

1. Смоделируйте `Order` с инвариантами и value objects.
2. Реализуйте публикацию доменных событий через outbox.
3. Найдите в проекте агрегат, который слишком велик, и разделите.

## Вопросы с ответами

> [!question]- Что такое aggregate root?
> Единственная точка входа в агрегат, отвечающая за сохранение инвариантов всего кластера объектов.

> [!question]- Entity или value object?
> Если важна идентичность — entity; если важно только значение — неизменяемый value object.

> [!question]- Почему транзакция ограничена одним агрегатом?
> Так проще масштабировать и избегать блокировок; консистентность между агрегатами — событийная.

## Связанные темы

- [[N:3ea331048679811b9ea3ddea76b7fa24]]
- [[N:3ea33104867981dcb475d2f8f1b52ab6]]
