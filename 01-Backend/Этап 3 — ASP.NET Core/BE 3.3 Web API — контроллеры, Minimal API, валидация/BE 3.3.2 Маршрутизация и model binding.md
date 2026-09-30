---
type: topic
domain: backend
stage: 3
section: "3.3"
order: 2
status: todo
level: middle
notion_id: 3ea3310486798110b4a1f57fe92969de
tags: [domain/backend, stage/3, level/middle, topic/aspnet, topic/routing, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Маршрутизация и model binding

↑ [[BE 3.3 Web API — контроллеры, Minimal API, валидация|3.3 Web API: контроллеры, Minimal API, валидация]] · ← [[BE 3.3.1 Контроллеры и Minimal API — когда что|Предыдущая]] · → [[BE 3.3.3 Валидация — DataAnnotations и FluentValidation|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->































> [!info] Зачем это на собесе
> Уточняют: откуда берутся параметры, что такое route constraints и как работает endpoint routing.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

Endpoint routing: `UseRouting` сопоставляет запрос с endpoint, последующие middleware (авторизация, CORS) видят выбранный endpoint, `UseEndpoints`/`Map*` исполняет его.

```csharp
app.MapGet("/orders/{id:guid}", (Guid id) => ...);
app.MapGet("/files/{**path}", (string path) => ...);       // catch-all
app.MapGet("/users/{name:alpha:minlength(3)}", ...);
```

Ограничения: `int`, `guid`, `bool`, `datetime`, `min`, `max`, `range`, `regex`, `alpha`.

### Model binding

| Источник | Атрибут | По умолчанию |
|---|---|---|
| Маршрут | `[FromRoute]` | параметры из шаблона |
| Query | `[FromQuery]` | простые типы |
| Тело | `[FromBody]` | сложные типы в `[ApiController]` |
| Заголовок | `[FromHeader]` | нет |
| Форма | `[FromForm]` | файлы, формы |
| DI | `[FromServices]` | зарегистрированные сервисы в Minimal API |

```csharp
app.MapGet("/search", ([AsParameters] SearchQuery q) => ...);   // группировка query в record

public record SearchQuery(string? Text, int Page = 1, [FromHeader(Name = "X-Tenant")] string? Tenant = null);
```

`System.Text.Json` десериализует тело; настройки (регистр, enum, null) задаются `ConfigureHttpJsonOptions`.

## Нюансы и подводные камни

- Тело запроса читается один раз; повторное чтение требует `EnableBuffering`.
- Формат даты/чисел зависит от культуры для query; используйте инвариантные форматы.
- Конфликт маршрутов даёт `AmbiguousMatchException`.
- Без ограничения `guid`/`int` невалидное значение приведёт к 404 или 400 в зависимости от типа.
- Регистронезависимость маршрутов включена, параметров JSON — только camelCase по умолчанию.

## Практика

1. Добавьте ограничения к маршрутам и проверьте ответы на неверный формат.
2. Соберите query-параметры фильтра через `[AsParameters]`.
3. Реализуйте catch-all маршрут для файлов.

## Вопросы с ответами

> [!question]- Что такое endpoint routing?
> Двухэтапная модель: выбор endpoint (`UseRouting`) и его исполнение, между ними работают middleware, знающие о выбранном endpoint.

> [!question]- Откуда берётся значение параметра, если атрибут не указан?
> Из шаблона маршрута, иначе из query для простых типов, из тела для сложных типов (в контроллерах с ApiController), из DI для зарегистрированных сервисов.

> [!question]- Как задать ограничение на параметр маршрута?
> Через `{id:guid}`, `{page:int:min(1)}` и другие constraints.

## Связанные темы

- [[N:3ea33104867981e587aedf938a06cbe8]]
- [[N:3ea33104867981f59cb0d625e950c6cb]]
