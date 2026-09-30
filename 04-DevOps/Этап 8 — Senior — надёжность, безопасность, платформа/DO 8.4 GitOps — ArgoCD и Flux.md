---
type: topic
domain: devops
stage: 8
order: 4
status: todo
level: senior
tags: [domain/devops, stage/8, level/senior, priority/nice]
reviewed: 
next_review: 
priority: nice
time: 9
---

# GitOps: ArgoCD и Flux

↑ [[DO Этап 8 · Senior — надёжность, безопасность, платформа|Этап 8 · Senior: надёжность, безопасность, платформа]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge nice">По желанию</span><span class="chip">~9 мин чтения</span><span class="chip">Уровень: senior</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> GitOps — современный способ доставки в Kubernetes. Нужно знать принципы, pull-модель и различия ArgoCD и Flux.

## Принципы GitOps (OpenGitOps)

1. **Декларативность**: желаемое состояние системы описано декларативно (YAML, Helm, Kustomize, Terraform).
2. **Версионирование и неизменяемость**: состояние хранится в Git (история, ревью, откат).
3. **Автоматическое получение**: изменения **автоматически подтягиваются** агентом.
4. **Непрерывная согласованность**: агент **постоянно сравнивает** фактическое состояние с Git и исправляет дрейф (**reconciliation**).

**Pull-модель** (агент внутри кластера забирает изменения) против **push** (CI имеет доступ и применяет `kubectl/helm`).

| | Push (CI деплоит) | Pull (GitOps) |
|---|---|---|
| Доступ к кластеру | у CI (учётные данные извне — риск) | у агента внутри; CI доступа не имеет |
| Дрейф | не обнаруживается | обнаруживается и исправляется |
| Аудит | логи CI | Git история + события агента |
| Откат | перезапуск пайплайна | `git revert` |
| Мульти-кластер | доставка секретов в CI | каждый кластер тянет сам |
| Безопасность | шире поверхность | уже |

## Схема

```text
Код приложения (repo app)  ──CI: build, test, image──▶ Registry
                                   │
                                   └─ обновление тега образа (PR/commit) ──▶ Репозиторий конфигурации (repo env / gitops)
                                                                                      │ pull
                                                      ArgoCD / Flux в кластере ◀──────┘ (сравнение и синхронизация)
                                                                   │
                                                               Kubernetes
```

Два репозитория: **код** и **конфигурация окружений** (манифесты, Helm values, Kustomize overlays): разделение ответственности, отдельный доступ и аудит (деплой = merge в репозиторий окружений). Промоушен: PR из `staging` в `prod` (или копирование тега), ревью/approval.

Обновление образов автоматизируют: **Argo CD Image Updater**, **Flux Image Automation**, **Renovate**, или пайплайн CI делает коммит тега.

## Argo CD

UI + контроллер + CLI. Ресурс **Application** описывает: источник (Git repo/path/revision, Helm/Kustomize/plain), назначение (кластер/namespace), политику синхронизации.

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata: { name: clinic-api, namespace: argocd }
spec:
  project: clinic
  source:
    repoURL: https://gitlab.example.com/clinic/gitops.git
    targetRevision: main
    path: apps/api/overlays/prod
    # helm: { valueFiles: [values-prod.yaml] }
  destination: { server: https://kubernetes.default.svc, namespace: clinic }
  syncPolicy:
    automated: { prune: true, selfHeal: true, allowEmpty: false }     # автоприменение, удаление лишнего, исправление дрейфа
    syncOptions: [CreateNamespace=true, ServerSideApply=true]
    retry: { limit: 5, backoff: { duration: 10s, factor: 2, maxDuration: 3m } }
```

Особенности:

- **статусы**: `Synced / OutOfSync`, `Healthy / Progressing / Degraded / Missing`;
- **App of Apps** и **ApplicationSet** (генерация Application по списку кластеров/каталогов/окружений: git/list/cluster generators) — масштабирование на десятки сервисов и кластеров;
- **AppProject**: ограничения (разрешённые репозитории, кластеры, namespaces, типы ресурсов) и RBAC;
- **sync waves и hooks** (`argocd.argoproj.io/sync-wave`, `PreSync/PostSync` Job): порядок (миграции → приложение);
- **drift**: `selfHeal` возвращает ручные изменения; `ignoreDifferences` для полей, изменяемых другими контроллерами (HPA replicas);
- **Rollback**: история синхронизаций, `argocd app rollback` (при авто-sync отключается; предпочтительно `git revert`);
- **Argo Rollouts** (canary/blue-green с анализом метрик) в паре;
- **SSO (OIDC/Keycloak)**, RBAC, аудит, мульти-кластерность (Hub-and-spoke), HA;
- секреты: SOPS/ksops, ESO, Vault plugin — **секреты не в Git открыто**.

## Flux

Набор контроллеров (GitOps Toolkit), Kubernetes-native, без отдельного UI (есть Weave GitOps/Headlamp плагины).

```yaml
apiVersion: source.toolkit.fluxcd.io/v1
kind: GitRepository
metadata: { name: gitops, namespace: flux-system }
spec: { interval: 1m, url: https://gitlab.example.com/clinic/gitops.git, ref: { branch: main }, secretRef: { name: flux-git } }
---
apiVersion: kustomize.toolkit.fluxcd.io/v1
kind: Kustomization
metadata: { name: apps-prod, namespace: flux-system }
spec:
  interval: 5m
  path: ./apps/prod
  prune: true
  sourceRef: { kind: GitRepository, name: gitops }
  healthChecks: [{ apiVersion: apps/v1, kind: Deployment, name: api, namespace: clinic }]
  dependsOn: [{ name: infra }]
  decryption: { provider: sops, secretRef: { name: sops-age } }
---
apiVersion: helm.toolkit.fluxcd.io/v2
kind: HelmRelease
metadata: { name: ingress-nginx, namespace: ingress-nginx }
spec: { interval: 10m, chart: { spec: { chart: ingress-nginx, version: 4.x, sourceRef: { kind: HelmRepository, name: ingress-nginx } } }, values: { controller: { replicaCount: 2 } } }
```

Компоненты: source-controller (Git/Helm/OCI/Bucket), kustomize-controller, helm-controller, notification-controller (Slack/Telegram/webhook), image-reflector/automation (обновление тегов в Git). Поддерживает SOPS «из коробки», OCI-артефакты, multi-tenancy, Cosign-проверку, `flux bootstrap` (сам себя управляет из Git), `flux diff/reconcile/suspend/resume`.

## Argo CD и Flux

| | Argo CD | Flux |
|---|---|---|
| UI | богатый веб-интерфейс, визуализация ресурсов | нет встроенного (сторонние) |
| Модель | Application/ApplicationSet | GitRepository + Kustomization/HelmRelease |
| Helm | рендерит (`helm template`), не хранит релиз Helm | нативный Helm-release (helm-controller) |
| Мульти-кластер | удобное управление из одной точки | каждый кластер со своим Flux (pull из общего репо) или remote |
| Секреты | плагины (ksops, vault) | SOPS нативно |
| Обновление образов | Image Updater (доп. компонент) | встроенная Image Automation |
| Кривая обучения | проще для старта (UI) | «Kubernetes-native», CLI |
| Экосистема | Argo Rollouts, Workflows, Events | Flagger |

Оба зрелы (CNCF Graduated). Выбор — по предпочтениям (UI и прозрачность — Argo; минимализм и композиция — Flux).

## Структура репозитория

```text
gitops/
  clusters/{prod,staging}/            # точки входа кластеров (Flux/Argo root apps)
  infra/                              # ingress, cert-manager, monitoring, policies, operators
  apps/
    api/{base, overlays/{dev,staging,prod}}
    web/...
  tenants/
```

Подходы к окружениям: **каталоги** (`overlays/prod`) — рекомендуется (ясный diff и ревью); **ветки** на окружение (проблемы слияний); **Helm values на окружение**.

## Практики

- **никаких ручных изменений** кластера (`kubectl edit/apply`); RBAC: людям read-only, запись — у GitOps-агента;
- **ревью и защита веток** репозитория окружений (кто может мерджить в prod), подписанные коммиты, CODEOWNERS;
- **промоушен** между окружениями через PR; автосинхронизация в dev/staging, для prod — ручное подтверждение или auto с окнами (`syncWindows`);
- **health checks и прогрессивные релизы** (Argo Rollouts/Flagger), автооткат по метрикам;
- **`prune`** осторожно (удаление ресурсов, отсутствующих в Git), защита критичных (аннотации `Prune=false`, PVC, namespaces);
- **секреты**: SOPS/ESO/Sealed Secrets; **drift-уведомления**;
- **мониторинг GitOps**: метрики `argocd_app_info`, `gotk_reconcile_condition`, алерты на OutOfSync/Degraded/ошибки sync;
- **bootstrap**: сам GitOps-агент и инфраструктурные компоненты описаны в Git; восстановление кластера = bootstrap + sync;
- **инфраструктура**: Terraform создаёт кластер и bootstrap GitOps; дальше всё — Git. Для облачных ресурсов из Git: **Crossplane**, Flux tofu-controller, Atlantis;
- **масштабирование**: ApplicationSet/Kustomization на сервис, sharding контроллеров, лимиты API-вызовов;
- **документирование процесса**: как вносить изменения, аварийные правки (break-glass → коммит после), откат.

## Проблемы

| Проблема | Причина/решение |
|---|---|
| Постоянный `OutOfSync` | поля, изменяемые контроллерами (HPA, mutating webhooks) → `ignoreDifferences`, server-side apply |
| Порядок применения (CRD до CR, namespace, миграции) | sync waves, `dependsOn`, hooks |
| Секреты в Git | SOPS/ESO/Sealed Secrets |
| Удалён ресурс при `prune` | защита критичных, ревью diff |
| Долгая синхронизация | размер репозитория, интервалы, вебхуки для мгновенного триггера |
| Git — SPOF для деплоя | зеркала, кэш, возможность ручного вмешательства (break-glass) |
| Откат данных (миграции БД) | GitOps откатывает манифесты, но не данные: совместимые миграции |

## Вопросы с ответами

> [!question]- Чем GitOps отличается от обычного CI/CD?
> Состояние окружений хранится в Git, а агент в кластере по pull-модели непрерывно приводит фактическое состояние к репозиторию, исправляя дрейф; у CI нет прямого доступа к кластеру.

> [!question]- Что такое drift и как его решает GitOps?
> Дрейф — расхождение между Git и кластером из-за ручных правок. Агент (Argo CD/Flux) обнаруживает OutOfSync и с `selfHeal` автоматически возвращает состояние к эталону из Git.

> [!question]- Как хранить секреты в GitOps?
> Не в открытом виде: SOPS или Sealed Secrets шифруют значения в Git, External Secrets Operator хранит в Git только ссылки на внешний менеджер секретов.
