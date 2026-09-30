---
type: topic
domain: backend
stage: 7
section: "7.2"
order: 4
status: todo
level: senior
notion_id: 3ea3310486798148be44dd7a434f317a
tags: [domain/backend, stage/7, level/senior, topic/observability, topic/tracing, priority/should]
reviewed:
next_review:
priority: should
time: 3
---

# Распределённый трейсинг: trace context, W3C traceparent, проброс через gRPC и HTTP

↑ [[BE 7.2 Observability — логи, метрики, трейсинг, OpenTelemetry|7.2 Observability: логи, метрики, трейсинг, OpenTelemetry]] · ← [[BE 7.2.3 OpenTelemetry в .NET — SDK, инструментация, Activity, Meter|Предыдущая]] · → [[BE 7.2.5 OTLP и OpenTelemetry Collector — receivers, processors, exporters|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: senior</span></div>
<!-- meta:end -->







































> [!info] Зачем это на собесе
> Как трейс проходит через границы сервисов и очередей.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

**Trace** — дерево **span**-ов одного запроса. Каждый span: имя, время, родитель, атрибуты, события, статус.

Контекст передаётся между процессами заголовком W3C:

```text
traceparent: 00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01
             ver  trace-id (128 бит)               parent span-id   flags (sampled)
tracestate:  vendor=value
baggage:     tenant=acme,userTier=gold          (сквозные метки, осторожно)
```

| Транспорт | Как пробрасывается |
|---|---|
| HTTP | заголовок `traceparent` автоматически инструментацией `HttpClient`/ASP.NET Core |
| gRPC | metadata `traceparent`, инструментация `Grpc.Net.Client`/`AspNetCore` |
| Kafka/RabbitMQ | заголовки сообщения: продюсер вставляет, консьюмер извлекает и создаёт span с `Link`/родителем |
| Фоновые задачи | явная передача контекста при постановке задачи |

```csharp
// Извлечение контекста из сообщения Kafka
var parent = Propagator.Extract(default, headers, (h, k) => h.TryGetLastBytes(k, out var v) ? [Encoding.UTF8.GetString(v)] : []);
using var activity = Source.StartActivity("process orders", ActivityKind.Consumer, parent.ActivityContext);
```

Виды span: `Server`, `Client`, `Producer`, `Consumer`, `Internal`.

## Нюансы и подводные камни

- Потерянный заголовок на границе (прокси, шлюз, очередь) обрывает трейс.
- Baggage передаётся всем downstream-сервисам и попадает в сеть: не кладите секреты.
- Семплирование должно быть согласованным (`ParentBased`), иначе трейсы неполные.
- Пакетная обработка сообщений порождает один span на много входящих: используйте `Link`.
- Часы разных серверов расходятся: порядок span-ов определяют по связям, а не по времени.

## Практика

1. Пробросьте трейс через HTTP, gRPC и Kafka и посмотрите его в Jaeger/Tempo.
2. Найдите, где обрывается цепочка, и исправьте.
3. Добавьте `trace_id` в ответ об ошибке.

## Вопросы с ответами

> [!question]- Что содержит заголовок traceparent?
> Версию, `trace-id`, `parent span-id` и флаги (например, sampled).

> [!question]- Как проследить запрос через брокер?
> Записывать контекст в заголовки сообщения и восстанавливать его в потребителе.

## Связанные темы

- [[N:3ea331048679815b881ac9af6cde7167]]
- [[N:3ea33104867981b2897cdf14acc698c7]]
