---
type: topic
domain: devops
stage: 5
order: 17
status: todo
level: middle
tags: [domain/devops, stage/5, level/middle, priority/should]
reviewed: 
next_review: 
priority: should
time: 8
---

# Observability Kubernetes: metrics-server, Prometheus, логи и аудит

↑ [[DO Этап 5 · Kubernetes|Этап 5 · Kubernetes]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~8 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> Без наблюдаемости кластером управлять невозможно; спрашивают стек метрик, логов и аудита.

## Слои наблюдаемости

| Слой | Что | Инструменты |
|---|---|---|
| **Метрики** | ресурсы, состояние объектов, приложения | metrics-server, kube-state-metrics, node-exporter, cAdvisor, Prometheus, Grafana, VictoriaMetrics |
| **Логи** | stdout контейнеров, логи нод/компонентов, аудит | Fluent Bit/Vector/Promtail → Loki/ELK/ClickHouse |
| **Трассировки** | сквозные запросы | OpenTelemetry Collector → Tempo/Jaeger |
| **События и аудит** | события кластера, аудит API | kubernetes-event-exporter, Audit log |
| **Профилирование, eBPF** | глубинная диагностика | Pixie, Parca, Hubble, Beyla |

## metrics-server

Лёгкий агрегатор **текущих** CPU/памяти (из kubelet/cAdvisor) для `kubectl top` и **HPA**. Не хранит историю и не подходит для алертинга.

```bash
kubectl top nodes; kubectl top pods -A --sort-by=cpu --containers
kubectl get apiservices | grep metrics                    # v1beta1.metrics.k8s.io Available
```

Проблемы: `error: Metrics API not available` — не установлен, TLS kubelet (`--kubelet-insecure-tls` только для тестов), сеть до 10250.

## Prometheus-стек

**kube-prometheus-stack** (Helm): Prometheus Operator, Alertmanager, Grafana, node-exporter, kube-state-metrics, правила алертов и дашборды.

Источники метрик:

- **cAdvisor** (в kubelet): `container_cpu_usage_seconds_total`, `container_memory_working_set_bytes`, `container_cpu_cfs_throttled_*`, сеть, диск;
- **kube-state-metrics**: состояние объектов (`kube_pod_status_phase`, `kube_deployment_status_replicas_available`, `kube_pod_container_status_restarts_total`, `kube_node_status_condition`, `kube_cronjob_*`, `kube_persistentvolumeclaim_*`);
- **node-exporter**: метрики нод (CPU, память, диски, сеть);
- **control plane**: apiserver (`apiserver_request_duration_seconds`, `apiserver_request_total`), etcd, scheduler, controller-manager;
- **приложения**: `/metrics` (Prometheus client, OTel), **ingress-nginx**, CoreDNS, CNI, cert-manager.

**ServiceMonitor / PodMonitor / PrometheusRule** (CRD Prometheus Operator) — декларативное подключение целей и правил:

```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata: { name: api, namespace: clinic, labels: { release: kube-prometheus-stack } }
spec:
  selector: { matchLabels: { app: api } }
  endpoints: [{ port: http, path: /metrics, interval: 30s }]
---
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata: { name: api-alerts, namespace: clinic }
spec:
  groups:
    - name: api
      rules:
        - alert: HighErrorRate
          expr: sum(rate(http_server_requests_seconds_count{app="api",status=~"5.."}[5m])) / sum(rate(http_server_requests_seconds_count{app="api"}[5m])) > 0.05
          for: 10m
          labels: { severity: critical }
          annotations: { summary: "5xx > 5% за 10 мин", runbook_url: "https://wiki/runbooks/api-5xx" }
```

### Полезные запросы PromQL

```promql
# перезапуски подов за час
increase(kube_pod_container_status_restarts_total[1h]) > 3
# поды не Ready
kube_pod_status_ready{condition="false"} == 1
# CPU-троттлинг
sum by (pod) (rate(container_cpu_cfs_throttled_periods_total[5m])) / sum by (pod) (rate(container_cpu_cfs_periods_total[5m]))
# память относительно лимита
container_memory_working_set_bytes / on(pod, container) kube_pod_container_resource_limits{resource="memory"} > 0.9
# реплики недоступны
kube_deployment_status_replicas_unavailable > 0
# диск PVC заполняется
kubelet_volume_stats_available_bytes / kubelet_volume_stats_capacity_bytes < 0.15
# ноды NotReady
kube_node_status_condition{condition="Ready",status="true"} == 0
```

Типовые алерты кластера (kube-prometheus-mixin): `KubePodCrashLooping`, `KubePodNotReady`, `KubeDeploymentReplicasMismatch`, `KubeNodeNotReady`, `KubeletDown`, `KubeAPIDown`, `etcdInsufficientMembers`, `NodeFilesystemSpaceFillingUp`, `KubeQuotaExceeded`, `CPUThrottlingHigh`, `KubePersistentVolumeFillingUp`, истечение сертификатов.

Масштабирование: **Thanos / Mimir / VictoriaMetrics** для долговременного хранения и HA, шардирование, `remote_write`, контроль кардинальности (метрики с user_id, url — запрещены).

## Логи

Контейнерные логи лежат на ноде `/var/log/pods/...` (ротация kubelet: `containerLogMaxSize`, `containerLogMaxFiles`); `kubectl logs` читает их — после удаления пода пропадают. Нужен **централизованный сбор**:

```text
Pod stdout → файл на ноде → DaemonSet-агент (Fluent Bit / Promtail / Vector / OTel Collector filelog) → Loki / Elasticsearch / ClickHouse
```

Агент обогащает метаданными Kubernetes (namespace, pod, container, labels, node), парсит JSON, фильтрует, маскирует ПДн. Рекомендации: **структурированные JSON-логи** с `trace_id`; метки низкой кардинальности (Loki: `namespace`, `app`, `container`, не `pod` в метках при больших масштабах); контроль объёма (уровни, sampling); хранение по политике; алерты по логам (Loki ruler).

**Логи компонентов**: `journalctl -u kubelet`, логи control plane (static pods), ingress-контроллера, CoreDNS.

## Аудит Kubernetes API

**Audit policy** определяет, какие запросы к apiserver фиксировать и с какой детализацией (`None`, `Metadata`, `Request`, `RequestResponse`):

```yaml
apiVersion: audit.k8s.io/v1
kind: Policy
omitStages: ["RequestReceived"]
rules:
  - level: None
    users: ["system:kube-proxy"]
    verbs: ["watch"]
  - level: Metadata
    resources: [{ group: "", resources: ["secrets", "configmaps", "tokenreviews"] }]     # не логировать содержимое секретов!
  - level: RequestResponse
    resources: [{ group: "rbac.authorization.k8s.io" }, { group: "", resources: ["pods/exec", "pods/portforward"] }]
  - level: Metadata
```

Флаги apiserver: `--audit-policy-file`, `--audit-log-path`, `--audit-log-maxage/maxbackup/maxsize` или webhook backend. Аудит отвечает: кто, когда, что создал/удалил/exec в поде, откуда. Отправка в SIEM/Loki/ClickHouse, алерты на подозрительное (`exec` в prod, изменение RBAC, чтение Secret, `cluster-admin` binding). Управляемые кластеры — через облачные сервисы логирования.

**События (Events)** живут ~1 час: `kubernetes-event-exporter` отправляет их в логи/метрики/алерты (`FailedScheduling`, `BackOff`, `Unhealthy`, `OOMKilling`).

## Трассировка и OpenTelemetry

**OTel Operator** и **Collector** (DaemonSet/Deployment/sidecar): приём OTLP от приложений, атрибуты k8s (`k8sattributes` processor), экспорт в Tempo/Jaeger/ClickHouse; авто-инструментация через аннотации (`instrumentation.opentelemetry.io/inject-dotnet: "true"`).

## Дашборды Grafana и SLO

Готовые: Kubernetes / Compute Resources (cluster, namespace, pod), Nodes, Networking, API server, etcd, CoreDNS, Ingress-NGINX, Alertmanager. Свои: золотые сигналы сервисов (RED — Rate, Errors, Duration; USE — Utilization, Saturation, Errors для ресурсов), бизнес-метрики, SLO/error budget (Sloth, Pyrra).

## Практика и подводные камни

- **метки и кардинальность**: не добавлять `pod`/`user_id` без нужды в метрики приложений; `label_values`;
- **ресурсы Prometheus**: память растёт с числом серий; retention, sharding, remote storage;
- **алерты на симптомы** (ошибки, латентность, доступность), а не на каждый сбой; группировка, `for:`, маршрутизация по командам, runbook;
- **мониторинг мониторинга**: Watchdog-алерт, внешний heartbeat (dead man's switch);
- **HA**: два Prometheus + Alertmanager кластер;
- **безопасность**: защита `/metrics` (NetworkPolicy, mTLS), ограничение доступа к Grafana, скрытие секретов в логах/метриках, права на kubelet-метрики (RBAC `nodes/metrics`);
- **стоимость**: объём логов и метрик (sampling, агрегация, TTL).
- Инструменты: **k9s**, **Lens**, **Headlamp**, **Robusta**/**Komodor**, **Pixie**.

## Вопросы с ответами

> [!question]- Чем metrics-server отличается от Prometheus?
> metrics-server отдаёт текущие CPU/память для `kubectl top` и HPA без истории; Prometheus собирает и хранит метрики во времени, поддерживает запросы PromQL и алертинг.

> [!question]- Для чего нужен kube-state-metrics?
> Экспортирует метрики о состоянии объектов Kubernetes (реплики, фазы подов, рестарты, условия нод, CronJob), на которых строятся алерты о сбоях кластера.

> [!question]- Зачем аудит-логи Kubernetes?
> Фиксируют, кто и какие операции выполнял через API (создание, exec, изменение RBAC, чтение Secret), что нужно для расследования инцидентов и контроля доступа; их отправляют в SIEM и настраивают алерты.
