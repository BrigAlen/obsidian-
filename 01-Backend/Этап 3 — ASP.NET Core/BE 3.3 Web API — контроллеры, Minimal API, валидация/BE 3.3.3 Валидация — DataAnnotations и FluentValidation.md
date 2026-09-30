---
type: topic
domain: backend
stage: 3
section: "3.3"
order: 3
status: todo
level: middle
notion_id: 3ea33104867981f59cb0d625e950c6cb
tags: [domain/backend, stage/3, level/middle, topic/aspnet, topic/validation, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Валидация: DataAnnotations и FluentValidation

↑ [[BE 3.3 Web API — контроллеры, Minimal API, валидация|3.3 Web API: контроллеры, Minimal API, валидация]] · ← [[BE 3.3.2 Маршрутизация и model binding|Предыдущая]] · → [[BE 3.3.4 Фильтры — action, exception, resource, endpoint filters|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->














> [!info] Зачем это на собесе
> Валидацию входа проверяют почти на каждом собеседовании: где она, какой формат ответа и где не хватает атрибутов.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

### DataAnnotations

```csharp
public record CreateOrderRequest(
    [property: Required, StringLength(100)] string Customer,
    [property: Range(1, 1000)] int Quantity,
    [property: EmailAddress] string Email);
```

С `[ApiController]` невалидная модель автоматически даёт `400` с `ValidationProblemDetails`. Атрибуты просты, но плохо выражают сложные и контекстные правила.

### FluentValidation

```csharp
public class CreateOrderValidator : AbstractValidator<CreateOrderRequest>
{
    public CreateOrderValidator(IProductCatalog catalog)
    {
        RuleFor(x => x.Customer).NotEmpty().MaximumLength(100);
        RuleFor(x => x.Quantity).InclusiveBetween(1, 1000);
        RuleFor(x => x.Email).EmailAddress();
        RuleFor(x => x.ProductId).MustAsync(catalog.ExistsAsync).WithMessage("Товар не найден");
    }
}

builder.Services.AddValidatorsFromAssemblyContaining<CreateOrderValidator>();
```

| Критерий | DataAnnotations | FluentValidation |
|---|---|---|
| Где правила | атрибуты в модели | отдельный класс |
| Условные и зависимые правила | ограниченно | `When`, `Must`, `DependentRules` |
| Асинхронные проверки, DI | нет | да |
| Локализация | ресурсы | ресурсы + гибкость |

### В Minimal API

```csharp
orders.MapPost("/", async (CreateOrderRequest req, IValidator<CreateOrderRequest> v, IOrderService s) =>
{
    var result = await v.ValidateAsync(req);
    if (!result.IsValid) return Results.ValidationProblem(result.ToDictionary());
    return Results.Created(...);
});
```

Можно вынести в endpoint filter (см. [[N:3ea331048679812d8326dfc4bc122908]]).

## Нюансы и подводные камни

- Валидация формы (формат, диапазоны) ≠ бизнес-инварианты: вторые проверяются в доменной логике.
- Не доверяйте клиентской валидации.
- Не возвращайте детали, раскрывающие внутренности (SQL, стек).
- Проверки уникальности через валидатор не заменяют unique-индекс: возможны гонки.
- Nullable reference types не заменяют `Required` для JSON: `null` может прийти.

## Практика

1. Реализуйте валидатор с зависимыми правилами и локализацией.
2. Сделайте generic endpoint filter, вызывающий `IValidator<T>`.
3. Убедитесь, что формат ошибок единый (`ValidationProblemDetails`).

## Вопросы с ответами

> [!question]- Где должна быть валидация?
> На границе (форма входных данных) и в домене (инварианты). На клиенте — только для UX.

> [!question]- Когда FluentValidation лучше DataAnnotations?
> Когда правила сложные, условные, асинхронные или требуют DI.

> [!question]- Заменяет ли валидатор unique-индекс?
> Нет, между проверкой и записью возможна гонка; ограничение должно быть в БД.

## Связанные темы

- [[N:3ea3310486798110b4a1f57fe92969de]]
- [[N:3ea331048679812d8326dfc4bc122908]]
