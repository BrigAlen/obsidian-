---
type: topic
domain: db
stage: 4
section: "4.2"
order: 2
status: todo
level: middle
notion_id: 3ea33104867981d09b39fd0a7d9a635d
tags: [domain/db, stage/4, level/middle, topic/minio, topic/s3, topic/docker, priority/should]
reviewed:
next_review:
priority: should
time: 6
---

# MinIO: развёртывание, mc, политики доступа

↑ [[DB 4.2 Объектное хранилище — MinIO и S3|4.2 Объектное хранилище: MinIO и S3]] · ← [[DB 4.2.1 Объектное хранилище и S3 API — buckets, objects, keys, метаданные|Предыдущая]] · → [[DB 4.2.3 Работа с MinIO из .NET — загрузка, скачивание, стриминг|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~6 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> MinIO — популярное self-hosted S3-совместимое хранилище: спрашивают запуск, управление и политики.

## Что такое MinIO

Высокопроизводительное S3-совместимое объектное хранилище с открытым исходным кодом (Go). Запускается одной бинарной, подходит для локальной разработки, on-premise и Kubernetes.

Режимы:

- **Standalone** — один сервер, один диск (разработка);
- **SNSD / SNMD** — один сервер, несколько дисков (erasure coding);
- **MNMD (distributed)** — несколько серверов и дисков: отказоустойчивость и масштаб.

**Erasure coding**: данные разбиваются на блоки данных и чётности (например 8+4); объект доступен при потере части дисков/узлов, есть защита от bit rot (контрольные суммы).

## Запуск в Docker

```yaml
services:
  minio:
    image: minio/minio:latest
    command: server /data --console-address ":9001"
    ports:
      - "9000:9000"     # S3 API
      - "9001:9001"     # веб-консоль
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: change-me-please
    volumes:
      - minio-data:/data
    healthcheck:
      test: ["CMD", "mc", "ready", "local"]
      interval: 10s
volumes:
  minio-data:
```

Секреты — через переменные окружения/секреты, не хранить пароль по умолчанию. В Kubernetes: Operator/Helm-чарт MinIO.

## mc — командная строка

```sh
mc alias set local http://localhost:9000 minioadmin change-me-please
mc mb local/uploads                          # создать бакет
mc cp ./report.pdf local/uploads/reports/    # загрузить
mc ls local/uploads --recursive
mc cat local/uploads/reports/report.pdf
mc rm --recursive --force local/uploads/tmp/
mc mirror ./dist local/static                # синхронизация каталога
mc stat local/uploads/reports/report.pdf
mc admin info local
mc version enable local/uploads              # версионирование
mc ilm rule add --expire-days 30 local/uploads --prefix tmp/   # lifecycle
mc event add local/uploads arn:minio:sqs::primary:webhook --event put   # уведомления
```

## Пользователи и политики

Политики в формате, совместимом с IAM AWS:

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": ["s3:GetObject", "s3:PutObject", "s3:DeleteObject"],
    "Resource": ["arn:aws:s3:::uploads/*"]
  }, {
    "Effect": "Allow",
    "Action": ["s3:ListBucket"],
    "Resource": ["arn:aws:s3:::uploads"]
  }]
}
```

```sh
mc admin policy create local app-uploads policy.json
mc admin user add local app-service <secret>
mc admin policy attach local app-uploads --user app-service
mc admin user svcacct add local app-service          # service account с ограничением
mc anonymous set download local/public              # публичное чтение бакета
```

Принципы: отдельный пользователь или service account на каждое приложение, **минимальные права** (только нужные бакеты и действия), ротация ключей, отказ от root-ключей в приложениях.

## Аутентификация

- встроенные пользователи;
- внешние провайдеры: **OIDC** (Keycloak), LDAP/AD;
- STS (временные учётные данные) для клиентов.

## Возможности

- версионирование, Object Lock (WORM, retention, legal hold);
- lifecycle (истечение, переход между уровнями);
- репликация между кластерами (site, bucket);
- шифрование (SSE-S3/KMS, TLS);
- **уведомления о событиях** (webhook, Kafka, NATS, AMQP, Redis): обработка загрузок;
- метрики Prometheus (`/minio/v2/metrics/cluster`), `mc admin`;
- квоты на бакеты.

## Особенности эксплуатации

- диски выделенные (XFS), одинакового размера; не использовать RAID поверх erasure coding;
- балансировщик перед узлами (Nginx/HAProxy), TLS;
- мониторинг здоровья дисков и самовосстановление (`mc admin heal`);
- бэкапы через репликацию на второй кластер или внешний S3;
- лицензия AGPLv3 и коммерческая; проверьте условия использования в вашем проекте и варианты (например, альтернативы: Ceph RGW, SeaweedFS, Garage).

## Вопросы с ответами

> [!question]- Зачем MinIO, если есть AWS S3?
> Self-hosted или on-premise окружение, локальная разработка и тесты с тем же S3 API, контроль данных и стоимости, работа в закрытых контурах.

> [!question]- Как дать приложению доступ только к одному бакету?
> Создать политику с нужными действиями и ресурсом бакета, отдельного пользователя или service account и назначить политику; root-ключи в приложения не выдавать.

> [!question]- Что такое erasure coding?
> Разбиение данных на блоки с избыточной чётностью так, что при потере нескольких дисков или узлов объект восстанавливается; эффективнее полной репликации по месту.
