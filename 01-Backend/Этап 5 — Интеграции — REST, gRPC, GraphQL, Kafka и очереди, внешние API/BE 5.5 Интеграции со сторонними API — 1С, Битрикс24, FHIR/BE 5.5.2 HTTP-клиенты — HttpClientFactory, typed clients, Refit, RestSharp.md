---
type: topic
domain: backend
stage: 5
section: "5.5"
order: 2
status: todo
level: middle
notion_id: 3ea33104867981289a30fe09384fdd52
tags: [domain/backend, stage/5, level/middle, topic/integration, topic/http, priority/nice]
reviewed:
next_review:
priority: nice
time: 3
---

# HTTP-клиенты: HttpClientFactory, typed clients, Refit, RestSharp

↑ [[BE 5.5 Интеграции со сторонними API — 1С, Битрикс24, FHIR|5.5 Интеграции со сторонними API: 1С, Битрикс24, FHIR]] · ← [[BE 5.5.1 Как строить интеграцию со сторонним API — адаптер, anti-corruption layer, таймауты, ретраи|Предыдущая]] · → [[BE 5.5.3 Интеграция с 1С — OData, HTTP-сервисы, обмен файлами|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge nice">По желанию</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->












> [!info] Зачем это на собесе
> Какие инструменты вы используете для вызова REST и почему.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

| Инструмент | Когда |
|---|---|
| `HttpClient` + `IHttpClientFactory` (см. [[N:3ea331048679813982d5cc11f4554a52]]) | по умолчанию, полный контроль |
| Typed client | клиент к одному сервису с методами |
| Refit | декларативный интерфейс `[Get]`, `[Post]`, кодогенерация |
| RestSharp | удобный fluent-клиент, меньше в современных проектах |
| Kiota/NSwag | клиент, сгенерированный из OpenAPI |
| Flurl | fluent URL-строитель |

```csharp
public interface IOrdersApi
{
    [Get("/orders/{id}")]
    Task<OrderDto> GetAsync(Guid id, CancellationToken ct);

    [Post("/orders")]
    Task<OrderDto> CreateAsync([Body] CreateOrder body, [Header("Idempotency-Key")] string key, CancellationToken ct);
}

services.AddRefitClient<IOrdersApi>()
        .ConfigureHttpClient(c => c.BaseAddress = new("https://orders.internal"))
        .AddStandardResilienceHandler();
```

Выбор: если есть OpenAPI — генерируйте клиент; если API простой — typed client/Refit; общий каркас (авторизация, ретраи, логи) — через `DelegatingHandler`.

```csharp
public class ApiKeyHandler(IOptions<ApiOptions> o) : DelegatingHandler
{
    protected override Task<HttpResponseMessage> SendAsync(HttpRequestMessage r, CancellationToken ct)
    { r.Headers.Add("X-Api-Key", o.Value.Key); return base.SendAsync(r, ct); }
}
```

## Нюансы и подводные камни

- `new HttpClient()` на запрос и статический клиент навсегда — обе крайности плохи.
- `Refit` бросает `ApiException` на не-2xx: обрабатывайте или используйте `IApiResponse`.
- Сериализацию настраивайте одинаково (`System.Text.Json` options).
- Логируйте без заголовков авторизации и тел с персональными данными.
- Сгенерированный код не правьте руками.

## Практика

1. Опишите клиент через Refit и подключите resilience handler.
2. Сгенерируйте клиент из OpenAPI через Kiota.
3. Напишите `DelegatingHandler` для подписи запросов.

## Вопросы с ответами

> [!question]- Зачем DelegatingHandler?
> Конвейер middleware для исходящих запросов: авторизация, логирование, ретраи, метрики.

> [!question]- Refit или ручной HttpClient?
> Refit сокращает шаблонный код и типизирует вызовы, ручной клиент даёт гибкость для нестандартных API.

## Связанные темы

- [[N:3ea33104867981e6845fee5306c0eb22]]
- [[N:3ea331048679819194a5e1550b6aaabe]]
