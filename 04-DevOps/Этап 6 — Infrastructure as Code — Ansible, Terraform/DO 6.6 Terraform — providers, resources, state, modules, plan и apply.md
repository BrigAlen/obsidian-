---
type: topic
domain: devops
stage: 6
order: 6
status: todo
level: middle
tags: [domain/devops, stage/6, level/middle, priority/nice]
reviewed: 
next_review: 
priority: nice
time: 10
---

# Terraform: providers, resources, state, modules, plan и apply

↑ [[DO Этап 6 · Infrastructure as Code — Ansible, Terraform|Этап 6 · Infrastructure as Code: Ansible, Terraform]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge nice">По желанию</span><span class="chip">~10 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> Terraform — стандарт IaC-провижининга. Нужны providers, resources, state, modules и цикл plan/apply.

## Основы

**Terraform** (HashiCorp; форк **OpenTofu** под Linux Foundation) — декларативный инструмент: на языке **HCL** описываем ресурсы, а Terraform строит **граф зависимостей**, сравнивает с **state** и реальностью, показывает **plan** и применяет **apply**. Множество провайдеров: AWS, Azure, GCP, Yandex Cloud, Kubernetes, Helm, GitHub, Cloudflare, Keycloak, PostgreSQL, Docker и др.

```bash
terraform init          # загрузка провайдеров/модулей, настройка backend
terraform fmt -recursive; terraform validate
terraform plan -out=tfplan        # что изменится (+ create, ~ update, - destroy, -/+ replace)
terraform apply tfplan            # применить сохранённый план
terraform destroy
terraform output; terraform state list; terraform show
terraform import aws_s3_bucket.b my-bucket      # взять существующий ресурс под управление (или блоки import {})
terraform taint / -replace=aws_instance.app     # пересоздать ресурс
terraform workspace list|new|select
```

## Структура конфигурации

```hcl
terraform {
  required_version = ">= 1.8"
  required_providers {
    yandex = { source = "yandex-cloud/yandex", version = "~> 0.130" }
  }
  backend "s3" {                       # удалённый state (см. следующую тему)
    bucket = "tf-state-clinic"
    key    = "prod/network.tfstate"
  }
}

provider "yandex" {
  zone      = var.zone
  folder_id = var.folder_id
  # аутентификация через переменные окружения / сервисный аккаунт, не в коде
}

variable "zone"      { type = string, default = "ru-central1-a" }
variable "env"       { type = string }
variable "vm_count"  { type = number, default = 2, validation { condition = var.vm_count <= 10, error_message = "Не более 10." } }
variable "db_password" { type = string, sensitive = true }

locals {
  name_prefix = "clinic-${var.env}"
  common_tags = { env = var.env, managed_by = "terraform" }
}

data "yandex_compute_image" "ubuntu" { family = "ubuntu-2404-lts" }    # чтение существующего

resource "yandex_vpc_network" "main" { name = "${local.name_prefix}-net" }

resource "yandex_vpc_subnet" "app" {
  name           = "${local.name_prefix}-app"
  zone           = var.zone
  network_id     = yandex_vpc_network.main.id          # неявная зависимость
  v4_cidr_blocks = ["10.10.10.0/24"]
}

resource "yandex_compute_instance" "app" {
  count       = var.vm_count
  name        = "${local.name_prefix}-app-${count.index}"
  platform_id = "standard-v3"
  resources { cores = 2, memory = 4 }
  boot_disk { initialize_params { image_id = data.yandex_compute_image.ubuntu.id, size = 30 } }
  network_interface { subnet_id = yandex_vpc_subnet.app.id, nat = false }
  metadata = { user-data = file("${path.module}/cloud-init.yaml") }
  labels   = local.common_tags

  lifecycle {
    create_before_destroy = true
    prevent_destroy       = false
    ignore_changes        = [metadata]
  }
}

output "app_ips" { value = yandex_compute_instance.app[*].network_interface[0].ip_address }
```

### Основные конструкции

| Конструкция | Назначение |
|---|---|
| **provider** | плагин для API платформы, конфигурация и версия |
| **resource** | создаваемый/управляемый объект (`тип.имя`) |
| **data** | чтение существующих данных (не создаёт) |
| **variable** | входные параметры (type, default, description, `validation`, `sensitive`) |
| **locals** | вычисляемые значения внутри модуля |
| **output** | выходные значения (для других модулей/пользователя) |
| **module** | переиспользуемая группа ресурсов |
| **`count` / `for_each`** | множественные экземпляры (`for_each` по map/set — стабильнее, чем `count` по индексу) |
| **`dynamic` block** | генерация вложенных блоков |
| **`depends_on`** | явная зависимость |
| **`lifecycle`** | `create_before_destroy`, `prevent_destroy`, `ignore_changes`, `replace_triggered_by`, `precondition/postcondition` |
| **`provisioner`** | локальные/удалённые команды (последнее средство; предпочитать cloud-init/Ansible) |
| **`moved` / `import` / `removed`** | рефакторинг и импорт без пересоздания |

Функции и выражения: `for`-выражения, `merge`, `lookup`, `concat`, `join`, `format`, `cidrsubnet`, `templatefile`, `file`, `jsonencode`, условия `cond ? a : b`, `try`, `can`, `coalesce`.

## Граф зависимостей

Неявные зависимости по ссылкам (`yandex_vpc_network.main.id`) формируют порядок; независимые ресурсы создаются **параллельно** (`-parallelism=10`). `terraform graph | dot -Tsvg`.

## State

JSON-файл (`terraform.tfstate`): сопоставление ресурсов кода с реальными объектами (ID), метаданные, **зависимости**; кэш атрибутов, ускоряет plan. Содержит **чувствительные данные в открытом виде** (пароли, ключи, адреса): защищать.

- **не редактировать вручную**; команды: `terraform state list/show/mv/rm`, `import`, `refresh`;
- **удалённый backend** (S3/Object Storage + блокировка, Terraform Cloud/HCP, GitLab-managed state, Consul, PostgreSQL) — в команде обязателен (см. отдельную тему);
- `terraform plan -refresh-only`: синхронизация state с реальностью (дрейф);
- потеря state = Terraform «забудет» ресурсы (создаст дубли/конфликты): включить версионирование бэкенда.

## Plan и apply

```text
  + create
  ~ update in-place
  - destroy
-/+ destroy and then create replacement   (ПРОВЕРЯТЬ: это потеря данных для БД/дисков)
```

Практика: **всегда читайте plan**, особенно `-/+` и `destroy`; сохраняйте план (`-out`) и применяйте именно его; в CI — plan на PR с комментарием, apply после merge; защита критичных ресурсов `prevent_destroy`, `deletion_protection` у провайдера.

## Modules

Переиспользуемый «пакет» ресурсов с входами/выходами.

```text
modules/vpc/{main.tf,variables.tf,outputs.tf,versions.tf,README.md}
envs/prod/{main.tf,terraform.tfvars,backend.tf}
```

```hcl
module "network" {
  source  = "../../modules/vpc"            # или git::https://...//modules/vpc?ref=v1.2.0, registry.terraform.io/...
  version = "~> 1.2"                       # для registry
  name    = "clinic-prod"
  cidr    = "10.10.0.0/16"
  zones   = ["ru-central1-a", "ru-central1-b"]
}

resource "yandex_compute_instance" "app" {
  subnet_id = module.network.app_subnet_ids[0]
}
```

Правила: маленькие сфокусированные модули, явные входы/выходы, версионирование через теги Git/реестр, документация (`terraform-docs`), без провайдер-конфигурации внутри модуля, тесты (`terraform test`, Terratest), не злоупотреблять вложенностью.

## Переменные и окружения

Источники значений (приоритет по возрастанию): `default` → `terraform.tfvars`/`*.auto.tfvars` → `-var-file` → `TF_VAR_name` → `-var`. Секреты — через `TF_VAR_*`, переменные CI, secret manager, **не** в репозитории; `sensitive = true` скрывает вывод (но не из state).

## Практики

- версии: `required_version`, провайдеры с `~>`, **lock-файл** `.terraform.lock.hcl` в Git;
- `terraform fmt`, `validate`, **`tflint`**, **`checkov`/`tfsec`/`trivy config`** (безопасность), `terraform-docs`, pre-commit;
- единый стиль имён и **теги/метки** на ресурсах;
- разделение state по **слоям и окружениям** (network, data, app; dev/stage/prod), а не один огромный;
- `for_each` вместо `count` для именованных ресурсов;
- не использовать `provisioner` для конфигурации ПО: cloud-init/Ansible/образы Packer;
- ресурсы с состоянием (БД, диски) — `prevent_destroy`, бэкапы;
- `terraform import`/`moved` при рефакторинге, чтобы не пересоздавать;
- документация, владельцы, процессы изменений.

## Вопросы с ответами

> [!question]- Что такое state и почему он важен?
> Файл соответствия кода и реальных ресурсов (ID, атрибуты, зависимости). По нему Terraform определяет, что создавать, менять или удалять. Содержит чувствительные данные, поэтому хранится в защищённом удалённом backend с блокировкой и бэкапом.

> [!question]- Чем count отличается от for_each?
> `count` индексирует экземпляры числами (удаление элемента из середины сдвигает индексы и вызывает пересоздание), `for_each` — по ключам map/set, что стабильнее для именованных ресурсов.

> [!question]- Что означает -/+ в plan?
> Ресурс будет уничтожен и создан заново (replace): для дисков и БД это потеря данных, поэтому такие изменения нужно проверять и защищать.
