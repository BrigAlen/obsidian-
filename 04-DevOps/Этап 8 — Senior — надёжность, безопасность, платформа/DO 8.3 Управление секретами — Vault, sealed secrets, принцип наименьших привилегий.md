---
type: topic
domain: devops
stage: 8
order: 3
status: todo
level: senior
tags: [domain/devops, stage/8, level/senior, priority/nice]
reviewed: 
next_review: 
priority: nice
time: 8
---

# Управление секретами: Vault, sealed secrets, принцип наименьших привилегий

↑ [[DO Этап 8 · Senior — надёжность, безопасность, платформа|Этап 8 · Senior: надёжность, безопасность, платформа]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge nice">По желанию</span><span class="chip">~8 мин чтения</span><span class="chip">Уровень: senior</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> Секреты — главный вектор атак на инфраструктуру. Senior должен знать Vault, sealed secrets и динамические учётные данные.

## Жизненный цикл секрета

Создание → **хранение** → **доставка** → использование → **ротация** → отзыв/удаление. На каждом шаге: шифрование, контроль доступа, аудит, минимальная длительность жизни.

Антипаттерны: секреты в Git/образах/логах/тикетах/чате, общие пароли, «вечные» токены, один секрет на всё, секреты в переменных CI без защиты, ручная ротация «когда-нибудь».

## Принцип наименьших привилегий

- доступ **только к нужным** секретам, **только нужным** идентичностям (сервисам, людям), **на нужное время**;
- **разделение по окружениям** (dev/staging/prod: разные секреты, разные хранилища/пути/аккаунты);
- **сервис-специфичные учётные записи БД** с минимальными правами (не `postgres`/`root`);
- доступ людей к prod-секретам — **по запросу** (JIT, break-glass), с аудитом и сроком; большинство не должно уметь читать prod-секреты;
- **ротация и отзыв** при увольнении/инциденте;
- сегментация ключей шифрования (KMS) по ролям.

## HashiCorp Vault

Централизованное хранилище секретов и криптографических сервисов (форк-альтернатива — **OpenBao**).

Возможности:

- **Secrets engines**: `kv` (v2 — версии секретов), **`database`** (динамические учётные данные БД), `aws/gcp/azure` (динамические облачные ключи), `pki` (выпуск сертификатов), `transit` (шифрование как сервис: приложение не хранит ключи), `ssh` (подписанные сертификаты/OTP), `totp`;
- **Auth methods**: `kubernetes` (по ServiceAccount токену), `jwt/oidc` (CI, SSO людей), `approle` (сервисы/CI), `aws/gcp` (IAM), `ldap`, `token`, `userpass`;
- **Policies** (HCL): доступ к путям и операциям;
- **Leases и TTL**: секреты имеют срок жизни, автоматически отзываются;
- **Audit devices**: подробный журнал всех обращений;
- **Namespaces** (Enterprise), репликация, **HA** (Raft integrated storage, 3/5 узлов), **auto-unseal** через KMS/HSM.

```hcl
# policy: приложение читает только свои секреты
path "secret/data/clinic/prod/api/*" { capabilities = ["read"] }
path "database/creds/clinic-api"      { capabilities = ["read"] }
```

```bash
vault kv put secret/clinic/prod/api/stripe api_key=sk_live_...
vault kv get -field=api_key secret/clinic/prod/api/stripe
vault read database/creds/clinic-api          # динамический логин/пароль с TTL
vault write auth/kubernetes/role/clinic-api bound_service_account_names=api bound_service_account_namespaces=clinic policies=clinic-api ttl=1h
```

### Динамические секреты

Vault **создаёт уникального временного пользователя БД** под запрос (`CREATE ROLE "v-token-api-abc" ... VALID UNTIL ...`) и **удаляет** по истечении lease.

Плюсы: нет долгоживущих паролей, компрометация одного экземпляра ограничена TTL, каждое обращение атрибутируется, автоматическая ротация, отзыв одним действием (`vault lease revoke -prefix`). Требования: приложение умеет **переподключаться** при смене учётных данных, соотношение нагрузки на БД (создание ролей), пулы соединений и TTL.

### Доставка в приложение

| Способ | Описание |
|---|---|
| **Vault Agent** (sidecar/init) | аутентифицируется, получает секреты, рендерит файлы/шаблоны, обновляет, перезапускает процесс |
| **Vault Secrets Operator (VSO)** | Kubernetes-оператор: синхронизирует секреты Vault в Kubernetes Secret (`VaultStaticSecret`, `VaultDynamicSecret`) |
| **Vault CSI Provider** | монтирует секреты томом без Kubernetes Secret |
| **External Secrets Operator (ESO)** | универсальная синхронизация из Vault/AWS SM/Yandex Lockbox/Azure KV/GCP SM в K8s Secret |
| Прямой API/SDK | приложение само обращается (сложнее, гибче) |
| **Vault Injector** (mutating webhook) | аннотациями добавляет agent-sidecar |

```yaml
# Vault Agent injector
annotations:
  vault.hashicorp.com/agent-inject: "true"
  vault.hashicorp.com/role: "clinic-api"
  vault.hashicorp.com/agent-inject-secret-db: "database/creds/clinic-api"
  vault.hashicorp.com/agent-inject-template-db: |
    {{- with secret "database/creds/clinic-api" -}}
    Host=db;Database=clinic;Username={{ .Data.username }};Password={{ .Data.password }}
    {{- end }}
```

## Sealed Secrets и SOPS (секреты в Git для GitOps)

**Проблема**: GitOps требует, чтобы всё было в Git, но секреты нельзя хранить в открытом виде.

**Sealed Secrets** (Bitnami): контроллер в кластере владеет закрытым ключом; `kubeseal` шифрует Secret открытым ключом → `SealedSecret` (безопасно коммитить); расшифровывается только в целевом кластере/namespace.

```bash
kubectl create secret generic api-db --from-literal=password=... --dry-run=client -o yaml | kubeseal --format yaml > sealed-api-db.yaml
```

Минусы: ключ кластера надо бэкапить; привязка к кластеру; ротация сложнее.

**SOPS** (Mozilla) + **age/KMS/PGP**: шифрует **значения** в YAML/JSON/ENV, оставляя ключи читаемыми (удобные диффы); интеграция с Flux/Argo (helm-secrets, ksops), Terraform (`sops` provider), Ansible.

```bash
sops --encrypt --age age1... secrets.yaml > secrets.enc.yaml
sops --decrypt secrets.enc.yaml
```

Правила: отдельные ключи по окружениям, хранение ключа вне репозитория, контроль состава получателей (`.sops.yaml`), аудит.

**External Secrets Operator** — альтернатива: в Git лежат только **ссылки** (`ExternalSecret`), а значения — во внешнем менеджере (Vault, облако): единый источник истины, ротация без коммитов.

```yaml
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata: { name: api-db, namespace: clinic }
spec:
  refreshInterval: 1h
  secretStoreRef: { name: vault, kind: ClusterSecretStore }
  target: { name: api-db }
  data: [{ secretKey: password, remoteRef: { key: secret/clinic/prod/db, property: password } }]
```

## Облачные менеджеры секретов

**AWS Secrets Manager/SSM Parameter Store**, **Azure Key Vault**, **GCP Secret Manager**, **Yandex Lockbox**: IAM-доступ, версии, автоматическая ротация (Lambda/функции), шифрование KMS, аудит (CloudTrail), интеграция с сервисами. Проще в эксплуатации, чем Vault, привязаны к облаку; часто сочетаются с ESO.

## Идентичность вместо паролей

Лучший секрет — **его отсутствие**: **Workload Identity** — сервис получает **краткоживущий токен по идентичности** (IRSA/EKS Pod Identity, GKE Workload Identity, Azure Workload Identity, **SPIFFE/SPIRE**), **OIDC-федерация** CI → облако/Vault (GitHub/GitLab JWT) без хранимых ключей, **mTLS** с краткоживущими сертификатами (cert-manager, Vault PKI, service mesh), **IAM database auth**.

## Ротация

- **автоматическая** по расписанию и по событию (компрометация, уход сотрудника); динамические секреты — ротация «встроенная»;
- поддержка **двух активных версий** при переходе (old/new), плавная замена без простоя;
- приложение перечитывает (reload) секреты без рестарта либо поды перезапускаются (Reloader);
- сертификаты — автоматически (ACME, cert-manager); ключи шифрования — версии в KMS;
- проверка, что старые отозваны; уведомления до истечения; учения по массовой ротации («секреты скомпрометированы»).

## Защита самого хранилища

- **Vault**: unseal keys (Shamir) или auto-unseal, шифрование на диске, TLS, аудит, политики, минимальный root-токен (после инициализации отозвать), HA, бэкапы (Raft snapshots), мониторинг (метрики, логи), сегментация сети, отдельный кластер для prod;
- **KMS/HSM** для корня доверия; разделение обязанностей (операторы Vault ≠ администраторы приложений);
- защита бэкапов; **break-glass** процедуры; многофакторная аутентификация для людей;
- **Kubernetes Secrets**: шифрование etcd (KMS provider), RBAC, NetworkPolicy, запрет `list`/`watch` Secrets для большинства.

## Аудит и обнаружение утечек

- журнал доступа к секретам (Vault audit, CloudTrail), алерты на необычное чтение;
- сканирование репозиториев/образов/логов (gitleaks, trufflehog, GitHub secret scanning, push protection);
- **honeytokens/canary tokens** (ловушки: поддельные ключи, срабатывающие при использовании);
- мониторинг использования ключей облака (GuardDuty), аномалии;
- процедура реагирования: обнаружение → отзыв → ротация → анализ влияния → постмортем.

## Практические рекомендации

1. Выбрать **единый источник истины** (Vault/облачный менеджер) + синхронизация в K8s (ESO/VSO/CSI).
2. **Динамические** учётные данные везде, где возможно; остальное — с автоматической ротацией.
3. **Workload Identity/OIDC** вместо статических ключей для доступа к облаку и CI.
4. Для GitOps — ESO (ссылки) либо SOPS/Sealed Secrets (шифрование).
5. **Не использовать env** для особо чувствительных данных, если есть файлы/тома; не логировать.
6. Разделение сред, минимальные права, аудит, регулярные учения по ротации.

## Вопросы с ответами

> [!question]- Что такое динамические секреты в Vault и чем они лучше статических?
> Vault создаёт уникальные краткоживущие учётные данные (например, пользователя БД) по запросу и автоматически отзывает по TTL: нет долгоживущих паролей, ограниченный ущерб при утечке, аудит по каждому обращению и встроенная ротация.

> [!question]- Чем Sealed Secrets/SOPS отличаются от External Secrets Operator?
> Sealed Secrets и SOPS хранят **зашифрованные значения в Git** и расшифровывают в кластере/пайплайне; ESO хранит в Git лишь **ссылки**, а значения берёт из внешнего менеджера секретов — единый источник истины и ротация без коммитов.

> [!question]- Что значит «лучший секрет — его отсутствие»?
> Использование идентичности вместо паролей: workload identity, OIDC-федерация CI, mTLS с краткоживущими сертификатами — нет долгоживущих секретов, которые можно украсть.
