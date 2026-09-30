---
type: topic
domain: devops
stage: 8
order: 2
status: todo
level: senior
tags: [domain/devops, stage/8, level/senior, priority/nice]
reviewed: 
next_review: 
priority: nice
time: 6
---

# DevSecOps: сканирование образов (Trivy), зависимости, supply chain

↑ [[DO Этап 8 · Senior — надёжность, безопасность, платформа|Этап 8 · Senior: надёжность, безопасность, платформа]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge nice">По желанию</span><span class="chip">~6 мин чтения</span><span class="chip">Уровень: senior</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> Практические инструменты: сканирование образов Trivy, контроль зависимостей, защита цепочки поставок в конвейере и кластере.

## Поверхность атаки

Код → зависимости → образ → пайплайн → реестр → кластер → рантайм. Уязвимости возникают на каждом шаге; защита — автоматизированные проверки и политики.

## Trivy

Универсальный сканер (Aqua Security): **образы**, файловые системы, репозитории, **IaC** (Terraform, Kubernetes, Dockerfile, Helm), **secret detection**, **лицензии**, **SBOM**, кластеры Kubernetes.

```bash
trivy image registry.example.com/clinic/api:1.4.2
trivy image --severity HIGH,CRITICAL --ignore-unfixed --exit-code 1 registry.example.com/clinic/api:1.4.2   # блокировать сборку
trivy fs --scanners vuln,secret,misconfig,license .
trivy config ./deploy ./terraform                          # Dockerfile, k8s, Terraform
trivy image --format cyclonedx -o sbom.json IMAGE          # SBOM
trivy image --format sarif -o trivy.sarif IMAGE            # для GitHub/GitLab Security
trivy k8s --report summary cluster
trivy image --vex vex.json IMAGE                           # учёт исключений (VEX)
```

**Результат**: список CVE с серьёзностью (CRITICAL/HIGH/MEDIUM/LOW), версией, исправленной версией (`FixedVersion`), пакетом; источник — базы NVD, GitHub Advisory, дистрибутивов (обновляется при запуске; в закрытых сетях — зеркало БД `--db-repository`).

Интерпретация: **не всё критично**: CVE «без исправления» (`--ignore-unfixed`), недостижимый код, не эксплуатируемое (проверять **EPSS**, CISA KEV, **reachability**), переоценка серьёзности вендором. **Триаж**: `.trivyignore` с причиной и сроком пересмотра, VEX (подтверждение «не затронуты»).

Интеграции CI:

```yaml
trivy-image:
  stage: test
  image: { name: aquasec/trivy:latest, entrypoint: [""] }
  variables: { TRIVY_CACHE_DIR: .trivycache/ }
  cache: { paths: [.trivycache/] }
  script:
    - trivy image --severity CRITICAL --exit-code 1 --ignore-unfixed "$IMAGE:$CI_COMMIT_SHORT_SHA"
    - trivy image --format json -o trivy-report.json "$IMAGE:$CI_COMMIT_SHORT_SHA"
  artifacts: { when: always, paths: [trivy-report.json] }
```

Альтернативы: **Grype** (Anchore) + **Syft** (SBOM), **Docker Scout**, **Snyk**, **Clair**, **Harbor** (встроенный Trivy), облачные сканеры реестров (ECR, ACR, GAR), **Trivy Operator** (постоянное сканирование в кластере: `VulnerabilityReport`, `ConfigAuditReport`, `RbacAssessmentReport`).

## Зависимости (SCA)

- .NET: `dotnet list package --vulnerable --include-transitive`, NuGet Audit (`<NuGetAudit>`), `Directory.Packages.props` (центральное управление версиями);
- JS: `npm audit --omit=dev`, `npm ci`, `pnpm audit`, `socket.dev`;
- универсально: `trivy fs`, `osv-scanner`, **OWASP Dependency-Check**, **Dependency-Track** (портал SBOM), Snyk, GitHub Dependabot alerts;
- **автообновления**: **Renovate**/**Dependabot** создают MR с обновлением и прогоном тестов; группировка, расписание, автослияние для patch-версий с зелёными тестами;
- **lock-файлы** и `npm ci` / `--locked-mode` для воспроизводимости; `packageSourceMapping`/scoped-реестры против dependency confusion;
- политика SLA на устранение (Critical — 7 дней, High — 30, Medium — 90).

## Безопасные образы

- минимальные базы (distroless/chiseled/alpine/Wolfi), multi-stage, non-root, актуальные теги; **регулярная пересборка** (еженедельно/при новых CVE) — уязвимости появляются в уже собранных образах;
- **фиксация digest** базовых образов + Renovate;
- `hadolint` (Dockerfile), **Dockle**, `docker-bench-security`;
- **приватные зеркала** базовых образов («золотые образы»), запрет `:latest`;
- удаление лишних пакетов и shell в проде.

## Supply chain: подпись и provenance

**Sigstore / cosign**: подпись образа (keyless через OIDC CI), проверка при деплое; **SBOM** и **attestations** (`cosign attest`), **SLSA provenance**; политики допуска в K8s (**Kyverno** `verifyImages`, policy-controller, Connaisseur).

```bash
cosign sign --yes registry.example.com/clinic/api@sha256:<digest>
cosign verify registry.example.com/clinic/api@sha256:<digest> \
  --certificate-identity-regexp 'https://gitlab.example.com/clinic/.*' --certificate-oidc-issuer https://gitlab.example.com
```

Риски цепочки поставок: скомпрометированный пакет/action/образ, typosquatting, dependency confusion, скомпрометированный CI/раннер, утечки секретов. Меры: закрепление версий и хэшей, проверенные источники, минимальные права CI, изоляция раннеров, подписанные коммиты, ревью изменений пайплайнов (CODEOWNERS), SBOM + мониторинг новых CVE по хранимым SBOM (Dependency-Track), воспроизводимые сборки.

## Секреты и конфигурации

- **gitleaks/trufflehog** в pre-commit, CI и сканирование истории; GitLab/GitHub Secret Scanning (push protection);
- **IaC-сканирование**: Trivy config, Checkov, tfsec, KICS, kube-linter, Kubescape (по CIS/NSA/MITRE);
- Dockerfile/Helm: запрет `privileged`, root, `latest`, `hostPath`;
- проверка Terraform/K8s манифестов политиками (Conftest/OPA, Kyverno CLI) на этапе PR.

## DAST и динамические проверки

OWASP ZAP (baseline/full scan на staging), Nuclei, fuzzing API (Schemathesis, RESTler), nmap/testssl.sh для периметра; в CI — `zap-baseline.py` против временного окружения; результаты — в Security Dashboard; регулярные **пентесты**.

## Runtime-защита

- **Falco / Tetragon**: обнаружение подозрительного поведения (shell в контейнере, запись в `/etc`, исходящие соединения на майнеры, чтение секретов);
- **Kubernetes Audit**, алерты; сетевые политики, PSA/Kyverno; **seccomp/AppArmor**;
- мониторинг образов в работающем кластере (Trivy Operator): «образ безопасный на момент сборки, через месяц — уязвим»;
- реакция: изоляция пода/ноды, отзыв секретов, откат, расследование; план IR.

## Управление уязвимостями как процесс

1. **Инвентаризация** (SBOM всех сервисов, реестр образов, зависимости).
2. **Сканирование** непрерывно (CI, реестр, кластер) и по расписанию.
3. **Приоритизация**: серьёзность × эксплуатируемость (EPSS/KEV) × достижимость × критичность сервиса × наличие исправления.
4. **Исправление**: обновление зависимостей/образов, патчи, компенсирующие меры (WAF, NetworkPolicy, отключение функции).
5. **Исключения** с обоснованием и сроком (VEX).
6. **Метрики**: число открытых уязвимостей по серьёзности, **MTTR уязвимостей**, покрытие сканированием, доля образов старше N дней.
7. **Отчётность** и ответственность по командам; единый дашборд (DefectDojo, GitLab Security Dashboard).

## Шкала зрелости (пример)

| Уровень | Практики |
|---|---|
| Базовый | SCA + secret scanning в CI, сканирование образов, non-root |
| Средний | SAST, IaC-сканирование, quality/security gates, Renovate, SBOM, политики K8s (PSA) |
| Продвинутый | подпись и проверка образов, SLSA provenance, admission-политики, runtime-защита, reachability-анализ, регулярные red-team/pentest |

## Вопросы с ответами

> [!question]- Как использовать Trivy в пайплайне?
> Сканировать образ после сборки, блокировать по порогу (`--severity HIGH,CRITICAL --ignore-unfixed --exit-code 1`), сохранять отчёт и SBOM как артефакты, управлять исключениями через `.trivyignore`/VEX и регулярно пересканировать образы в реестре.

> [!question]- Почему образ нужно пересобирать и пересканировать регулярно?
> Новые уязвимости обнаруживаются и в уже собранных образах; обновление базового образа и зависимостей устраняет их, а сканирование в реестре и кластере показывает текущий риск.

> [!question]- Как защититься от подмены образа в цепочке поставок?
> Подписывать образы (cosign) в доверенном CI, публиковать SBOM/provenance и проверять подпись политиками допуска в кластере (Kyverno/policy-controller); фиксировать digest и использовать доверенные реестры.
