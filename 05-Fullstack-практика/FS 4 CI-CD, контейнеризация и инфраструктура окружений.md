---
type: topic
domain: fullstack
stage: 0
order: 4
notion_id: ebcb8d229f914f90878c2f656a7ea836
status: todo
level: middle+
tags: [domain/fullstack, kind/project, level/middle+, priority/should]
priority: should
time: 7
---

# CI-CD, контейнеризация и инфраструктура окружений

↑ [[FS Fullstack-практика]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~7 мин чтения</span><span class="chip">Уровень: middle+</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> Показывает путь от коммита до продакшна: контейнеры, пайплайн, окружения и безопасность. Связывает Backend/Frontend с DevOps.

## Цель

Автоматизировать поставку проекта Clinic: воспроизводимые образы, CI/CD-пайплайн, окружения (dev/staging/prod), инфраструктуру как код, безопасное хранение секретов, миграции БД и стратегию релиза/отката.

## Контейнеризация

- **api / worker / migrator**: multi-stage Dockerfile (`sdk` → `aspnet:*-chiseled`), non-root, порт 8080, `HEALTHCHECK` на уровне оркестратора, конфигурация из окружения;
- **web**: Node-сборка → `nginx-unprivileged` с SPA fallback, кэш-заголовками и runtime-конфигом (`config.json` из переменных окружения — один образ на все окружения);
- `.dockerignore`, фиксированные версии базовых образов, OCI-лейблы (`revision`, `source`, `version`), кэш BuildKit;
- **compose** для dev: `db`, `redis`, `keycloak` (импорт realm), `api`, `worker`, `web`, `mailhog`/`otel-collector`; `make up` поднимает всё; профили (`debug`, `observability`); healthcheck и `depends_on: service_healthy`.

## Пайплайн

```text
MR:    lint → unit-тесты → интеграционные (Testcontainers) → contract-check (OpenAPI) → SAST/SCA/secrets → сборка образов (без push) → review-стенд
main:  + сборка и push образов (tag sha) → Trivy → deploy staging → migrate → smoke/e2e → готов к релизу
tag:   promote образов (sha → vX.Y.Z) → ручное подтверждение → deploy production (canary/rolling) → smoke → аннотация релиза
```

Принципы: **fail fast**, параллельные независимые задания, кэш зависимостей/слоёв, отмена устаревших пайплайнов, `rules: changes` для monorepo, **build once, deploy many**, артефакты неизменяемы, защищённые переменные/окружения.

### Фрагмент `.gitlab-ci.yml`

```yaml
stages: [lint, test, build, scan, deploy-staging, verify, release, deploy-prod]

contract:
  stage: test
  script:
    - npx @stoplight/spectral-cli lint api/openapi.yaml
    - oasdiff breaking "origin/$CI_DEFAULT_BRANCH:api/openapi.yaml" api/openapi.yaml --fail-on ERR
    - npm --prefix web run gen:api && git diff --exit-code web/src/api

e2e:
  stage: verify
  image: mcr.microsoft.com/playwright:v1.48.0-noble
  script:
    - npm --prefix web ci
    - BASE_URL=https://staging.clinic.example.com npx playwright test --project=chromium
  artifacts: { when: always, paths: [web/playwright-report], expire_in: 1 week }
  needs: [deploy-staging]

deploy-production:
  stage: deploy-prod
  environment: { name: production, url: https://clinic.example.com }
  resource_group: production
  when: manual
  rules: [{ if: '$CI_COMMIT_TAG =~ /^v\d+\.\d+\.\d+$/' }]
  script:
    - helm upgrade --install clinic deploy/helm/clinic -n clinic -f deploy/values/prod.yaml --set global.tag=${CI_COMMIT_TAG#v} --atomic --wait --timeout 10m
    - curl -fsS --retry 10 --retry-delay 5 https://clinic.example.com/api/health/ready
```

## Окружения

| Окружение | Назначение | Данные | Деплой |
|---|---|---|---|
| **dev** (локально) | разработка | seed, синтетика | `make up` (compose) |
| **review** | стенд на MR | синтетика, короткоживущий | автоматически на MR, удаляется при закрытии |
| **staging** | приёмка, e2e, нагрузка | обезличенная копия/синтетика | автоматически из `main` |
| **production** | пользователи | реальные | по тегу, вручную, с защитой |

Принципы: одинаковые образы и чарты, различаются `values` и секреты; staging максимально близок к проду; ограниченный доступ к prod; защита переменных и веток.

## Инфраструктура как код

- **Terraform**: сеть (VPC/подсети/SG), кластер Kubernetes (managed), managed PostgreSQL/Redis (или ВМ), объектное хранилище, DNS, IAM, реестр; remote state с блокировкой, окружения в отдельных state; plan на MR, apply из CI;
- **Helm-чарт** `clinic` (Deployment/Service/Ingress/HPA/PDB/ConfigMap/ExternalSecret, Job миграций как pre-upgrade hook), values per environment;
- **GitOps (ArgoCD)**: репозиторий окружений, CI обновляет тег образа, агент синхронизирует; откат — `git revert`;
- **Ansible** (если ВМ): `common`, `docker`, `nginx`, `stack` роли; шаблоны `.env`/compose/nginx; Vault;
- политики и проверки: `tflint`, `checkov`, `helm lint`, `kubeconform`, `conftest/Kyverno`.

## Секреты и конфигурация

- **не в Git и не в образах**: External Secrets Operator + Vault/облачный менеджер (или SOPS/Sealed Secrets);
- отдельные секреты для окружений, минимальные права: БД-пользователи `migrator` (DDL) и `app` (DML);
- CI: **Masked/Protected** переменные, OIDC к облаку вместо статических ключей, `CI_JOB_TOKEN`;
- конфигурация — ConfigMap/переменные; рестарт при изменении (checksum/reloader);
- сканирование секретов (gitleaks, secret detection), ротация, аудит.

## Миграции БД

- отдельный шаг (Job/`migrator`) **до** выкатки API; обратно совместимые (expand/contract); `lock_timeout`, `CREATE INDEX CONCURRENTLY`;
- тестируются на чистой БД и на копии данных; линтер миграций (squawk);
- откат кода не требует отката схемы; деструктивные изменения — отложенным релизом.

## Стратегия релиза и откат

- **rolling update** с `maxUnavailable: 0`, readiness/startup probes, PDB, graceful shutdown; для критичных изменений — **canary** (Argo Rollouts: 10% → 50% → 100% с анализом p95/5xx) или blue-green;
- **feature flags** для постепенного включения функций;
- **автооткат**: `helm --atomic`, провал smoke-теста, провал анализа canary;
- **ручной откат**: предыдущий тег (образ неизменяем) / `argocd app rollback` / `git revert`;
- совместимость версий API и SPA при раздельной выкатке (backend первым, обратно совместимый);
- **окна релизов**, коммуникация, аннотации на дашбордах.

## Безопасность цепочки

- Trivy (образы/IaC), SAST, SCA (Dependabot/Renovate), hadolint;
- SBOM (Syft) и подпись образов (cosign), admission-политики (Kyverno) на проверку подписи;
- защищённые ветки, обязательные ревью и CODEOWNERS на `.gitlab-ci.yml`, `deploy/`, Dockerfile;
- runner'ы: эфемерные, изолированные, без лишних прав; запрет привилегированного режима без необходимости.

## Метрики и улучшение

- **DORA**: частота деплоев, lead time, change failure rate, MTTR;
- длительность пайплайна (цель MR ≤ 10 мин), flaky, cache hit;
- стоимость CI; доля автоматических откатов; время восстановления.

## Что делаем

- [ ] Dockerfile для api/worker/migrator/web, compose для dev, `make up`;
- [ ] `.gitlab-ci.yml` с полным путём commit → staging → prod, contract-check, e2e;
- [ ] Helm-чарт + values для окружений, GitOps (ArgoCD) или `helm upgrade --atomic`;
- [ ] Terraform для облачной инфраструктуры, remote state;
- [ ] Секреты через ESO/Vault (или SOPS), без секретов в Git;
- [ ] Миграции отдельным шагом, проверка совместимости;
- [ ] Сканирование (Trivy, SAST, secrets), SBOM и подпись образов;
- [ ] Стратегия canary/rollback и runbook релиза;
- [ ] Дашборд DORA.

## Результат / артефакты

- образы в реестре с версиями и SBOM; чарт и values; Terraform-модули;
- работающий пайплайн (ссылка на успешные запуски), review-стенд на MR;
- документ «Как выпустить релиз и откатиться» (runbook), схема окружений;
- метрики пайплайна и DORA.

## Что рассказать на собесе

- как устроен путь от коммита до прода и почему «build once, deploy many»;
- как организованы окружения, секреты и миграции без простоя;
- какие проверки безопасности и качества встроены и какие гейты блокируют релиз;
- как выполняется откат и как вы проверяете успех релиза (smoke, canary-анализ, метрики);
- что измеряете (DORA) и что улучшили (время пайплайна, стабильность).
