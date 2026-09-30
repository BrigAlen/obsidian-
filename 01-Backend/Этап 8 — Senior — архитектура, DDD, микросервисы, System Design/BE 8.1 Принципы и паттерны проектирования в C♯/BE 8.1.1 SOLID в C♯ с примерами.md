---
type: topic
domain: backend
stage: 8
section: "8.1"
order: 1
status: todo
level: senior
notion_id: 3ea331048679816f9f1cf6add2d19fc4
tags: [domain/backend, stage/8, level/senior, topic/design, topic/solid, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# SOLID в C# с примерами

↑ [[BE 8.1 Принципы и паттерны проектирования в C♯|8.1 Принципы и паттерны проектирования в C♯]] · → [[BE 8.1.2 DRY, KISS, YAGNI, GRASP, Law of Demeter|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: senior</span></div>
<!-- meta:end -->





> [!info] Зачем это на собесе
> SOLID спрашивают всегда. Нужно приводить пример нарушения и исправления, а не заучивать определения.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

| Принцип | Суть | Признак нарушения |
|---|---|---|
| **S** — Single Responsibility | у класса одна причина для изменения | «God class», сервис на 2000 строк |
| **O** — Open/Closed | открыт для расширения, закрыт для изменения | `switch` по типу, который растёт с каждой фичей |
| **L** — Liskov Substitution | подтип можно подставить вместо базового без нарушения поведения | `NotSupportedException` в наследнике, усиление предусловий |
| **I** — Interface Segregation | много узких интерфейсов лучше одного широкого | пустые реализации методов |
| **D** — Dependency Inversion | зависеть от абстракций, а не от реализаций | `new SqlRepo()` внутри бизнес-класса |

```csharp
// OCP: расширяем стратегиями, не правя калькулятор
public interface IDiscount { bool AppliesTo(Order o); decimal Apply(Order o); }
public class PriceCalculator(IEnumerable<IDiscount> discounts)
{
    public decimal Total(Order o) => o.Subtotal - discounts.Where(d => d.AppliesTo(o)).Sum(d => d.Apply(o));
}

// LSP: нарушение
class Bird { public virtual void Fly() { } }
class Penguin : Bird { public override void Fly() => throw new NotSupportedException(); }   // подтип ломает контракт

// ISP: узкие интерфейсы
public interface IOrderReader { Task<Order?> GetAsync(Guid id); }
public interface IOrderWriter { Task AddAsync(Order o); }

// DIP: бизнес-логика зависит от абстракции; реализация подключается в корне композиции
public class OrderService(IOrderWriter writer, IClock clock) { }
```

SRP — не «один метод», а «одна причина для изменения» (один актор-владелец требований). DIP ≠ DI: DIP — принцип направления зависимостей, DI — техника внедрения.

## Нюансы и подводные камни

- Слепое следование SOLID даёт лишние интерфейсы и абстракции без пользы (over-engineering).
- OCP не значит «никогда не менять код»: расширяемость закладывайте там, где реально ожидаются изменения.
- Наследование ради переиспользования нарушает LSP; предпочитайте композицию.
- Интерфейс с одной реализацией ради тестов — допустим, но не обязателен для всего.

## Практика

1. Найдите в коде `switch` по типу и замените на стратегии.
2. Разбейте «толстый» интерфейс репозитория на читающий и пишущий.
3. Найдите нарушение LSP и переработайте иерархию.

## Вопросы с ответами

> [!question]- Приведите пример нарушения LSP.
> Наследник, бросающий `NotSupportedException` на унаследованный метод или требующий более строгих условий, чем базовый класс.

> [!question]- Чем DIP отличается от DI?
> DIP задаёт, что зависеть надо от абстракций; DI — способ передать конкретную реализацию снаружи.

> [!question]- Что такое SRP на практике?
> Класс изменяется по одной причине — от одного источника требований.

## Связанные темы

- [[N:3ea33104867981069c30de7503b92394]]
- [[N:3ea33104867981b19175c65aa63799ff]]
