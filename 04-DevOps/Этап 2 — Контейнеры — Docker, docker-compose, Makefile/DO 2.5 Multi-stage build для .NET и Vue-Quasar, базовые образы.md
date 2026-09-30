---
type: topic
domain: devops
stage: 2
order: 5
status: todo
level: junior
tags: [domain/devops, stage/2, level/junior, priority/must]
reviewed: 
next_review: 
priority: must
time: 6
---

# Multi-stage build для .NET и Vue-Quasar, базовые образы

↑ [[DO Этап 2 · Контейнеры — Docker, docker-compose, Makefile|Этап 2 · Контейнеры: Docker, docker-compose, Makefile]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~6 мин чтения</span><span class="chip">Уровень: junior</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> Multi-stage — стандарт для компактных и безопасных образов. Ожидают пример для .NET и фронтенда (Vue/Quasar) с nginx.

## Идея

Несколько стадий `FROM` в одном Dockerfile: тяжёлая стадия сборки (SDK, компиляторы, dev-зависимости) и лёгкая финальная (только рантайм и артефакты). В итоговый образ копируются только нужные файлы через `COPY --from=`.

Плюсы: размер (сотни МБ → десятки), безопасность (нет компиляторов и исходников), кэш, единая сборка без внешних скриптов.

## .NET

```dockerfile
# syntax=docker/dockerfile:1.7
FROM mcr.microsoft.com/dotnet/sdk:9.0 AS build
WORKDIR /src
COPY Directory.Build.props Directory.Packages.props ./
COPY src/Api/Api.csproj src/Api/
COPY src/Application/Application.csproj src/Application/
COPY src/Infrastructure/Infrastructure.csproj src/Infrastructure/
RUN --mount=type=cache,target=/root/.nuget/packages dotnet restore src/Api/Api.csproj
COPY . .
RUN --mount=type=cache,target=/root/.nuget/packages \
    dotnet publish src/Api/Api.csproj -c Release -o /app/publish --no-restore /p:UseAppHost=false

FROM build AS test                   # отдельная стадия тестов: docker build --target test .
RUN dotnet test --no-build -c Release

FROM mcr.microsoft.com/dotnet/aspnet:9.0-noble-chiseled AS final
WORKDIR /app
COPY --from=build /app/publish .
USER $APP_UID                        # chiseled-образы уже содержат пользователя app (UID 1654)
ENV ASPNETCORE_HTTP_PORTS=8080
EXPOSE 8080
ENTRYPOINT ["dotnet", "Api.dll"]
```

Базовые образы .NET: `sdk` (сборка), `aspnet` (веб-рантайм), `runtime` (консоль), `runtime-deps` (self-contained/AOT); варианты: `-alpine` (musl, маленький), `-noble-chiseled` (Ubuntu без shell и пакетного менеджера, не root), `-distroless`. **Native AOT**: публикуем в один бинарь на `runtime-deps`/`chiseled-extra`: старт за миллисекунды.

## Vue/Quasar (SPA) + nginx

```dockerfile
# syntax=docker/dockerfile:1.7
FROM node:22-alpine AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN --mount=type=cache,target=/root/.npm npm ci
COPY . .
ARG VITE_APP_VERSION
RUN npm run build                     # quasar build → dist/spa

FROM nginxinc/nginx-unprivileged:1.27-alpine AS final      # nginx без root, порт 8080
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist/spa /usr/share/nginx/html
EXPOSE 8080
HEALTHCHECK CMD wget -qO- http://localhost:8080/ >/dev/null || exit 1
```

```nginx
# nginx.conf
server {
  listen 8080;
  root /usr/share/nginx/html;
  location / { try_files $uri $uri/ /index.html; }         # history fallback SPA
  location /assets/ { expires 1y; add_header Cache-Control "public, immutable"; }
  location = /index.html { add_header Cache-Control "no-cache"; }
}
```

**Конфигурация окружения во время запуска** (один образ на все окружения): генерировать `config.json` из переменных окружения в entrypoint (`envsubst`), а не вшивать адреса API при сборке.

## Полезные приёмы

- `docker build --target build .` — остановиться на стадии;
- `COPY --from=nginx:alpine /etc/nginx/nginx.conf ...` — копирование из внешнего образа;
- **параллельные стадии**: BuildKit собирает независимые стадии одновременно (бэкенд и фронтенд в одном Dockerfile);
- **стадия тестов и линтеров** отдельно; результаты в CI как артефакты (`--output`);
- **secret mount** для приватных NuGet/npm источников;
- **ARG для версий** базовых образов;
- единый Dockerfile для разных окружений vs отдельные — держите минимальные различия.

## Выбор базового образа

| Вариант | Размер | Плюсы | Минусы |
|---|---|---|---|
| Debian/Ubuntu (`-bookworm`, `-noble`) | ~100–200 МБ | совместимость (glibc), привычные инструменты | больше CVE и размер |
| `-slim` | меньше | компромисс | |
| **Alpine** | ~5–10 МБ | компактный, `apk` | musl (проблемы с некоторыми бинарями/DNS/производительностью), другие утилиты |
| **Chiseled / distroless** | минимум | нет shell и пакетного менеджера, меньше поверхности атаки, non-root | сложнее отладка (`docker debug`, ephemeral containers в K8s) |
| **scratch** | 0 | для статических бинарей (Go) | нужны сертификаты, tz вручную |

## Типичные ошибки

- копирование всего `bin/obj` с хоста (нет `.dockerignore`);
- SDK в финальном образе (1 ГБ вместо 100–200 МБ);
- исходники и `.git` в образе;
- секреты в слоях сборки;
- образ привязан к `latest`;
- приложение под root.

## Вопросы с ответами

> [!question]- Зачем multi-stage build?
> Отделить окружение сборки от рантайма: в итоговый образ попадают только артефакты, поэтому он меньше, быстрее скачивается и содержит меньше уязвимостей.

> [!question]- Как собрать фронтенд и раздать его через nginx одним Dockerfile?
> Стадия `node` собирает проект (`npm ci`, `build`), финальная стадия `nginx` копирует собранную статику (`COPY --from=build`) и конфиг с fallback на `index.html`.

> [!question]- Что такое chiseled-образ?
> Минимальный образ Ubuntu для .NET без shell и пакетного менеджера, запускаемый не от root: меньше размер и поверхность атаки.
