---
type: topic
domain: db
stage: 7
order: 2
notion_id: 31bbc75924594c94a7d76c8a5b964f74
status: todo
level: middle+
tags: [domain/db, stage/7, level/middle+, priority/nice]
reviewed: 
next_review: 
priority: nice
time: 5
---

# TLS, шифрование и управление секретами БД

↑ [[DB Этап 7 · Эксплуатация и безопасность БД|Этап 7 · Эксплуатация и безопасность БД]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge nice">По желанию</span><span class="chip">~5 мин чтения</span><span class="chip">Уровень: middle+</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> Защита данных «в пути» и «на диске» и правильная работа с секретами — обязательная часть эксплуатации и аудитов.

## Шифрование в пути (TLS)

По умолчанию трафик PostgreSQL **не шифруется**: пароли в SCRAM не передаются в открытом виде, но запросы и данные видны в сети.

Серверная настройка:

```conf
# postgresql.conf
ssl = on
ssl_cert_file = '/etc/ssl/pg/server.crt'
ssl_key_file  = '/etc/ssl/pg/server.key'          # права 0600, владелец postgres
ssl_ca_file   = '/etc/ssl/pg/ca.crt'              # для проверки клиентских сертификатов
ssl_min_protocol_version = 'TLSv1.2'
```

```text
# pg_hba.conf: требуем TLS
hostssl  app  app_service  10.0.0.0/16  scram-sha-256
hostnossl all all 0.0.0.0/0 reject
```

Клиент (строка подключения):

| `sslmode` | Поведение |
|---|---|
| `disable` | без TLS |
| `prefer` (по умолчанию) | TLS если доступен, иначе без (**небезопасно**) |
| `require` | TLS обязателен, **сертификат не проверяется** (защита от прослушивания, но не от MITM) |
| `verify-ca` | проверяет подпись CA |
| `verify-full` | проверяет CA **и имя хоста** (рекомендуется) |

```text
Host=db.internal;Database=app;Username=app_service;SSL Mode=VerifyFull;Root Certificate=/certs/ca.crt
```

**mTLS**: клиентские сертификаты (`clientcert=verify-full`, аутентификация `cert`): сервис доказывает личность сертификатом.

Управление сертификатами: внутренний CA (cert-manager, Vault PKI, step-ca), автоматическая выдача и ротация, короткий срок жизни, перечитывание без перезапуска (`SELECT pg_reload_conf()`). Аналогично TLS для репликации (`sslmode=verify-full` в `primary_conninfo`), PgBouncer (`client_tls_sslmode`, `server_tls_sslmode`), Redis, ClickHouse, MinIO.

## Шифрование на диске (at rest)

| Уровень | Как | Комментарии |
|---|---|---|
| **Диск/том** | LUKS/dm-crypt, шифрование облачных дисков (EBS, Azure Disk), шифрование LVM | защищает при краже носителя; прозрачно для БД; самый простой путь |
| **Файловая система** | eCryptfs, fscrypt | реже |
| **Transparent Data Encryption (TDE)** | в PostgreSQL ядре нет (есть в форках: EDB, Percona pg_tde); есть в SQL Server, Oracle, MySQL | шифрует файлы данных и WAL |
| **Столбцы** | `pgcrypto` (`pgp_sym_encrypt`), шифрование в приложении | чувствительные поля (паспорт, карта); теряется возможность поиска и индексации |
| **Бэкапы** | шифрование pgBackRest/WAL-G, SSE в S3 | обязательно |
| **Клиентское (application-level)** | приложение шифрует до записи (envelope encryption, KMS) | БД не видит открытые данные |

**Envelope encryption**: данные шифруются ключом данных (DEK), а DEK шифруется ключом в KMS (KEK). Ротация KEK без перешифровки всех данных.

```sql
CREATE EXTENSION pgcrypto;
INSERT INTO cards (user_id, pan_enc) VALUES (1, pgp_sym_encrypt('4111111111111111', :'key'));
```

Ключ не должен храниться вместе с данными и попадать в логи запросов.

## Управление секретами БД

Проблемы: пароль в репозитории, в `.env`, в образе, в логах, общий пароль у всех, вечные пароли.

Практики:

- **никогда не коммитить секреты**; сканирование (gitleaks, trufflehog, GitHub secret scanning);
- хранилища: **HashiCorp Vault**, AWS Secrets Manager, Azure Key Vault, GCP Secret Manager, Kubernetes Secrets (+ шифрование etcd, External Secrets Operator, Sealed Secrets, SOPS);
- **динамические секреты**: Vault создаёт временного пользователя БД с TTL для каждого сервиса и отзывает его;

```text
vault read database/creds/app-readwrite
  → username: v-app-readwrite-x8f2..., password: A1b2..., lease_duration: 1h
```

- **ротация**: регулярная смена паролей и ключей без простоя (две активные учётные записи, постепенный переход);
- **доставка в приложение**: переменные окружения (минимум), смонтированные файлы из секретов (`/run/secrets`), sidecar/agent (Vault Agent), CSI driver; без записи в логи и стектрейсы;
- разные секреты для dev/stage/prod, минимальные права, отдельные учётные записи на сервис;
- **IAM-аутентификация** (AWS RDS IAM, Azure AD, Workload Identity): токен вместо пароля;
- **шифрование бэкапов** и отдельное хранение ключей;
- **аудит доступа** к секретам, оповещения на чтение;
- отзыв при компрометации: процедура и учения.

Пример Kubernetes:

```yaml
env:
  - name: ConnectionStrings__Default
    valueFrom:
      secretKeyRef: { name: app-db, key: connection-string }
```

## Безопасность соединений и сетей

- БД в **приватной сети**, без публичного IP; доступ через VPN, bastion, прокси;
- firewall/SecurityGroup: только нужные источники;
- **pg_hba.conf** с явными правилами и `reject` по умолчанию;
- отдельные роли и ограничения по IP;
- обновления безопасности PostgreSQL (minor-версии) регулярно;
- защита от SQL-инъекций: параметризованные запросы (Npgsql/EF), минимальные права, WAF.

## Соответствие требованиям

PCI DSS (карточные данные), GDPR и 152-ФЗ (персональные данные: шифрование, минимизация, право на удаление), ISO 27001, SOC 2: контроль доступа, аудит, шифрование, резервные копии, управление ключами.

## Вопросы с ответами

> [!question]- Чем sslmode=require отличается от verify-full?
> `require` шифрует трафик, но не проверяет сертификат сервера (уязвим к MITM). `verify-full` проверяет цепочку доверия и соответствие имени хоста.

> [!question]- Как безопасно хранить пароли БД в Kubernetes?
> Секреты в защищённом хранилище (Vault, облачный менеджер секретов, External Secrets/Sealed Secrets), шифрование etcd, минимальные права доступа к Secret, без коммитов в репозиторий, динамические учётные данные и ротация.

> [!question]- Что такое envelope encryption?
> Данные шифруются ключом данных, а сам ключ данных шифруется мастер-ключом в KMS. Позволяет менять мастер-ключ без перешифровки всех данных и ограничить доступ к ключу.
