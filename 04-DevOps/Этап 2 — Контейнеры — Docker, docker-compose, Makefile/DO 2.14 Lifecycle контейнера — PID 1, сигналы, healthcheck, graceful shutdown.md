---
type: topic
domain: devops
stage: 2
order: 14
status: todo
level: junior
tags: [domain/devops, stage/2, level/junior, priority/must]
reviewed: 
next_review: 
priority: must
time: 5
---

# Lifecycle контейнера: PID 1, сигналы, healthcheck, graceful shutdown

↑ [[DO Этап 2 · Контейнеры — Docker, docker-compose, Makefile|Этап 2 · Контейнеры: Docker, docker-compose, Makefile]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~5 мин чтения</span><span class="chip">Уровень: junior</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> Graceful shutdown и обработка сигналов — частая причина потерянных запросов при деплое. Связывает Docker и Kubernetes.

## Жизненный цикл

```text
created → running → (paused) → stopping → exited → removed
                      └── healthcheck: starting → healthy / unhealthy
```

`docker stop`: отправляет **SIGTERM** PID 1, ждёт `--time`/`stop_grace_period` (10 с по умолчанию), затем **SIGKILL**. `docker kill` — сразу SIGKILL (или другой сигнал). В Kubernetes: SIGTERM → `terminationGracePeriodSeconds` (30 с) → SIGKILL.

## PID 1 в контейнере

Процесс с PID 1 в своём PID namespace — особенный:

1. **Сигналы**: ядро **не применяет действия по умолчанию** для PID 1: если процесс не установил обработчик SIGTERM, сигнал игнорируется → контейнер «не останавливается» 10 секунд и убивается SIGKILL.
2. **Зомби**: PID 1 обязан вызывать `wait()` для осиротевших потомков; иначе накапливаются процессы-зомби.

Типичные ошибки:

| Проблема | Причина | Решение |
|---|---|---|
| Остановка 10 с, код 137 | shell-форма `CMD npm start` (PID 1 = `sh`, приложение — дочерний и сигнал не получает) | exec-форма `CMD ["node","server.js"]`, `exec` в скриптах |
| Скрипт-обёртка съедает сигналы | `./entrypoint.sh` запускает приложение без `exec` | `exec "$@"` в конце |
| Зомби | приложение порождает процессы, не собирая их | init-процесс: `docker run --init`, `init: true` в compose, **tini**/dumb-init |
| Приложение не реагирует на SIGTERM | нет обработчика (Node: `process.on('SIGTERM')`, Python: `signal`, .NET: генерик-хост обрабатывает автоматически) | реализовать graceful shutdown |

```dockerfile
# tini как init
RUN apk add --no-cache tini
ENTRYPOINT ["/sbin/tini", "--", "docker-entrypoint.sh"]
CMD ["node", "server.js"]
```

Для .NET: `IHostApplicationLifetime`, `Host.ShutdownTimeout`; Node.js: `server.close()`; `npm start` **не** передаёт сигналы: запускать `node` напрямую.

## Graceful shutdown

Последовательность корректного завершения:

1. Получить SIGTERM.
2. **Перестать принимать новые запросы**: readiness → not ready (в Kubernetes — убрать из Endpoints), закрыть listener.
3. **Дождаться завершения текущих запросов** (с таймаутом).
4. Завершить фоновые задачи/очереди (закоммитить offsets, вернуть сообщения), сбросить буферы, логи, метрики/трейсы.
5. Закрыть соединения с БД/кэшем.
6. Выйти с кодом 0.

```csharp
// .NET
builder.Host.ConfigureHostOptions(o => o.ShutdownTimeout = TimeSpan.FromSeconds(25));
app.Lifetime.ApplicationStopping.Register(() => logger.LogInformation("Получен сигнал остановки"));
```

**Согласование таймаутов**: `terminationGracePeriodSeconds` (K8s) / `stop_grace_period` > `ShutdownTimeout` приложения > время обработки самого долгого запроса. Балансировщик должен перестать направлять трафик до SIGTERM: в Kubernetes — **`preStop` hook** с паузой (`sleep 5–10`) из-за задержки распространения Endpoints:

```yaml
lifecycle:
  preStop: { exec: { command: ["sh", "-c", "sleep 10"] } }
terminationGracePeriodSeconds: 45
```

## Healthcheck

```dockerfile
HEALTHCHECK --interval=30s --timeout=3s --start-period=30s --retries=3 \
  CMD curl -fsS http://localhost:8080/health/live || exit 1
```

- состояния: `starting` (льготный период) → `healthy` / `unhealthy`;
- Docker сам не перезапускает unhealthy (Swarm/K8s/autoheal — да);
- **различайте**: *liveness* («процесс жив») и *readiness* («готов принимать трафик»: БД доступна, прогрев завершён). Проверка liveness, зависящая от внешних систем, приводит к каскадным перезапускам;
- лёгкая проверка (без тяжёлых запросов), быстрый ответ, без побочных эффектов;
- в образе должен быть инструмент проверки (curl/wget) или встроенная команда приложения (`myapp healthcheck`); distroless: проверка через само приложение.

В Kubernetes: `livenessProbe`, `readinessProbe`, `startupProbe` (см. отдельную тему).

## Старт

- **init-задачи** (миграции, ожидание зависимостей) лучше отдельным шагом/контейнером (`init container`, compose `service_completed_successfully`);
- приложение должно переживать временную недоступность зависимостей (retry с backoff) — не «падать сразу»;
- `start_period`/`startupProbe` для медленного старта;
- конфигурация через переменные окружения, файлы секретов; ошибка конфигурации — **fail fast** с понятным сообщением.

## Перезапуски

Restart policy + backoff (Docker удваивает задержку до 1 мин; Kubernetes: CrashLoopBackOff до 5 мин). Задача — не «перезапускать вечно», а исправлять причину: алерт на число перезапусков.

## Запись логов и сигналы

- логи в stdout/stderr, без буферизации (`PYTHONUNBUFFERED=1`, `console.log`);
- `SIGHUP` для перечитывания конфигурации (nginx `reload`), `SIGUSR1` — переоткрытие логов; `STOPSIGNAL SIGQUIT` для nginx (graceful) вместо SIGTERM (быстрое);
- `docker kill --signal=HUP web`.

## Проверка

```bash
docker run -d --name t myapp && time docker stop t          # 10+ с → сигнал не обрабатывается
docker inspect -f '{{.State.ExitCode}}' t                     # 143 (SIGTERM) хорошо, 137 (SIGKILL) плохо
docker top t                                                  # PID 1 — это ваше приложение?
docker run --init ...; docker exec t ps -ef                   # зомби
```

## Вопросы с ответами

> [!question]- Почему контейнер останавливается 10 секунд и завершается кодом 137?
> Приложение не получило/не обработало SIGTERM (часто из-за shell-формы CMD или скрипта без exec), и Docker по таймауту послал SIGKILL.

> [!question]- Зачем нужен init (tini) в контейнере?
> PID 1 должен пересылать сигналы и собирать зомби-процессы. tini выполняет эту роль, если приложение само этого не делает.

> [!question]- Как реализовать корректную остановку сервиса при деплое в Kubernetes?
> Обработать SIGTERM: перевести readiness в «не готов», завершить текущие запросы в пределах таймаута; preStop с паузой, согласованные `terminationGracePeriodSeconds` и shutdown timeout приложения.
