---
type: topic
domain: devops
stage: 5
order: 1
status: todo
level: middle
tags: [domain/devops, stage/5, level/middle, priority/should]
reviewed: 
next_review: 
priority: should
time: 4
---

# Зачем оркестратор и архитектура Kubernetes

↑ [[DO Этап 5 · Kubernetes|Этап 5 · Kubernetes]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~4 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> Базовый вопрос про Kubernetes: какие проблемы он решает и из каких компонентов состоит.

## Проблемы, которые решает оркестратор

Контейнеры решают упаковку, но в проде возникают задачи: на каких серверах запускать, как перезапускать упавшие, как масштабировать, как обновлять без простоя, как находить друг друга и балансировать, где хранить конфигурации и секреты, как ограничивать ресурсы.

Kubernetes (K8s) — оркестратор контейнеров: **декларативно** описываем желаемое состояние, а контроллеры постоянно приводят реальность к нему (**reconciliation loop**).

Возможности: планирование подов по нодам, самовосстановление (перезапуск, замена при падении узла), горизонтальное масштабирование, rolling updates и откаты, service discovery и балансировка, конфигурации и секреты, управление хранилищами, batch-задачи, расширяемость (CRD, операторы).

## Архитектура

```text
                   ┌──────────────────── Control Plane ────────────────────┐
kubectl/CI ──HTTPS─▶ kube-apiserver ◀──▶ etcd (хранилище состояния)
                   │      ▲     ▲
                   │  kube-scheduler   kube-controller-manager   cloud-controller-manager
                   └────────────────────────────────────────────────────────┘
                                   │
        ┌──────────────────────────┴───────────────────────────┐
        ▼ Node 1                                               ▼ Node N
   kubelet ─ container runtime (containerd) ─ pods       kubelet ... 
   kube-proxy (Service → iptables/IPVS)   CNI-плагин (сеть подов)
```

### Control plane

| Компонент | Роль |
|---|---|
| **kube-apiserver** | единая точка входа REST API: аутентификация, авторизация (RBAC), admission, валидация; единственный, кто пишет в etcd |
| **etcd** | распределённое хранилище ключ-значение (Raft) со всем состоянием кластера; критичен для бэкапов и HA |
| **kube-scheduler** | выбирает ноду для нового пода (ресурсы, affinity, taints, топология) |
| **kube-controller-manager** | набор контроллеров: Node, ReplicaSet, Deployment, Job, EndpointSlice, ServiceAccount… |
| **cloud-controller-manager** | интеграция с облаком (LoadBalancer, диски, маршруты) |

### Node (рабочий узел)

| Компонент | Роль |
|---|---|
| **kubelet** | агент: получает PodSpec, управляет контейнерами через CRI, проверяет probes, отчитывается о статусе |
| **Container runtime** | containerd / CRI-O (через **CRI**) |
| **kube-proxy** | реализует Service: правила iptables/IPVS/nftables (или заменён eBPF в Cilium) |
| **CNI-плагин** | сеть подов: Calico, Cilium, Flannel, Weave |
| **CSI-драйверы** | тома |

## Основные объекты

| Объект | Назначение |
|---|---|
| **Pod** | минимальная единица: один или несколько контейнеров с общей сетью и томами |
| **ReplicaSet** | поддерживает N реплик пода |
| **Deployment** | декларативное управление ReplicaSet: rolling update, откат |
| **StatefulSet** | приложения с состоянием (стабильные имена, тома) |
| **DaemonSet** | под на каждой ноде (агенты логов/мониторинга) |
| **Job / CronJob** | разовые и периодические задачи |
| **Service** | стабильный адрес и балансировка между подами |
| **Ingress / Gateway** | внешний L7-доступ |
| **ConfigMap / Secret** | конфигурация и секреты |
| **PersistentVolume / PVC / StorageClass** | постоянное хранилище |
| **Namespace** | логическая изоляция ресурсов, квоты, права |
| **ServiceAccount, Role/RoleBinding** | идентичность и RBAC |
| **HPA/VPA, PDB, NetworkPolicy, LimitRange, ResourceQuota** | масштабирование, доступность, сетевые политики, лимиты |
| **CRD / Operator** | расширение API, автоматизация сложных систем |

Все объекты — YAML/JSON с полями `apiVersion`, `kind`, `metadata` (name, namespace, labels, annotations), `spec` (желаемое), `status` (фактическое).

## Принцип работы

1. `kubectl apply -f deployment.yaml` → API server валидирует и сохраняет в etcd.
2. Контроллер Deployment создаёт ReplicaSet → контроллер RS создаёт Pod-объекты (без ноды).
3. Scheduler назначает ноду (`spec.nodeName`).
4. kubelet на ноде видит под, через CRI запускает контейнеры, настраивает сеть (CNI) и тома.
5. kubelet отчитывается о статусе; контроллеры следят за отклонениями и исправляют.

**Watch-механизм**: компоненты подписываются на изменения API, а не опрашивают.

## Labels и selectors

Метки (`app: api, tier: backend`) — основной механизм связи: Service выбирает поды по селектору, Deployment управляет подами по `matchLabels`. Аннотации — несистемные метаданные.

## Дистрибутивы и способы развёртывания

- управляемые: **EKS, GKE, AKS, Yandex Managed Kubernetes, VK Cloud**: control plane обслуживает провайдер;
- self-managed: **kubeadm**, **k3s/RKE2** (лёгкие), **Talos**, **OpenShift**, Kubespray, Cluster API;
- локально: kind, minikube, k3d, Docker Desktop.

## Когда Kubernetes нужен, а когда нет

**Нужен**: много сервисов и команд, требования к отказоустойчивости и автомасштабированию, частые релизы, гибридные/мультиоблачные среды, стандартизация платформы.

**Не нужен**: один-два сервиса, небольшая команда, стабильная нагрузка — достаточно docker compose/systemd/PaaS (Fly, Render), Nomad, ECS. Kubernetes добавляет сложность (сеть, безопасность, обновления, стоимость, компетенции).

## Вопросы с ответами

> [!question]- Что такое reconciliation loop?
> Контроллеры сравнивают желаемое состояние (spec в etcd) с фактическим и предпринимают действия, чтобы их совместить; делают это непрерывно.

> [!question]- Какие компоненты входят в control plane?
> kube-apiserver, etcd, kube-scheduler, kube-controller-manager (и cloud-controller-manager при облачной интеграции).

> [!question]- Зачем нужен kube-proxy?
> Реализует сервисы: программирует правила iptables/IPVS на нодах, чтобы трафик на ClusterIP распределялся по подам.
