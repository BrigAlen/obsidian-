---
type: topic
domain: devops
stage: 2
order: 8
status: todo
level: junior
tags: [domain/devops, stage/2, level/junior, priority/must]
reviewed: 
next_review: 
priority: must
time: 5
---

# Отладка контейнеров: logs, exec, inspect, stats

↑ [[DO Этап 2 · Контейнеры — Docker, docker-compose, Makefile|Этап 2 · Контейнеры: Docker, docker-compose, Makefile]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~5 мин чтения</span><span class="chip">Уровень: junior</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> «Контейнер падает/не работает — что делаете?» Нужна методичность и знание четырёх базовых команд.

## Основные команды

```bash
docker ps -a                                  # все контейнеры, статусы, коды выхода
docker logs -f --tail 200 --since 10m api     # логи (stdout/stderr)
docker logs --timestamps api 2>&1 | grep -i error
docker exec -it api sh                        # зайти в запущенный контейнер (bash, если есть)
docker exec api env; docker exec api cat /etc/hosts
docker inspect api                            # полная конфигурация и состояние (JSON)
docker inspect -f '{{.State.ExitCode}} {{.State.OOMKilled}} {{.State.Error}}' api
docker stats --no-stream                      # CPU, память, сеть, I/O в реальном времени
docker top api                                # процессы внутри
docker diff api                               # изменённые файлы в слое записи
docker events --since 1h                      # события демона
docker cp api:/app/logs/app.log ./            # достать файл
```

## Алгоритм диагностики

**1. Статус**: `docker ps -a`

| Статус | Значение |
|---|---|
| `Up` | работает (`(healthy)`/`(unhealthy)` при healthcheck) |
| `Restarting` | падает и перезапускается (restart policy): смотреть логи и код выхода |
| `Exited (0)` | завершился штатно (задача выполнена или main-процесс не задаёт долгоживущий процесс) |
| `Exited (1)` | ошибка приложения |
| `Exited (125/126/127)` | ошибка docker run / команда не исполняема / команда не найдена |
| `Exited (137)` | SIGKILL: **OOM** или `docker kill`/таймаут остановки |
| `Exited (139)` | SIGSEGV (падение, segfault) |
| `Exited (143)` | SIGTERM: корректная остановка |

**2. Логи**: `docker logs` — причина выхода почти всегда в последних строках. Нет вывода — приложение пишет в файл вместо stdout, либо падает раньше логирования.

**3. inspect**: `State.ExitCode`, `OOMKilled`, `Error`, `Config.Env`, `Config.Cmd/Entrypoint`, `Mounts`, `NetworkSettings`, `HostConfig.RestartPolicy`, `Health` (последние проверки healthcheck).

**4. Воспроизвести интерактивно**: запустить тот же образ с переопределённой командой:

```bash
docker run --rm -it --entrypoint sh myapp:1.0          # без выполнения приложения
docker run --rm -it --env-file .env --network appnet myapp:1.0 sh
docker compose run --rm --no-deps --entrypoint sh api
docker commit crashed_container debug_img && docker run -it --entrypoint sh debug_img    # для упавшего
```

**5. Сеть**: `docker exec api nc -zv db 5432`, `getent hosts db`, `docker network inspect`; образ без утилит — `docker run --rm -it --network container:api nicolaka/netshoot`.

**6. Ресурсы**: `docker stats` (память приближается к лимиту?), `docker inspect ... .HostConfig.Memory`, `dmesg | grep -i oom` на хосте.

**7. Хост**: место (`df -h`, `docker system df`), inode, лимиты файлов, версия Docker/ядра, журнал демона `journalctl -u docker`.

## Типичные причины падений

| Симптом | Причина |
|---|---|
| Сразу `Exited (0)` | PID 1 завершился: команда не долгоживущая (`nginx` без `daemon off`), демонизация в фон |
| `Exited (1)` сразу | нет конфигурации/переменных, не подключился к БД, ошибка миграции, неверный порт |
| `exec format error` | архитектура образа (arm64/amd64) или shebang/CRLF в скрипте |
| `permission denied` | права на файлы/тома, `USER` non-root, read-only ФС |
| `not found` у `/docker-entrypoint.sh` | CRLF (Windows) в скрипте или нет интерпретатора (alpine без bash) |
| `address already in use` | порт занят на хосте/в контейнере |
| Контейнер «живёт», но не отвечает | слушает `127.0.0.1`, неверный порт, healthcheck unhealthy |
| Перезапуски с 137 | нехватка памяти (лимит), утечка |
| Зависает остановка 10 с | приложение не обрабатывает SIGTERM (shell-форма, PID 1) |
| DNS не резолвится | default bridge, не та сеть, `search`/`ndots` |
| Растёт диск | логи json-file без ротации, тома, слой записи |

## Отладочные контейнеры и инструменты

- `nicolaka/netshoot` — набор сетевых инструментов (tcpdump, dig, curl, nmap);
- `docker run --pid=container:api --cap-add SYS_PTRACE ...` — доступ к процессам;
- `docker debug` (Docker Desktop/Pro) — shell в distroless;
- `docker run --rm -it -v /var/run/docker.sock:/var/run/docker.sock docker sh` — осторожно с сокетом;
- Kubernetes: `kubectl debug -it pod/name --image=busybox --target=app`, `kubectl logs --previous`, `kubectl describe pod`, `kubectl get events`.

## Логи и метрики

- драйвер логирования: `docker info --format '{{.LoggingDriver}}'`; `docker logs` работает с `json-file`/`local`/`journald`;
- централизованные логи и метрики (cAdvisor, Prometheus, Loki) для истории, когда контейнер удалён;
- `docker compose logs -f service`, `docker compose ps`, `docker compose top`.

## Вопросы с ответами

> [!question]- Контейнер постоянно перезапускается. Что делаете?
> Смотрю `docker ps -a` (код выхода), `docker logs`, `docker inspect` (OOMKilled, ошибка), временно отключаю restart policy, запускаю интерактивно с переопределённым entrypoint и проверяю конфигурацию, зависимости и ресурсы.

> [!question]- Что означает код выхода 137?
> Процесс убит SIGKILL: чаще всего OOM killer (превышен лимит памяти) или принудительная остановка после таймаута `docker stop`.

> [!question]- Как зайти в контейнер без shell?
> Использовать отладочный контейнер в том же namespace (`docker debug`, `kubectl debug`, `--pid/--network container:`), либо отладочный вариант образа.
