---
type: topic
domain: devops
stage: 3
order: 8
status: todo
level: middle
tags: [domain/devops, stage/3, level/middle, priority/must]
reviewed: 
next_review: 
priority: must
time: 5
---

# Секреты и окружения: dev, staging, prod

↑ [[DO Этап 3 · CI-CD|Этап 3 · CI-CD]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~5 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> Утечка секретов — самая частая причина инцидентов. Спрашивают, где хранить, как передавать и как разделять окружения.

## Окружения

| Окружение | Данные | Доступ |
|---|---|---|
| **dev** | синтетические/обезличенные | разработчики |
| **staging** | приближено к проду (структура, объём), без реальных ПДн | команда, QA |
| **prod** | реальные | ограниченный круг, аудит |

Принципы: **изоляция** (отдельные кластеры/аккаунты/БД/ключи на окружение), **паритет** конфигурации (одинаковые образы и шаблоны, отличаются значения), **неизменяемые артефакты**, **наименьшие привилегии** (у dev нет доступа к prod-секретам), **защита прод-деплоя** (ручное подтверждение, protected branches/tags).

## Конфигурация и секреты

- **конфигурация** (URL, флаги, размеры пулов) — не секрет: переменные окружения, ConfigMap, файлы в Git (per-environment values);
- **секреты** (пароли, токены, ключи, сертификаты, строки подключения) — хранятся отдельно, шифруются, ротируются, доступ аудируется;
- **12-factor**: конфигурация через окружение, код не содержит значений окружений.

## Где НЕ хранить секреты

Git (даже в приватном репозитории и «удалив» позже — история), образы Docker (`ENV`, `ARG`, слои), логи, артефакты пайплайна, аргументы командной строки (видны в `ps`), чат/вики, `.env` в репозитории.

## Варианты хранения и доставки

| Подход | Описание | Особенности |
|---|---|---|
| **CI/CD variables** (GitLab/GitHub Secrets) | `Masked`, `Protected`, scope по окружению | просто; ограничено по ротации и аудиту |
| **HashiCorp Vault** | динамические секреты, политики, аудит, TTL | мощно; требует эксплуатации |
| **Облачные менеджеры** (AWS Secrets Manager, Yandex Lockbox, Azure Key Vault, GCP Secret Manager) | IAM-доступ, ротация, версии | удобно в облаке |
| **Kubernetes Secrets** | base64 (не шифрование!) | включить шифрование etcd, RBAC; External Secrets Operator / CSI driver синхронизируют из внешних хранилищ |
| **Sealed Secrets / SOPS (age, KMS)** | зашифрованные секреты **в Git** (GitOps) | расшифровка в кластере/пайплайне |
| **Ansible Vault** | зашифрованные файлы переменных | для конфигурации серверов |
| **OIDC / Workload Identity** | временные токены вместо паролей | лучший вариант для доступа к облаку из CI |

### Секреты в пайплайне

```yaml
deploy-staging:
  stage: deploy
  environment: staging                      # переменные с scope=staging доступны только здесь
  id_tokens:
    VAULT_ID_TOKEN: { aud: https://vault.example.com }
  script:
    - export VAULT_TOKEN=$(vault write -field=token auth/jwt/login role=deploy-staging jwt=$VAULT_ID_TOKEN)
    - DB_PASSWORD=$(vault kv get -field=password secret/clinic/staging/db)
    - ./deploy.sh staging
```

- **Masked** — скрывает значение в логах; **Protected** — только для защищённых веток/тегов; переменные типа **File** для сертификатов и ключей;
- отдельные значения для каждого окружения (scope);
- **не выводить** `env`, `set -x`, не передавать секреты как аргументы;
- **OIDC** вместо статических облачных ключей;
- токены с минимальными правами и сроком жизни; у CI — `CI_JOB_TOKEN`.

### Секреты в рантайме

- файлы секретов (`/run/secrets/db_password`, `*_FILE` переменные) безопаснее, чем ENV (видны в `docker inspect`, `/proc/<pid>/environ`, дампах);
- Kubernetes: смонтированный Secret (volume) или `envFrom`; обновляется без пересборки; перезапуск подов по хэшу (`checksum/secret` в Helm) или Reloader;
- Vault Agent / CSI: подгрузка секретов с обновлением;
- приложение читает секрет при старте/обновлении и не логирует.

## Разделение по окружениям

```text
deploy/
  values.yaml              # общие
  values-dev.yaml          # отличия dev
  values-staging.yaml
  values-prod.yaml
```

- в Git — структура и несекретные значения; ссылки на секреты (`existingSecret: clinic-db`) или зашифрованные значения (SOPS);
- одинаковые имена переменных во всех окружениях;
- различия документированы; проверка дрейфа;
- разные учётные записи/ключи для каждого окружения (компрометация dev не затрагивает prod);
- **данные**: не копировать прод в dev без обезличивания (маскирование ПДн).

## Ротация и утечки

- **ротация** по расписанию и при увольнении/инциденте; динамические секреты (Vault database engine) с TTL;
- сканирование репозиториев и истории (**gitleaks**, **trufflehog**, GitHub/GitLab Secret Detection) в pre-commit и CI;
- **при утечке**: считать скомпрометированным → отозвать и заменить → аудит использования → очистка истории вторична;
- политики: запрет пушей секретов (push rules), защита от коммитов `.env`;
- мониторинг обращения к секретам, алерты на аномалии.

## Практика .NET

```csharp
builder.Configuration
  .AddJsonFile("appsettings.json")
  .AddJsonFile($"appsettings.{env}.json", optional: true)
  .AddEnvironmentVariables()                      // переопределение: ConnectionStrings__Default
  .AddKeyPerFile("/run/secrets", optional: true); // файлы-секреты
// User Secrets — только для локальной разработки (dotnet user-secrets)
```

## Вопросы с ответами

> [!question]- Где хранить секреты для пайплайна и как не допустить утечки?
> В защищённом хранилище (CI variables с Masked/Protected, Vault, облачный менеджер), с OIDC вместо статических ключей; не хранить в Git, образах и логах; scope по окружениям; сканирование и ротация.

> [!question]- Безопасен ли Kubernetes Secret?
> По умолчанию это base64, а не шифрование. Нужны шифрование etcd, строгий RBAC, внешние хранилища (External Secrets, CSI) или Sealed Secrets/SOPS для Git.

> [!question]- Что делать при попадании секрета в репозиторий?
> Немедленно отозвать и заменить секрет, проверить журналы использования, затем очистить историю; удаление коммитом недостаточно.
