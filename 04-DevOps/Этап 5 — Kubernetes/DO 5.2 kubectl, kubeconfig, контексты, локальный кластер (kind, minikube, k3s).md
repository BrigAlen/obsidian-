---
type: topic
domain: devops
stage: 5
order: 2
status: todo
level: middle
tags: [domain/devops, stage/5, level/middle, priority/should]
reviewed: 
next_review: 
priority: should
time: 6
---

# kubectl, kubeconfig, контексты, локальный кластер (kind, minikube, k3s)

↑ [[DO Этап 5 · Kubernetes|Этап 5 · Kubernetes]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~6 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> Ежедневный инструмент: нужны основные команды, работа с контекстами и способы запуска локального кластера.

## kubeconfig и контексты

`~/.kube/config` (или `KUBECONFIG`) хранит **clusters** (адрес, CA), **users** (credentials: сертификат, токен, exec-плагин OIDC) и **contexts** (кластер + пользователь + namespace).

```bash
kubectl config get-contexts
kubectl config current-context
kubectl config use-context prod-cluster
kubectl config set-context --current --namespace=clinic      # namespace по умолчанию
export KUBECONFIG=~/.kube/config:~/.kube/stage.yaml; kubectl config view --flatten
```

Удобства: `kubectx`/`kubens`, `k9s` (TUI), Lens, `stern` (логи нескольких подов), `kubecolor`, алиас `k=kubectl`, автодополнение (`source <(kubectl completion bash)`).

**Безопасность**: kubeconfig с админ-правами — секрет; не коммитить; отдельные контексты для prod с подтверждением (prompt в shell), минимальные права (RBAC), короткоживущие токены (OIDC).

## Основные команды

```bash
kubectl get pods -n clinic -o wide                   # -o wide | yaml | json | name | custom-columns | jsonpath
kubectl get all; kubectl get deploy,svc,ing,cm,secret
kubectl get pods -l app=api --watch
kubectl describe pod api-7d9f-xk2lp                  # события, статус, причины
kubectl logs api-7d9f-xk2lp -c app -f --tail 100 --previous
kubectl exec -it api-7d9f-xk2lp -- sh
kubectl port-forward svc/api 8080:80                 # локальный доступ к сервису
kubectl cp pod:/app/file ./file
kubectl top pods|nodes                               # нужен metrics-server

kubectl apply -f manifest.yaml                       # декларативно (предпочтительно)
kubectl apply -k overlays/prod                       # kustomize
kubectl diff -f manifest.yaml                        # что изменится
kubectl delete -f manifest.yaml
kubectl create deployment web --image=nginx --replicas=2 --dry-run=client -o yaml > d.yaml   # генерация манифеста
kubectl scale deploy/api --replicas=5
kubectl set image deploy/api app=registry/api:1.4.3
kubectl rollout status|history|undo deploy/api
kubectl rollout restart deploy/api
kubectl edit deploy/api                              # правка «вживую» (избегать в проде — дрейф)
kubectl explain pod.spec.containers.resources        # встроенная документация по полям
kubectl api-resources; kubectl api-versions
kubectl auth can-i create deployments -n clinic --as system:serviceaccount:clinic:ci
kubectl get events --sort-by=.lastTimestamp
kubectl label pod x env=dev; kubectl annotate ...
kubectl debug -it pod/api --image=busybox --target=app
kubectl cordon|drain|uncordon node1
```

Императивно (`create`, `run`, `expose`) — для экспериментов; **декларативно** (`apply` + Git) — для продакшна.

## Вывод и фильтрация

```bash
kubectl get pods -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.status.phase}{"\n"}{end}'
kubectl get pods -o custom-columns=NAME:.metadata.name,NODE:.spec.nodeName,IP:.status.podIP
kubectl get pods --field-selector=status.phase!=Running -A
kubectl get pod x -o json | jq '.status.containerStatuses[].state'
kubectl get nodes -L topology.kubernetes.io/zone
```

## Локальные кластеры

| Инструмент | Особенности |
|---|---|
| **kind** (Kubernetes in Docker) | ноды = контейнеры Docker; быстрый многонодовый кластер; CI-тесты; `kind create cluster --config`, `kind load docker-image` |
| **minikube** | ВМ или Docker-драйвер; аддоны (`minikube addons enable ingress metrics-server`); `minikube tunnel` для LoadBalancer |
| **k3s / k3d** | облегчённый дистрибутив (один бинарь), k3d — в Docker; подходит для edge, homelab, VPS |
| **Docker Desktop / Rancher Desktop** | встроенный кластер |
| **microk8s** | snap-дистрибутив Canonical |

```bash
kind create cluster --name dev --config - <<'EOF'
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
  - role: control-plane
    extraPortMappings: [{ containerPort: 80, hostPort: 8080 }]
  - role: worker
  - role: worker
EOF
kubectl cluster-info --context kind-dev
```

Для разработки: **Tilt**, **Skaffold**, **Telepresence**, **DevSpace** — быстрые циклы «код → образ → кластер».

## Удобные приёмы

- `--dry-run=client -o yaml` и `kubectl explain` для написания манифестов;
- `kubectl diff` перед `apply`; `--server-side` apply для больших ресурсов;
- `kubectl get events` — первая точка диагностики;
- `kubectl rollout status` в пайплайнах для ожидания готовности (`--timeout`);
- манифесты валидировать (`kubeconform`, `kubectl apply --dry-run=server`);
- не использовать `latest`, не редактировать ресурсы руками в проде (GitOps).

## Вопросы с ответами

> [!question]- Что такое контекст kubeconfig?
> Сочетание кластера, пользователя и namespace; `kubectl config use-context` переключает, куда будут направлены команды.

> [!question]- Чем kubectl apply отличается от create?
> `create` создаёт ресурс и падает, если он есть; `apply` декларативно применяет желаемое состояние (создаёт или обновляет, сохраняя последнюю применённую конфигурацию / server-side apply).

> [!question]- Чем kind отличается от minikube?
> kind запускает ноды как контейнеры Docker (быстрые многонодовые кластеры, удобно для CI); minikube — одна нода в ВМ/контейнере с набором аддонов для локальной разработки.
