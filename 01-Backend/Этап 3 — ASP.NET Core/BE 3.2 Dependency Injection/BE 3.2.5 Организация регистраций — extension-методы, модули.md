---
type: topic
domain: backend
stage: 3
section: "3.2"
order: 5
status: todo
level: middle
notion_id: 3ea3310486798126917dc3763b7b5959
tags: [domain/backend, stage/3, level/middle, topic/aspnet, topic/di, topic/architecture, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Организация регистраций: extension-методы, модули

↑ [[BE 3.2 Dependency Injection|3.2 Dependency Injection]] · ← [[BE 3.2.4 Keyed services, фабрики, декораторы, IServiceScopeFactory|Предыдущая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->

















































> [!info] Зачем это на собесе
> Про поддерживаемость: как не превратить `Program.cs` в 500 строк регистраций.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

Каждый модуль (слой, фича, библиотека) предоставляет extension-метод на `IServiceCollection`, а `Program.cs` только вызывает их.

```csharp
public static class OrdersModule
{
    public static IServiceCollection AddOrders(this IServiceCollection services, IConfiguration cfg)
    {
        services.AddScoped<IOrderService, OrderService>();
        services.AddScoped<IOrderRepository, OrderRepository>();
        services.AddOptions<OrdersOptions>().Bind(cfg.GetSection("Orders")).ValidateOnStart();
        return services;
    }

    public static IEndpointRouteBuilder MapOrders(this IEndpointRouteBuilder app)
    {
        var g = app.MapGroup("/orders");
        g.MapGet("{id:guid}", (Guid id, IOrderService s) => s.GetAsync(id));
        return app;
    }
}

// Program.cs
builder.Services.AddOrders(builder.Configuration).AddPayments(builder.Configuration);
app.MapOrders();
```

| Подход | Плюсы | Минусы |
|---|---|---|
| Extension-методы `AddXxx` | просто, стандарт платформы | нужно вызывать вручную |
| Сканирование сборок (Scrutor, конвенции) | меньше кода | неявно, сложно отлаживать |
| Модули с интерфейсом `IModule` | единообразие | лишний уровень абстракции |

Соглашение: `AddXxx` — регистрации, `UseXxx` — middleware, `MapXxx` — endpoints.

## Нюансы и подводные камни

- Сканирование всех классов по суффиксу «Service» регистрирует лишнее.
- Порядок регистрации влияет на перезапись сервисов.
- Модуль не должен читать `IConfiguration` напрямую при каждом вызове; передавайте секцию или Options.
- Для тестов оставляйте возможность заменить сервисы через `ConfigureTestServices`.

## Практика

1. Разнесите регистрации проекта по модулям `AddXxx`.
2. Добавьте `MapGroup` с общим префиксом и авторизацией.
3. Напишите тест, проверяющий, что все зависимости разрешаются (`ValidateOnBuild`).

## Вопросы с ответами

> [!question]- Как организовать регистрации в большом проекте?
> Extension-методами по модулям и слоям; `Program.cs` остаётся тонким.

> [!question]- Что удобнее: ручные регистрации или сканирование?
> Ручные явнее и безопаснее, сканирование удобно для однотипных обработчиков (MediatR, валидаторы).

## Связанные темы

- [[N:3ea331048679816788e0df486d1eca06]]
- [[N:3ea33104867981e587aedf938a06cbe8]]
