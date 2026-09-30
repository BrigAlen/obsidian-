---
type: topic
domain: backend
stage: 3
section: "3.5"
order: 2
status: todo
level: middle
notion_id: 3ea33104867981e0adc9fe8799f5ec40
tags: [domain/backend, stage/3, level/middle, topic/aspnet, topic/health, topic/kubernetes, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Health checks: liveness и readiness

↑ [[BE 3.5 Инфраструктура приложения — ошибки, health checks, фоновые задачи|3.5 Инфраструктура приложения: ошибки, health checks, фоновые задачи]] · ← [[BE 3.5.1 Глобальная обработка ошибок — IExceptionHandler, middleware|Предыдущая]] · → [[BE 3.5.3 Фоновые задачи — IHostedService, BackgroundService, Worker, Hangfire и Quartz|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->



































> [!info] Зачем это на собесе
> Разница liveness/readiness и что проверять — базовый вопрос для Kubernetes и DevOps.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

| Проба | Вопрос | Реакция оркестратора |
|---|---|---|
| Liveness | процесс жив, не завис? | перезапустить контейнер |
| Readiness | готов принимать трафик? | убрать из балансировки |
| Startup | закончил ли запуск? | подождать, не убивать |

```csharp
builder.Services.AddHealthChecks()
    .AddCheck("self", () => HealthCheckResult.Healthy(), tags: ["live"])
    .AddNpgSql(cs, tags: ["ready"])
    .AddRedis(redis, tags: ["ready"])
    .AddKafka(kafkaCfg, tags: ["ready"]);

app.MapHealthChecks("/health/live",  new() { Predicate = r => r.Tags.Contains("live") });
app.MapHealthChecks("/health/ready", new() { Predicate = r => r.Tags.Contains("ready") });
```

```yaml
livenessProbe:  { httpGet: { path: /health/live,  port: 8080 }, periodSeconds: 10 }
readinessProbe: { httpGet: { path: /health/ready, port: 8080 }, periodSeconds: 5 }
```

## Нюансы и подводные камни

- Liveness не должен проверять внешние зависимости: падение БД не должно приводить к перезапуску всех подов (каскад).
- Readiness с тяжёлыми проверками нагружает зависимости; кэшируйте результат.
- Не публикуйте подробности health-check наружу.
- Задавайте таймауты проверкам.
- Для деградации используйте статус `Degraded`.

## Практика

1. Добавьте проверки БД и брокера в readiness.
2. Остановите БД и понаблюдайте, как под выводится из балансировки.
3. Настройте `startupProbe` для медленного старта.

## Вопросы с ответами

> [!question]- Liveness или readiness?
> Liveness — «перезапусти меня», readiness — «пока не присылай трафик».

> [!question]- Что нельзя проверять в liveness?
> Внешние зависимости: их сбой вызовет ненужные перезапуски.

> [!question]- Зачем startup probe?
> Даёт медленно стартующему приложению время, не убивая его liveness-пробой.

## Связанные темы

- [[N:3ea33104867981469ec0c25216311408]]
- [[N:3ea33104867981b28ed6dcb331e6f3c6]]
