---
type: topic
domain: backend
stage: 7
section: "7.3"
order: 3
status: todo
level: senior
notion_id: 3ea331048679811aa59dd143aea4d4c6
tags: [domain/backend, stage/7, level/senior, topic/reliability, topic/polly, topic/dotnet, priority/should]
reviewed:
next_review:
priority: should
time: 3
---

# Polly и Microsoft.Extensions.Resilience

↑ [[BE 7.3 Надёжность и отказоустойчивость|7.3 Надёжность и отказоустойчивость]] · ← [[BE 7.3.2 Circuit breaker, bulkhead, fallback|Предыдущая]] · → [[BE 7.3.4 Идемпотентность операций и дедупликация|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: senior</span></div>
<!-- meta:end -->










> [!info] Зачем это на собесе
> Практика: как реализовать паттерны устойчивости в .NET без ручного кода.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

Polly v8 предоставляет `ResiliencePipeline`, а пакеты `Microsoft.Extensions.Http.Resilience` и `Microsoft.Extensions.Resilience` интегрируют его с DI и `HttpClient`.

| Стратегия | Назначение |
|---|---|
| Retry | повторы с backoff и jitter |
| Circuit breaker | размыкание при сбоях |
| Timeout | ограничение времени попытки |
| Hedging | параллельные запросы для снижения хвостовой задержки |
| Fallback | запасное значение |
| Rate limiter, Concurrency limiter | ограничение нагрузки |

```csharp
// Готовый набор для HttpClient: rate limiter → total timeout → retry → circuit breaker → attempt timeout
builder.Services.AddHttpClient<IBilling, BillingClient>().AddStandardResilienceHandler();

// Своя настройка
builder.Services.AddHttpClient("pay").AddResilienceHandler("pay", b => b
    .AddRetry(new HttpRetryStrategyOptions { MaxRetryAttempts = 3, BackoffType = DelayBackoffType.Exponential, UseJitter = true, Delay = TimeSpan.FromMilliseconds(200) })
    .AddCircuitBreaker(new HttpCircuitBreakerStrategyOptions { SamplingDuration = TimeSpan.FromSeconds(30), FailureRatio = 0.5, MinimumThroughput = 20, BreakDuration = TimeSpan.FromSeconds(15) })
    .AddTimeout(TimeSpan.FromSeconds(3)));

// Для произвольного кода
builder.Services.AddResiliencePipeline("db", p => p.AddRetry(new() { MaxRetryAttempts = 2 }).AddTimeout(TimeSpan.FromSeconds(5)));
public class Repo([FromKeyedServices("db")] ResiliencePipeline pipeline) { public Task Run() => pipeline.ExecuteAsync(async ct => { /* ... */ }).AsTask(); }
```

Метрики и логи стратегий (`resilience.polly.*`) экспортируются через OpenTelemetry.

## Нюансы и подводные камни

- Порядок стратегий важен: внешний таймаут → retry → breaker → таймаут попытки.
- Не оборачивайте ретраем неидемпотентные вызовы без ключа.
- `AddStandardResilienceHandler` подходит по умолчанию; значения тюнингуйте под SLA зависимости.
- Не смешивайте старый Polly (v7) и v8 API.
- Тесты: используйте `FakeTimeProvider` и управляемые обработчики для проверки ретраев.

## Практика

1. Подключите standard handler и проверьте его метрики.
2. Настройте hedging для идемпотентного GET.
3. Напишите тест, проверяющий число попыток при 503.

## Вопросы с ответами

> [!question]- Что входит в standard resilience handler?
> Ограничитель, общий таймаут, retry, circuit breaker и таймаут попытки в правильном порядке.

> [!question]- Что такое hedging?
> Отправка дополнительного запроса при долгом ожидании, чтобы уменьшить хвост задержки.

## Связанные темы

- [[N:3ea3310486798199ad00dfecba3308bf]]
- [[N:3ea33104867981c5a9dbc796f665fb11]]
