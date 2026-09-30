---
type: topic
domain: devops
stage: 5
order: 6
status: todo
level: middle
tags: [domain/devops, stage/5, level/middle, priority/should]
reviewed: 
next_review: 
priority: should
time: 6
---

# NetworkPolicy и сетевая модель Kubernetes

↑ [[DO Этап 5 · Kubernetes|Этап 5 · Kubernetes]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~6 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> Сетевая модель K8s и изоляция трафика — часть безопасности кластера; спрашивают default deny и правила ingress/egress.

## Сетевая модель

Требования Kubernetes:

1. Каждый под получает **уникальный IP** (из Pod CIDR).
2. Поды **напрямую общаются** друг с другом без NAT (независимо от ноды).
3. Агенты на ноде доступны подам на этой ноде.
4. Контейнеры в поде делят сетевой стек (общий `localhost`).

Реализуют **CNI-плагины**: Calico (BGP/IPIP/VXLAN, политики), Cilium (eBPF, L7-политики, замена kube-proxy, Hubble), Flannel (простая оверлей-сеть, без политик), Weave, cloud CNI (AWS VPC CNI, Azure CNI). Виды: **overlay** (VXLAN, инкапсуляция) и **routed** (BGP/VPC-native).

Сети: **Pod CIDR**, **Service CIDR** (виртуальные ClusterIP), сеть нод. Не должны пересекаться друг с другом и с корпоративными сетями.

## Проблема по умолчанию

**Все поды могут общаться со всеми** (все namespaces). Компрометация одного пода открывает доступ к БД, внутренним API и метаданным облака. **NetworkPolicy** ограничивает трафик на L3/L4 (и L7 в Cilium).

NetworkPolicy работает **только если CNI её поддерживает** (Calico, Cilium — да; Flannel — нет); без поддержки объект создаётся, но ничего не делает.

## Принцип работы

- политика выбирает **поды** (`podSelector`) в своём namespace;
- как только под выбран хотя бы одной политикой типа `Ingress`/`Egress`, **всё, что явно не разрешено в этом направлении, запрещено** (whitelist);
- политики **аддитивны** (объединение разрешений); запретительных правил нет;
- связь работает, если разрешена **обеими сторонами** (egress источника и ingress назначения, если политики применены к обоим);
- правила: источники/цели — `podSelector`, `namespaceSelector`, `ipBlock`; порты и протоколы.

### Default deny

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata: { name: default-deny-all, namespace: clinic }
spec:
  podSelector: {}                 # все поды namespace
  policyTypes: [Ingress, Egress]  # без правил = запретить всё
```

Затем точечные разрешения.

### Разрешить API принимать трафик только от ingress-контроллера и ходить в БД

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata: { name: api, namespace: clinic }
spec:
  podSelector: { matchLabels: { app: api } }
  policyTypes: [Ingress, Egress]
  ingress:
    - from:
        - namespaceSelector: { matchLabels: { kubernetes.io/metadata.name: ingress-nginx } }
          podSelector:       { matchLabels: { app.kubernetes.io/name: ingress-nginx } }
      ports: [{ protocol: TCP, port: 8080 }]
  egress:
    - to: [{ podSelector: { matchLabels: { app: postgres } } }]
      ports: [{ protocol: TCP, port: 5432 }]
    - to: [{ namespaceSelector: { matchLabels: { kubernetes.io/metadata.name: kube-system } }, podSelector: { matchLabels: { k8s-app: kube-dns } } }]
      ports: [{ protocol: UDP, port: 53 }, { protocol: TCP, port: 53 }]      # DNS!
    - to: [{ ipBlock: { cidr: 0.0.0.0/0, except: [169.254.169.254/32, 10.0.0.0/8] } }]   # интернет, но не метаданные и внутренние сети
      ports: [{ protocol: TCP, port: 443 }]
```

Важные моменты:

- **DNS (53/UDP+TCP)** и доступ к kube-dns нужно разрешать явно в egress, иначе имена не резолвятся;
- в `from` список элементов — **ИЛИ**, а `namespaceSelector` и `podSelector` **в одном элементе** — **И**;
- ограничение по namespace через метку `kubernetes.io/metadata.name` (автоматическая);
- метаданные облака `169.254.169.254` блокируйте из подов, которым не нужны;
- служебный трафик: healthchecks от kubelet и нод не блокируется политиками (зависит от CNI), мониторинг (Prometheus) нужно разрешить в ingress;
- политики на `Service` IP применяются к подам-бэкендам после DNAT.

## Расширенные политики

- **Cilium** (`CiliumNetworkPolicy`): L7 (HTTP методы/пути, gRPC, Kafka), FQDN-политики (`toFQDNs`), политики по идентичности, кластерные (`CiliumClusterwideNetworkPolicy`);
- **Calico** (`GlobalNetworkPolicy`, порядок/приоритеты, deny-правила, `Order`);
- **Admin/Baseline NetworkPolicy** (новый API): кластерные правила, которые нельзя переопределить;
- **service mesh** (Istio/Linkerd): mTLS и авторизация по идентичности (AuthorizationPolicy).

## Отладка

```bash
kubectl get netpol -A; kubectl describe netpol api -n clinic
kubectl run tmp --rm -it --image=nicolaka/netshoot -n clinic -- bash
#   curl -m3 http://api:8080; nc -zv postgres 5432; nslookup api
```

- Cilium: `cilium monitor --type drop`, Hubble UI/CLI (`hubble observe --verdict DROPPED`);
- Calico: `calicoctl`, логирование политик (`LOG` action);
- симптом «внезапно всё перестало работать после default deny» — забыт DNS, метрики, ingress-контроллер, kube-apiserver (для операторов).

Инструменты проверки: `netpol-analyzer`, Network Policy Editor (Cilium), `kubectl-np-viewer`.

## Другие аспекты сети

- **kube-proxy режимы**: iptables, **IPVS** (быстрее при тысячах сервисов), nftables; Cilium заменяет kube-proxy (eBPF);
- **hostNetwork** и `hostPort` — обходят изоляцию, избегать;
- **Egress**: NAT через ноды/egress gateway (фиксированные IP для внешних allowlist);
- **MTU** и оверлей: потери больших пакетов;
- **IPv4/IPv6 dual-stack**; **Multus** — несколько сетевых интерфейсов;
- **Service mesh**: sidecar или ambient, mTLS, политика;
- **Безопасность**: разделение namespaces по окружениям/командам + NetworkPolicy + RBAC + Pod Security.

## Вопросы с ответами

> [!question]- Что происходит, если в namespace нет ни одной NetworkPolicy?
> Весь трафик между подами разрешён (по умолчанию «все со всеми»). Политики начинают ограничивать только выбранные ими поды.

> [!question]- Как сделать default deny и что нельзя забыть?
> Политика с пустым `podSelector` и типами Ingress/Egress без правил; затем разрешить нужное: входящий от ingress-контроллера, исходящий к БД и обязательно DNS (53 UDP/TCP к kube-dns).

> [!question]- Почему NetworkPolicy может не работать?
> CNI-плагин не поддерживает политики (например, Flannel), либо политика не выбирает нужные поды (метки), либо правила `from` сформулированы неверно (И/ИЛИ селекторов).
