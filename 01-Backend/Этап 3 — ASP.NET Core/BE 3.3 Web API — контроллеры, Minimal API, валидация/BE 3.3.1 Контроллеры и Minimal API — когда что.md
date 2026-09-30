---
type: topic
domain: backend
stage: 3
section: "3.3"
order: 1
status: todo
level: middle
notion_id: 3ea33104867981e587aedf938a06cbe8
tags: [domain/backend, stage/3, level/middle, topic/aspnet, topic/webapi, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Контроллеры и Minimal API: когда что

↑ [[BE 3.3 Web API — контроллеры, Minimal API, валидация|3.3 Web API: контроллеры, Minimal API, валидация]] · → [[BE 3.3.2 Маршрутизация и model binding|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->




















> [!info] Зачем это на собесе
> Вопрос на архитектурное мышление: «Minimal API или контроллеры?» — важно назвать критерии, а не «что нравится».

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

| Критерий | Контроллеры (MVC) | Minimal API |
|---|---|---|
| Структура | классы, атрибуты, `[ApiController]` | лямбды/методы, `MapGet/Post…` |
| Фильтры | action/resource/exception/result | endpoint filters |
| Model binding и валидация | богатые, автоматические 400 | ближе к ручной; валидацию подключают (.NET 10 — встроенная) |
| Производительность | чуть больше накладных | быстрее старт и меньше аллокаций |
| Совместимость | зрелая экосистема | быстро развивается, AOT-friendly |
| Подходит для | большие API с общей логикой | микросервисы, небольшие API, high-load |

```csharp
// Контроллер
[ApiController, Route("orders")]
public class OrdersController(IOrderService svc) : ControllerBase
{
    [HttpGet("{id:guid}")]
    public async Task<ActionResult<OrderDto>> Get(Guid id, CancellationToken ct)
        => await svc.FindAsync(id, ct) is { } dto ? dto : NotFound();
}

// Minimal API
var orders = app.MapGroup("/orders").RequireAuthorization();
orders.MapGet("{id:guid}", async (Guid id, IOrderService svc, CancellationToken ct) =>
    await svc.FindAsync(id, ct) is { } dto ? Results.Ok(dto) : Results.NotFound());
```

Оба подхода можно смешивать в одном приложении. Что бы вы ни выбрали, держите endpoint тонким: разбор запроса → вызов сервиса/обработчика → формирование ответа.

## Нюансы и подводные камни

- Логика в контроллере/лямбде — плохой знак: выносите в сервисы/handlers.
- `[ApiController]` включает автоматический 400 при невалидной модели, binding source inference и ProblemDetails.
- Minimal API с большим числом endpoint без `MapGroup` превращает `Program.cs` в свалку.
- Возврат `ActionResult<T>` даёт типизацию для OpenAPI.

## Практика

1. Реализуйте один и тот же CRUD в двух стилях и сравните объём кода.
2. Вынесите endpoint-ы в extension-метод `MapXxx`.
3. Сравните throughput через `bombardier` или k6.

## Вопросы с ответами

> [!question]- Когда выбрать Minimal API?
> Для небольших сервисов и когда важны скорость старта/AOT; с группировкой (`MapGroup`) подходит и для больших.

> [!question]- Что делает атрибут ApiController?
> Автоматическая валидация модели с ответом 400, вывод источников binding, ProblemDetails, обязательность атрибутного роутинга.

> [!question]- Чем отличается ControllerBase от Controller?
> `Controller` добавляет поддержку View; для API достаточно `ControllerBase`.

## Связанные темы

- [[N:3ea3310486798110b4a1f57fe92969de]]
- [[N:3ea3310486798126917dc3763b7b5959]]
