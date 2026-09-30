---
type: topic
domain: devops
stage: 5
order: 14
status: todo
level: middle
tags: [domain/devops, stage/5, level/middle, priority/should]
reviewed: 
next_review: 
priority: should
time: 6
---

# Отладка: kubectl get, describe, logs, exec, events

↑ [[DO Этап 5 · Kubernetes|Этап 5 · Kubernetes]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~6 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> «Под не запускается/сервис недоступен — что делаете?» Нужен систематический подход и знание, где искать причину.

## Порядок диагностики

1. **Что видим**: `kubectl get pods -n ns -o wide` — статус, рестарты, нода.
2. **Почему**: `kubectl describe pod <pod>` — блок **Events** и состояние контейнеров (`Last State`, `Reason`, `Exit Code`).
3. **Что говорит приложение**: `kubectl logs <pod> [-c container] [--previous]`.
4. **События кластера**: `kubectl get events -n ns --sort-by=.lastTimestamp`.
5. **Внутри**: `kubectl exec -it`, `kubectl debug`.
6. **Сеть и зависимости**: сервисы, endpoints, DNS, политики.
7. **Ресурсы и ноды**: `kubectl top`, `describe node`.

```bash
kubectl get pods -n clinic -o wide --show-labels
kubectl get pods -A --field-selector=status.phase!=Running,status.phase!=Succeeded
kubectl describe pod api-7d9f-xk2lp -n clinic
kubectl logs api-7d9f-xk2lp -n clinic --tail 200 -f
kubectl logs api-7d9f-xk2lp -n clinic --previous              # логи предыдущего (упавшего) контейнера
kubectl logs -l app=api -n clinic --all-containers --prefix   # по лейблу, все поды
kubectl exec -it api-7d9f-xk2lp -n clinic -- sh
kubectl exec api-7d9f-xk2lp -- env | sort; kubectl exec api-7d9f-xk2lp -- cat /etc/resolv.conf
kubectl get events -n clinic --sort-by=.lastTimestamp | tail -20
kubectl get events --field-selector type=Warning -A
stern api -n clinic                                           # логи нескольких подов
```

## Типичные состояния и причины

| Статус | Что смотреть | Типичные причины |
|---|---|---|
| **Pending** | `describe pod` → Events: `FailedScheduling` | не хватает CPU/памяти, taints, `nodeSelector`/affinity, нет PV или зона, квота, PodSecurity |
| **ContainerCreating** (долго) | Events | тома (PVC не привязан, CSI), CNI, секрет/конфиг отсутствует |
| **ImagePullBackOff / ErrImagePull** | Events: `Failed to pull image` | опечатка в имени/теге, приватный реестр без `imagePullSecrets`, лимиты pull, сеть, архитектура |
| **CrashLoopBackOff** | `logs --previous`, exit code | исключение при старте, нет конфигурации/секрета, не подключается к БД, неверная команда, OOM, probe |
| **CreateContainerConfigError** | Events | нет ConfigMap/Secret/ключа |
| **RunContainerError** | Events | неверный `command`, права, runtime |
| **OOMKilled** (137) | `Last State: Terminated Reason: OOMKilled` | `limits.memory` мал, утечка, куча рантайма |
| **Error / Completed** | | Job-под: нормальное/ошибочное завершение |
| **Terminating** (завис) | finalizers, нода `NotReady`, контейнер не завершается | `kubectl delete pod --grace-period=0 --force` (осторожно), проверить finalizers |
| **Running, но 0/1 Ready** | `describe` → `Readiness probe failed` | приложение не готово, неверный путь/порт, зависимость недоступна |
| **Evicted** | `describe pod`: The node was low on resource | давление по памяти/диску, QoS |
| **Unknown/NodeLost** | `kubectl get nodes` | нода недоступна |

Exit-коды: `0` успех, `1` ошибка приложения, `126/127` команда не выполняется/не найдена, `137` SIGKILL (OOM), `139` SIGSEGV, `143` SIGTERM.

## Диагностика сервисов и сети

```bash
kubectl get svc,endpoints,endpointslices -n clinic
kubectl describe svc api -n clinic                       # Selector, Endpoints, Port/TargetPort
kubectl get pods -l app=api -n clinic                    # совпадают ли метки с selector
kubectl run tmp --rm -it --image=nicolaka/netshoot -n clinic -- bash
#   nslookup api; curl -v http://api:80/health; nc -zv postgres 5432; dig +short kubernetes.default.svc.cluster.local
kubectl port-forward svc/api 8080:80 -n clinic           # обход Ingress
kubectl get ingress -n clinic; kubectl describe ingress clinic
kubectl logs -n ingress-nginx deploy/ingress-nginx-controller --tail 100
kubectl get networkpolicy -A
```

Правило: если `Endpoints` пустые — Service не видит готовых подов (метки/readiness). Проверьте по цепочке: клиент → DNS → Service (ClusterIP) → Endpoints → Pod → приложение.

## kubectl debug

```bash
kubectl debug -it pod/api-xxx --image=busybox:1.36 --target=app -n clinic          # эфемерный контейнер в том же поде (общие namespaces процессов)
kubectl debug pod/api-xxx -it --copy-to=api-debug --container=app --image=ubuntu    # копия пода с изменёнными параметрами
kubectl debug node/worker-1 -it --image=ubuntu                                      # shell на ноде (mount хоста в /host)
```

Позволяет диагностировать distroless-образы без shell и падающие поды (запуск с `sleep`).

## Ноды и кластер

```bash
kubectl get nodes -o wide; kubectl describe node worker-1      # Conditions: Ready, MemoryPressure, DiskPressure, PIDPressure; Allocatable; Events
kubectl top nodes; kubectl top pods -A --sort-by=memory | head
kubectl get componentstatuses   # устарело; проверка control plane: kubectl get --raw='/readyz?verbose'
kubectl cluster-info dump | less
# на ноде:
journalctl -u kubelet -f; crictl ps -a; crictl logs <id>; crictl images; systemctl status containerd
```

Часто: нода `NotReady` (kubelet, CNI, диск, сеть), переполненный диск (образы `crictl rmi --prune`, логи), нехватка inode, проблемы с сертификатами kubelet, скачки задержек API.

## Другие полезные приёмы

- `kubectl get pod x -o yaml` — фактические spec/status, `ownerReferences` (кто создал), `finalizers`;
- `kubectl get all -n ns`, `kubectl api-resources`, `kubectl explain`;
- **`kubectl rollout status/history/undo`** при проблемном деплое;
- `kubectl diff -f`, `helm get manifest`, `helm diff`: что реально применилось;
- сравнение «рабочего» и «нерабочего» окружений (диф манифестов);
- `kubectl auth can-i` — проблемы прав (Forbidden);
- админ-контроллеры (Kyverno/Gatekeeper) могут **отклонять** ресурсы: смотреть ответ `apply`;
- `kubectl get events` хранятся ~1 час — фиксируйте сразу; централизованный сбор событий (kubernetes-event-exporter);
- `kubectl logs` ограничены ротацией: настоящие логи — в централизованной системе (Loki/ELK).

## Шпаргалка «что проверить»

| Симптом | Первая команда |
|---|---|
| Деплой «завис» | `kubectl rollout status`, `describe deploy/rs/pod` |
| 502/503 из Ingress | `get endpoints`, `describe pod` (readiness), логи ingress |
| Под перезапускается | `logs --previous`, `describe` (Last State) |
| Под не создаётся | `get events`, `describe rs` (квоты, PodSecurity, webhook) |
| Нет доступа к БД | `exec` → `nc`/`nslookup`, NetworkPolicy, Secret |
| Тормозит | `top`, throttling, HPA, логи/метрики/трейсы |

## Вопросы с ответами

> [!question]- Под в CrashLoopBackOff. С чего начнёте?
> `kubectl logs --previous` и `kubectl describe pod` (Last State, Exit Code, Events): ищу исключение, отсутствие конфигурации/секрета, недоступную зависимость, OOMKilled или провал liveness.

> [!question]- Service есть, но запросы не доходят. Что проверите?
> `kubectl get endpoints`: пусты ли адреса (селектор/метки, readiness), `targetPort`, затем доступность из соседнего пода и NetworkPolicy, далее Ingress.

> [!question]- Как диагностировать distroless-под без shell?
> `kubectl debug -it pod/x --image=busybox --target=container` создаёт эфемерный контейнер с общим PID-пространством.
