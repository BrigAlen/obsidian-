---
type: topic
domain: devops
stage: 3
order: 3
status: todo
level: middle
tags: [domain/devops, stage/3, level/middle, priority/must]
reviewed: 
next_review: 
priority: must
time: 10
---

# GitLab CI: .gitlab-ci.yml, stages, jobs, rules, runners, кэш

↑ [[DO Этап 3 · CI-CD|Этап 3 · CI-CD]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~10 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> GitLab CI — основной CI/CD в вашем стеке. Нужно уметь писать `.gitlab-ci.yml`: stages, rules, кэш, артефакты, окружения, раннеры.

## Структура

Файл `.gitlab-ci.yml` в корне репозитория. **Pipeline** состоит из **stages**, внутри — **jobs**; jobs выполняются на **runners**.

```yaml
stages: [build, test, package, deploy]

variables:
  DOTNET_CLI_TELEMETRY_OPTOUT: "1"
  NUGET_PACKAGES: $CI_PROJECT_DIR/.nuget
  IMAGE: $CI_REGISTRY_IMAGE/api

default:
  image: mcr.microsoft.com/dotnet/sdk:9.0
  interruptible: true
  retry: { max: 2, when: [runner_system_failure, stuck_or_timeout_failure] }

build:
  stage: build
  script:
    - dotnet restore --locked-mode
    - dotnet build -c Release --no-restore
  cache:
    key: { files: [packages.lock.json] }
    paths: [.nuget/]
  artifacts:
    paths: [src/**/bin/Release/]
    expire_in: 1 day

unit-tests:
  stage: test
  needs: [build]
  script:
    - dotnet test -c Release --no-build --logger "junit;LogFilePath=report.xml" --collect:"XPlat Code Coverage"
  coverage: '/Total\s+\|\s+(\d+\.?\d*)%/'
  artifacts:
    when: always
    reports:
      junit: "**/report.xml"
      coverage_report: { coverage_format: cobertura, path: "**/coverage.cobertura.xml" }

docker-image:
  stage: package
  image: docker:27
  services: [docker:27-dind]
  variables: { DOCKER_TLS_CERTDIR: "/certs" }
  before_script:
    - echo "$CI_REGISTRY_PASSWORD" | docker login -u "$CI_REGISTRY_USER" --password-stdin "$CI_REGISTRY"
  script:
    - docker build --pull -t $IMAGE:$CI_COMMIT_SHORT_SHA -t $IMAGE:$CI_COMMIT_REF_SLUG .
    - docker push --all-tags $IMAGE
  rules:
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
    - if: $CI_COMMIT_TAG

deploy-staging:
  stage: deploy
  environment: { name: staging, url: https://staging.example.com }
  script: ./scripts/deploy.sh staging $CI_COMMIT_SHORT_SHA
  rules: [{ if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH }]

deploy-prod:
  stage: deploy
  environment: { name: production, url: https://example.com }
  script: ./scripts/deploy.sh production $CI_COMMIT_TAG
  rules: [{ if: $CI_COMMIT_TAG =~ /^v\d+\.\d+\.\d+$/, when: manual }]
  resource_group: production        # не более одного деплоя одновременно
```

## Основные ключевые слова

| Слово | Назначение |
|---|---|
| `stages` | порядок стадий |
| `image`, `services` | контейнер для выполнения задания и сопутствующие сервисы (БД для тестов) |
| `script`, `before_script`, `after_script` | команды |
| `variables` | переменные |
| `rules` | условия включения задания (`if`, `changes`, `exists`, `when`) |
| `needs` | зависимости между заданиями (DAG) — не ждать всей стадии |
| `artifacts` | файлы между заданиями и для скачивания; `reports` (junit, coverage, sast, dotenv) |
| `cache` | кэш между пайплайнами (`key`, `paths`, `policy`) |
| `environment` | окружение деплоя, URL, откат, `on_stop` |
| `when` | `on_success`, `manual`, `always`, `delayed` |
| `allow_failure` | не блокирует пайплайн |
| `parallel`, `parallel:matrix` | размножение заданий |
| `extends`, `!reference`, `include`, `.hidden` шаблоны | переиспользование |
| `trigger` | дочерние и мультипроектные пайплайны |
| `resource_group` | сериализация деплоев |
| `interruptible` | отменять устаревшие пайплайны |
| `retry`, `timeout` | повторы и таймауты |

## rules и workflow

```yaml
workflow:
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
    - if: $CI_COMMIT_BRANCH && $CI_OPEN_MERGE_REQUESTS
      when: never                   # не дублировать ветка+MR-пайплайн
    - if: $CI_COMMIT_BRANCH
    - if: $CI_COMMIT_TAG

lint-frontend:
  rules:
    - changes: [web/**/*]           # только если менялся фронтенд
```

`only/except` — устаревшее; используйте `rules`.

## Переиспользование

```yaml
include:
  - project: platform/ci-templates
    ref: v2.1.0
    file: /templates/dotnet.yml
  - template: Security/SAST.gitlab-ci.yml

.deploy-base:
  image: registry.example.com/tools/kubectl:1.31
  before_script: [kubectl config use-context $KUBE_CONTEXT]

deploy-dev:
  extends: .deploy-base
  script: [helm upgrade --install api ./chart --set image.tag=$CI_COMMIT_SHORT_SHA]
```

**CI/CD components** (каталог) и шаблоны в отдельном репозитории — единые стандарты для всех сервисов.

## Runners

**Runner** — агент, выполняющий задания. **Executors**: `docker` (типовой), `kubernetes` (каждое задание — под), `shell`, `docker+machine`/autoscaler (облачные ВМ).

- **shared** (общие) и **project/group** (выделенные), теги (`tags: [docker, gpu]`) для выбора раннера;
- **protected runners**: только для защищённых веток/тегов (прод-деплой);
- регистрация: токен аутентификации, `config.toml` (`concurrent`, `[runners.docker] privileged`, `volumes`);
- **Docker-in-Docker** (`privileged = true`) — риск безопасности; альтернативы: **Kaniko**, BuildKit rootless, Buildah, socket binding (осторожно);
- автомасштабирование и эфемерные раннеры; ограничение ресурсов.

## Кэш и артефакты

- **cache**: ускорение (зависимости), «best effort», может отсутствовать; `key` по lock-файлу; `policy: pull-push / pull`;
- **artifacts**: гарантированная передача результатов между заданиями; `expire_in`; `reports`;
- кэш Docker-слоёв: `--cache-from` из реестра или BuildKit cache.

## Переменные и секреты

- **предопределённые**: `CI_COMMIT_SHA`, `CI_COMMIT_SHORT_SHA`, `CI_COMMIT_REF_SLUG`, `CI_COMMIT_TAG`, `CI_PIPELINE_ID`, `CI_REGISTRY*`, `CI_JOB_TOKEN`, `CI_ENVIRONMENT_NAME`, `CI_MERGE_REQUEST_IID`, `CI_DEFAULT_BRANCH`;
- **CI/CD Variables** (Settings → CI/CD): `Masked` (скрыть в логах), `Protected` (только для защищённых веток/тегов), `File`-тип, scope по окружению;
- секреты — из **HashiCorp Vault/облачного хранилища** (`id_tokens` + OIDC) вместо долгоживущих паролей;
- не печатать секреты (`set +x`); `CI_JOB_TOKEN` с минимальными правами.

## Окружения и review apps

`environment: name: review/$CI_COMMIT_REF_SLUG` + `on_stop` создаёт временное окружение под MR и удаляет его по закрытию; страница **Environments** показывает деплои и позволяет откат (повторный запуск прошлого деплоя). **Protected environments** — ручное подтверждение и список допустимых пользователей.

## Практики

- короткий MR-пайплайн, `interruptible` для отмены устаревших;
- `needs` для DAG: ускорение;
- `parallel:matrix`: тесты на нескольких версиях;
- сохранение отчётов (JUnit, покрытие, SAST, контейнерное сканирование) — виджеты в MR;
- **Merge Trains** и `merge request pipelines` — проверка результата слияния;
- `needs:project`, `trigger` для мультирепо;
- **линтинг** CI-файла (CI Lint, `glab ci lint`).

## Вопросы с ответами

> [!question]- Чем cache отличается от artifacts?
> Cache — ускорение между пайплайнами (зависимости), хранится на раннере/в хранилище и может отсутствовать. Artifacts — результаты заданий, гарантированно передаваемые следующим заданиям и доступные для скачивания.

> [!question]- Зачем protected variables и protected runners?
> Секреты продакшна доступны только заданиям на защищённых ветках/тегах и выполняются только на доверенных раннерах, исключая утечку через MR из форков или произвольных веток.

> [!question]- Что делает needs?
> Задаёт прямые зависимости между заданиями (DAG): задание стартует, как только завершились указанные, не дожидаясь всей предыдущей стадии, и может использовать их артефакты.
