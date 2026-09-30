---
type: topic
domain: devops
stage: 9
order: 8
status: todo
level: final
tags: [domain/devops, stage/9, level/final, priority/must]
reviewed: 
next_review: 
priority: must
time: 14
---

# Проектируем CI-CD для Clinic в GitLab: .gitlab-ci.yml, образы, деплой на стенды

↑ [[DO Этап 9 · Собес Middle DevOps — вопросы, практика, деплой систем|Этап 9 · Собес Middle DevOps: вопросы, практика, деплой систем]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~14 мин чтения</span><span class="chip">Уровень: final</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> Задача «спроектируйте CI/CD» — классика. Нужен структурированный ответ: стадии, образы, окружения, безопасность, откат. Ниже — решение для учебного проекта Clinic (API, SPA, миграции).

## Требования

- репозиторий: monorepo (`src/Api`, `src/Worker`, `src/Migrator`, `web/`, `deploy/`);
- образы: `api`, `worker`, `migrator`, `web` → **GitLab Container Registry**;
- окружения: `review` (по MR), `staging` (из `main`), `production` (по тегу, вручную);
- деплой на серверы через **Ansible + docker compose** (позже — Helm/GitOps);
- быстрые проверки в MR, полный прогон на `main`; безопасность и отчёты;
- откат за минуты.

## Схема

```text
MR:   lint → unit-tests → build (без push) → security (SAST, secrets, SCA) → review-stand (опционально)
main: lint → tests → build+push (tag sha) → trivy → deploy staging → smoke/e2e → [ручное] prod-ready
tag vX.Y.Z: retag образов (promote sha → vX.Y.Z) → manual approve → deploy production → smoke → аннотация релиза
```

## .gitlab-ci.yml (основной каркас)

```yaml
workflow:
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
    - if: $CI_COMMIT_TAG =~ /^v\d+\.\d+\.\d+$/

stages: [lint, test, build, scan, deploy-staging, verify, release, deploy-prod]

variables:
  REGISTRY: $CI_REGISTRY_IMAGE
  DOCKER_BUILDKIT: "1"
  NUGET_PACKAGES: $CI_PROJECT_DIR/.nuget
  npm_config_cache: $CI_PROJECT_DIR/.npm

default:
  interruptible: true
  retry: { max: 1, when: [runner_system_failure, stuck_or_timeout_failure] }

include:
  - template: Security/SAST.gitlab-ci.yml
  - template: Security/Secret-Detection.gitlab-ci.yml
  - template: Security/Dependency-Scanning.gitlab-ci.yml

.dotnet: { image: mcr.microsoft.com/dotnet/sdk:9.0, cache: { key: { files: [Directory.Packages.props] }, paths: [.nuget/] } }
.node:   { image: node:22-alpine, cache: { key: { files: [web/package-lock.json] }, paths: [.npm/] } }

lint-backend:
  extends: .dotnet
  stage: lint
  script: [dotnet format --verify-no-changes]
  rules: [{ changes: ["src/**/*", "Directory.*.props"] }, { if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH }]

lint-frontend:
  extends: .node
  stage: lint
  script: [cd web, npm ci, npm run lint, npm run type-check]
  rules: [{ changes: ["web/**/*"] }, { if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH }]

lint-infra:
  stage: lint
  image: registry.example.com/tools/infra-lint:1.0     # hadolint, shellcheck, yamllint, ansible-lint, docker compose config
  script: [hadolint src/*/Dockerfile web/Dockerfile, ansible-lint deploy/ansible, docker compose -f compose.yaml config -q]

test-backend:
  extends: .dotnet
  stage: test
  services: [{ name: postgres:17, alias: db, variables: { POSTGRES_PASSWORD: test } }]
  variables: { ConnectionStrings__Default: "Host=db;Username=postgres;Password=test;Database=postgres" }
  script:
    - dotnet test -c Release --logger "junit;LogFilePath=$CI_PROJECT_DIR/junit.xml" --collect:"XPlat Code Coverage"
  coverage: '/Total\s+\|\s+(\d+\.?\d*)%/'
  artifacts: { when: always, reports: { junit: junit.xml } }

test-frontend:
  extends: .node
  stage: test
  script: [cd web, npm ci, npm run test:unit -- --coverage]
  artifacts: { when: always, reports: { junit: web/junit.xml } }

.build-image:
  stage: build
  image: docker:27
  services: [docker:27-dind]
  variables: { DOCKER_TLS_CERTDIR: "/certs" }
  before_script: [echo "$CI_REGISTRY_PASSWORD" | docker login -u "$CI_REGISTRY_USER" --password-stdin "$CI_REGISTRY"]
  script:
    - docker buildx build --cache-from type=registry,ref=$REGISTRY/$IMG:cache --cache-to type=registry,ref=$REGISTRY/$IMG:cache,mode=max
        --label org.opencontainers.image.revision=$CI_COMMIT_SHA --label org.opencontainers.image.source=$CI_PROJECT_URL
        -f $DOCKERFILE -t $REGISTRY/$IMG:$CI_COMMIT_SHORT_SHA ${PUSH:+--push} .

build-api:      { extends: .build-image, variables: { IMG: api,      DOCKERFILE: src/Api/Dockerfile,      PUSH: "1" }, rules: [{ if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH }, { if: $CI_PIPELINE_SOURCE == "merge_request_event", variables: { PUSH: "" } }] }
build-worker:   { extends: .build-image, variables: { IMG: worker,   DOCKERFILE: src/Worker/Dockerfile,   PUSH: "1" }, rules: [{ if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH }] }
build-migrator: { extends: .build-image, variables: { IMG: migrator, DOCKERFILE: src/Migrator/Dockerfile, PUSH: "1" }, rules: [{ if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH }] }
build-web:      { extends: .build-image, variables: { IMG: web,      DOCKERFILE: web/Dockerfile,          PUSH: "1" }, rules: [{ if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH }] }

trivy:
  stage: scan
  image: { name: aquasec/trivy:latest, entrypoint: [""] }
  parallel: { matrix: [{ IMG: [api, worker, migrator, web] }] }
  script: [trivy image --severity HIGH,CRITICAL --ignore-unfixed --exit-code 1 "$REGISTRY/$IMG:$CI_COMMIT_SHORT_SHA"]
  needs: [build-api, build-worker, build-migrator, build-web]
  rules: [{ if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH }]

.deploy:
  image: registry.example.com/tools/ansible:11      # ansible + коллекции
  before_script:
    - mkdir -p ~/.ssh && cp "$SSH_PRIVATE_KEY" ~/.ssh/id_ed25519 && chmod 600 ~/.ssh/id_ed25519
    - echo "$ANSIBLE_VAULT_PASSWORD" > .vault_pass && chmod 600 .vault_pass
  script:
    - cd deploy/ansible
    - ansible-playbook -i inventories/$DEPLOY_ENV playbooks/deploy.yml -e tag=$DEPLOY_TAG --vault-password-file ../../.vault_pass
  after_script: [rm -f .vault_pass ~/.ssh/id_ed25519]

deploy-staging:
  extends: .deploy
  stage: deploy-staging
  variables: { DEPLOY_ENV: staging, DEPLOY_TAG: $CI_COMMIT_SHORT_SHA }
  environment: { name: staging, url: https://staging.clinic.example.com }
  resource_group: staging
  needs: [trivy]
  rules: [{ if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH }]

smoke-staging:
  stage: verify
  image: curlimages/curl:8.10.1
  script: [curl -fsS --retry 10 --retry-delay 5 --retry-connrefused https://staging.clinic.example.com/api/health/ready]
  needs: [deploy-staging]
  rules: [{ if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH }]

promote-images:          # релиз по тегу: без пересборки, добавляем версионный тег тем же образам
  stage: release
  image: { name: gcr.io/go-containerregistry/crane:debug, entrypoint: [""] }
  parallel: { matrix: [{ IMG: [api, worker, migrator, web] }] }
  script:
    - crane auth login -u "$CI_REGISTRY_USER" -p "$CI_REGISTRY_PASSWORD" "$CI_REGISTRY"
    - crane tag "$REGISTRY/$IMG:$CI_COMMIT_SHORT_SHA" "${CI_COMMIT_TAG#v}"
  rules: [{ if: $CI_COMMIT_TAG =~ /^v\d+\.\d+\.\d+$/ }]

deploy-production:
  extends: .deploy
  stage: deploy-prod
  variables: { DEPLOY_ENV: production, DEPLOY_TAG: $CI_COMMIT_TAG }
  environment: { name: production, url: https://clinic.example.com }
  resource_group: production
  when: manual
  needs: [promote-images]
  rules: [{ if: $CI_COMMIT_TAG =~ /^v\d+\.\d+\.\d+$/ }]
```

В `promote-images` образ тегируется по SHA коммита, на который указывает тег релиза: коммит уже прошёл пайплайн `main`, образы собраны и просканированы — **build once, deploy many**.

## Deploy-плейбук (идея)

1. `docker login` на сервере токеном deploy (`read_registry`);
2. рендер `.env`/`compose.yaml` (Ansible, значения из Vault);
3. `docker compose pull`;
4. запуск `migrate` (одноразово, до новой версии API), проверка кода выхода;
5. `docker compose up -d --wait --remove-orphans`;
6. smoke-тест (`uri`), при неуспехе — откат на предыдущий тег (`previous_tag` сохраняется в файле на сервере) и `fail`;
7. аннотация релиза в Grafana, уведомление в чат.

## Окружения и секреты

- **Variables** уровня окружения: `SSH_PRIVATE_KEY` (file), `ANSIBLE_VAULT_PASSWORD`, токены — `Masked` + `Protected` (доступны только на защищённых `main` и тегах `v*`);
- разные серверы и ключи для staging и production; **protected environments**: prod — ручное подтверждение, список допустимых пользователей;
- OIDC/Vault для облачных ресурсов вместо статических ключей (по мере зрелости);
- `CI_JOB_TOKEN` для registry, минимальные права deploy-токена.

## Review-окружения

`environment: review/$CI_COMMIT_REF_SLUG` + `on_stop`: короткоживущий стенд на MR (поддомен, отдельный compose-проект с TTL); удаление при закрытии MR; ограничение ресурсов.

## Качество и безопасность

- **SAST, Secret Detection, Dependency Scanning** (шаблоны GitLab), Trivy по образам, `hadolint`, `ansible-lint`;
- **Quality gate**: обязательные тесты и отсутствие критичных уязвимостей (merge только при зелёном пайплайне); покрытие нового кода;
- **Approval rules**: ревью, CODEOWNERS для `.gitlab-ci.yml`, `deploy/`, Dockerfile;
- подписанные образы (cosign) и SBOM — на следующем этапе.

## Производительность

- `rules: changes` и `needs` (DAG), `interruptible`, кэш NuGet/npm, BuildKit cache в реестре, параллельные сборки образов, лёгкие раннеры; цель: MR-пайплайн ≤ 10 минут.

## Откат и эксплуатация

- **откат**: повторный запуск `deploy-production` для предыдущего тега (образ в реестре неизменяем) или `make deploy ENV=production TAG=<prev>`;
- миграции обратно совместимы — откат кода без отката БД;
- метрики: DORA, время пайплайна, flaky, стоимость; политика очистки реестра (теги MR, сохранение релизов);
- мониторинг после релиза: аннотации, алерты, автоматический smoke.

## Развитие

- **GitOps**: CI обновляет тег образа в репозитории окружений, ArgoCD применяет;
- **Kubernetes/Helm** вместо compose; canary через Argo Rollouts;
- подписи (cosign), SBOM, admission-политики;
- e2e (Playwright) на staging, нагрузочные тесты (k6) по расписанию;
- мультипроектные пайплайны, component-каталог шаблонов CI.

## Вопросы с ответами

> [!question]- Как вы гарантируете, что в прод уходит тот же образ, что тестировали?
> Образы собираются один раз на коммите `main` и тегируются по SHA; релизный тег лишь добавляет версионный тег тому же образу (`crane tag`) — без пересборки; деплой использует неизменяемые теги.

> [!question]- Как обеспечить безопасность деплоя в prod из CI?
> Protected variables/environments, ручное подтверждение, отдельные ключи/серверы, минимальные права токенов, `resource_group` против параллельных деплоев, OIDC вместо статических секретов и аудит запусков.

> [!question]- Как организовать откат в этой схеме?
> Перезапуск деплоя на предыдущий версионный тег (образ неизменяем и остаётся в реестре) при обратно совместимых миграциях БД; автоматический откат при неудачном smoke-тесте.
