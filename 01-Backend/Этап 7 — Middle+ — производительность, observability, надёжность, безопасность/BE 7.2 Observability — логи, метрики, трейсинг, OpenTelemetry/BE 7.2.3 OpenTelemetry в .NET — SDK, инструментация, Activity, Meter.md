---
type: topic
domain: backend
stage: 7
section: "7.2"
order: 3
status: todo
level: senior
notion_id: 3ea331048679815b881ac9af6cde7167
tags: [domain/backend, stage/7, level/senior, topic/observability, topic/opentelemetry, topic/dotnet, priority/should]
reviewed:
next_review:
priority: should
time: 3
---

# OpenTelemetry в .NET: SDK, инструментация, Activity, Meter

↑ [[BE 7.2 Observability — логи, метрики, трейсинг, OpenTelemetry|7.2 Observability: логи, метрики, трейсинг, OpenTelemetry]] · ← [[BE 7.2.2 Структурные логи — Serilog, корреляция, уровни, что не логировать|Предыдущая]] · → [[BE 7.2.4 Распределённый трейсинг — trace context, W3C traceparent, проброс через gRPC и HTTP|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: senior</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> OpenTelemetry — стандарт телеметрии. Ждут знания, как он лежит на .NET-примитивах.

## Объяснение

**OpenTelemetry (OTel)** — вендор-нейтральный стандарт API/SDK/протокола (OTLP) для трейсов, метрик и логов.

В .NET он опирается на встроенные типы:

| Сигнал | .NET-примитив |
|---|---|
| Трейсы | `ActivitySource`, `Activity` (= span) |
| Метрики | `Meter`, `Counter<T>`, `Histogram<T>`, `ObservableGauge<T>` |
| Логи | `ILogger` + OTel-провайдер |

```csharp
builder.Services.AddOpenTelemetry()
    .ConfigureResource(r => r.AddService("orders", serviceVersion: "1.4.0"))
    .WithTracing(t => t
        .AddAspNetCoreInstrumentation()
        .AddHttpClientInstrumentation()
        .AddEntityFrameworkCoreInstrumentation()
        .AddSource("Orders")                       // свои спаны
        .SetSampler(new ParentBasedSampler(new TraceIdRatioBasedSampler(0.1)))
        .AddOtlpExporter())
    .WithMetrics(m => m
        .AddAspNetCoreInstrumentation().AddRuntimeInstrumentation()
        .AddMeter("Orders").AddOtlpExporter());
builder.Logging.AddOpenTelemetry(o => o.AddOtlpExporter());
```

Собственные сигналы:

```csharp
static readonly ActivitySource Source = new("Orders");
static readonly Meter Meter = new("Orders");
static readonly Counter<long> Created = Meter.CreateCounter<long>("orders.created");

using var activity = Source.StartActivity("CreateOrder");
activity?.SetTag("order.items", items.Count);
Created.Add(1, new KeyValuePair<string, object?>("channel", "web"));
```

Endpoint и заголовки экспортера задаются переменными окружения: `OTEL_EXPORTER_OTLP_ENDPOINT`, `OTEL_SERVICE_NAME`, `OTEL_RESOURCE_ATTRIBUTES`.

## Нюансы и подводные камни

- Метки метрик — только с ограниченным набором значений.
- Не создавайте `Meter`/`ActivitySource` на каждый запрос: статические экземпляры.
- Атрибуты спана не должны содержать секретов и персональных данных.
- Без семплирования трейсы 100% запросов дорого хранить.
- Версии инструментаций и SDK нужно обновлять вместе.

## Практика

1. Подключите OTel к сервису и экспортируйте в локальный Collector.
2. Добавьте собственный span и метрику.
3. Настройте семплирование 10% и сохранение ошибок 100% (tail sampling на Collector).

## Вопросы с ответами

> [!question]- Что такое OTLP?
> Протокол передачи телеметрии OpenTelemetry (gRPC/HTTP).

> [!question]- Как Activity связан со span?
> `Activity` — реализация span в .NET; OTel-SDK экспортирует Activity как span.

## Связанные темы

- [[N:3ea33104867981edac43cf84838e178a]]
- [[N:3ea3310486798148be44dd7a434f317a]]
