---
type: topic
domain: backend
stage: 8
section: "8.1"
order: 3
status: todo
level: senior
notion_id: 3ea33104867981b19175c65aa63799ff
tags: [domain/backend, stage/8, level/senior, topic/design, topic/patterns, topic/creational, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Порождающие паттерны: Factory Method, Abstract Factory, Builder, Singleton (фабрика отчётов)

↑ [[BE 8.1 Принципы и паттерны проектирования в C♯|8.1 Принципы и паттерны проектирования в C♯]] · ← [[BE 8.1.2 DRY, KISS, YAGNI, GRASP, Law of Demeter|Предыдущая]] · → [[BE 8.1.4 Структурные паттерны — Adapter, Decorator, Facade, Proxy, Composite|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: senior</span></div>
<!-- meta:end -->



> [!info] Зачем это на собесе
> Порождающие паттерны спрашивают с примерами из реальной практики и знанием, как DI заменяет часть из них.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

| Паттерн | Задача | Пример |
|---|---|---|
| Factory Method | подкласс/метод решает, какой объект создать | `ReportFactory.Create(type)` |
| Abstract Factory | семейство связанных объектов | UI-темы, провайдеры БД (`DbProviderFactory`) |
| Builder | пошаговая сборка сложного объекта | `WebApplicationBuilder`, `StringBuilder`, `SqlBuilder` |
| Singleton | единственный экземпляр | в .NET — `AddSingleton`, а не статическое поле |
| Prototype | клонирование | `record` с `with` |
| Object Pool | переиспользование дорогих объектов | `ArrayPool`, `ObjectPool<T>` |

```csharp
// Factory: выбор отчёта по типу; зависимости приходят из DI
public interface IReport { string Type { get; } Task<byte[]> BuildAsync(ReportRequest r, CancellationToken ct); }

public class ReportFactory(IEnumerable<IReport> reports)
{
    private readonly Dictionary<string, IReport> _map = reports.ToDictionary(r => r.Type);
    public IReport Create(string type) => _map.TryGetValue(type, out var r) ? r : throw new NotSupportedException(type);
}
// регистрация: services.AddScoped<IReport, InvoiceReport>(); ... — новый отчёт = новый класс (OCP)

// Builder
var order = new OrderBuilder().ForCustomer(c).WithItem(sku, 2).WithDiscount(10).Build();

// Singleton: потокобезопасная ленивая инициализация
public sealed class Config { private static readonly Lazy<Config> _i = new(() => new Config()); public static Config Instance => _i.Value; }
```

В приложениях с DI вместо ручного Singleton используйте регистрацию `AddSingleton`: проще тестировать и заменять.

## Нюансы и подводные камни

- Классический Singleton — глобальное состояние: скрытые зависимости, проблемы в тестах и потокобезопасности.
- Фабрика с `switch` нарушает OCP; регистрация реализаций в DI и словарь по ключу — гибче (см. keyed services).
- Builder без валидации в `Build()` создаёт невалидные объекты.
- Избыточные фабрики там, где достаточно конструктора.

## Практика

1. Реализуйте фабрику отчётов на DI (`IEnumerable<IReport>`).
2. Сделайте fluent-Builder для сложного объекта с валидацией.
3. Замените статический Singleton на DI-singleton.

## Вопросы с ответами

> [!question]- Factory Method или Abstract Factory?
> Factory Method создаёт один продукт, Abstract Factory — семейство согласованных продуктов.

> [!question]- Почему Singleton называют антипаттерном?
> Глобальное изменяемое состояние, скрытые зависимости, трудности тестирования; в DI используют управляемое время жизни.

## Связанные темы

- [[N:3ea33104867981069c30de7503b92394]]
- [[N:3ea33104867981d99fb3d9af9f9dec4f]]
