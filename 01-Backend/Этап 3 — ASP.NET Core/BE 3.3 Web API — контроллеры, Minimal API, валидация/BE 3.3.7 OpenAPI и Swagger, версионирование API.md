---
type: topic
domain: backend
stage: 3
section: "3.3"
order: 7
status: todo
level: middle
notion_id: 3ea331048679816ca2a9e01efe418d51
tags: [domain/backend, stage/3, level/middle, topic/aspnet, topic/openapi, topic/versioning, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# OpenAPI и Swagger, версионирование API

↑ [[BE 3.3 Web API — контроллеры, Minimal API, валидация|3.3 Web API: контроллеры, Minimal API, валидация]] · ← [[BE 3.3.6 Ответы и ошибки — IResult, ProblemDetails, статус-коды|Предыдущая]] · → [[BE 3.3.8 Загрузка и скачивание файлов, стриминг|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->



































> [!info] Зачем это на собесе
> Про контракт и эволюцию API: как документировать и как вносить ломающие изменения.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

**OpenAPI** — спецификация описания HTTP API; **Swagger UI** — интерфейс для просмотра/вызова. В .NET 9 встроенная генерация `Microsoft.AspNetCore.OpenApi` заменила Swashbuckle по умолчанию.

```csharp
builder.Services.AddOpenApi();
app.MapOpenApi();                  // /openapi/v1.json
// UI: Scalar или Swagger UI поверх json
```

```csharp
orders.MapGet("{id:guid}", Get)
      .WithName("GetOrder")
      .WithSummary("Получить заказ")
      .Produces<OrderDto>()
      .ProducesProblem(404);
```

### Версионирование

| Способ | Пример | Замечание |
|---|---|---|
| URL | `/v2/orders` | самый простой, видно в логах |
| Заголовок | `X-Api-Version: 2` | чище URL, сложнее тестировать |
| Media type | `application/vnd.app.v2+json` | «строгий REST» |
| Query | `?api-version=2.0` | стандарт `Asp.Versioning` |

```csharp
builder.Services.AddApiVersioning(o => { o.DefaultApiVersion = new(1, 0); o.ReportApiVersions = true; })
    .AddApiExplorer();
```

### Ломающие и безопасные изменения

| Безопасно | Ломающее |
|---|---|
| новое необязательное поле в ответе | удаление/переименование поля |
| новый endpoint | смена типа поля, обязательности |
| новое значение enum с толерантным клиентом | смена семантики кода ответа |

Политика: объявить deprecation (заголовки `Deprecation`/`Sunset`), поддерживать N версий, тестировать контрактами.

## Нюансы и подводные камни

- Генерация клиента из OpenAPI (NSwag, Kiota) ускоряет интеграции, но требует точной схемы (`Produces`).
- Не публикуйте Swagger на проде без необходимости или защитите его.
- Не смешивайте версии в одной модели: копируйте DTO по версиям.
- Схема без описания ошибок вводит потребителей в заблуждение.

## Практика

1. Подключите `AddOpenApi` и Scalar, добавьте описания и примеры.
2. Реализуйте v1 и v2 одного endpoint и заголовки deprecation.
3. Сгенерируйте типизированный клиент из схемы.

## Вопросы с ответами

> [!question]- Чем OpenAPI отличается от Swagger?
> OpenAPI — стандарт описания; Swagger — набор инструментов (UI, codegen) для него.

> [!question]- Как версионировать API?
> Чаще по URL или заголовку; главное — правила совместимости и срок поддержки старых версий.

> [!question]- Что считать ломающим изменением?
> Удаление или переименование полей, изменение типов и семантики, ужесточение валидации.

## Связанные темы

- [[N:3ea3310486798146aa7cd46cc1613ab6]]
- [[N:3ea331048679813385bfc8013c2dc64f]]
