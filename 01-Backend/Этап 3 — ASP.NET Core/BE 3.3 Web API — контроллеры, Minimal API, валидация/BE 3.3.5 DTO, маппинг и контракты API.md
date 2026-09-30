---
type: topic
domain: backend
stage: 3
section: "3.3"
order: 5
status: todo
level: middle
notion_id: 3ea331048679818c931fc74c6d958606
tags: [domain/backend, stage/3, level/middle, topic/aspnet, topic/api-design, topic/mapping, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# DTO, маппинг и контракты API

↑ [[BE 3.3 Web API — контроллеры, Minimal API, валидация|3.3 Web API: контроллеры, Minimal API, валидация]] · ← [[BE 3.3.4 Фильтры — action, exception, resource, endpoint filters|Предыдущая]] · → [[BE 3.3.6 Ответы и ошибки — IResult, ProblemDetails, статус-коды|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->































































> [!info] Зачем это на собесе
> Проверяют, отделяете ли вы модель хранения от внешнего контракта, и как относитесь к AutoMapper.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

**DTO (Data Transfer Object)** — форма данных на границе API. Контракт отделяется от сущностей БД и доменных моделей, чтобы менять их независимо и не «светить» лишнего (пароль-хэши, внутренние ID).

```csharp
public record OrderDto(Guid Id, string Customer, decimal Total, IReadOnlyList<OrderItemDto> Items);
public record CreateOrderRequest(string Customer, IReadOnlyList<OrderItemRequest> Items);
```

| Способ маппинга | Плюсы | Минусы |
|---|---|---|
| Ручной (`ToDto()`) | явный, быстрый, легко отлаживать | много кода |
| Mapperly / source generators | без рефлексии, проверка на этапе компиляции | генерируемый код |
| AutoMapper | меньше кода | рефлексия, скрытая логика, ошибки в рантайме, лицензия |
| Проекция в запросе (`Select`) | грузит только нужные поля | привязка к EF |

```csharp
var dtos = await db.Orders
    .Where(o => o.CustomerId == id)
    .Select(o => new OrderDto(o.Id, o.Customer.Name, o.Total, ...))
    .ToListAsync(ct);
```

### Контракты API

- Разделяйте запросы и ответы; не переиспользуйте одну модель для create/update/response.
- Добавление полей — совместимо, удаление и смена типа — ломающее изменение.
- Публикуйте схему (OpenAPI) и версионируйте.
- Используйте `record`, `init`, nullable-аннотации для ясности контракта.

## Нюансы и подводные камни

- Возврат EF-сущностей ведёт к циклам сериализации, ленивым запросам и утечке данных.
- Mass assignment (over-posting): не биндите тело прямо в сущность.
- Не смешивайте бизнес-логику в мапперах.
- Даты передавайте в ISO 8601 UTC, деньги — как `decimal`/строка, а не `double`.

## Практика

1. Замените возврат сущностей на DTO и проекции `Select`.
2. Реализуйте маппинг через Mapperly.
3. Проверьте over-posting: добавьте поле `IsAdmin` и попробуйте его отправить.

## Вопросы с ответами

> [!question]- Зачем DTO, если есть сущности?
> Чтобы отделить внешний контракт от модели хранения, скрыть лишнее и менять их независимо.

> [!question]- Что не так с AutoMapper?
> Скрытая рефлексия и сложная отладка, ошибки видны только в рантайме, соблазн класть логику в профили; многие команды выбирают явный маппинг или Mapperly.

> [!question]- Что такое over-posting?
> Атака/ошибка, когда клиент присылает лишние поля, которые биндятся в сущность; лечится отдельными request-DTO.

## Связанные темы

- [[N:3ea331048679812d8326dfc4bc122908]]
- [[N:3ea3310486798146aa7cd46cc1613ab6]]
