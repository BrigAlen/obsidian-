---
type: topic
domain: devops
stage: 6
order: 7
status: todo
level: middle
tags: [domain/devops, stage/6, level/middle, priority/nice]
reviewed: 
next_review: 
priority: nice
time: 8
---

# Terraform в команде: remote state, блокировки, модули, окружения, drift, CI для инфраструктуры

↑ [[DO Этап 6 · Infrastructure as Code — Ansible, Terraform|Этап 6 · Infrastructure as Code: Ansible, Terraform]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge nice">По желанию</span><span class="chip">~8 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> В одиночку Terraform прост, в команде — нет: удалённый state, блокировки, окружения, drift и CI. Классический senior-вопрос.

## Remote state и блокировки

Локальный `terraform.tfstate` в команде недопустим: нет общей версии, риск потери, нет блокировок, секреты на ноутбуках.

```hcl
terraform {
  backend "s3" {
    bucket                      = "tf-state-clinic"
    key                         = "prod/network/terraform.tfstate"
    region                      = "ru-central1"
    endpoints                   = { s3 = "https://storage.yandexcloud.net" }
    skip_region_validation      = true
    skip_credentials_validation = true
    skip_requesting_account_id  = true
    use_lockfile                = true          # блокировка через объект в S3 (Terraform ≥ 1.10)
    # или dynamodb_table = "tf-locks" (AWS), YDB-таблица (Yandex)
    encrypt                     = true
  }
}
```

| Backend | Особенности |
|---|---|
| **S3 + блокировка** (DynamoDB / `use_lockfile`) | популярный; **включить версионирование бакета** |
| **GCS**, **azurerm** (Blob) | нативные блокировки |
| **Terraform Cloud / HCP / Terraform Enterprise / Spacelift / env0 / Atlantis** | state, runs, права, политики |
| **GitLab-managed Terraform state** | HTTP backend, встроенные блокировки |
| **PostgreSQL / Consul / etcd** | для self-hosted |

Требования к backend: **блокировка** (предотвращает параллельные `apply`, которые портят state), **версионирование** (откат), **шифрование** (KMS), **ограниченный доступ** (IAM: только CI и несколько администраторов), **бэкапы**, отдельный бакет/аккаунт для state. Бутстрап: бакет для state создают отдельно (вручную/другим состоянием).

Застрявшая блокировка: `terraform force-unlock <ID>` — только убедившись, что другой процесс не выполняется.

## Разделение state

Один огромный state = медленный plan, большой blast radius (взрыв последствий), долгие блокировки. Делят по:

- **окружениям**: отдельный state (и часто отдельный аккаунт) для dev/stage/prod;
- **слоям и жизненному циклу**: `network` (редко меняется) → `data` (БД) → `platform` (k8s) → `apps` (часто);
- **командам/сервисам** с чёткими границами.

Связь между состояниями: `data "terraform_remote_state"` (жёсткая связь) или лучше **outputs → SSM/Parameter Store/реестр** / `data`-источники по тегам (слабая связь).

Альтернативы: **Terragrunt** (DRY backend/переменных, зависимости между модулями, `run-all`), **workspaces** (несколько state одной конфигурации: удобно для однотипных окружений, но слабая изоляция и риск ошибиться окружением — для prod чаще отдельные каталоги/аккаунты).

```text
infra/
  modules/                # переиспользуемые модули (versioned)
  live/
    dev/   {network,data,app}/ …
    stage/ {network,data,app}/ …
    prod/  {network,data,app}/ …
```

## Структура репозитория и модули

- модули в отдельном репозитории с **версиями** (теги), окружения ссылаются на конкретную версию: `source = "git::…//modules/vpc?ref=v1.4.0"`;
- **одинаковый код для окружений**, различия — в `*.tfvars`/`terragrunt.hcl`;
- реестр модулей (Terraform Registry private, GitLab Module Registry, Artifactory);
- **обновление модулей** — через PR, `terraform plan` по каждому окружению.

## Drift (дрейф)

Реальность отличается от кода/state: ручные правки в консоли, аварийные изменения, другие инструменты, автоматические изменения облака.

**Обнаружение**: `terraform plan` (показывает расхождения), **по расписанию** в CI (nightly `plan -detailed-exitcode`: код 2 = есть изменения → алерт), `plan -refresh-only`, специализированные инструменты (driftctl/Spacelift/env0/Terraform Cloud health checks), аудит-логи облака.

**Реакция**: либо **привести реальность к коду** (`apply`), либо **обновить код** по осознанному ручному изменению (и/или `import`); `lifecycle.ignore_changes` — для атрибутов, которыми управляет кто-то другой (автоскейлер, теги). **Профилактика**: запретить ручные изменения (IAM: только CI имеет права на запись; людям — read-only + break-glass), GitOps-процесс.

## CI/CD для инфраструктуры

Типовой процесс:

```text
PR:   fmt → validate → tflint → checkov/tfsec → terraform plan (для каждого затронутого окружения) → комментарий с планом в PR → ревью
merge: apply в dev/stage автоматически; prod — после ручного подтверждения (protected environment)
расписание: drift detection (plan), обновление зависимостей (Renovate), сканирование
```

```yaml
# GitLab CI (фрагмент)
.tf: { image: { name: hashicorp/terraform:1.9, entrypoint: [""] }, before_script: [cd infra/live/$ENV/app, terraform init -input=false] }

plan:
  extends: .tf
  stage: plan
  script:
    - terraform fmt -check -recursive
    - terraform validate
    - terraform plan -input=false -out=plan.tfplan -detailed-exitcode || [ $? -eq 2 ]
    - terraform show -no-color plan.tfplan > plan.txt
  artifacts: { paths: [infra/live/$ENV/app/plan.tfplan, infra/live/$ENV/app/plan.txt], expire_in: 1 week }

apply:
  extends: .tf
  stage: apply
  script: [terraform apply -input=false plan.tfplan]
  needs: [plan]
  environment: { name: $ENV }
  rules: [{ if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH, when: manual }]
  resource_group: tf-$ENV                # не параллельно для одного окружения
```

Инструменты: **Atlantis** (plan/apply по комментариям в PR), **Terraform Cloud/HCP**, **Spacelift**, **env0**, **Digger**, **Terragrunt**, GitOps для инфраструктуры (**Crossplane**, Flux tofu-controller).

Принципы: **apply только из CI** (единая точка, аудит), применяется **ровно тот план**, что прошёл ревью; **OIDC** для доступа CI к облаку (без статических ключей); минимальные права раздельно для plan (read) и apply (write); защита prod (manual approval, windows); блокировка `resource_group`.

## Политики и безопасность

- **Policy as code**: OPA/Conftest, Sentinel, `checkov`, `tfsec/trivy`: запрещать публичные бакеты, открытые `0.0.0.0/0`, незашифрованные диски, нетегированные ресурсы, слишком дорогие типы;
- **секреты**: не в `.tf` и не в `tfvars` в Git; использовать Vault/secret manager/`TF_VAR` из CI; помнить, что **state содержит секреты** (шифрование и доступ), `sensitive` не защищает state; эфемерные значения (`ephemeral` ресурсы в новых версиях);
- **права**: разделение ролей; аудит выполнения; подписанные модули/проверенные провайдеры (lock-файл, зеркала);
- **защита критичного**: `prevent_destroy`, `deletion_protection`, защита state-бакета (versioning, MFA delete), ограничение `destroy`.

## Тестирование

`terraform validate`, `terraform test` (нативные тесты, mock-провайдеры), **Terratest** (Go, реальные ресурсы в sandbox), **kitchen-terraform**, preview-окружения, `plan`-ассерты (Conftest), проверка совместимости версий провайдеров в отдельной ветке.

## Обновления и версии

Закрепляйте версии Terraform и провайдеров; обновления — отдельными PR (Renovate), сначала dev; читать changelog (breaking changes); `terraform init -upgrade`; мигрировать state-форматы осторожно; совместимость OpenTofu/Terraform (лицензия BSL у Terraform ≥1.6).

## Организация команды

- владельцы модулей и стандарты (naming, tags, структура), README и `terraform-docs`;
- review чек-лист для изменений: что будет пересоздано, влияние на prod, стоимость (**Infracost** в PR), безопасность;
- процедура **аварийных ручных изменений**: break-glass доступ, последующее отражение в коде;
- документация по восстановлению state (версии бэкенда, `import`), тренировка;
- метрики: время применения, число дрейфов, доля ручных изменений.

## Вопросы с ответами

> [!question]- Зачем нужна блокировка state и что делать, если она «зависла»?
> Блокировка предотвращает параллельные apply, портящие state. Если процесс прерван, блокировка может остаться; после проверки, что никто не выполняет операцию, снимают `terraform force-unlock`.

> [!question]- Как обнаружить и устранить drift?
> Регулярный `terraform plan` (например, по расписанию в CI с `-detailed-exitcode`) и `-refresh-only` показывают расхождения; затем либо применяют код, либо обновляют код/импортируют ресурс; профилактика — запрет ручных изменений.

> [!question]- Как организовать окружения и state в команде?
> Отдельные state (и часто аккаунты) на окружения и слои (network/data/app), переиспользуемые версионируемые модули, одинаковый код с разными переменными; изменения только через CI с plan на PR и подтверждением apply для prod.
