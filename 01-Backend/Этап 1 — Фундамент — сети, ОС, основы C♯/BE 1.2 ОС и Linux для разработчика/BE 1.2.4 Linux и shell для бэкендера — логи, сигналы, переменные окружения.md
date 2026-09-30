---
type: topic
domain: backend
stage: 1
section: "1.2"
order: 4
status: todo
level: junior
notion_id: 3ea331048679818c8019d4ec5550c756
tags: [domain/backend, stage/1, topic/os, topic/linux, level/junior, priority/should]
reviewed:
next_review:
priority: should
time: 5
---

# Linux и shell для бэкендера: логи, сигналы, переменные окружения

↑ [[BE 1.2 ОС и Linux для разработчика|1.2 ОС и Linux для разработчика]] · ← [[BE 1.2.3 Файловая система, права, дескрипторы|Предыдущая]] · → [[BE 1.2.5 Кодировки, часовые пояса, время на сервере|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~5 мин чтения</span><span class="chip">Уровень: junior</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> Сервисы живут в Linux-контейнерах. Бэкендер должен уметь зайти в контейнер, посмотреть логи и процессы, понять, почему сервис не стартует или не останавливается корректно.

## Подтемы
- [ ] Переменные окружения и конфигурация .NET
- [ ] Сигналы и graceful shutdown
- [ ] Логи
- [ ] Команды для прода

## Объяснение

### Переменные окружения
Главный способ конфигурировать сервис в контейнере (12-factor app).
```bash
export ConnectionStrings__Postgres="Host=db;Database=clinic;Username=app;Password=..."
printenv | grep ASPNETCORE
```
В .NET переменные окружения — один из провайдеров конфигурации. Двойное подчёркивание `__` = разделитель уровней (`:` в JSON):
```csharp
// appsettings.json: { "Minio": { "Endpoint": "minio:9000" } }
// переопределение в docker-compose: Minio__Endpoint=minio-prod:9000
var endpoint = builder.Configuration["Minio:Endpoint"];
```
Важные: `ASPNETCORE_ENVIRONMENT` (Development, Staging, Production), `ASPNETCORE_URLS` или `ASPNETCORE_HTTP_PORTS`, `DOTNET_` для настроек рантайма (`DOTNET_gcServer`).

### Сигналы
- `SIGTERM` (15) — вежливая просьба завершиться. Docker и Kubernetes шлют его при остановке.
- `SIGKILL` (9) — немедленное убийство, перехватить нельзя. Docker шлёт его через 10 секунд (`stop_grace_period`) после SIGTERM.
- `SIGINT` (2) — Ctrl+C.
- `SIGHUP` — часто «перечитать конфиг» (nginx).

.NET Generic Host ловит SIGTERM и запускает **graceful shutdown**: перестаёт принимать запросы, дожидается текущих, вызывает `StopAsync` у фоновых сервисов.
```csharp
builder.Services.Configure<HostOptions>(o => o.ShutdownTimeout = TimeSpan.FromSeconds(25));

public class Worker(ILogger<Worker> log) : BackgroundService
{
    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        while (!stoppingToken.IsCancellationRequested)       // токен отменится по SIGTERM
            await ProcessBatchAsync(stoppingToken);
    }
}
```
> [!warning] PID 1 и shell-форма ENTRYPOINT
> Если в Dockerfile `ENTRYPOINT` написан в shell-форме (`ENTRYPOINT dotnet app.dll`), PID 1 — это shell, который не пересылает SIGTERM приложению. Сервис убивается по SIGKILL без graceful shutdown. Используйте exec-форму: `ENTRYPOINT ["dotnet", "app.dll"]`.

### Логи
- В контейнере: `docker logs -f --tail 200 service`, `docker compose logs -f patient_storage`.
- На хосте с systemd: `journalctl -u nginx -f --since "10 min ago"`.
- Структурированные JSON-логи удобно фильтровать через `jq`.

### Команды, которые пригодятся на проде
```bash
docker exec -it patient_storage sh          # зайти в контейнер
ps aux | grep dotnet                        # процессы
top / htop                                  # CPU и память
df -h ; du -sh /var/lib/docker/*            # место на диске
free -m                                     # память
ss -tlnp                                    # какие порты слушаются
curl -s localhost:8080/health | jq          # проверить сервис изнутри
env | sort                                  # переменные окружения процесса
tail -f /var/log/nginx/error.log
```

## Нюансы и подводные камни
- Секреты в переменных окружения видны через `docker inspect` и `/proc/<pid>/environ`. Для чувствительного — secrets-механизмы (Docker secrets, Vault, Kubernetes Secrets).
- Переменные читаются при старте: изменение требует перезапуска (кроме файловых конфигов с `reloadOnChange`).
- Exit code 137 = SIGKILL (часто OOMKilled), 143 = SIGTERM.
- Минимальные образы (alpine, chiseled) не содержат bash, curl и ps: для отладки используют `docker debug` или временный образ.

## Вопросы с ответами
> [!question]- Как сервис на .NET узнаёт о том, что его останавливают, и что должен сделать?
> Получает SIGTERM. Generic Host отменяет stoppingToken и вызывает StopAsync у hosted-сервисов. Сервис перестаёт брать новую работу, дорабатывает текущие запросы и задачи, закрывает соединения, сбрасывает буферы логов и телеметрии.

> [!question]- Чем SIGTERM отличается от SIGKILL?
> SIGTERM можно перехватить и корректно завершиться. SIGKILL убивает процесс немедленно, без возможности обработки.

> [!question]- Как передать конфигурацию в контейнер с .NET-сервисом?
> Через переменные окружения с разделителем __ (перекрывают appsettings), смонтированные файлы конфигурации, секреты. Порядок провайдеров определяет приоритет.

> [!question]- Сервис в контейнере завершился с кодом 137. Что проверить?
> Это SIGKILL: чаще всего OOMKilled (docker inspect покажет OOMKilled: true) или истёк grace period при остановке. Проверить память, лимиты и корректность обработки SIGTERM.

## Связанные темы
- Предыдущая: [[N:3ea3310486798130af0ae91c7852a262]] · Следующая: [[N:3ea3310486798180a101f27fb02bd5ef]]
- Конфигурация ASP.NET Core: [[N:3ea33104867981bf8a02c3a4b52c7ec7]]
- Graceful shutdown: [[N:3ea331048679819b82adf7f42ef440d8]]
- Bash: [[N:3ea33104867981a594f6f9930f55ceb6]]
- systemd и journalctl: [[N:3ea3310486798111bc8cdb6ca96fd5df]]
- Dockerfile: ENTRYPOINT и CMD: [[N:3ea331048679813ba277c45d46eb1f58]]
