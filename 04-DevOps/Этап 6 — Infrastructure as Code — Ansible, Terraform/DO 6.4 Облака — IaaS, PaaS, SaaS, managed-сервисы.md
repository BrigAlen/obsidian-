---
type: topic
domain: devops
stage: 6
order: 4
status: todo
level: middle
tags: [domain/devops, stage/6, level/middle, priority/nice]
reviewed: 
next_review: 
priority: nice
time: 5
---

# Облака: IaaS, PaaS, SaaS, managed-сервисы

↑ [[DO Этап 6 · Infrastructure as Code — Ansible, Terraform|Этап 6 · Infrastructure as Code: Ansible, Terraform]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge nice">По желанию</span><span class="chip">~5 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> Базовая облачная терминология: модели обслуживания, управляемые сервисы, когда что выбирать и как считать стоимость.

## Модели обслуживания

| Модель | Вы управляете | Провайдер | Примеры |
|---|---|---|---|
| **On-premise** | всё (железо, сеть, ОС, ПО, данные) | — | собственный ЦОД |
| **IaaS** (Infrastructure as a Service) | ОС, рантайм, приложения, данные | железо, виртуализация, сеть | EC2, Yandex Compute, Azure VMs, GCE, DigitalOcean, Hetzner |
| **PaaS** (Platform as a Service) | приложение и данные | ОС, рантайм, масштабирование | Heroku, Azure App Service, Google App Engine, AWS Elastic Beanstalk, Yandex Serverless Containers, Render, Fly.io |
| **FaaS / Serverless** | код функций | всё остальное, масштабирование «до нуля» | AWS Lambda, Yandex Cloud Functions, Azure Functions, Cloud Run |
| **SaaS** (Software as a Service) | только использование и настройки | всё | Gmail, Office 365, Jira, GitHub, Slack, Salesforce |
| **CaaS** (Containers) | контейнеры и оркестрация | платформа контейнеров | ECS, EKS, AKS, GKE, Yandex Managed Kubernetes |

Чем выше уровень (IaaS → SaaS), тем меньше ответственности и контроля, тем быстрее старт. Модель **общей ответственности (shared responsibility)**: провайдер отвечает за безопасность **облака** (ЦОД, гипервизор), клиент — за безопасность **в облаке** (конфигурация, данные, доступы, ОС на IaaS).

## Управляемые сервисы (managed)

Провайдер берёт эксплуатацию: развёртывание, обновления, бэкапы, репликацию, мониторинг, SLA.

| Категория | Примеры |
|---|---|
| Базы данных | RDS/Aurora, Azure SQL, Cloud SQL, Yandex Managed PostgreSQL/ClickHouse/Redis/MongoDB |
| Kubernetes | EKS, GKE, AKS, Yandex Managed Kubernetes |
| Очереди/стриминг | SQS/SNS, Kinesis, Managed Kafka, Service Bus, Pub/Sub |
| Кэш | ElastiCache, Memorystore, Azure Cache |
| Объектное хранилище | S3, Blob Storage, GCS, Yandex Object Storage |
| Балансировщики, CDN, DNS | ALB/NLB, CloudFront, Route 53, Cloud DNS |
| Идентичность | IAM, Entra ID, Yandex Cloud IAM, Cognito |
| Секреты и ключи | Secrets Manager, Key Vault, KMS, Lockbox |
| Наблюдаемость | CloudWatch, Azure Monitor, Managed Prometheus/Grafana |
| Реестры | ECR, ACR, Artifact Registry, Container Registry |
| Serverless | Lambda, Cloud Run, Functions |

**Плюсы managed**: скорость, надёжность (SLA), меньше операционной нагрузки, масштабирование, встроенные бэкапы/HA, безопасность по умолчанию. **Минусы**: стоимость, ограничения настройки, vendor lock-in, зависимость от провайдера, меньше контроля над версиями и внутренними параметрами, сложнее миграции.

Правило: **управляемые сервисы для недифференцирующих компонентов** (БД, очереди, k8s control plane), self-hosted — где нужен контроль, есть экспертиза или важна цена при больших объёмах.

## Основные строительные блоки IaaS

- **Регион / зона доступности (AZ)**: регион — географическая область, AZ — изолированные ЦОДы внутри (отказоустойчивость по зонам);
- **VPC / сеть**: изолированная виртуальная сеть, подсети (public/private), маршрутные таблицы, Internet/NAT gateway, peering, VPN, Direct Connect;
- **Compute**: виртуальные машины (типы, vCPU/RAM, образы, диски), autoscaling groups, spot/preemptible;
- **Storage**: блочные диски (EBS), объектное (S3), файловое (EFS/NFS), снапшоты;
- **Security groups / NACL / firewall**;
- **IAM**: пользователи, роли, политики, federation/SSO;
- **Load Balancer**, **DNS**, **CDN**.

## Модели развёртывания

| Модель | Описание |
|---|---|
| **Публичное облако** | общая инфраструктура провайдера |
| **Частное облако** | для одной организации (on-prem OpenStack, VMware, Yandex Private) |
| **Гибридное** | сочетание on-prem и публичного облака |
| **Мультиоблако** | несколько провайдеров (устойчивость, избегание lock-in, соответствие требованиям; сложность и цена) |

## Стоимость (FinOps)

- **модели оплаты**: по запросу (on-demand), **резервирование/commitment** (Reserved, Savings Plans, committed use) — скидки до 40–70% за срок 1–3 года, **spot/preemptible** (до 90% дешевле, могут быть отозваны: для stateless/batch), бесплатные уровни;
- **что стоит денег**: вычисления, диски и IOPS, **исходящий трафик (egress)**, межзональный и межрегиональный трафик, NAT Gateway, балансировщики, снапшоты и бэкапы, управляемые сервисы, API-запросы, лицензии, мониторинг/логи;
- **оптимизация**: rightsizing, выключение неиспользуемого (dev по расписанию), autoscaling, lifecycle хранилища, spot, удаление осиротевших дисков/снапшотов/IP, архитектурные решения (CDN, кэш, сжатие), теги и отчётность по командам (showback/chargeback), бюджеты и алерты, аномалии расходов;
- **TCO**: сравнивать с on-prem с учётом людей, оборудования, энергии, амортизации.

## Надёжность в облаке

- **multi-AZ** для критичных компонентов; multi-region для DR/глобальных сервисов;
- **SLA** провайдера (например, 99.95%) ≠ ваш SLA; композитный SLA меньше;
- дизайн «для отказа» (design for failure): автозамена, health checks, stateless, хранение состояния в managed;
- RPO/RTO, бэкапы в другом регионе/аккаунте.

## Безопасность и соответствие

IAM по минимальным правам, MFA, отдельные аккаунты/проекты для окружений (landing zone, организационная структура), шифрование (KMS), логи аудита (CloudTrail), сетевые ограничения, сканирование конфигураций (CSPM), региональные требования к данным (152-ФЗ: хранение ПДн россиян в РФ; GDPR), сертификации провайдера.

## Российские и зарубежные облака

Зарубежные: AWS, Microsoft Azure, Google Cloud. Российские: **Yandex Cloud**, **VK Cloud**, SberCloud (Cloud.ru), Selectel, MTS Cloud, Timeweb Cloud — часто выбор из-за требований к данным и санкционных рисков. Альтернативы: Hetzner, DigitalOcean, OVH, Cloudflare; on-prem: OpenStack, Proxmox, VMware, bare metal.

## Serverless

Функции и контейнеры без управления серверами: автоскейл до нуля, оплата за вызовы/время. Плюсы — простота и цена при нерегулярной нагрузке; минусы — холодный старт, лимиты времени/памяти, vendor lock-in, сложность отладки и локального тестирования, стоимость при постоянной высокой нагрузке.

## Вопросы с ответами

> [!question]- Чем IaaS отличается от PaaS и SaaS?
> IaaS даёт виртуальную инфраструктуру (ВМ, сеть, диски), ОС и ПО на вас; PaaS — платформу для запуска приложений без управления ОС; SaaS — готовое приложение, вы только используете.

> [!question]- Что такое модель общей ответственности?
> Провайдер обеспечивает безопасность инфраструктуры облака, клиент — конфигурацию, доступы, данные и (на IaaS) ОС и приложения.

> [!question]- Когда выбирать managed-сервис, а когда self-hosted?
> Managed — для типовых компонентов, когда важны скорость, надёжность и низкая операционная нагрузка; self-hosted — при особых требованиях к настройке, контроле данных, высокой цене на масштабе или наличии экспертизы.
