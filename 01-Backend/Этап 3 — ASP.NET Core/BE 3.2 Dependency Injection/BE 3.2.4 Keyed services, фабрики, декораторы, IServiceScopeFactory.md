---
type: topic
domain: backend
stage: 3
section: "3.2"
order: 4
status: todo
level: middle
notion_id: 3ea331048679816788e0df486d1eca06
tags: [domain/backend, stage/3, level/middle, topic/aspnet, topic/di, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Keyed services, фабрики, декораторы, IServiceScopeFactory

↑ [[BE 3.2 Dependency Injection|3.2 Dependency Injection]] · ← [[BE 3.2.3 Captive dependency и другие ловушки DI|Предыдущая]] · → [[BE 3.2.5 Организация регистраций — extension-методы, модули|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->



















> [!info] Зачем это на собесе
> Показывает, что вы умеете выходить за рамки «один интерфейс — одна реализация».

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

### Keyed services (.NET 8)

```csharp
builder.Services.AddKeyedSingleton<INotifier, EmailNotifier>("email");
builder.Services.AddKeyedSingleton<INotifier, SmsNotifier>("sms");

public class Alerts([FromKeyedServices("sms")] INotifier notifier) { }
var email = provider.GetRequiredKeyedService<INotifier>("email");
```

### Фабрики

```csharp
builder.Services.AddScoped<IPricing>(sp =>
{
    var opts = sp.GetRequiredService<IOptions<PricingOptions>>().Value;
    return opts.UseNew ? sp.GetRequiredService<NewPricing>() : sp.GetRequiredService<OldPricing>();
});
```

Фабрика нужна, когда реализация выбирается в рантайме или требует параметров, которых нет в контейнере (`Func<T>`-фабрики или `ActivatorUtilities.CreateInstance`).

### Декораторы

Встроенный контейнер не поддерживает их напрямую; используют Scrutor или ручную регистрацию:

```csharp
builder.Services.AddScoped<OrderService>();
builder.Services.AddScoped<IOrderService>(sp =>
    new LoggingOrderService(sp.GetRequiredService<OrderService>(), sp.GetRequiredService<ILogger<LoggingOrderService>>()));

// Scrutor
builder.Services.Decorate<IOrderService, CachingOrderService>();
```

### IServiceScopeFactory

Создаёт scope вне HTTP-запроса — для фоновых задач, обработчиков сообщений и singleton-ов (см. [[N:3ea33104867981d2bc3bc47bf945c910]]).

## Нюансы и подводные камни

- Декоратор с неверным порядком регистрации зациклится на себе.
- Ключи в Keyed Services — `object`: используйте константы/enum, а не «магические» строки.
- `GetService` возвращает `null`, `GetRequiredService` бросает: предпочитайте второй.
- Регистрация одной реализации под несколькими интерфейсами: singleton нужно зарегистрировать сам и делегировать интерфейсы, иначе экземпляров будет несколько.

## Практика

1. Реализуйте выбор канала уведомления по ключу.
2. Добавьте кэширующий декоратор к сервису через Scrutor.
3. Создайте scope в обработчике очереди.

## Вопросы с ответами

> [!question]- Для чего нужны keyed services?
> Для регистрации нескольких реализаций одного интерфейса и выбора нужной по ключу без своих фабрик.

> [!question]- Как реализовать декоратор при встроенном контейнере?
> Ручной регистрацией через фабрику либо библиотекой Scrutor (`Decorate`).

> [!question]- Когда нужен IServiceScopeFactory?
> Когда код работает вне HTTP-запроса или в singleton и должен получать scoped-сервисы.

## Связанные темы

- [[N:3ea33104867981d2bc3bc47bf945c910]]
- [[N:3ea3310486798126917dc3763b7b5959]]
