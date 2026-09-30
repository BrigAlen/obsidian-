---
type: topic
domain: devops
stage: 5
order: 16
status: todo
level: middle
tags: [domain/devops, stage/5, level/middle, priority/should]
reviewed: 
next_review: 
priority: should
time: 8
---

# Безопасность workloads: SecurityContext, Pod Security Standards, admission policies

↑ [[DO Этап 5 · Kubernetes|Этап 5 · Kubernetes]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~8 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> Hardening подов и политики допуска — обязательная часть зрелого кластера: SecurityContext, Pod Security Standards, Kyverno/Gatekeeper.

## Угрозы

Компрометация пода → побег на ноду (privileged, hostPath, docker.sock, опасные capabilities), доступ к API (токен SA), боковое перемещение по сети, кража секретов, майнеры. Защита — минимизация привилегий на всех слоях.

## securityContext

```yaml
spec:
  securityContext:                        # уровень пода
    runAsNonRoot: true
    runAsUser: 10001
    runAsGroup: 10001
    fsGroup: 10001                        # группа для томов
    fsGroupChangePolicy: OnRootMismatch
    seccompProfile: { type: RuntimeDefault }
    supplementalGroups: []
  automountServiceAccountToken: false
  containers:
    - name: app
      image: registry.example.com/clinic/api@sha256:...
      securityContext:                    # уровень контейнера (приоритетнее)
        allowPrivilegeEscalation: false
        readOnlyRootFilesystem: true
        privileged: false
        capabilities: { drop: ["ALL"], add: ["NET_BIND_SERVICE"] }
        runAsNonRoot: true
      volumeMounts: [{ name: tmp, mountPath: /tmp }]
  volumes: [{ name: tmp, emptyDir: { medium: Memory, sizeLimit: 64Mi } }]
```

| Поле | Смысл |
|---|---|
| `runAsNonRoot`, `runAsUser` | запрет root (проверка по числовому UID) |
| `allowPrivilegeEscalation: false` | запрет повышения (setuid, `no_new_privs`) |
| `readOnlyRootFilesystem: true` | неизменяемая ФС; запись только в `emptyDir`/тома |
| `capabilities.drop: [ALL]` | убрать capabilities, вернуть только нужные |
| `privileged: true` | **запретить**: полный доступ к хосту |
| `seccompProfile: RuntimeDefault` | фильтр системных вызовов |
| `seLinuxOptions`, `appArmorProfile` | MAC |
| `hostNetwork/hostPID/hostIPC`, `hostPath` | **избегать** (нарушают изоляцию) |
| `procMount`, `sysctls` | ограничивать небезопасные |
| `runtimeClassName` | sandbox-runtime (gVisor, Kata) для недоверенных нагрузок |

## Pod Security Standards (PSS) и Pod Security Admission (PSA)

Три профиля:

| Профиль | Описание |
|---|---|
| **privileged** | без ограничений (системные компоненты) |
| **baseline** | минимальные ограничения: запрещены privileged, hostNetwork/PID/IPC, hostPath, опасные capabilities, hostPort… |
| **restricted** | лучшие практики hardening: non-root, drop ALL, seccomp RuntimeDefault, запрет privilege escalation, ограниченные типы томов |

**PSA** (встроенный admission-контроллер, замена PodSecurityPolicy, удалённой в 1.25) включается **метками namespace**:

```bash
kubectl label namespace clinic \
  pod-security.kubernetes.io/enforce=restricted \
  pod-security.kubernetes.io/enforce-version=latest \
  pod-security.kubernetes.io/warn=restricted \
  pod-security.kubernetes.io/audit=restricted
```

Режимы: **enforce** (отклонить), **audit** (запись в аудит-лог), **warn** (предупреждение пользователю). Внедрение: начать с `warn`/`audit` на `restricted`, исправить нарушения, затем `enforce`. Системные namespaces (`kube-system`) — `privileged`, прикладные — `baseline/restricted`. PSA проверяет только поля пода (без кастомных политик).

## Admission-политики (policy as code)

Для всего, что PSA не покрывает: **Kyverno**, **OPA Gatekeeper**, **ValidatingAdmissionPolicy** (встроенные CEL-политики, GA в 1.30).

Примеры правил:

- запрет `latest` и обязательный digest/реестр из списка доверенных;
- обязательные `requests/limits`, probes, метки (`owner`, `team`);
- запрет `hostPath`, `privileged`, `NodePort`, `LoadBalancer` без согласования;
- обязательные `securityContext` и non-root;
- проверка **подписей образов** (cosign, Kyverno `verifyImages`);
- обязательные `NetworkPolicy`, запрет пересечения host/path у Ingress;
- мутации: добавление меток, `imagePullSecrets`, `securityContext` по умолчанию.

```yaml
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata: { name: require-non-root-and-limits }
spec:
  validationFailureAction: Enforce          # Audit для начала
  background: true
  rules:
    - name: non-root
      match: { any: [{ resources: { kinds: [Pod] } }] }
      validate:
        message: "Контейнеры должны запускаться не от root и без повышения привилегий"
        pattern:
          spec:
            containers:
              - securityContext: { runAsNonRoot: true, allowPrivilegeEscalation: false }
    - name: no-latest
      match: { any: [{ resources: { kinds: [Pod] } }] }
      validate:
        message: "Тег latest запрещён"
        pattern: { spec: { containers: [{ image: "!*:latest" }] } }
```

Gatekeeper: `ConstraintTemplate` (Rego) + `Constraint`. Политики тестируются (`kyverno test`, `conftest`) и хранятся в Git; режим `audit` для начального внедрения; исключения (`exclude`) для системных namespace; влияние на доступность (webhook `failurePolicy` и отказоустойчивость самих контроллеров).

## Другие слои безопасности workload

- **Образы**: минимальные, сканируются (Trivy Operator, Grype), подписаны, из доверенного реестра; обновляются;
- **ServiceAccount**: отдельный на приложение, без автомонтирования токена, минимальный RBAC; облачные identity (IRSA/Workload Identity) вместо ключей;
- **Secrets**: внешние хранилища, шифрование etcd, тома вместо env;
- **Сеть**: NetworkPolicy (default deny), mTLS (mesh), egress-ограничения, блок `169.254.169.254`;
- **Ресурсы**: requests/limits, квоты (защита от DoS), `pids` лимиты;
- **Runtime-защита**: **Falco** (подозрительные syscalls, shell в контейнере, чтение `/etc/shadow`), Tetragon, eBPF-наблюдение; аудит-логи API; алерты;
- **Изоляция**: sandbox-runtime (gVisor/Kata) для недоверенного кода, выделенные ноды/пулы (taints) для чувствительных нагрузок, отдельные кластеры для разных уровней доверия;
- **Узлы**: минимальные ОС (Talos, Bottlerocket, Flatcar), автоматическое обновление, закрытый SSH, CIS-бенчмарки (`kube-bench`);
- **Цепочка поставок**: SBOM, provenance, admission-проверки подписи;
- **Kubelet/API**: authz Webhook, закрытые порты, аудит, private endpoint;
- **Compliance**: Kubescape, `kube-bench`, `kube-hunter`, CIS/NSA-hardening, Trivy Operator отчёты.

## Диагностика отказов admission

```bash
kubectl apply -f pod.yaml
# Error from server (Forbidden): pods "x" is forbidden: violates PodSecurity "restricted:latest": allowPrivilegeEscalation != false (container "app" must set securityContext.allowPrivilegeEscalation=false), unrestricted capabilities, runAsNonRoot != true, seccompProfile ...
kubectl get events -n clinic | grep -i -E 'FailedCreate|forbidden'          # для Deployment/ReplicaSet причина в событиях RS
kubectl describe rs api-xxx -n clinic
kubectl get clusterpolicy,policyreport -A                                    # Kyverno отчёты
```

Типичная проблема: Deployment создан, а подов нет: RS не может создать поды из-за политики — смотреть `describe rs` и `events`.

## Чек-лист безопасного пода

- [ ] non-root (числовой UID), `allowPrivilegeEscalation: false`, `drop: [ALL]`, seccomp RuntimeDefault;
- [ ] `readOnlyRootFilesystem: true` (+ `emptyDir` для записи);
- [ ] нет `privileged`, host*-namespaces, `hostPath`, docker.sock;
- [ ] requests/limits, probes;
- [ ] отдельный ServiceAccount, `automountServiceAccountToken: false`;
- [ ] образ по digest, из доверенного реестра, просканирован и подписан;
- [ ] секреты из хранилища, не в env и не в образе;
- [ ] NetworkPolicy (deny по умолчанию) и PSA `restricted`;
- [ ] политики Kyverno/Gatekeeper, runtime-мониторинг (Falco).

## Вопросы с ответами

> [!question]- Что такое Pod Security Standards?
> Три профиля (privileged, baseline, restricted) с набором ограничений на поля подов; применяются через Pod Security Admission метками namespace в режимах enforce/audit/warn.

> [!question]- Чем Kyverno/Gatekeeper отличаются от Pod Security Admission?
> PSA проверяет только фиксированный набор полей безопасности пода; Kyverno/Gatekeeper — политики как код для любых ресурсов (теги, лимиты, метки, подписи образов, мутации), с гибкими исключениями.

> [!question]- Почему Deployment создан, а подов нет?
> Вероятно, admission-политика (PSA, Kyverno) отклоняет создание подов ReplicaSet'ом; причину показывает `kubectl describe rs` и события.
