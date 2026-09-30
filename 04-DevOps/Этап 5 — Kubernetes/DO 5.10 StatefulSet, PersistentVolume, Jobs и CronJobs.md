---
type: topic
domain: devops
stage: 5
order: 10
status: todo
level: middle
tags: [domain/devops, stage/5, level/middle, priority/should]
reviewed: 
next_review: 
priority: should
time: 10
---

# StatefulSet, PersistentVolume, Jobs и CronJobs

↑ [[DO Этап 5 · Kubernetes|Этап 5 · Kubernetes]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~10 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> Запуск БД и очередей в Kubernetes: нужно понимать StatefulSet, PV/PVC, Jobs и их ограничения.

## StatefulSet

Контроллер для приложений с состоянием: в отличие от Deployment даёт

- **стабильные сетевые имена**: `db-0`, `db-1`, `db-2` (порядковые), сохраняются при пересоздании;
- **стабильное хранилище**: у каждой реплики свой PVC (`volumeClaimTemplates`), привязывается к этой реплике;
- **упорядоченный** запуск/остановка/обновление (`podManagementPolicy: OrderedReady` или `Parallel`);
- **headless Service** для DNS каждого пода: `db-0.db.clinic.svc.cluster.local`.

```yaml
apiVersion: v1
kind: Service
metadata: { name: pg }
spec: { clusterIP: None, selector: { app: pg }, ports: [{ port: 5432 }] }
---
apiVersion: apps/v1
kind: StatefulSet
metadata: { name: pg }
spec:
  serviceName: pg
  replicas: 3
  selector: { matchLabels: { app: pg } }
  updateStrategy: { type: RollingUpdate, rollingUpdate: { partition: 0 } }
  template:
    metadata: { labels: { app: pg } }
    spec:
      terminationGracePeriodSeconds: 60
      containers:
        - name: postgres
          image: postgres:17
          ports: [{ containerPort: 5432 }]
          env: [{ name: POSTGRES_PASSWORD, valueFrom: { secretKeyRef: { name: pg, key: password } } }]
          volumeMounts: [{ name: data, mountPath: /var/lib/postgresql/data }]
          readinessProbe: { exec: { command: ["pg_isready", "-U", "postgres"] } }
  volumeClaimTemplates:
    - metadata: { name: data }
      spec:
        accessModes: [ReadWriteOnce]
        storageClassName: fast-ssd
        resources: { requests: { storage: 100Gi } }
```

Особенности:

- PVC **не удаляются** при удалении StatefulSet (защита данных; политика `persistentVolumeClaimRetentionPolicy`);
- StatefulSet **не настраивает репликацию сам**: кластеризацию БД обеспечивает приложение/оператор;
- `partition` в rolling update — поэтапное обновление (canary для stateful);
- масштабирование вниз удаляет поды с наибольшим индексом.

**Для БД в K8s** лучше использовать **операторы** (CloudNativePG, Zalando Postgres Operator, Crunchy, Strimzi для Kafka, Redis Operator, ClickHouse Operator): они автоматизируют репликацию, failover, бэкапы, обновления. Альтернатива — управляемые БД вне кластера (часто надёжнее).

## PersistentVolume и PersistentVolumeClaim

| Объект | Роль |
|---|---|
| **PersistentVolume (PV)** | кусок хранилища в кластере (диск, NFS, облачный том), cluster-scoped |
| **PersistentVolumeClaim (PVC)** | запрос приложения на хранилище (размер, режим доступа, класс) |
| **StorageClass** | «профиль» для **динамического** создания PV (provisioner, тип диска, reclaimPolicy, `volumeBindingMode`, `allowVolumeExpansion`) |
| **CSI-драйвер** | плагин хранилища (AWS EBS, GCE PD, Ceph, Longhorn, OpenEBS, local-path) |

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata: { name: fast-ssd }
provisioner: ebs.csi.aws.com
parameters: { type: gp3, iops: "6000" }
reclaimPolicy: Retain                      # Delete по умолчанию: удалит диск вместе с PVC
volumeBindingMode: WaitForFirstConsumer    # привязка после выбора ноды (учёт зоны!)
allowVolumeExpansion: true
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata: { name: uploads }
spec:
  accessModes: [ReadWriteOnce]
  storageClassName: fast-ssd
  resources: { requests: { storage: 20Gi } }
```

**Access modes**: `ReadWriteOnce` (один узел), `ReadOnlyMany`, `ReadWriteMany` (несколько узлов: NFS, CephFS, EFS), `ReadWriteOncePod` (один под). Блочные диски облака — RWO и **привязаны к зоне доступности**: под с PVC может запускаться только в той же зоне.

**reclaimPolicy**: `Retain` (данные сохраняются после удаления PVC, ручная очистка) / `Delete` (том удаляется). Для критичных данных — Retain и снапшоты.

Расширение тома: увеличить `spec.resources.requests.storage` (при `allowVolumeExpansion`). **VolumeSnapshot** (CSI) — снимки и клонирование; бэкапы: Velero, Kasten, операторы БД.

Другие типы томов: `emptyDir` (временный, живёт с подом; `medium: Memory` для tmpfs), `hostPath` (каталог ноды: опасно), `configMap`/`secret`/`projected`, `local` PV (локальные NVMe).

## Job и CronJob

**Job** — разовая задача «запустить до успешного завершения».

```yaml
apiVersion: batch/v1
kind: Job
metadata: { name: migrate }
spec:
  backoffLimit: 2                   # число повторов при ошибке
  activeDeadlineSeconds: 600
  ttlSecondsAfterFinished: 3600     # автоудаление
  completions: 1
  parallelism: 1
  template:
    spec:
      restartPolicy: Never          # или OnFailure (Always для Job недопустимо)
      containers:
        - name: migrate
          image: registry.example.com/clinic/migrator:1.4.2
          envFrom: [{ secretRef: { name: db-migration } }]
```

Режимы: одиночный, параллельный с `completions`/`parallelism`, **indexed** (`completionMode: Indexed`, `JOB_COMPLETION_INDEX`), work queue.

**CronJob** — Job по расписанию:

```yaml
apiVersion: batch/v1
kind: CronJob
metadata: { name: backup }
spec:
  schedule: "0 3 * * *"
  timeZone: "Europe/Moscow"
  concurrencyPolicy: Forbid          # Allow | Forbid | Replace — что делать при наложении
  startingDeadlineSeconds: 300       # окно запуска после пропуска
  successfulJobsHistoryLimit: 3
  failedJobsHistoryLimit: 3
  suspend: false
  jobTemplate:
    spec:
      backoffLimit: 1
      template:
        spec:
          restartPolicy: OnFailure
          containers:
            - name: backup
              image: registry.example.com/tools/pg-backup:1.0
              args: ["--dest", "s3://backups/pg"]
```

Подводные камни CronJob: часовой пояс (по умолчанию UTC/контроллер), **идемпотентность** (Job может запуститься дважды/пропуститься), `concurrencyPolicy`, мониторинг невыполненных/упавших (kube-state-metrics: `kube_cronjob_status_last_successful_time`, алерты), накопление завершённых подов (`ttlSecondsAfterFinished`), ресурсы и сетевые политики для задач, «слишком много пропущенных запусков» (100) блокирует CronJob.

## DaemonSet

Под на каждой ноде (или подмножестве): агенты логов (Fluent Bit, Promtail), мониторинг (node-exporter), CNI, CSI-узловые драйверы, ingress на hostNetwork. Обновление по rolling, tolerations для master/taint-нод.

## Практики для stateful

- **стабильная идентичность и хранилище** нужны не всем — часто проще вынести состояние в управляемые сервисы;
- **антиaffinity по зонам/нодам** для реплик; PDB `maxUnavailable: 1`;
- **бэкапы и проверка восстановления** (VolumeSnapshot, Velero, PITR БД);
- **graceful shutdown** с достаточным `terminationGracePeriodSeconds`;
- не полагаться на `hostPath`/local без понимания привязки к ноде;
- мониторинг заполнения томов (`kubelet_volume_stats_*`), алерты, авторасширение;
- производительность диска (IOPS) и класс хранилища под нагрузку;
- обновление Kubernetes/нод: `drain` с учётом PDB и перепривязкой томов;
- тестировать сценарии: потеря ноды/зоны, восстановление из бэкапа.

## Вопросы с ответами

> [!question]- Чем StatefulSet отличается от Deployment?
> Даёт стабильные имена подов, собственное persistent-хранилище каждой реплике, упорядоченный запуск/обновление и headless-сервис для DNS каждого пода; Deployment подходит для взаимозаменяемых stateless-подов.

> [!question]- Что происходит с данными при удалении StatefulSet?
> PVC по умолчанию сохраняются (данные защищены); PV остаются в зависимости от `reclaimPolicy` StorageClass.

> [!question]- Как защититься от наложения запусков CronJob?
> `concurrencyPolicy: Forbid` (или Replace), идемпотентность задач, таймаут `activeDeadlineSeconds` и мониторинг.
