---
type: topic
domain: devops
stage: 9
order: 9
status: todo
level: final
tags: [domain/devops, stage/9, level/final, priority/must]
reviewed: 
next_review: 
priority: must
time: 8
---

# Переезд Clinic с docker compose в Kubernetes: план, Helm-чарты, что поменяется

↑ [[DO Этап 9 · Собес Middle DevOps — вопросы, практика, деплой систем|Этап 9 · Собес Middle DevOps: вопросы, практика, деплой систем]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~8 мин чтения</span><span class="chip">Уровень: final</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> «План миграции с compose на Kubernetes» — типовой проектный вопрос. Нужны шаги, риски, что меняется в архитектуре и эксплуатации. (Clinic — учебный пример.)

## Зачем переезжать (и когда не нужно)

**Причины**: рост числа сервисов и команд, HA (несколько узлов, автоперезапуск, зоны), автомасштабирование, частые релизы (rolling/canary), декларативная конфигурация и GitOps, политики безопасности, единая платформа.

**Не переезжать**, если: 1–3 сервиса, одна команда, стабильная нагрузка, нет компетенций и бюджета на эксплуатацию кластера — compose/systemd проще и дешевле. Альтернативы: управляемый Kubernetes (снять эксплуатацию control plane), Nomad, ECS/Cloud Run.

## Что меняется

| Compose | Kubernetes |
|---|---|
| сервис в `compose.yaml` | Deployment + Service (+ HPA, PDB) |
| `ports:` | Ingress / Service типа LoadBalancer |
| `env_file`, `secrets` | ConfigMap, Secret (+ ESO/SOPS) |
| `volumes` | PVC/StorageClass |
| `depends_on` + healthcheck | readiness/startup probes, init-контейнеры, Jobs |
| `restart: unless-stopped` | контроллеры пересоздают поды; probes |
| `deploy.resources` | `requests/limits` |
| nginx reverse proxy на хосте | Ingress-контроллер (nginx/Traefik) + cert-manager |
| Ansible шаблонизирует конфиги | Helm/Kustomize + GitOps |
| `docker compose up` | `helm upgrade --install` / ArgoCD sync |
| логи `docker logs` | централизованные (Loki), `kubectl logs` |
| cAdvisor/node_exporter | kube-prometheus-stack |
| сеть compose | Service DNS, NetworkPolicy |

## Целевая архитектура

```text
Ingress (nginx) + cert-manager ─┬─ web (Deployment, Service)
                                ├─ api (Deployment, HPA, PDB) ── Service
                                └─ keycloak (StatefulSet/Operator)
api/worker ── PostgreSQL (оператор CloudNativePG или managed), Redis, ClickHouse (оператор), MinIO/S3 (внешнее)
otel-collector (DaemonSet agent + Deployment gateway) → ClickHouse
Мониторинг: kube-prometheus-stack, Loki, Grafana; секреты: External Secrets + Vault/SOPS; GitOps: ArgoCD
```

**Stateful-компоненты**: БД, ClickHouse, Keycloak-БД, MinIO — решение: **оставить вне кластера/управляемые сервисы** (безопаснее и проще на старте) либо операторы (CloudNativePG, Altinity ClickHouse Operator, MinIO Operator) с бэкапами. Часто: stateless в K8s, данные — managed/отдельные ВМ.

## План миграции (этапы)

1. **Подготовка**: провести аудит (сервисы, зависимости, конфигурации, секреты, состояние, трафик); определить **целевую платформу** (managed K8s / k3s на ВМ), размер кластера, зоны; решить по stateful; нагрузка и ресурсы (метрики compose → requests/limits).
2. **Доводка приложений под 12-factor/K8s** (если не сделано): конфигурация из окружения, **health endpoints** (live/ready/startup), graceful shutdown (SIGTERM), логи в stdout (JSON), stateless сессии (Redis), метрики/трейсы, корректные таймауты/ретраи, non-root образы, миграции вне старта приложения.
3. **Кластер и платформа** (через IaC): Terraform создаёт кластер, сети, ноды; ставятся Ingress-NGINX, cert-manager, ExternalDNS, metrics-server, kube-prometheus-stack, Loki, Velero, политики (Kyverno/PSA), RBAC/OIDC через Keycloak, ESO.
4. **Упаковка приложений**: **Helm-чарты** (один общий библиотечный чарт + values на сервисы) или Kustomize: Deployment, Service, Ingress, ConfigMap, HPA, PDB, ServiceAccount, NetworkPolicy, probes, ресурсы, securityContext; Jobs для миграций (Helm hook).
5. **CI/CD**: сборка образов как раньше; обновление тега в репозитории окружений → **ArgoCD** (или `helm upgrade --atomic` в пайплайне на старте); окружения `staging`, `prod` (namespaces/кластеры), промоушен образов по тегам.
6. **Секреты и конфигурация**: перенос `.env` в ConfigMap/Secret; секреты через External Secrets/SOPS; Keycloak realm — импорт/Operator; cert-manager вместо certbot.
7. **Данные**: стратегия переноса БД (dump/restore, логическая репликация для малого простоя), ClickHouse (перелив/реплика), MinIO (`mc mirror`); проверка целостности; **окна и план отката**.
8. **Наблюдаемость**: OTel Collector (DaemonSet + Gateway), дашборды, алерты (кластерные + SLO), логи в Loki; сравнение метрик со старой инфраструктурой.
9. **Тестирование**: функциональное, нагрузочное, chaos (убить под/ноду), проверка откатов, DR-восстановление (Velero), безопасность (NetworkPolicy, PSA, сканирование).
10. **Параллельный запуск (shadow/canary)**: поднять staging в K8s, затем прод в K8s **параллельно со старым**, направлять трафик постепенно (DNS weights / балансировщик: 5% → 25% → 100%), наблюдать SLO.
11. **Cutover**: заморозка изменений, финальная синхронизация данных, переключение DNS/балансировщика, мониторинг, готовность к откату (старое окружение остаётся несколько дней/недель).
12. **Завершение**: удалить старое окружение после периода стабилизации, обновить документацию, runbook'и, обучить команду (on-call), ретроспектива.

## Пример Helm-values для api

```yaml
# values-prod.yaml
replicaCount: 3
image: { repository: registry.example.com/clinic/api, tag: "1.4.2" }
service: { port: 80, targetPort: 8080 }
ingress:
  enabled: true
  className: nginx
  host: clinic.example.com
  path: /api
  annotations: { cert-manager.io/cluster-issuer: letsencrypt }
resources: { requests: { cpu: 250m, memory: 384Mi }, limits: { memory: 768Mi } }
autoscaling: { enabled: true, minReplicas: 3, maxReplicas: 10, targetCPUUtilizationPercentage: 70 }
probes:
  startup:   { path: /health/startup, failureThreshold: 30, periodSeconds: 5 }
  liveness:  { path: /health/live,  periodSeconds: 10 }
  readiness: { path: /health/ready, periodSeconds: 5 }
podDisruptionBudget: { minAvailable: 2 }
topologySpreadConstraints: [{ maxSkew: 1, topologyKey: topology.kubernetes.io/zone, whenUnsatisfiable: ScheduleAnyway }]
securityContext: { runAsNonRoot: true, readOnlyRootFilesystem: true, allowPrivilegeEscalation: false, capabilities: { drop: [ALL] } }
env:
  - { name: OTEL_EXPORTER_OTLP_ENDPOINT, value: "http://otel-collector.observability:4317" }
  - { name: OTEL_SERVICE_NAME, value: clinic-api }
envFrom: [{ configMapRef: { name: api-config } }, { secretRef: { name: api-secrets } }]
migration: { enabled: true, image: registry.example.com/clinic/migrator }
```

## Что нужно учесть

- **Состояние и данные**: PVC, зоны, бэкапы (Velero + снапшоты + PITR БД), тест восстановления;
- **Сеть**: Ingress, TLS, внутренние адреса (`postgres.clinic.svc`), NetworkPolicy, egress к внешним сервисам, реальный IP клиента (`externalTrafficPolicy`, `use-forwarded-headers`);
- **Keycloak**: `KC_HOSTNAME`/proxy headers за ingress, кэш Infinispan между репликами, большие cookie (буферы ingress);
- **WebSocket/SSE**: аннотации ingress, таймауты;
- **Ресурсы**: начальные requests по фактическим метрикам, VPA-рекомендации, PDB и anti-affinity;
- **Обновление/откат**: rolling, `helm rollback`/Git revert, миграции совместимы;
- **Безопасность**: PSA restricted, RBAC, секреты в ESO, сканирование, подпись образов, NetworkPolicy default deny;
- **Стоимость и эксплуатация**: кластер (ноды, LB, диски, трафик), обновления Kubernetes (раз в 3–4 мес), обучение команды, on-call;
- **Локальная разработка**: kind/k3d, Tilt/Skaffold, либо сохранить compose для dev (`docker compose` + общие образы);
- **Совместимость**: единые образы для compose и K8s (`build once`).

## Риски и снижение

| Риск | Снижение |
|---|---|
| Потеря данных при переносе | репликация/дамп с проверкой, откат, бэкапы до начала |
| Простой при cutover | параллельный запуск, DNS weights, логическая репликация БД |
| Недооценка сложности эксплуатации | managed K8s, GitOps, обучение, runbook'и, платформа шаблонов |
| Неправильные ресурсы → OOM/троттлинг | нагрузочные тесты, VPA/метрики, лимиты памяти с запасом |
| Проблемы сети/DNS/Ingress | раннее тестирование на staging, NetworkPolicy пошагово |
| Рост стоимости | FinOps: requests по факту, autoscaling, spot для воркеров, бюджеты |
| Расхождение окружений | GitOps, единые чарты, IaC |
| Команда не готова | обучение, пилот на одном сервисе, документация |

## Поэтапный подход по сервисам

Начать со **stateless-сервиса с минимальным риском** (например, `web` или второстепенный воркер), затем `api`, потом stateful/внешние зависимости; старый и новый контуры работают вместе (общая БД по сети); трафик переключается по сервисам.

## Вопросы с ответами

> [!question]- Как бы вы спланировали миграцию с docker compose на Kubernetes?
> Аудит и подготовка приложений (health, graceful shutdown, stdout-логи, конфигурация из окружения), платформа через IaC (кластер, ingress, cert-manager, мониторинг, секреты), Helm-чарты и GitOps, перенос данных, параллельный запуск и постепенное переключение трафика, готовый откат и период стабилизации.

> [!question]- Что делать с базами данных при переезде?
> Часто оставить вне кластера/в managed-сервисах или использовать проверенные операторы с бэкапами; данные переносить репликацией или dump/restore с проверкой и планом отката.

> [!question]- Что сложнее всего при миграции?
> Данные и состояние, изменение модели эксплуатации (обновления кластера, сеть, безопасность), настройка ресурсов и наблюдаемости и подготовка команды.
