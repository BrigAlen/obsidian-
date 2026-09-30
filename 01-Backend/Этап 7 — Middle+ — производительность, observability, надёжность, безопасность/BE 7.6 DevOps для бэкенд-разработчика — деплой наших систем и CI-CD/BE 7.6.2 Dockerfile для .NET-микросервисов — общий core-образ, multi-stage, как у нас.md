---
type: topic
domain: backend
stage: 7
section: "7.6"
order: 2
status: todo
level: senior
notion_id: 3ea33104867981548b3aef7030878932
tags: [domain/backend, stage/7, level/senior, topic/devops, topic/docker, topic/dotnet, priority/nice]
reviewed:
next_review:
priority: nice
time: 3
---

# Dockerfile для .NET-микросервисов: общий core-образ, multi-stage, как у нас

↑ [[BE 7.6 DevOps для бэкенд-разработчика — деплой наших систем и CI-CD|7.6 DevOps для бэкенд-разработчика: деплой наших систем и CI/CD]] · ← [[BE 7.6.1 Путь кода до прода — сборка, образ, registry, миграции, деплой|Предыдущая]] · → [[BE 7.6.3 Как поднимается Clinic — docker compose, Makefile, порядок запуска, healthcheck|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge nice">По желанию</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: senior</span></div>
<!-- meta:end -->


> [!info] Зачем это на собесе
> Написать хороший Dockerfile для .NET — типичное практическое задание.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

Multi-stage сборка: тяжёлый SDK-образ для сборки, лёгкий runtime-образ для запуска.

```dockerfile
# syntax=docker/dockerfile:1
FROM mcr.microsoft.com/dotnet/sdk:9.0 AS build
WORKDIR /src
# сначала только файлы проектов — кэш слоя restore
COPY Directory.Build.props Directory.Packages.props ./
COPY src/Orders.Api/Orders.Api.csproj src/Orders.Api/
COPY src/Orders.Domain/Orders.Domain.csproj src/Orders.Domain/
RUN --mount=type=cache,target=/root/.nuget/packages dotnet restore src/Orders.Api/Orders.Api.csproj
COPY src/ src/
RUN dotnet publish src/Orders.Api/Orders.Api.csproj -c Release -o /app --no-restore /p:UseAppHost=false

FROM mcr.microsoft.com/dotnet/aspnet:9.0-noble-chiseled AS final
WORKDIR /app
COPY --from=build /app .
USER $APP_UID                       # не root
ENV ASPNETCORE_HTTP_PORTS=8080
EXPOSE 8080
ENTRYPOINT ["dotnet", "Orders.Api.dll"]
```

**Общий базовый (core) образ**: команда собирает свой образ на основе `aspnet` с часто нужным (корневые сертификаты, шрифты для генерации PDF, часовой пояс, локали, инструменты диагностики) и публикует в приватный registry. Сервисы наследуют его — единые обновления безопасности и меньше дублирования.

Практики:

- `.dockerignore` (`bin/`, `obj/`, `.git`, `node_modules`).
- Порядок слоёв от редко к часто меняющимся.
- Слои кэша NuGet (`--mount=type=cache`).
- Минимальные образы (chiseled/alpine), запуск не от root, read-only файловая система.
- Метки `org.opencontainers.image.*` (версия, коммит).
- Сканирование образа (Trivy, Grype).
- Встроенная публикация: `dotnet publish /t:PublishContainer` без Dockerfile.

## Нюансы и подводные камни

- Кириллица в PDF без шрифтов в образе — квадраты.
- `alpine` (musl) иногда несовместим с нативными библиотеками.
- Секреты в `ARG`/`ENV` остаются в слоях образа.
- Большой контекст сборки замедляет `docker build`.
- Часовой пояс и локаль в контейнере: задавайте явно.

## Практика

1. Уменьшите образ сервиса с 800 МБ до ~100 МБ через multi-stage и chiseled.
2. Проверьте кэширование слоёв: изменение кода не должно вызывать повторный restore.
3. Просканируйте образ Trivy и устраните критические уязвимости.

## Вопросы с ответами

> [!question]- Зачем multi-stage?
> В финальный образ попадает только runtime и результат публикации, без SDK и исходников.

> [!question]- Зачем копировать csproj отдельно?
> Чтобы слой `restore` кэшировался и не выполнялся при изменении только кода.

## Связанные темы

- [[N:3ea3310486798125809fff12478abc94]]
- [[N:3ea33104867981a9874fd15bb01e9c43]]
