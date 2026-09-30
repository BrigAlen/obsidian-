---
type: topic
domain: devops
stage: 5
order: 12
status: todo
level: middle
tags: [domain/devops, stage/5, level/middle, priority/should]
reviewed: 
next_review: 
priority: should
time: 7
---

# Эксплуатация кластера: обновления, drain, PDB, affinity, taints и tolerations

↑ [[DO Этап 5 · Kubernetes|Этап 5 · Kubernetes]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~7 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> Плановое обслуживание без простоя: drain, PDB, распределение подов — повседневная работа администратора кластера.

## Обновление Kubernetes

- Kubernetes выпускает минорные версии ~3 раза в год; поддерживаются последние **три** минорные версии (~14 месяцев);
- пропускать минорные версии **нельзя**: 1.29 → 1.30 → 1.31;
- порядок: **control plane сначала**, затем ноды (допустимое отклонение версий kubelet от apiserver: до 3 минорных для новых версий, kube-proxy/kubelet не новее apiserver);
- подготовка: прочитать release notes и **deprecation/removal API** (`kubectl convert`, `pluto`, `kubent`), обновить манифесты/чарты, совместимость CNI/CSI/ingress/операторов; тест на staging; **бэкап etcd**;
- **управляемые кластеры**: обновление control plane кнопкой/API, ноды — rolling (surge-узлы) или пересоздание пулов; **kubeadm**: `kubeadm upgrade plan/apply`, затем `kubelet`;
- стратегии нод: in-place rolling, **blue/green пулов нод** (создать новый пул, drain старого), immutable-образы нод (Talos, Bottlerocket).

## Обслуживание ноды: cordon и drain

```bash
kubectl cordon node-1                     # пометить unschedulable (новые поды не назначаются)
kubectl drain node-1 --ignore-daemonsets --delete-emptydir-data --grace-period=60 --timeout=10m
# обслуживание, обновление...
kubectl uncordon node-1
kubectl get nodes -o wide
```

`drain` **выселяет (evict)** поды, уважая **PodDisruptionBudget**; DaemonSet-поды игнорируются; поды без контроллера не выселяются без `--force`; `emptyDir`-данные теряются; поды с локальными PV «застревают».

## PodDisruptionBudget

Гарантирует минимальную доступность при **добровольных** прерываниях (drain, автоскейлер, обновления).

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata: { name: api }
spec:
  minAvailable: 2          # или maxUnavailable: 1 (или проценты)
  selector: { matchLabels: { app: api } }
  unhealthyPodEvictionPolicy: AlwaysAllow
```

Ошибки: `minAvailable` = числу реплик → `drain` **навсегда блокируется**; одна реплика + `minAvailable: 1` — нельзя обновлять ноду. Не защищает от **недобровольных** отказов (падение ноды, OOM).

## Размещение подов

### nodeSelector и nodeAffinity

```yaml
spec:
  nodeSelector: { node-pool: general }
  affinity:
    nodeAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:          # жёсткое правило
        nodeSelectorTerms:
          - matchExpressions: [{ key: topology.kubernetes.io/zone, operator: In, values: [zone-a, zone-b] }]
      preferredDuringSchedulingIgnoredDuringExecution:         # предпочтение
        - weight: 50
          preference: { matchExpressions: [{ key: disktype, operator: In, values: [ssd] }] }
```

### podAffinity / podAntiAffinity

```yaml
affinity:
  podAntiAffinity:
    requiredDuringSchedulingIgnoredDuringExecution:
      - topologyKey: kubernetes.io/hostname                     # не более одного пода app=api на ноде
        labelSelector: { matchLabels: { app: api } }
  podAffinity:
    preferredDuringSchedulingIgnoredDuringExecution:
      - weight: 100
        podAffinityTerm:
          topologyKey: kubernetes.io/hostname
          labelSelector: { matchLabels: { app: redis } }        # держать рядом с кэшем
```

`topologyKey` задаёт «домен»: `kubernetes.io/hostname` (нода), `topology.kubernetes.io/zone` (зона).

### topologySpreadConstraints (предпочтительнее anti-affinity для равномерности)

```yaml
topologySpreadConstraints:
  - maxSkew: 1
    topologyKey: topology.kubernetes.io/zone
    whenUnsatisfiable: DoNotSchedule          # или ScheduleAnyway
    labelSelector: { matchLabels: { app: api } }
```

### Taints и tolerations

**Taint** на ноде **отталкивает** поды; **toleration** в поде позволяет на них попасть.

```bash
kubectl taint nodes gpu-1 dedicated=gpu:NoSchedule
kubectl taint nodes gpu-1 dedicated=gpu:NoSchedule-     # снять
```

```yaml
tolerations:
  - { key: dedicated, operator: Equal, value: gpu, effect: NoSchedule }
```

Эффекты: `NoSchedule` (не планировать), `PreferNoSchedule` (мягко), `NoExecute` (выселять уже работающие; `tolerationSeconds`). Системные taints: `node.kubernetes.io/not-ready`, `unreachable`, `node-role.kubernetes.io/control-plane:NoSchedule`.

Применение: выделенные пулы (GPU, spot, системные), изоляция арендаторов. **Toleration лишь разрешает** — для обязательного размещения нужен ещё nodeSelector/affinity.

## Приоритеты и вытеснение

`PriorityClass` (числа): критичные поды могут **вытеснять (preempt)** менее приоритетные при нехватке ресурсов. Системные: `system-cluster-critical`, `system-node-critical`. Используйте для инфраструктурных компонентов и для **overprovisioning**-подов (низкий приоритет «резерв»).

## Доступность и отказоустойчивость

- **минимум 2–3 реплики** критичных сервисов, распределение по **зонам** и нодам (spread constraints);
- **PDB** + **graceful shutdown** + readiness; `maxUnavailable: 0` в rolling;
- multi-AZ управляющий слой (3 control plane узла) и etcd;
- **ResourceQuota/LimitRange**, **PriorityClass**;
- **Cluster Autoscaler** с min/max на пул;
- автоматическое восстановление нод (node auto-repair, NPD — Node Problem Detector);
- **бэкапы**: etcd (снапшоты), Velero (ресурсы + тома), GitOps как источник истины.

## Повседневная эксплуатация

```bash
kubectl get nodes; kubectl describe node x                 # Conditions, Taints, Allocated resources
kubectl top nodes; kubectl get pods -A -o wide --field-selector spec.nodeName=node-1
kubectl get events -A --sort-by=.lastTimestamp | tail -30
kubectl get pods -A | grep -v Running
kubectl rollout restart deploy -n clinic                   # перезапуск с учётом стратегии
kubectl get pdb -A; kubectl get hpa -A
kubectl api-resources --verbs=list --namespaced -o name
```

Процессы: план обновлений (окна, ответственные), runbook, мониторинг состояния кластера (kube-state-metrics, алерты на NotReady ноды, Pending поды, заполнение дисков, срок сертификатов kubelet/apiserver), ротация сертификатов (`kubeadm certs renew`), управление версиями компонентов, аудит (Audit policy), политики (Kyverno/OPA), стоимость (FinOps).

## Вопросы с ответами

> [!question]- Как безопасно вывести ноду на обслуживание?
> `kubectl cordon` (запретить планирование), `kubectl drain --ignore-daemonsets --delete-emptydir-data` (выселить поды с учётом PDB), выполнить работы, затем `kubectl uncordon`.

> [!question]- Чем taint отличается от nodeSelector/affinity?
> Taint — свойство ноды, отталкивающее поды без toleration; nodeSelector/affinity — свойство пода, выбирающее ноды. Toleration лишь разрешает попасть на tainted-ноду, не обязывает.

> [!question]- Что такое PodDisruptionBudget и когда он мешает?
> Ограничение числа одновременно недоступных подов при добровольных прерываниях. Если `minAvailable` равен числу реплик (или реплика одна), `drain` блокируется и обновление ноды невозможно.
