---
type: topic
domain: backend
stage: 8
section: "8.1"
order: 4
status: todo
level: senior
notion_id: 3ea33104867981d99fb3d9af9f9dec4f
tags: [domain/backend, stage/8, level/senior, topic/design, topic/patterns, topic/structural, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Структурные паттерны: Adapter, Decorator, Facade, Proxy, Composite

↑ [[BE 8.1 Принципы и паттерны проектирования в C♯|8.1 Принципы и паттерны проектирования в C♯]] · ← [[BE 8.1.3 Порождающие паттерны — Factory Method, Abstract Factory, Builder, Singleton (фабрика отчётов)|Предыдущая]] · → [[BE 8.1.5 Поведенческие паттерны — Strategy, Chain of Responsibility, Command, Observer, Template Method, Mediator|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: senior</span></div>
<!-- meta:end -->




























> [!info] Зачем это на собесе
> Ждут отличий Adapter, Decorator и Proxy — их часто путают.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

| Паттерн | Цель | Пример в .NET |
|---|---|---|
| Adapter | приспособить чужой интерфейс к нужному | обёртка над SDK внешней системы (ACL) |
| Decorator | добавить поведение, не меняя класс, тем же интерфейсом | кэширующий/логирующий репозиторий, `Stream` (`GZipStream`) |
| Facade | простой интерфейс к сложной подсистеме | сервис-оркестратор заказов |
| Proxy | заместитель контролирует доступ (ленивая загрузка, кэш, права) | прокси EF для lazy loading, gRPC-клиент |
| Composite | древовидная структура с единым интерфейсом | дерево меню, `IServiceProvider`-иерархия, выражения |
| Bridge | развязать абстракцию и реализацию | драйверы + логика |
| Flyweight | разделяемые общие данные | `string interning` |

```csharp
// Decorator: кэш поверх репозитория без изменения клиента
public class CachedProducts(IProducts inner, IMemoryCache cache) : IProducts
{
    public Task<Product?> GetAsync(int id, CancellationToken ct) =>
        cache.GetOrCreateAsync($"p:{id}", _ => inner.GetAsync(id, ct))!;
}
services.AddScoped<IProducts, SqlProducts>();
services.Decorate<IProducts, CachedProducts>();      // Scrutor

// Adapter: внешний клиент → наш порт
public class AcmeGatewayAdapter(AcmeSdk sdk) : IPaymentGateway
{
    public async Task<PaymentResult> ChargeAsync(Charge c, CancellationToken ct) => Map(await sdk.CreateChargeAsync(Map(c), ct));
}
```

Различия: **Adapter меняет интерфейс**, **Decorator сохраняет** интерфейс и добавляет поведение, **Proxy сохраняет** интерфейс и **управляет доступом**, **Facade упрощает** набор интерфейсов.

## Нюансы и подводные камни

- Цепочки декораторов усложняют отладку: порядок важен.
- Прокси и декораторы должны сохранять контракт (LSP).
- Facade превращается в God object, если не ограничивать ответственность.
- Сквозные аспекты (логирование, кэш) удобны как декораторы, а не в бизнес-коде.

## Практика

1. Добавьте кэширующий декоратор к репозиторию через Scrutor.
2. Напишите адаптер к внешнему API под свой интерфейс.
3. Сделайте Composite для иерархии прав/меню.

## Вопросы с ответами

> [!question]- Чем Decorator отличается от Proxy?
> Декоратор добавляет функциональность, прокси контролирует доступ к объекту (ленивость, права, кэш); оба сохраняют интерфейс.

> [!question]- Adapter или Facade?
> Adapter приводит один интерфейс к другому, Facade упрощает работу с подсистемой.

## Связанные темы

- [[N:3ea33104867981b19175c65aa63799ff]]
- [[N:3ea33104867981f88d7cefc97436250e]]
