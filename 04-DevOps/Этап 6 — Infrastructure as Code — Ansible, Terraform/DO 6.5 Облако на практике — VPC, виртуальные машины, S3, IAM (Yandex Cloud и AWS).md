---
type: topic
domain: devops
stage: 6
order: 5
status: todo
level: middle
tags: [domain/devops, stage/6, level/middle, priority/nice]
reviewed: 
next_review: 
priority: nice
time: 8
---

# Облако на практике: VPC, виртуальные машины, S3, IAM (Yandex Cloud и AWS)

↑ [[DO Этап 6 · Infrastructure as Code — Ansible, Terraform|Этап 6 · Infrastructure as Code: Ansible, Terraform]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge nice">По желанию</span><span class="chip">~8 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> Нужно уметь описать базовую облачную инфраструктуру приложения: сеть, ВМ, хранилище, права — и назвать аналоги в AWS и Yandex Cloud.

## Соответствие понятий

| Понятие | AWS | Yandex Cloud |
|---|---|---|
| Организация / аккаунт | Organizations / Account | Organization / Cloud / Folder (каталог) |
| Сеть | VPC, Subnet | VPC Network, Subnet |
| Виртуальная машина | EC2 instance | Compute Cloud VM |
| Образ | AMI | Image |
| Диск | EBS | Disk (Network SSD/HDD) |
| Объектное хранилище | S3 | Object Storage (S3-совместимое) |
| Балансировщик | ALB / NLB | Application / Network Load Balancer |
| DNS | Route 53 | Cloud DNS |
| Идентичность | IAM users/roles/policies | IAM: users, service accounts, roles |
| Группы безопасности | Security Groups | Security Groups |
| Выход в интернет из приватной сети | NAT Gateway | NAT-шлюз (Gateway) |
| Managed PostgreSQL | RDS | Managed Service for PostgreSQL |
| Kubernetes | EKS | Managed Service for Kubernetes |
| Секреты | Secrets Manager | Lockbox |
| Метаданные ВМ | IMDS `169.254.169.254` | Metadata service `169.254.169.254` |
| CLI | `aws` | `yc` |

## Типовая сетевая архитектура (VPC)

```text
VPC 10.0.0.0/16
├─ Public subnets (по одной на зону): 10.0.0.0/24 (a), 10.0.1.0/24 (b)
│    балансировщик, bastion, NAT Gateway → Internet Gateway
├─ Private app subnets: 10.0.10.0/24 (a), 10.0.11.0/24 (b)
│    приложения, Kubernetes-ноды → выход в интернет через NAT
└─ Private data subnets: 10.0.20.0/24 (a), 10.0.21.0/24 (b)
     БД, кэш — без маршрута в интернет
```

- **Public subnet**: маршрут `0.0.0.0/0 → Internet Gateway`, ресурсы с публичными IP;
- **Private subnet**: маршрут `0.0.0.0/0 → NAT`, входящий трафик только изнутри;
- **Security Groups** (stateful) привязаны к ресурсам: «БД принимает 5432 только от SG приложения»; **Network ACL** (stateless) — на подсеть;
- подсети в **нескольких зонах** для отказоустойчивости; не пересекать CIDR с другими сетями (VPN, peering);
- **Bastion host** / **SSM Session Manager** / VPN для доступа к приватным ресурсам; SSH-ключи, отключить пароли;
- **VPC endpoints / Private Link**: доступ к S3/сервисам без выхода в интернет.

## Виртуальные машины

Выбор параметров: **тип/семейство** (general, compute-optimized, memory-optimized, burstable), vCPU/RAM, **диск** (тип, IOPS, размер), **образ ОС**, зона, сеть и SG, SSH-ключ, **metadata / user-data / cloud-init** для первичной настройки.

```yaml
# cloud-init (user-data)
#cloud-config
users:
  - name: deploy
    groups: [sudo, docker]
    shell: /bin/bash
    sudo: ALL=(ALL) NOPASSWD:ALL
    ssh_authorized_keys: ["ssh-ed25519 AAAA... ops@laptop"]
package_update: true
packages: [docker.io, git, curl]
runcmd:
  - systemctl enable --now docker
```

CLI примеры:

```bash
# AWS
aws ec2 run-instances --image-id ami-0abc --instance-type t3.medium --subnet-id subnet-123 \
  --security-group-ids sg-123 --key-name ops --user-data file://cloud-init.yaml \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=app-1},{Key=env,Value=prod}]'
aws ec2 describe-instances --filters Name=tag:env,Values=prod --query 'Reservations[].Instances[].[InstanceId,PrivateIpAddress]'

# Yandex Cloud
yc compute instance create --name app-1 --zone ru-central1-a --platform standard-v3 --cores 2 --memory 4 \
  --create-boot-disk image-family=ubuntu-2404-lts,size=30 --network-interface subnet-name=app-a,nat-ip-version=ipv4 \
  --ssh-key ~/.ssh/id_ed25519.pub --metadata-from-file user-data=cloud-init.yaml
yc compute instance list
```

Практики: **автомасштабирование** (Auto Scaling Group/Instance Group), **launch template**, **spot/прерываемые** ВМ для нагрузок без состояния, **снапшоты** дисков, **теги/метки** (env, team, cost-center), размер по метрикам (rightsizing), **обновления** ОС через immutable образы или Ansible, защита от удаления (termination protection).

## Объектное хранилище (S3 / Object Storage)

```bash
aws s3 mb s3://clinic-backups-prod; aws s3 cp dump.tgz s3://clinic-backups-prod/pg/ --sse AES256
aws s3 sync ./dist s3://clinic-static --delete --cache-control "max-age=31536000"
aws s3 ls s3://clinic-backups-prod --recursive --human-readable
# S3-совместимый endpoint (Yandex Cloud):
aws --endpoint-url=https://storage.yandexcloud.net s3 ls s3://bucket
yc storage bucket create --name clinic-backups
```

Возможности: версионирование, lifecycle, шифрование (SSE-S3/KMS), политики бакета, блокировка публичного доступа (**Block Public Access**), CORS, статический хостинг сайта, presigned URL, репликация, Object Lock. Доступ приложений — через **роли/сервисные аккаунты** (IAM), а не статические ключи.

## IAM

- **Пользователи** (люди; лучше SSO/федерация), **группы**, **роли** (временные полномочия для сервисов и людей), **политики** (JSON: Effect/Action/Resource/Condition), **service accounts** (Yandex);
- **принцип наименьших привилегий**: отдельная роль на сервис, ограничение по ресурсам и условиям (IP, MFA, теги);
- **MFA** для людей, запрет долгоживущих ключей root/администратора; **ротация** ключей;
- **Instance profile / IAM role для EC2**, **service account на ВМ (Yandex)** — приложение получает временные учётные данные из metadata-сервиса без ключей в конфиге;
- **IRSA / Workload Identity** для Kubernetes; **OIDC** для CI (GitHub/GitLab → роль);
- разделение **аккаунтов/каталогов** по окружениям и командам, организационные политики (SCP), аудит (CloudTrail, Audit Trails).

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": ["s3:GetObject", "s3:PutObject"],
    "Resource": "arn:aws:s3:::clinic-backups-prod/pg/*"
  }]
}
```

## Инфраструктура как код в облаке

Ресурсы описывают Terraform/OpenTofu (провайдеры `aws`, `yandex-cloud/yandex`), CloudFormation/CDK, Pulumi. Ручное создание в консоли допустимо для исследования, но рабочие ресурсы — через код и CI.

## Безопасность и стоимость на практике

- закрыть публичные порты: SSH только с bastion/VPN, БД в приватных подсетях без публичных IP;
- шифрование дисков и бакетов (KMS), бэкапы в другом регионе;
- логи и мониторинг: CloudWatch/Monitoring, аудит, алерты на нетипичные действия и расходы, бюджеты;
- теги и отчётность; выключение dev-ресурсов по расписанию; удалить «сирот» (диски, снапшоты, IP, NAT);
- внимание к **egress**, межзональному трафику и NAT Gateway (значимые статьи расходов);
- регулярный аудит прав (IAM Access Analyzer), сканирование конфигураций (Prowler, ScoutSuite, CSPM), политики соответствия.

## Вопросы с ответами

> [!question]- Чем public subnet отличается от private?
> В публичной подсети есть маршрут в интернет через Internet Gateway и ресурсы могут иметь публичные IP; в приватной выход наружу идёт через NAT, входящий трафик из интернета невозможен.

> [!question]- Как предоставить приложению на ВМ доступ к S3 без ключей в конфигурации?
> Назначить ВМ IAM-роль (instance profile) или сервисный аккаунт с минимальной политикой; SDK получает временные учётные данные из metadata-сервиса.

> [!question]- Что типично расходует бюджет неожиданно?
> Исходящий и межзональный трафик, NAT Gateway, забытые диски/снапшоты/IP, избыточные размеры ВМ и IOPS, логи и метрики, работающие dev-окружения.
