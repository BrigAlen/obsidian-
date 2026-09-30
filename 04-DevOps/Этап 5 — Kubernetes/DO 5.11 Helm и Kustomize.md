---
type: topic
domain: devops
stage: 5
order: 11
status: todo
level: middle
tags: [domain/devops, stage/5, level/middle, priority/should]
reviewed: 
next_review: 
priority: should
time: 11
---

# Helm и Kustomize

↑ [[DO Этап 5 · Kubernetes|Этап 5 · Kubernetes]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~11 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> Helm и Kustomize — стандартные способы упаковки и параметризации манифестов; спрашивают чем отличаются и как организовать окружения.

## Проблема

Десятки YAML-манифестов для сервиса × окружения (dev/stage/prod) → дублирование. Нужны параметризация, упаковка, версионирование и обновление.

## Helm

**Пакетный менеджер Kubernetes**: **чарт (chart)** — пакет шаблонов манифестов + значения по умолчанию; **релиз (release)** — установленный экземпляр чарта в кластере; **репозиторий** (HTTP или OCI-реестр).

```text
clinic-api/
  Chart.yaml            # имя, версия чарта (version), версия приложения (appVersion), зависимости
  values.yaml           # значения по умолчанию
  values-prod.yaml      # (дополнительно, не стандартное имя)
  templates/
    _helpers.tpl        # именованные шаблоны (функции)
    deployment.yaml
    service.yaml
    ingress.yaml
    configmap.yaml
    hpa.yaml
    NOTES.txt
    tests/test-connection.yaml
  charts/               # подчарты-зависимости
```

Шаблоны на языке Go templates + библиотека Sprig:

```yaml
# templates/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "clinic-api.fullname" . }}
  labels: {{- include "clinic-api.labels" . | nindent 4 }}
spec:
  replicas: {{ .Values.replicaCount }}
  selector:
    matchLabels: {{- include "clinic-api.selectorLabels" . | nindent 6 }}
  template:
    metadata:
      annotations:
        checksum/config: {{ include (print $.Template.BasePath "/configmap.yaml") . | sha256sum }}   # рестарт при смене конфигурации
      labels: {{- include "clinic-api.selectorLabels" . | nindent 8 }}
    spec:
      containers:
        - name: app
          image: "{{ .Values.image.repository }}:{{ .Values.image.tag | default .Chart.AppVersion }}"
          {{- with .Values.env }}
          env: {{- toYaml . | nindent 12 }}
          {{- end }}
          resources: {{- toYaml .Values.resources | nindent 12 }}
          {{- if .Values.probes.enabled }}
          readinessProbe: { httpGet: { path: /health/ready, port: http } }
          {{- end }}
```

```yaml
# values.yaml
replicaCount: 2
image: { repository: registry.example.com/clinic/api, tag: "" }
resources: { requests: { cpu: 250m, memory: 256Mi }, limits: { memory: 512Mi } }
ingress: { enabled: true, host: app.example.com, tls: true }
env: []
```

Основные объекты: `.Values`, `.Release` (`Name`, `Namespace`, `IsInstall`), `.Chart`, `.Capabilities`; функции `default`, `quote`, `required`, `include`, `toYaml`, `nindent`, `tpl`, `lookup`; управляющие конструкции `if/else`, `range`, `with`; `_helpers.tpl` для повторяемых блоков.

### Команды

```bash
helm create clinic-api
helm lint ./clinic-api
helm template api ./clinic-api -f values-prod.yaml          # посмотреть манифесты без установки
helm install api ./clinic-api -n clinic --create-namespace -f values-prod.yaml --set image.tag=1.4.2
helm upgrade --install api ./clinic-api -n clinic -f values-prod.yaml --set image.tag=$TAG --atomic --wait --timeout 5m
helm list -A; helm status api -n clinic
helm history api -n clinic; helm rollback api 3 -n clinic
helm uninstall api -n clinic
helm diff upgrade api ./clinic-api -f values-prod.yaml      # плагин helm-diff: что изменится
helm get values api; helm get manifest api
helm repo add bitnami https://charts.bitnami.com/bitnami; helm search repo postgres
helm dependency update; helm package ./clinic-api; helm push clinic-api-1.0.0.tgz oci://registry.example.com/charts
```

- **`--atomic`**: при неудаче автоматически откатывает; `--wait` ждёт готовности;
- `upgrade --install` — идемпотентная выкатка в CI;
- порядок значений (приоритет): `values.yaml` < `-f file` (последний побеждает) < `--set`;
- **Helm хранит состояние релизов в Secret** (`sh.helm.release.v1.*`) в namespace релиза → история и откат;
- **hooks** (`helm.sh/hook: pre-upgrade`) — миграции, тесты, очистка; `helm test`;
- **зависимости/subcharts** (Chart.yaml `dependencies`: postgresql, redis), `condition`, `alias`, глобальные значения `global.*`;
- **Library charts** — общие шаблоны для всех сервисов;
- **Umbrella chart** — один чарт для всего приложения из подчартов.
- **values.schema.json** — валидация значений; `required` для обязательных.

Ограничения Helm: шаблоны текста (отладка YAML-отступов, `nindent`), сложность; CRD из `crds/` не обновляются при `upgrade`; осторожно с `lookup` и секретами в values (Git!); дрейф при ручных правках.

## Kustomize

**Без шаблонов**: накладывает **патчи** на базовые манифесты (встроен в `kubectl -k`).

```text
deploy/
  base/
    kustomization.yaml    # resources: [deployment.yaml, service.yaml]
    deployment.yaml
    service.yaml
  overlays/
    dev/kustomization.yaml
    prod/
      kustomization.yaml
      replicas-patch.yaml
```

```yaml
# overlays/prod/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
namespace: clinic
resources: [../../base, ingress.yaml]
namePrefix: prod-
commonLabels: { env: prod }
images:
  - name: registry.example.com/clinic/api
    newTag: 1.4.2
replicas:
  - { name: api, count: 5 }
patches:
  - path: replicas-patch.yaml
  - target: { kind: Deployment, name: api }
    patch: |-
      - op: replace
        path: /spec/template/spec/containers/0/resources/limits/memory
        value: 1Gi
configMapGenerator:
  - name: api-config
    behavior: merge
    literals: [LOG_LEVEL=warn]
secretGenerator: []        # добавляет хэш в имя → автоматический рестарт при изменении
```

```bash
kubectl kustomize overlays/prod          # посмотреть
kubectl apply -k overlays/prod
kubectl diff -k overlays/prod
```

Возможности: `patchesStrategicMerge`, JSON6902 patch, `images`, `replicas`, `namePrefix/Suffix`, `commonLabels/Annotations`, генераторы ConfigMap/Secret с хэшем, `components` (переиспользуемые блоки), `replacements` (подстановки между ресурсами), `helmCharts` (рендер Helm в Kustomize).

## Helm или Kustomize

| | Helm | Kustomize |
|---|---|---|
| Подход | шаблонизация + пакеты | патчи поверх чистого YAML |
| Версионирование, распространение | чарты, репозитории, релизы, откат | Git, без релизов (откат через Git/GitOps) |
| Параметризация | гибкая (`values`) | ограниченная (патчи) |
| Сложность | Go templates, отладка | проще читать, меньше возможностей |
| Сторонние приложения | стандарт (чарты nginx, prometheus, postgres) | через `helmCharts` или готовые манифесты |
| Подходит | распространяемое ПО, сложная параметризация, общий чарт для всех сервисов | окружения одного приложения, минимум абстракции |

Часто комбинируют: Helm для стороннего ПО, Kustomize для своих сервисов/окружений; **ArgoCD/Flux** умеют обоими и Helm+Kustomize (post-renderer).

## Практики

- **один универсальный чарт** для однотипных сервисов (стандартизация) + `values` на сервис;
- версия чарта (`version`) по SemVer, `appVersion` = версия приложения; публикация в OCI-реестр;
- `values` окружений — в Git; секреты не в открытых values (SOPS, External Secrets, sealed);
- **линт и проверки в CI**: `helm lint`, `helm template | kubeconform -strict`, `kube-linter`, `kubeval`, `conftest`, `helm unittest`;
- **`helm diff`** перед применением; `--atomic`/`--wait`;
- ограничить `helm` права ServiceAccount'а CI (namespaced);
- не править ресурсы вручную (`kubectl edit`) — дрейф;
- в GitOps Helm рендерится контроллером: `helm template`-подобно, без `helm install`.

## Вопросы с ответами

> [!question]- Чем Helm отличается от Kustomize?
> Helm — шаблонизатор и менеджер пакетов с релизами и откатом; Kustomize — декларативные патчи поверх базовых манифестов без шаблонов, встроен в kubectl.

> [!question]- Что делает helm upgrade --install --atomic --wait?
> Устанавливает или обновляет релиз, ждёт готовности ресурсов и при неудаче автоматически откатывается на предыдущую версию.

> [!question]- Как перезапустить поды при изменении ConfigMap в Helm?
> Добавить в шаблон пода аннотацию `checksum/config` с хэшем шаблона ConfigMap: при изменении конфигурации меняется шаблон пода, и Deployment выполняет rolling update.
