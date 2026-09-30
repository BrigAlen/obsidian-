---
type: topic
domain: devops
stage: 2
order: 4
status: todo
level: junior
tags: [domain/devops, stage/2, level/junior, priority/must]
reviewed: 
next_review: 
priority: must
time: 5
---

# Dockerfile: инструкции, ENTRYPOINT и CMD, ARG и ENV

↑ [[DO Этап 2 · Контейнеры — Docker, docker-compose, Makefile|Этап 2 · Контейнеры: Docker, docker-compose, Makefile]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~5 мин чтения</span><span class="chip">Уровень: junior</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> Dockerfile — практика каждого собеседования: ENTRYPOINT против CMD, ARG против ENV, exec-форма.

## Основные инструкции

| Инструкция | Назначение |
|---|---|
| `FROM` | базовый образ (начало стадии) |
| `WORKDIR` | рабочий каталог (создаётся) |
| `COPY` | копирование файлов из контекста или другой стадии (`--from`, `--chown`) |
| `ADD` | как COPY + распаковка tar и URL (предпочитайте COPY) |
| `RUN` | выполнение команды при сборке (создаёт слой) |
| `ENV` | переменные окружения (сборка и рантайм) |
| `ARG` | переменные только на время сборки |
| `EXPOSE` | документирует порт (не публикует) |
| `USER` | пользователь для последующих инструкций и запуска |
| `ENTRYPOINT` | исполняемая команда контейнера |
| `CMD` | аргументы по умолчанию / команда по умолчанию |
| `HEALTHCHECK` | проверка здоровья |
| `VOLUME` | точка монтирования тома |
| `LABEL` | метаданные (OCI-аннотации) |
| `STOPSIGNAL`, `SHELL`, `ONBUILD` | сигнал остановки, оболочка, триггеры |

## ENTRYPOINT и CMD

- **ENTRYPOINT** — что запускается (фиксированная часть); `docker run image args` **добавляет** args к ENTRYPOINT;
- **CMD** — значения по умолчанию, которые **заменяются** аргументами `docker run`.

```dockerfile
ENTRYPOINT ["dotnet", "Api.dll"]
CMD ["--urls", "http://+:8080"]
# docker run image                 → dotnet Api.dll --urls http://+:8080
# docker run image --urls http://+:9000 → dotnet Api.dll --urls http://+:9000
```

Без ENTRYPOINT: `CMD ["nginx", "-g", "daemon off;"]` — команда целиком заменяется (`docker run image sh`).

### Exec-форма против shell-формы

```dockerfile
CMD ["nginx", "-g", "daemon off;"]     # exec-форма (JSON-массив): процесс = PID 1, получает сигналы
CMD nginx -g "daemon off;"             # shell-форма: /bin/sh -c "..." — PID 1 это shell, сигналы (SIGTERM) не доходят → остановка через 10 с и SIGKILL
```

**Используйте exec-форму** для ENTRYPOINT/CMD. Если нужна подстановка переменных — скрипт-обёртка с `exec "$@"`:

```bash
#!/bin/sh
set -e
# подготовка (миграции, генерация конфига из env)
exec "$@"            # exec заменяет shell процессом приложения (PID 1, получает сигналы)
```

```dockerfile
COPY docker-entrypoint.sh /usr/local/bin/
ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["dotnet", "Api.dll"]
```

## ARG и ENV

| | ARG | ENV |
|---|---|---|
| Доступно | только при сборке | при сборке и в контейнере |
| Задаётся | `--build-arg` | `-e`, `--env-file`, Dockerfile |
| Видно в образе | в `docker history` (**не** для секретов!) | в конфигурации образа и контейнере |

```dockerfile
ARG DOTNET_VERSION=9.0
FROM mcr.microsoft.com/dotnet/sdk:${DOTNET_VERSION} AS build
ARG BUILD_CONFIGURATION=Release
ARG GIT_SHA
ENV ASPNETCORE_URLS=http://+:8080 \
    DOTNET_EULA=1
LABEL org.opencontainers.image.revision=$GIT_SHA
```

ARG перед `FROM` действует только для выбора базового образа; внутри стадии ARG нужно объявить заново. **Секреты не передавайте через ARG/ENV** — используйте `RUN --mount=type=secret`.

## Пример Dockerfile для приложения

```dockerfile
# syntax=docker/dockerfile:1.7
FROM mcr.microsoft.com/dotnet/aspnet:9.0-alpine AS runtime
WORKDIR /app
RUN addgroup -S app && adduser -S app -G app
COPY --chown=app:app ./publish .
USER app
ENV ASPNETCORE_URLS=http://+:8080
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=3s --start-period=20s --retries=3 \
  CMD wget -qO- http://localhost:8080/health/live || exit 1
ENTRYPOINT ["dotnet", "Api.dll"]
```

## .dockerignore

Исключает файлы из контекста сборки: `.git`, `bin/`, `obj/`, `node_modules/`, `*.md`, `.env`, `Dockerfile`: ускоряет сборку, улучшает кэш, не утекают секреты.

## COPY против ADD

`ADD` автоматически распаковывает архивы и качает URL: неявное поведение; используйте `COPY`. Для загрузки — `RUN curl ... | tar` с проверкой контрольных сумм.

## Лучшие практики

- фиксированные версии базовых образов (`aspnet:9.0.5`, по возможности digest);
- multi-stage для уменьшения размера;
- объединять команды `RUN` с очисткой;
- **не root** (`USER`);
- один процесс на контейнер, stdout/stderr для логов;
- порядок инструкций под кэш;
- `HEALTHCHECK`;
- метаданные OCI `LABEL`;
- линт: **hadolint**, сканирование: Trivy.

## Вопросы с ответами

> [!question]- Чем ENTRYPOINT отличается от CMD?
> ENTRYPOINT задаёт исполняемую программу (аргументы `docker run` добавляются к ней), CMD — значения по умолчанию, которые полностью заменяются аргументами запуска. Часто используют вместе: ENTRYPOINT — программа, CMD — аргументы по умолчанию.

> [!question]- Почему важна exec-форма?
> Процесс запускается напрямую как PID 1 и получает сигналы (SIGTERM) для корректного завершения; в shell-форме сигналы получает `sh`, а не приложение.

> [!question]- Чем ARG отличается от ENV?
> ARG доступен только на этапе сборки, ENV сохраняется в образе и доступен в контейнере. Ни то ни другое не подходит для секретов.
