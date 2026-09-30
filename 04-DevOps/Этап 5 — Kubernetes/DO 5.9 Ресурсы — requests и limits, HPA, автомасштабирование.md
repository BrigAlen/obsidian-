---
type: topic
domain: devops
stage: 5
order: 9
status: todo
level: middle
tags: [domain/devops, stage/5, level/middle, priority/should]
reviewed: 
next_review: 
priority: should
time: 6
---

# Ресурсы: requests и limits, HPA, автомасштабирование

↑ [[DO Этап 5 · Kubernetes|Этап 5 · Kubernetes]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~6 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> requests и limits определяют планирование, стабильность и стоимость; HPA — основа автомасштабирования. Классические вопросы про OOMKilled и троттлинг.

## requests и limits

```yaml
resources:
  requests: { cpu: 250m, memory: 256Mi }     # гарантия и основа планирования
  limits:   { cpu: "1",  memory: 512Mi }     # потолок
```

- **requests** — сколько ресурсов планировщик **резервирует** для пода на ноде (сумма requests на ноде ≤ allocatable); определяет долю CPU при конкуренции;
- **limits** — максимум, который контейнер может использовать.

Единицы: CPU в **ядрах** (`1` = 1 vCPU, `500m` = 0,5 ядра); память в байтах (`Mi`, `Gi` — двоичные; `M`, `G` — десятичные).

### Поведение при превышении

| Ресурс | При превышении limits |
|---|---|
| **CPU** (сжимаемый) | **троттлинг** (CFS quota): процесс замедляется, но не убивается; латентность растёт |
| **Memory** (несжимаемый) | **OOM kill** контейнера (`OOMKilled`, exit 137), перезапуск |

Частая практика: **`requests.cpu` задавать, `limits.cpu` не задавать или задавать с запасом** (троттлинг вредит латентности даже при свободных ядрах ноды); **`limits.memory` = `requests.memory`** (предсказуемость, гарантированная память) или небольшой запас. Обсуждаемая тема; выбор зависит от политики кластера.

### QoS-классы

| Класс | Условие | Вытеснение при нехватке памяти на ноде |
|---|---|---|
| **Guaranteed** | для всех контейнеров `requests == limits` (CPU и memory) | последними |
| **Burstable** | заданы requests (меньше limits) | средние |
| **BestEffort** | ничего не задано | первыми |

При давлении на ноду kubelet **вытесняет (evicts)** поды по QoS и использованию сверх requests. Всегда задавайте requests.

## Подбор значений

- измерять реальное потребление (`kubectl top`, Prometheus: `container_memory_working_set_bytes`, `rate(container_cpu_usage_seconds_total)`), p95/p99 под пиком;
- **VPA** (Vertical Pod Autoscaler) в режиме рекомендаций (`Off`/`Initial`), Goldilocks;
- .NET: учитывать GC и лимиты памяти контейнера (`DOTNET_GCHeapHardLimit`, серверный GC, `DOTNET_gcServer`), число потоков = ядра по limits; JVM: `-XX:MaxRAMPercentage`; Node: `--max-old-space-size`;
- запас на пики, прогрев; слишком высокие requests — низкая утилизация и стоимость, слишком низкие — нестабильность и «шумные соседи».

## LimitRange и ResourceQuota

- **LimitRange**: значения по умолчанию и min/max для контейнеров в namespace;
- **ResourceQuota**: общий лимит namespace (CPU, память, число объектов, хранилище).

## Масштабирование

| Инструмент | Что масштабирует | По чему |
|---|---|---|
| **HPA** (Horizontal Pod Autoscaler) | число реплик | CPU/память (metrics-server), кастомные и внешние метрики |
| **VPA** | requests/limits пода | историческое потребление |
| **KEDA** | число реплик (в т.ч. до 0) | события: длина очереди (Kafka, RabbitMQ, SQS), Prometheus, cron, HTTP |
| **Cluster Autoscaler / Karpenter** | число нод | Pending поды из-за нехватки ресурсов; удаление недозагруженных нод |

### HPA

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata: { name: api }
spec:
  scaleTargetRef: { apiVersion: apps/v1, kind: Deployment, name: api }
  minReplicas: 3
  maxReplicas: 20
  metrics:
    - type: Resource
      resource: { name: cpu, target: { type: Utilization, averageUtilization: 70 } }     # от requests!
    - type: Pods
      pods: { metric: { name: http_requests_per_second }, target: { type: AverageValue, averageValue: "100" } }
  behavior:
    scaleUp:   { stabilizationWindowSeconds: 0,   policies: [{ type: Percent, value: 100, periodSeconds: 60 }] }
    scaleDown: { stabilizationWindowSeconds: 300, policies: [{ type: Pods,    value: 2,   periodSeconds: 60 }] }
```

Формула: `desired = ceil(current × currentMetric / targetMetric)`.

Важное:

- утилизация считается **относительно requests** → без requests HPA не работает;
- нужен **metrics-server** (для CPU/памяти); для кастомных метрик — Prometheus Adapter, KEDA;
- **не использовать HPA и VPA по одному и тому же ресурсу** одновременно;
- задержка реакции (scrape интервал, стабилизация): для резких пиков заранее больше minReplicas, scheduled scaling (KEDA cron);
- медленный старт приложения и readiness ограничивают скорость наращивания; прогрев; `startupProbe`;
- stateful нагрузки масштабируются сложнее;
- scale down осторожно (окно стабилизации) + graceful shutdown + PodDisruptionBudget;
- учитывать пределы зависимостей (пул соединений БД ↑ с числом подов): PgBouncer, лимиты.

### Cluster Autoscaler / Karpenter

Добавляют ноды, когда есть поды в `Pending` с `FailedScheduling` из-за ресурсов; удаляют недозагруженные. Условия: корректные requests, PDB, топологические ограничения, лимиты группы нод. Karpenter подбирает тип инстанса под поды (AWS), консолидация (bin packing), spot.

## Практики планирования

- **requests для всего**; limits памяти; мониторинг throttling (`container_cpu_cfs_throttled_periods_total`);
- `priorityClass`: критичные поды вытесняют менее важные;
- **overprovisioning** (pause-поды низкого приоритета) для быстрого масштабирования нод;
- `topologySpreadConstraints` и anti-affinity для распределения по зонам;
- `PodDisruptionBudget` для минимальной доступности;
- **nodeSelector / taints** для выделенных пулов (GPU, spot);
- учёт системного резерва нод (`kube-reserved`, `system-reserved`, allocatable);
- стоимость: rightsizing, spot/preemptible, автоскейл до минимума в dev, выключение по расписанию (KEDA cron, `kube-downscaler`).

## Диагностика

```bash
kubectl top pods -n clinic --containers; kubectl top nodes
kubectl describe node worker-1                 # Allocated resources, Conditions (MemoryPressure)
kubectl describe pod x                          # Last State: OOMKilled, Reason: Evicted
kubectl get hpa -w; kubectl describe hpa api    # <unknown>/70% = нет метрик/requests
kubectl get events --field-selector reason=FailedScheduling
```

| Проблема | Причина |
|---|---|
| Pod `Pending` (Insufficient cpu/memory) | requests больше свободного; нужен новый узел/уменьшить requests |
| `OOMKilled` | лимит памяти мал или утечка; JVM/.NET кучи без учёта лимита |
| Высокая латентность при низком CPU ноды | CPU throttling из-за limits |
| HPA `<unknown>` | нет metrics-server/requests |
| Поды вытеснены (Evicted) | давление ноды; BestEffort/Burstable |
| Флаппинг масштабирования | узкое окно стабилизации, шумная метрика |

## Вопросы с ответами

> [!question]- Чем requests отличается от limits?
> Requests — гарантированный и резервируемый для планирования объём ресурсов; limits — максимум. CPU сверх limits троттлится, память сверх limits приводит к OOM kill.

> [!question]- От чего считается averageUtilization в HPA?
> От requests пода: процент фактического потребления к запрошенному. Без requests автомасштабирование по CPU/памяти невозможно.

> [!question]- Как связаны HPA и Cluster Autoscaler?
> HPA увеличивает число подов; если они не помещаются на нодах (Pending), Cluster Autoscaler/Karpenter добавляет ноды; при снижении нагрузки — обратный процесс.
