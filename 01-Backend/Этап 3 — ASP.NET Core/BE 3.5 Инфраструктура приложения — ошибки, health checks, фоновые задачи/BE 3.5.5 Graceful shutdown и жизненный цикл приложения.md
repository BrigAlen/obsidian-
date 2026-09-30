---
type: topic
domain: backend
stage: 3
section: "3.5"
order: 5
status: todo
level: middle
notion_id: 3ea331048679819b82adf7f42ef440d8
tags: [domain/backend, stage/3, level/middle, topic/aspnet, topic/lifecycle, topic/kubernetes, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Graceful shutdown и жизненный цикл приложения

↑ [[BE 3.5 Инфраструктура приложения — ошибки, health checks, фоновые задачи|3.5 Инфраструктура приложения: ошибки, health checks, фоновые задачи]] · ← [[BE 3.5.4 CORS, rate limiting, сжатие ответов|Предыдущая]] · → [[BE 3.5.6 Реалтайм — SignalR и SSE|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> Как не терять запросы при деплое в Kubernetes.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

Последовательность при остановке: сигнал SIGTERM → `IHostApplicationLifetime.ApplicationStopping` → сервер перестаёт принимать новые соединения и ждёт текущие → остановка `IHostedService` (в обратном порядке) → `ApplicationStopped`.

```csharp
builder.Services.Configure<HostOptions>(o => o.ShutdownTimeout = TimeSpan.FromSeconds(30));

lifetime.ApplicationStopping.Register(() => log.LogInformation("Stopping..."));
```

В Kubernetes:

1. Под получает `Terminating`, его убирают из endpoints (readiness).
2. Параллельно отправляется SIGTERM.
3. По истечении `terminationGracePeriodSeconds` — SIGKILL.

Из-за гонки между удалением из балансировки и SIGTERM короткая задержка в `preStop` (`sleep 5`) предотвращает потерю запросов.

### Что делать при остановке

- Завершить in-flight запросы, не принимать новые.
- Остановить консюмеры: перестать читать, закончить текущее, закоммитить offset.
- Сбросить буферы (логи, метрики, outbox).
- Освободить блокировки и соединения.

## Нюансы и подводные камни

- `ShutdownTimeout` по умолчанию 30 секунд (в .NET 6+); должен быть меньше `terminationGracePeriodSeconds`.
- PID 1 в контейнере: используйте `exec` в entrypoint, чтобы сигнал дошёл до процесса.
- Долгие запросы должны реагировать на `RequestAborted`/`ApplicationStopping`.
- Данные в памяти, не сохранённые до остановки, теряются: используйте очереди и транзакции.

## Практика

1. Отправьте SIGTERM во время запроса и убедитесь, что он завершился.
2. Добавьте `preStop` и проверьте отсутствие 502 при rolling update.
3. Корректно остановите Kafka consumer.

## Вопросы с ответами

> [!question]- Что происходит при SIGTERM в ASP.NET Core?
> Хост начинает остановку: прекращает приём новых запросов, ждёт текущих до `ShutdownTimeout`, останавливает hosted services.

> [!question]- Почему при деплое бывают 502?
> Под ещё в балансировке, но уже остановился; лечится readiness, `preStop` и graceful shutdown.

## Связанные темы

- [[N:3ea3310486798119982ad4f3f641704d]]
- [[N:3ea3310486798109b98fefc0a974d817]]
