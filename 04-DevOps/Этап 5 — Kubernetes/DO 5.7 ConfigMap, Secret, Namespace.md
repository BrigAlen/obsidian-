---
type: topic
domain: devops
stage: 5
order: 7
status: todo
level: middle
tags: [domain/devops, stage/5, level/middle, priority/should]
reviewed: 
next_review: 
priority: should
time: 8
---

# ConfigMap, Secret, Namespace

↑ [[DO Этап 5 · Kubernetes|Этап 5 · Kubernetes]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~8 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> Конфигурация и секреты вне образа — основа 12-factor; спрашивают способы подачи и безопасность Secret.

## ConfigMap

Хранит **несекретную** конфигурацию (пары ключ–значение или файлы) отдельно от образа.

```yaml
apiVersion: v1
kind: ConfigMap
metadata: { name: api-config, namespace: clinic }
data:
  LOG_LEVEL: info
  FEATURE_X: "true"
  appsettings.Production.json: |
    { "Cache": { "Ttl": 300 }, "Clinic": { "Name": "Central" } }
binaryData: {}          # при необходимости base64
immutable: false        # true — защита от изменений и снижение нагрузки на apiserver
```

Создание: `kubectl create configmap api-config --from-literal=LOG_LEVEL=info --from-file=appsettings.json`. Лимит размера ~1 МиБ.

## Способы использования

```yaml
spec:
  containers:
    - name: app
      image: ...
      env:
        - name: LOG_LEVEL
          valueFrom: { configMapKeyRef: { name: api-config, key: LOG_LEVEL } }
        - name: ConnectionStrings__Default
          valueFrom: { secretKeyRef: { name: api-db, key: connection-string } }
      envFrom:                                   # все ключи как переменные
        - configMapRef: { name: api-config }
        - secretRef:    { name: api-secrets, optional: true }
      volumeMounts:
        - { name: cfg,     mountPath: /app/config, readOnly: true }
        - { name: secrets, mountPath: /run/secrets, readOnly: true }
  volumes:
    - name: cfg
      configMap: { name: api-config, items: [{ key: appsettings.Production.json, path: appsettings.Production.json }] }
    - name: secrets
      secret: { secretName: api-secrets, defaultMode: 0400 }
```

| Способ | Обновление при изменении |
|---|---|
| **Переменные окружения** | **не** обновляются (только при пересоздании пода) |
| **Том (volume)** | файлы обновляются автоматически (через задержку ~1 мин, atomic symlink swap), **кроме** подключения через `subPath` |
| Чтение из API приложением | динамически (нужны права RBAC) |

Приложение должно уметь перечитывать файлы (`reloadOnChange` в .NET `IOptionsMonitor`) либо нужен **рестарт**: Helm `checksum/config` аннотация в шаблоне пода, **Reloader** (stakater/reloader) или `kubectl rollout restart`. .NET: переменные окружения `Section__Key` (двойное подчёркивание) переопределяют JSON.

**immutable ConfigMap/Secret** + версионирование в имени (`api-config-v12`): безопасные обновления и откаты вместе с Deployment.

## Secret

Объект для **чувствительных данных** (пароли, токены, ключи, сертификаты). Данные в `data` — **base64** (это кодирование, а не шифрование!).

```yaml
apiVersion: v1
kind: Secret
metadata: { name: api-db, namespace: clinic }
type: Opaque                     # kubernetes.io/tls, kubernetes.io/dockerconfigjson, kubernetes.io/basic-auth, kubernetes.io/service-account-token
stringData:                      # удобнее: значения в открытом виде, K8s кодирует сам
  connection-string: "Host=pg;Database=clinic;Username=clinic;Password=s3cret"
```

```bash
kubectl create secret generic api-db --from-literal=password='...' 
kubectl create secret tls app-tls --cert=tls.crt --key=tls.key
kubectl create secret docker-registry regcred --docker-server=registry.example.com --docker-username=ci --docker-password=...
kubectl get secret api-db -o jsonpath='{.data.password}' | base64 -d
```

### Безопасность Secret

- **по умолчанию лежат в etcd незашифрованными** → включить **шифрование at rest** (`EncryptionConfiguration`, KMS provider) и защитить бэкапы etcd;
- **RBAC**: минимальные права на `get/list/watch` Secret (`list` раскрывает все значения!), отдельные ServiceAccounts;
- не передавать через переменные окружения, если есть выбор: они видны в `kubectl describe`, `/proc`, дампах и логах крэшей; **том** безопаснее (tmpfs, права `0400`);
- не хранить Secret-манифесты в Git в открытом виде: **Sealed Secrets**, **SOPS** (age/KMS), **External Secrets Operator** (синхронизация из Vault/AWS SM/Yandex Lockbox/Azure KV), **Secrets Store CSI Driver**;
- не логировать, маскировать;
- ротация: обновление внешнего хранилища → ESO синхронизирует → перезапуск/перечитывание;
- PodSecurity, NetworkPolicy ограничивают, откуда можно прочитать секреты; audit-логи на доступ к Secret.

## Namespace

Логическое разделение кластера: имена ресурсов уникальны **внутри** namespace.

```bash
kubectl create namespace clinic-staging
kubectl get ns; kubectl get pods -n clinic-staging; kubectl get pods -A
```

Стартовые: `default`, `kube-system` (системные компоненты), `kube-public`, `kube-node-lease`.

Применения: окружения (`dev/staging/prod` — лучше отдельные кластеры для prod), команды и продукты, изоляция по доступам.

Инструменты изоляции на уровне namespace:

- **RBAC** (Role/RoleBinding), **ResourceQuota** (суммарные лимиты CPU/памяти/числа объектов), **LimitRange** (значения по умолчанию и границы для контейнеров), **NetworkPolicy**, **Pod Security Admission** (метка `pod-security.kubernetes.io/enforce: restricted`);
- не все ресурсы в namespace (Node, PV, StorageClass, ClusterRole, CRD — cluster-scoped);
- Namespace — **не жёсткая граница безопасности** сама по себе (общее ядро нод, общая сеть без NetworkPolicy).

```yaml
apiVersion: v1
kind: ResourceQuota
metadata: { name: team-quota, namespace: clinic }
spec:
  hard: { requests.cpu: "8", requests.memory: 16Gi, limits.memory: 32Gi, pods: "50", persistentvolumeclaims: "10" }
---
apiVersion: v1
kind: LimitRange
metadata: { name: defaults, namespace: clinic }
spec:
  limits:
    - type: Container
      default:        { memory: 512Mi }
      defaultRequest: { cpu: 100m, memory: 128Mi }
```

Обращение между namespaces: `service.namespace.svc.cluster.local`.

## Практики

- конфигурация окружений — в Git (Helm values/Kustomize overlays), **секреты отдельно**;
- один образ на окружения; различается ConfigMap/Secret;
- валидация конфигурации при старте (fail fast);
- именование и метки; один Secret на назначение (минимальный доступ);
- `optional: false` по умолчанию — под не стартует без необходимого Secret (явная ошибка `CreateContainerConfigError`);
- документируйте обязательные ключи.

## Вопросы с ответами

> [!question]- Обновляются ли переменные окружения из ConfigMap при его изменении?
> Нет, переменные фиксируются при старте контейнера. Значения из смонтированного тома обновляются автоматически (кроме subPath); для env нужен перезапуск подов.

> [!question]- Безопасен ли Secret в Kubernetes?
> По умолчанию нет: это base64 в etcd. Нужны шифрование etcd, строгий RBAC, внешние хранилища (ESO/CSI) и запрет хранения открытых секретов в Git.

> [!question]- Чем Namespace отличается от отдельного кластера как граница изоляции?
> Namespace разделяет имена и права (RBAC, квоты), но ядро нод и сеть общие; для жёсткой изоляции (prod/dev, разные арендаторы) нужны отдельные кластеры или дополнительные механизмы.
