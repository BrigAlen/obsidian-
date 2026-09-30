---
type: topic
domain: devops
stage: 3
order: 6
status: todo
level: middle
tags: [domain/devops, stage/3, level/middle, priority/must]
reviewed: 
next_review: 
priority: must
time: 8
---

# Пайплайн для .NET-микросервисов и фронтенда в monorepo

↑ [[DO Этап 3 · CI-CD|Этап 3 · CI-CD]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~8 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> Практический кейс: CI для репозитория с несколькими сервисами и фронтендом — как не пересобирать всё на каждый коммит.

## Структура monorepo

```text
repo/
  src/
    Api/                 # .NET сервис
    Notifications/       # .NET сервис
    Shared/              # общие библиотеки
  web/                   # Vue 3 + Quasar
  deploy/                # Helm-чарты, compose, Ansible
  .gitlab-ci.yml
```

Цели: собирать и тестировать **только изменённое**, переиспользовать логику, параллелить, единая версия релиза, независимые образы сервисов.

## Определение затронутых частей

**`rules: changes`** (GitLab):

```yaml
.api-changes: &api-changes
  - src/Api/**/*
  - src/Shared/**/*
  - Directory.Packages.props

build-api:
  stage: build
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
      changes: *api-changes
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH        # на main — всегда полный прогон
  script: dotnet build src/Api -c Release
```

**Дочерние пайплайны** (`trigger:include`) — отдельный пайплайн на каждый сервис:

```yaml
api:
  trigger:
    include: src/Api/.gitlab-ci.yml
    strategy: depend
  rules: [{ changes: ["src/Api/**/*", "src/Shared/**/*"] }]
```

GitHub Actions: `on.push.paths`, `dorny/paths-filter`. Инструменты monorepo: **Nx**, **Turborepo**, **Bazel**, `nx affected`, `dotnet-affected`.

**Осторожность**: изменения общей библиотеки должны триггерить зависимые сервисы; на `main`/релизе — полная сборка как страховка.

## Шаблоны для однотипных сервисов

```yaml
.dotnet-service:
  image: mcr.microsoft.com/dotnet/sdk:9.0
  variables: { SERVICE: "" }
  script:
    - dotnet restore src/$SERVICE --locked-mode
    - dotnet build src/$SERVICE -c Release --no-restore
    - dotnet test tests/$SERVICE.Tests -c Release --no-build
  cache: { key: { files: [Directory.Packages.props] }, paths: [.nuget/] }

test-api:           { extends: .dotnet-service, variables: { SERVICE: Api } }
test-notifications: { extends: .dotnet-service, variables: { SERVICE: Notifications } }
```

Или `parallel: matrix: [{ SERVICE: [Api, Notifications] }]`.

## Пайплайн .NET-сервиса

1. **restore** (кэш NuGet, `--locked-mode`);
2. **build** (`-warnaserror`, анализаторы);
3. **unit-тесты** + покрытие (coverlet, `XPlat Code Coverage`) + JUnit-отчёт;
4. **интеграционные** тесты: Testcontainers (Docker-in-Docker) или `services:` (postgres, redis);
5. **статический анализ**: `dotnet format --verify-no-changes`, SonarQube, SCA (`dotnet list package --vulnerable`), Trivy;
6. **package**: `docker build` multi-stage (тесты внутри стадий), публикация в Registry с тегами `sha` и версия;
7. **контрактные тесты** (Pact/OpenAPI breaking changes).

## Пайплайн фронтенда (Vue 3 + Quasar)

```yaml
web-ci:
  image: node:22-alpine
  stage: test
  cache: { key: { files: [web/package-lock.json] }, paths: [web/.npm/] }
  rules: [{ changes: ["web/**/*"] }]
  script:
    - cd web && npm ci --cache .npm --prefer-offline
    - npm run lint
    - npm run type-check
    - npm run test:unit -- --coverage
    - npm run build
  artifacts: { paths: [web/dist/spa], expire_in: 1 week }

web-image:
  stage: package
  script:
    - docker build -f web/Dockerfile -t $CI_REGISTRY_IMAGE/web:$CI_COMMIT_SHORT_SHA web
    - docker push $CI_REGISTRY_IMAGE/web:$CI_COMMIT_SHORT_SHA
```

Этапы: `npm ci` (строго по lock), линт (ESLint, Prettier), типы (`vue-tsc`), unit (Vitest), e2e (Playwright) на review-стенде, сборка (Vite/Quasar), сканирование зависимостей (`npm audit`), образ nginx со статикой, **runtime-конфигурация** (один образ на все окружения).

## Версия и релиз

- единая версия продукта по тегу `vX.Y.Z` или независимые версии сервисов (`api-1.2.0`, tag-префиксы, changesets);
- **один коммит → набор образов** с одинаковым SHA-тегом; манифест деплоя фиксирует версии каждого сервиса;
- релизный пайплайн по тегу: собрать изменённые образы, промоутить, создать Release Notes.

## Деплой

- **Helm umbrella-чарт** или набор чартов; значения версий по сервисам: `--set api.image.tag=$SHA`;
- порядок: миграции → бэкенд → фронтенд; совместимость версий (API versioning);
- smoke-тест после выкладки; автооткат при провале проверки (`helm upgrade --atomic --wait`);
- GitOps: пайплайн обновляет тег в репозитории окружений (`deploy/values-staging.yaml`), ArgoCD применяет.

## Ускорение

- **`needs`** (DAG) вместо ожидания стадий; **параллельные** сервисы;
- кэш NuGet/npm/Docker layers; общий кэш BuildKit в реестре;
- лёгкие образы раннеров (предустановленные инструменты);
- **отмена устаревших** пайплайнов (`interruptible`);
- разделение: быстрый MR-пайплайн (lint + unit) и полный nightly/для `main` (e2e, нагрузка);
- **test impact analysis**: запуск тестов затронутых проектов;
- шардирование тестов (`--filter`, `parallel: 4`).

## Окружение для интеграционных тестов

```yaml
integration:
  services:
    - name: postgres:17
      alias: db
      variables: { POSTGRES_PASSWORD: test }
    - name: redis:7
  variables:
    ConnectionStrings__Default: Host=db;Username=postgres;Password=test
  script: dotnet test tests/Api.IntegrationTests
```

Либо Testcontainers: нужен Docker (раннер с DinD или socket), изоляция лучше.

## Ошибки

- один «гигантский» пайплайн на любой коммит;
- неверные `changes` (пропуск зависимых сервисов);
- пересборка образа на каждое окружение;
- версии сервисов несовместимы при независимых релизах (нужны контракты);
- нет локального воспроизведения (`make ci`): различия между CI и локальной сборкой.

## Вопросы с ответами

> [!question]- Как не собирать весь monorepo на каждый коммит?
> Определять затронутые части по изменённым путям (`rules: changes`, path filters, nx affected), запускать дочерние пайплайны сервисов; на `main` делать полный прогон как страховку.

> [!question]- Как гарантировать совместимость сервисов при независимых релизах?
> Контрактные тесты (Pact/OpenAPI diff), версионирование API и событий, обратная совместимость, проверка на staging комплектом версий.

> [!question]- Почему образ фронтенда должен быть один на все окружения?
> Чтобы тестировать именно то, что уйдёт в прод. Адреса API и настройки подставляются при запуске (runtime config), а не при сборке.
