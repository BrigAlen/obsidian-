---
type: topic
domain: backend
stage: 3
section: "3.1"
order: 6
status: todo
level: middle
notion_id: 3ea331048679813982d5cc11f4554a52
tags: [domain/backend, stage/3, level/middle, topic/aspnet, topic/http, topic/httpclient, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# HttpClient и IHttpClientFactory, HeaderPropagation

↑ [[BE 3.1 Хост, конфигурация и middleware pipeline|3.1 Хост, конфигурация и middleware pipeline]] · ← [[BE 3.1.5 Логирование — ILogger, уровни, structured logging, Serilog|Предыдущая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->



































> [!info] Зачем это на собесе
> Классическая ошибка `new HttpClient()` на каждый запрос и знание Polly/resilience — признак опыта.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

Два противоположных подводных камня:

- Создавать `HttpClient` на каждый запрос — исчерпание сокетов (`SocketException`, TIME_WAIT).
- Один статический `HttpClient` навсегда — DNS кэшируется, изменения адреса не подхватываются.

`IHttpClientFactory` решает оба: управляет пулом `HttpMessageHandler` и периодически пересоздаёт их.

```csharp
builder.Services.AddHttpClient<IPaymentsClient, PaymentsClient>(c =>
{
    c.BaseAddress = new Uri("https://payments.internal/");
    c.Timeout = TimeSpan.FromSeconds(10);
})
.AddStandardResilienceHandler();   // retry, circuit breaker, timeout (Microsoft.Extensions.Http.Resilience)

public class PaymentsClient(HttpClient http) : IPaymentsClient
{
    public async Task<PaymentDto?> GetAsync(Guid id, CancellationToken ct)
        => await http.GetFromJsonAsync<PaymentDto>($"payments/{id}", ct);
}
```

| Способ | Когда |
|---|---|
| Typed client | клиент к конкретному сервису с методами |
| Named client | несколько настроек одним типом |
| `CreateClient()` | простые случаи |

### Проброс заголовков

```csharp
builder.Services.AddHeaderPropagation(o => { o.Headers.Add("X-Correlation-Id"); o.Headers.Add("Authorization"); });
builder.Services.AddHttpClient<IPaymentsClient, PaymentsClient>().AddHeaderPropagation();
app.UseHeaderPropagation();
```

Так входящие заголовки автоматически копируются в исходящие запросы к другим сервисам.

### Устойчивость

Retry с экспоненциальной паузой и jitter, circuit breaker, timeout на попытку и общий. Повторять можно только идемпотентные запросы.

## Нюансы и подводные камни

- Всегда передавайте `CancellationToken`.
- Проверяйте `EnsureSuccessStatusCode()` или статус: 4xx/5xx не бросают исключение сами.
- Читайте тело потоком, а `HttpResponseMessage` освобождайте (`using`).
- `Timeout` клиента не заменяет таймаут на попытку в resilience handler.
- Не логируйте заголовок `Authorization`.

## Практика

1. Настройте typed client с retry и circuit breaker и сымитируйте падение сервиса.
2. Пробросьте `X-Correlation-Id` между двумя своими сервисами.
3. Воспроизведите исчерпание сокетов в цикле с `new HttpClient()`.

## Вопросы с ответами

> [!question]- Почему нельзя создавать HttpClient на каждый запрос?
> Каждое соединение остаётся в TIME_WAIT, сокеты заканчиваются под нагрузкой; нужен повторно используемый handler.

> [!question]- Зачем IHttpClientFactory?
> Управляет временем жизни handler-ов (решает проблему DNS), даёт типизированные клиенты и подключение resilience и логирования.

> [!question]- Что можно ретраить?
> Идемпотентные операции и временные ошибки (5xx, таймауты, 429); POST без ключа идемпотентности — только осторожно.

## Связанные темы

- [[N:3ea33104867981a6a9f0dc668b236e7a]]
- [[N:3ea331048679810f8b4def6f1c5f7146]]
