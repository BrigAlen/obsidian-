---
type: topic
domain: devops
stage: 5
order: 8
status: todo
level: middle
tags: [domain/devops, stage/5, level/middle, priority/should]
reviewed: 
next_review: 
priority: should
time: 6
---

# Probes: liveness, readiness, startup

↑ [[DO Этап 5 · Kubernetes|Этап 5 · Kubernetes]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~6 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> Неправильные probes — частая причина каскадных перезапусков и потери трафика; спрашивают различия трёх типов.

## Три вида проб

| Probe | Вопрос | При провале |
|---|---|---|
| **startupProbe** | приложение уже запустилось? | пока не пройдена, liveness/readiness не выполняются; после `failureThreshold` — контейнер убивается |
| **livenessProbe** | приложение живо (не зависло)? | kubelet **перезапускает** контейнер |
| **readinessProbe** | готово принимать трафик? | под **исключается из Endpoints** Service (трафик не идёт), контейнер не перезапускается |

Способы: `httpGet` (код 200–399), `tcpSocket` (порт открыт), `exec` (команда, код 0), `grpc` (стандартный gRPC Health Checking).

```yaml
containers:
  - name: app
    image: registry.example.com/clinic/api:1.4.2
    ports: [{ name: http, containerPort: 8080 }]
    startupProbe:
      httpGet: { path: /health/startup, port: http }
      periodSeconds: 5
      failureThreshold: 30            # до 150 с на старт
    livenessProbe:
      httpGet: { path: /health/live, port: http }
      periodSeconds: 10
      timeoutSeconds: 2
      failureThreshold: 3
    readinessProbe:
      httpGet: { path: /health/ready, port: http }
      periodSeconds: 5
      timeoutSeconds: 2
      failureThreshold: 3
      successThreshold: 1
```

Параметры: `initialDelaySeconds`, `periodSeconds`, `timeoutSeconds`, `successThreshold`, `failureThreshold`, `terminationGracePeriodSeconds` (для probe).

## Что проверять

**Liveness**: «процесс жив и способен отвечать» — **лёгкая проверка без внешних зависимостей** (не БД, не другие сервисы!). Цель — выявить «зависание» (deadlock, исчерпан пул потоков). Если liveness зависит от БД, то при сбое БД все поды начнут перезапускаться: каскадный отказ и усугубление инцидента.

**Readiness**: «можно ли сейчас направлять запросы»: инициализация завершена, прогрев кэша, соединения с критичными зависимостями установлены; может учитывать БД/кэш (тогда при сбое зависимости под выводится из балансировки, но не убивается). Временная перегрузка: readiness может возвращать 503, чтобы сбросить нагрузку.

**Startup**: для медленных приложений (.NET с прогревом, JVM): защищает от преждевременного liveness; даёт большое окно запуска без увеличения `initialDelaySeconds`.

### ASP.NET Core Health Checks

```csharp
builder.Services.AddHealthChecks()
    .AddCheck("self", () => HealthCheckResult.Healthy(), tags: new[] { "live" })
    .AddNpgSql(connectionString, tags: new[] { "ready" })
    .AddRedis(redisConnection, tags: new[] { "ready" });

app.MapHealthChecks("/health/live",  new HealthCheckOptions { Predicate = r => r.Tags.Contains("live") });
app.MapHealthChecks("/health/ready", new HealthCheckOptions { Predicate = r => r.Tags.Contains("ready") });
```

## Типичные ошибки

| Ошибка | Последствие |
|---|---|
| Нет readiness | трафик идёт на под до готовности → 5xx при деплое |
| Liveness проверяет БД/зависимости | каскадные перезапуски при сбое зависимости |
| Слишком агрессивные пороги (`timeoutSeconds: 1`, `failureThreshold: 1`) | ложные перезапуски под нагрузкой (GC-паузы, CPU throttling) |
| Одинаковые liveness и readiness | нельзя отделить «не готов» от «завис» |
| Нет startupProbe у медленного приложения | перезапуски в цикле во время старта (`CrashLoopBackOff`) |
| Probe на тяжёлый эндпоинт | создаёт нагрузку, ложные отказы |
| Probe проходит через Ingress/аутентификацию | пробы — напрямую на под, без авторизации |
| Прослушивание `127.0.0.1` | kubelet обращается к IP пода: probe не проходит |
| Не учтён graceful shutdown | при остановке readiness должна стать «не готов» до закрытия |

## Probes и rolling update

Поток трафика на новый под начинается **после readiness** (и `minReadySeconds`); пока нет — Deployment не считает под доступным; неудачный rollout останавливается (`progressDeadlineSeconds`). При остановке пода: readiness → «не готов», удаляется из Endpoints (есть задержка распространения → `preStop` sleep), SIGTERM, graceful shutdown.

## Graceful shutdown

```yaml
lifecycle:
  preStop: { exec: { command: ["sh", "-c", "sleep 10"] } }     # даём время убраться из Endpoints/LB
terminationGracePeriodSeconds: 45                              # > preStop + время завершения запросов
```

В приложении: обработка SIGTERM, переключение readiness на «не готов», завершение запросов (`ShutdownTimeout` .NET < `terminationGracePeriodSeconds`).

## Диагностика

```bash
kubectl describe pod api-xxx          # Events: Liveness probe failed: HTTP probe failed with statuscode: 503 / Readiness probe failed / Startup probe failed
kubectl get pod api-xxx -o jsonpath='{.status.containerStatuses[0].restartCount}'
kubectl logs api-xxx --previous
kubectl get endpoints api             # список готовых адресов
kubectl exec -it api-xxx -- wget -qO- localhost:8080/health/ready
```

Причины провала: медленный старт, нехватка CPU (throttling) → таймауты, миграции при старте, зависимость недоступна, неверный путь/порт, аутентификация на health-эндпоинте, перегрузка пула потоков.

## Практики

- три пробы по назначению, отдельные эндпоинты; лёгкие и быстрые (< 100 мс);
- liveness — без внешних зависимостей; readiness — с критичными;
- разумные пороги (`failureThreshold ≥ 3`, `timeoutSeconds` 2–5);
- `startupProbe` для медленного старта;
- метрики: число перезапусков, готовность подов, время до Ready; алерты;
- на health-эндпоинтах не использовать аутентификацию и не логировать на каждый запрос (шум);
- нагрузочно проверять поведение при сбое зависимости.

## Вопросы с ответами

> [!question]- В чём разница между liveness и readiness?
> Liveness определяет, жив ли процесс: при провале контейнер перезапускается. Readiness определяет готовность принимать трафик: при провале под убирается из балансировки, но не перезапускается.

> [!question]- Почему liveness не должна зависеть от БД?
> При сбое БД все поды провалят проверку и будут перезапущены одновременно, что ухудшит ситуацию. Зависимости проверяют в readiness.

> [!question]- Зачем startupProbe?
> Даёт медленно стартующему приложению достаточное время на запуск, не вызывая преждевременных перезапусков liveness-пробой и не требуя огромных initialDelaySeconds.
