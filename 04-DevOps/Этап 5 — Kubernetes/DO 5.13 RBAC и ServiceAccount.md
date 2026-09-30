---
type: topic
domain: devops
stage: 5
order: 13
status: todo
level: middle
tags: [domain/devops, stage/5, level/middle, priority/should]
reviewed: 
next_review: 
priority: should
time: 7
---

# RBAC и ServiceAccount

↑ [[DO Этап 5 · Kubernetes|Этап 5 · Kubernetes]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~7 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> Контроль доступа к API Kubernetes — базовая безопасность: Role/ClusterRole, ServiceAccount, принцип наименьших привилегий.

## Аутентификация и авторизация

Запрос к API проходит: **аутентификация** (кто?) → **авторизация** (можно ли?) → **admission** (мутация/валидация политиками) → etcd.

**Аутентификация**: клиентские сертификаты (kubeadm-админ), bearer-токены ServiceAccount, **OIDC** (Keycloak, Dex, облачные IAM), webhook, exec-плагины облаков. Пользователей как объектов в K8s **нет** — они внешние (имя и группы из сертификата/токена).

**Авторизация**: режим **RBAC** (Role-Based Access Control) по умолчанию (`--authorization-mode=Node,RBAC`).

## Объекты RBAC

| Объект | Область | Назначение |
|---|---|---|
| **Role** | namespace | набор разрешений (verbs на resources) в namespace |
| **ClusterRole** | кластер | разрешения на cluster-scoped ресурсы (nodes, PV, CRD), на все namespaces или шаблон для агрегирования |
| **RoleBinding** | namespace | связывает Role/ClusterRole с субъектами **в namespace** |
| **ClusterRoleBinding** | кластер | связывает ClusterRole с субъектами **во всём кластере** |

Субъекты: `User`, `Group`, `ServiceAccount`.

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata: { name: deployer, namespace: clinic }
rules:
  - apiGroups: ["apps"]
    resources: ["deployments", "deployments/scale"]
    verbs: ["get", "list", "watch", "update", "patch"]
  - apiGroups: [""]
    resources: ["pods", "pods/log"]
    verbs: ["get", "list", "watch"]
  - apiGroups: [""]
    resources: ["configmaps"]
    resourceNames: ["api-config"]           # только конкретный ресурс
    verbs: ["get", "update"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata: { name: ci-deployer, namespace: clinic }
subjects:
  - kind: ServiceAccount
    name: ci
    namespace: clinic
  - kind: Group
    name: clinic-developers
    apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: Role
  name: deployer
  apiGroup: rbac.authorization.k8s.io
```

**Verbs**: `get`, `list`, `watch`, `create`, `update`, `patch`, `delete`, `deletecollection`, а также `exec` (subresource `pods/exec`), `impersonate`, `bind`, `escalate`. Правила только **разрешающие** (запретов нет): права — объединение всех привязок.

Встроенные ClusterRole: `cluster-admin` (всё), `admin` (полный в namespace), `edit` (изменять, без RBAC), `view` (только чтение) — их можно связывать RoleBinding в конкретном namespace.

```bash
kubectl create role ... ; kubectl create rolebinding dev-view --clusterrole=view --group=clinic-developers -n clinic
kubectl auth can-i delete pods -n clinic --as alice
kubectl auth can-i --list -n clinic --as system:serviceaccount:clinic:ci
kubectl get clusterrolebindings -o wide | grep cluster-admin
```

## ServiceAccount

**Идентичность для подов/процессов** внутри кластера (у каждого namespace есть `default`).

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: api
  namespace: clinic
  annotations:
    eks.amazonaws.com/role-arn: arn:aws:iam::123456789:role/clinic-api    # IRSA / Workload Identity
automountServiceAccountToken: false       # не монтировать токен, если API кластера не нужен
```

```yaml
spec:
  serviceAccountName: api
  automountServiceAccountToken: false
```

- поды используют SA для обращения к API (операторы, контроллеры, CI, ingress-controller);
- токен — **проецируемый, короткоживущий** (bound service account token, audience, expiration; с 1.24 не создаются вечные Secret-токены), монтируется в `/var/run/secrets/kubernetes.io/serviceaccount/`;
- **облачная идентичность** (IRSA на AWS, GKE Workload Identity, Azure Workload Identity) — доступ подов к облачным API без долгоживущих ключей;
- **отдельный SA на приложение** с минимальными правами; не использовать `default` и не выдавать ему прав; отключать автомонтирование, если не нужен доступ к API.

## Принцип наименьших привилегий

- **Role** (namespaced) вместо ClusterRole, конкретные `resources`/`verbs`/`resourceNames`, без `*`;
- избегать опасных прав: `secrets` (get/list = чтение всех секретов), `pods/exec`, `create pods` (запуск привилегированного пода = доступ к ноде), `impersonate`, `escalate`/`bind`, `nodes/proxy`, `*` на `*`;
- **`cluster-admin`** — единицам людей, через временный доступ (break-glass, JIT), не для CI;
- **CI/CD**: SA с правами деплоя только в нужных namespace; токены короткоживущие или OIDC; GitOps-агент вместо внешнего доступа;
- **группы** из IdP вместо отдельных пользователей; регулярный аудит (`rbac-lookup`, `kubectl-who-can`, **rbac-tool**, `krane`, Kubescape), журнал аудита API (Audit Policy);
- **Pod Security** и **NetworkPolicy** дополняют RBAC.

Типичный набор ролей: **администратор платформы** (cluster-admin, ограниченно), **разработчик** (`edit`/`view` в своих namespace), **SRE/дежурный** (`view` всюду + `pods/exec`, `logs` по запросу), **CI** (deployer в namespace), **операторы/контроллеры** (узкие ClusterRole).

## Диагностика

```bash
kubectl auth can-i create pods -n clinic --as dev-user
# ошибка: Error from server (Forbidden): pods is forbidden: User "x" cannot list resource "pods" in API group "" in the namespace "clinic"
kubectl describe rolebinding -n clinic; kubectl get role,rolebinding -n clinic
```

В логах аудита видно, кто и что делал (`audit.k8s.io`), отказ авторизации.

## Доступ пользователей

- **OIDC** через Keycloak: `kubectl oidc-login` (kubelogin), группы из токена маппятся в RBAC; короткоживущие токены, MFA на стороне IdP;
- не раздавать админский kubeconfig с сертификатом без срока; сертификатные пользователи (CSR API) — ограниченно;
- облачные IAM (EKS access entries, GKE IAM → RBAC);
- доступ к prod — через бастион/VPN/private endpoint, с аудитом.

## Вопросы с ответами

> [!question]- Чем Role отличается от ClusterRole и RoleBinding от ClusterRoleBinding?
> Role действует в namespace, ClusterRole — в масштабе кластера (и для cluster-scoped ресурсов). RoleBinding даёт права в одном namespace (можно связать и с ClusterRole), ClusterRoleBinding — во всём кластере.

> [!question]- Зачем отдельный ServiceAccount для приложения?
> Чтобы выдать минимальные права именно ему, не использовать `default`, отключить токен при ненужности и ограничить ущерб при компрометации пода.

> [!question]- Почему права на secrets опасны?
> `get/list` на Secret даёт чтение всех секретов namespace (включая токены SA), то есть фактически повышение привилегий.
