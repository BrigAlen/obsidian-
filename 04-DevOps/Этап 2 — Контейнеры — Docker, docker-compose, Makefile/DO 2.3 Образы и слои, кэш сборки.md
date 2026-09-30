---
type: topic
domain: devops
stage: 2
order: 3
status: todo
level: junior
tags: [domain/devops, stage/2, level/junior, priority/must]
reviewed: 
next_review: 
priority: must
time: 5
---

# Образы и слои, кэш сборки

↑ [[DO Этап 2 · Контейнеры — Docker, docker-compose, Makefile|Этап 2 · Контейнеры: Docker, docker-compose, Makefile]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~5 мин чтения</span><span class="chip">Уровень: junior</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> Слои и кэш определяют скорость сборки и размер образов; вопрос о порядке инструкций в Dockerfile — классика.

## Слои

Образ состоит из **неизменяемых слоёв** (layers). Каждая инструкция `RUN`, `COPY`, `ADD` создаёт слой; `ENV`, `CMD`, `LABEL` и т. п. — метаданные.

```text
FROM mcr.microsoft.com/dotnet/aspnet:9.0      ── базовые слои
COPY --from=build /app/publish .              ── слой с файлами приложения
```

```bash
docker image inspect app:1.0 | jq '.[0].RootFS.Layers'
docker history app:1.0                         # какие инструкции, размеры слоёв
docker system df -v
dive app:1.0                                   # анализ слоёв (утилита dive)
```

Свойства:

- слои **общие** между образами: одинаковый базовый слой хранится на диске один раз и скачивается один раз;
- содержимое адресуется хэшем (`sha256`): изменение файла → новый слой;
- удаление файла в более позднем слое **не уменьшает** размер (файл остаётся в нижнем слое): очищать нужно в том же `RUN`;
- контейнер = слои образа (read-only) + тонкий слой записи.

## Кэш сборки

Docker выполняет инструкции по порядку; если инструкция и её входные данные не изменились — берётся слой из кэша. **После первой инвалидации кэша все последующие слои пересобираются.**

Инвалидация: изменена сама инструкция, изменился контекст для `COPY`/`ADD` (хэш содержимого файлов), изменился `ARG`, изменился базовый образ (с `--pull`).

### Правильный порядок: редкие изменения — выше

```dockerfile
# плохо: любая правка кода инвалидирует установку зависимостей
COPY . .
RUN dotnet restore && dotnet publish -c Release -o /app

# хорошо: сначала файлы зависимостей
COPY *.sln ./
COPY src/Api/Api.csproj src/Api/
COPY src/Domain/Domain.csproj src/Domain/
RUN dotnet restore                       # кэшируется, пока csproj не изменились
COPY . .
RUN dotnet publish src/Api -c Release -o /app --no-restore
```

Для Node: сначала `package.json` + lock → `npm ci` → потом исходники.

### Объединение команд и очистка

```dockerfile
RUN apt-get update && apt-get install -y --no-install-recommends curl \
 && rm -rf /var/lib/apt/lists/*          # очистка в том же слое
```

## BuildKit: кэш-маунты и секреты

```dockerfile
# syntax=docker/dockerfile:1.7
FROM node:22-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN --mount=type=cache,target=/root/.npm npm ci          # кэш пакетов между сборками
COPY . .
RUN npm run build

# секреты не попадают в слои и историю
RUN --mount=type=secret,id=npmrc,target=/root/.npmrc npm ci
# docker build --secret id=npmrc,src=$HOME/.npmrc .
```

Кэш между запусками CI:

```bash
docker buildx build --cache-from type=registry,ref=registry/app:cache \
                    --cache-to   type=registry,ref=registry/app:cache,mode=max -t registry/app:1.0 --push .
```

`--cache-to type=gha` — кэш GitHub Actions; `type=local`, `type=s3`. Без общего кэша каждая сборка в CI «холодная».

## Теги и digest

- тег (`app:1.0`, `latest`) — подвижный указатель;
- **digest** (`app@sha256:...`) неизменяемо идентифицирует образ; в продакшне для воспроизводимости ссылаются на digest или неизменяемые теги;
- не полагайтесь на `latest`.

## Мультиархитектурные образы

`docker buildx build --platform linux/amd64,linux/arm64 -t app:1.0 --push .` → манифест-лист, клиент получает нужную архитектуру.

## Очистка

```bash
docker image prune; docker image prune -a --filter "until=168h"
docker builder prune
docker system prune -a --volumes       # осторожно: удаляет неиспользуемое, включая тома
```

## Вопросы с ответами

> [!question]- Почему в Dockerfile сначала копируют файлы зависимостей, а потом весь код?
> Чтобы слой установки зависимостей кэшировался: он пересобирается только при изменении файлов зависимостей, а не при каждой правке исходников.

> [!question]- Уменьшит ли размер образа удаление файла отдельной инструкцией RUN rm?
> Нет: файл остаётся в нижнем слое. Очистку нужно выполнять в том же `RUN`, где файл создан, либо использовать multi-stage build.

> [!question]- Как ускорить сборку образов в CI?
> Правильный порядок слоёв, `.dockerignore`, BuildKit cache mounts, общий внешний кэш (`--cache-from/--cache-to`), multi-stage и параллельные стадии.
