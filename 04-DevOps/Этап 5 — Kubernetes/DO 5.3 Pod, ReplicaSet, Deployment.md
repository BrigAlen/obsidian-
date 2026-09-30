---
type: topic
domain: devops
stage: 5
order: 3
status: todo
level: middle
tags: [domain/devops, stage/5, level/middle, priority/should]
reviewed: 
next_review: 
priority: should
time: 7
---

# Pod, ReplicaSet, Deployment

↑ [[DO Этап 5 · Kubernetes|Этап 5 · Kubernetes]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~7 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> Pod, ReplicaSet и Deployment — основа K8s; спрашивают жизненный цикл, rolling update и откат.

## Pod

Минимальная развёртываемая единица: один или несколько **тесно связанных контейнеров**, разделяющих сетевой namespace (один IP, localhost), тома и IPC. Контейнеры одного пода всегда на одной ноде.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: api
  labels: { app: api }
spec:
  containers:
    - name: app
      image: registry.example.com/clinic/api:1.4.2
      ports: [{ containerPort: 8080 }]
      env:
        - { name: ASPNETCORE_ENVIRONMENT, value: Production }
      resources:
        requests: { cpu: 250m, memory: 256Mi }
        limits:   { memory: 512Mi }
      readinessProbe: { httpGet: { path: /health/ready, port: 8080 } }
    - name: log-shipper              # sidecar
      image: fluent/fluent-bit:3
  restartPolicy: Always
```

**Паттерны нескольких контейнеров**: **sidecar** (вспомогательный: прокси, агент логов), **init-контейнеры** (выполняются до основных последовательно: миграции, ожидание зависимости, загрузка конфигурации), **ambassador**, **adapter**; нативные sidecar-контейнеры (`initContainers` с `restartPolicy: Always`, K8s 1.29+).

## Жизненный цикл

| Фаза (`status.phase`) | Значение |
|---|---|
| `Pending` | принят, но ещё не запущен (планирование, загрузка образа) |
| `Running` | хотя бы один контейнер работает |
| `Succeeded` | все контейнеры завершились успешно (Job) |
| `Failed` | завершились с ошибкой |
| `Unknown` | нет связи с нодой |

Состояния контейнера: `Waiting` (причины: `ContainerCreating`, `ImagePullBackOff`, `CrashLoopBackOff`), `Running`, `Terminated` (`exitCode`, `reason`: `Completed`, `Error`, `OOMKilled`).

Завершение: SIGTERM → `preStop` hook → `terminationGracePeriodSeconds` (30 с) → SIGKILL.

**Поды одноразовые (ephemeral)**: не «перезапускаются» на другую ноду — заменяются новыми. Голый Pod без контроллера при падении ноды не восстановится: в проде поды создают через Deployment/StatefulSet/Job.

## ReplicaSet

Поддерживает заданное число одинаковых подов (по селектору и шаблону). Обычно создаётся Deployment'ом, напрямую не используется.

## Deployment

Декларативное управление stateless-приложением: создаёт ReplicaSet, обеспечивает **rolling update** и **откат**.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata: { name: api, labels: { app: api } }
spec:
  replicas: 3
  revisionHistoryLimit: 5
  selector: { matchLabels: { app: api } }
  strategy:
    type: RollingUpdate
    rollingUpdate: { maxSurge: 1, maxUnavailable: 0 }
  minReadySeconds: 10
  progressDeadlineSeconds: 300
  template:
    metadata: { labels: { app: api } }
    spec:
      containers:
        - name: app
          image: registry.example.com/clinic/api:1.4.2
          ports: [{ containerPort: 8080 }]
          resources: { requests: { cpu: 250m, memory: 256Mi }, limits: { memory: 512Mi } }
          readinessProbe: { httpGet: { path: /health/ready, port: 8080 }, periodSeconds: 5 }
          livenessProbe:  { httpGet: { path: /health/live,  port: 8080 }, initialDelaySeconds: 15 }
      terminationGracePeriodSeconds: 45
```

Правила: `selector` должен совпадать с `template.metadata.labels` и неизменяем; **обновление запускается при изменении `spec.template`** (образ, env, ресурсы), не при изменении `replicas`.

### Rolling update

1. Создаётся новый ReplicaSet, растёт число новых подов (до `maxSurge` сверх желаемого).
2. Новые поды должны стать **Ready**; старые уменьшаются (не более `maxUnavailable` недоступных).
3. Завершается, когда все поды новой версии готовы.

С `maxUnavailable: 0, maxSurge: 1` ёмкость никогда не падает ниже желаемой (нужен запас ресурсов). Без readiness probe трафик пойдёт на поды до готовности приложения.

Стратегия `Recreate`: сначала удалить все старые поды (простой).

### Откат и история

```bash
kubectl rollout status deploy/api --timeout=300s
kubectl rollout history deploy/api
kubectl rollout undo deploy/api [--to-revision=3]
kubectl rollout pause|resume deploy/api
kubectl set image deploy/api app=registry.example.com/clinic/api:1.4.3 --record
```

`revisionHistoryLimit` — сколько старых ReplicaSet хранить для отката. Застрявший rollout (`ProgressDeadlineExceeded`) — причины: образ не загружается, падает readiness, нет ресурсов; диагностика `kubectl describe deploy`, `get rs`, `describe pod`, `get events`.

## Масштабирование и самовосстановление

```bash
kubectl scale deploy/api --replicas=5
kubectl autoscale deploy/api --min=3 --max=10 --cpu-percent=70     # HPA
```

Упал под → RS создаёт новый; упала нода → поды пересоздаются на других нодах (после `pod-eviction-timeout`/taints); падение приложения → kubelet перезапускает контейнер (`CrashLoopBackOff` с экспоненциальной задержкой до 5 минут).

## Типичные проблемы подов

| Статус | Причина и действия |
|---|---|
| `Pending` | нет ресурсов на нодах, taints/affinity, нет PV, квоты: `kubectl describe pod` → Events (`FailedScheduling`) |
| `ImagePullBackOff` / `ErrImagePull` | неверный образ/тег, нет доступа к реестру (`imagePullSecrets`), сеть |
| `CrashLoopBackOff` | приложение падает: `kubectl logs --previous`, код выхода, конфигурация, зависимости, OOM, неверный probe |
| `CreateContainerConfigError` | отсутствует ConfigMap/Secret, ошибка в env |
| `OOMKilled` (exit 137) | превышен `limits.memory` |
| `Evicted` | нехватка ресурсов на ноде (давление по памяти/диску) |
| `Terminating` завис | finalizers, нода недоступна, процесс не завершается |
| `Running`, но 0/1 Ready | не проходит readiness probe |

## Практики

- один основной процесс на контейнер, логи в stdout;
- всегда задавать **requests/limits**, **probes**, graceful shutdown;
- конкретные теги образов, `imagePullPolicy: IfNotPresent`;
- `securityContext`: non-root, read-only rootfs;
- метки по стандарту (`app.kubernetes.io/name|instance|version|component|part-of|managed-by`);
- не запускать «голые» поды в проде;
- несколько реплик + PodDisruptionBudget + anti-affinity для доступности.

## Вопросы с ответами

> [!question]- Чем Deployment отличается от ReplicaSet?
> ReplicaSet лишь поддерживает число подов. Deployment управляет ReplicaSet'ами, обеспечивая rolling update, откат и историю версий.

> [!question]- Как работает rolling update и что регулируют maxSurge и maxUnavailable?
> Новые поды создаются постепенно, старые удаляются по мере готовности новых; `maxSurge` — сколько подов сверх желаемого можно создать, `maxUnavailable` — сколько можно временно потерять.

> [!question]- Что делать при CrashLoopBackOff?
> `kubectl logs --previous`, `describe pod` (код выхода, причина), проверить конфигурацию, секреты, зависимости, лимиты памяти и probes.
