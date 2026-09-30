---
type: topic
domain: devops
stage: 3
order: 12
status: todo
level: middle
tags: [domain/devops, stage/3, level/middle, priority/must]
reviewed: 
next_review: 
priority: must
time: 6
---

# DevSecOps и supply chain: SAST, SCA, SBOM, подпись и provenance

↑ [[DO Этап 3 · CI-CD|Этап 3 · CI-CD]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~6 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> Безопасность цепочки поставок — тренд и требование заказчиков: SAST, SCA, SBOM, подпись артефактов, provenance.

## Shift left

Безопасность встраивается **на ранних этапах** (в IDE, pre-commit, CI), а не проверяется в конце. Каждая проверка автоматизирована и даёт быструю обратную связь.

| Этап | Проверки |
|---|---|
| Код | pre-commit, секреты, линтеры безопасности, IDE-плагины |
| Commit/MR | **SAST**, **secret detection**, **SCA**, IaC-сканирование |
| Build | SBOM, сборка в изолированной среде, воспроизводимая |
| Package | **container scanning**, подпись, attestations |
| Deploy | policy-as-code (admission), проверка подписей |
| Run | DAST, runtime-защита (Falco), мониторинг уязвимостей, pentest |

## SAST (статический анализ кода)

Поиск уязвимостей в исходниках: SQL-инъекции, XSS, небезопасная криптография, хардкод секретов. Инструменты: **Semgrep**, SonarQube, **CodeQL**, GitLab SAST, Security Code Scan / Roslyn-анализаторы (.NET), ESLint-security. Плюсы: рано, по строкам; минусы: ложные срабатывания — триаж, настройка правил.

## SCA (анализ зависимостей)

Известные уязвимости (CVE) и лицензии в зависимостях (прямых и **транзитивных**).

```bash
dotnet list package --vulnerable --include-transitive
npm audit --omit=dev
trivy fs --scanners vuln,license --severity HIGH,CRITICAL .
osv-scanner -r .
```

Автообновления: **Renovate**, **Dependabot**; политики: блокировать High/Critical с доступным исправлением, срок устранения (SLA); lock-файлы и `npm ci`/`--locked-mode`; внутренние прокси (Nexus) с проверкой; **dependency confusion** защита (`packageSourceMapping`, scope).

## Secret detection

`gitleaks`, `trufflehog`, GitHub/GitLab Secret Detection: pre-commit + CI + сканирование истории; push rules; при находке — отзыв секрета.

## Container scanning

```bash
trivy image --severity HIGH,CRITICAL --ignore-unfixed --exit-code 1 registry/app:1.4.2
grype registry/app:1.4.2; docker scout cves ...
```

Проверяются пакеты ОС и языковые зависимости; политики: порог, игнор-файл (`.trivyignore`) с причиной и сроком; регулярное пересканирование реестра (уязвимости находятся после сборки); минимальные базовые образы сокращают шум.

## IaC и конфигурации

**Checkov, tfsec/Trivy config, KICS, Kubescape, kube-linter, Conftest/OPA, hadolint**: публичные бакеты, открытые порты `0.0.0.0/0`, privileged-поды, отсутствие шифрования, неограниченные IAM-права.

## DAST и тестирование на проникновение

**OWASP ZAP**, Burp, Nuclei на staging: проверка работающего приложения (заголовки, XSS, инъекции, авторизация). Fuzzing (API, парсеры). Регулярный pentest, bug bounty.

## Цепочка поставок (supply chain)

Атаки: подмена зависимости (typosquatting, dependency confusion), скомпрометированный пакет/action, компрометация CI, подмена образа/артефакта (SolarWinds, Codecov, xz, event-stream).

### SBOM

**Software Bill of Materials** — перечень компонентов и версий артефакта (форматы **CycloneDX**, **SPDX**). Позволяет быстро найти уязвимые сборки при новой CVE (log4shell).

```bash
syft registry/app:1.4.2 -o cyclonedx-json > sbom.json
trivy image --format cyclonedx -o sbom.json registry/app:1.4.2
grype sbom:sbom.json
```

Хранить как артефакт/attestation рядом с образом; требовательные заказчики и регуляторы просят SBOM.

### Подпись и проверка

**Sigstore/cosign**: подпись образов и артефактов; **keyless-подпись** через OIDC (идентичность CI), запись в прозрачный журнал **Rekor**; проверка при деплое.

```bash
cosign sign --yes registry/app@sha256:...
cosign attest --predicate sbom.json --type cyclonedx registry/app@sha256:...
cosign verify registry/app@sha256:... \
  --certificate-identity-regexp '^https://gitlab.example.com/clinic/.+' --certificate-oidc-issuer https://gitlab.example.com
```

Альтернативы: Notation (Notary v2), GPG для пакетов. Политики допуска в Kubernetes: **Kyverno** `verifyImages`, **Sigstore policy-controller**, Connaisseur: запрет неподписанных образов.

### Provenance и SLSA

**Provenance** — подтверждаемое описание: из какого исходного коммита, каким пайплайном и на каком билдере собран артефакт (in-toto attestation). **SLSA** (Supply-chain Levels for Software Artifacts): уровни зрелости (L1–L3+): скриптованная сборка, подписанный provenance, изолированный воспроизводимый билдер, защита от подделки. GitHub: `actions/attest-build-provenance`, SLSA generator; GitLab: SLSA provenance для артефактов.

### Укрепление CI

- **закрепление версий и digest** actions/образов (`@sha`), Renovate;
- минимальные права токенов (`permissions`, `CI_JOB_TOKEN` scope), OIDC вместо статических ключей;
- **эфемерные изолированные раннеры**, protected branches/environments, запрет секретов в MR из форков;
- обязательное ревью кода, **подписанные коммиты**, защита веток, CODEOWNERS для `.gitlab-ci.yml` и Dockerfile;
- внутренние зеркала и запрет прямого доступа в интернет для сборок (по возможности), **воспроизводимые сборки**;
- мониторинг изменений в pipeline-конфигурации, журналы аудита.

## Политики и управление уязвимостями

- **SLA устранения** (Critical — 7 дней, High — 30…);
- триаж: эксплуатируемость (EPSS, CISA KEV), достижимость, наличие исправления; исключения с обоснованием и сроком (**VEX**);
- единый дашборд (DefectDojo, Dependency-Track, Security Dashboard);
- **policy as code**: OPA/Conftest, Kyverno, Gatekeeper;
- метрики: число уязвимостей по серьёзности, время устранения, покрытие сканированием.

## Пример пайплайна безопасности

```yaml
include:
  - template: Security/SAST.gitlab-ci.yml
  - template: Security/Secret-Detection.gitlab-ci.yml
  - template: Security/Dependency-Scanning.gitlab-ci.yml

image-scan:
  stage: test
  image: { name: aquasec/trivy:latest, entrypoint: [""] }
  script: trivy image --exit-code 1 --severity CRITICAL --ignore-unfixed $IMAGE:$CI_COMMIT_SHORT_SHA

sbom-sign:
  stage: package
  script:
    - syft $IMAGE:$CI_COMMIT_SHORT_SHA -o cyclonedx-json > sbom.json
    - cosign sign --yes $IMAGE@$DIGEST
    - cosign attest --yes --predicate sbom.json --type cyclonedx $IMAGE@$DIGEST
```

## Вопросы с ответами

> [!question]- Чем SAST отличается от SCA и DAST?
> SAST анализирует исходный код, SCA ищет известные уязвимости и лицензии в зависимостях, DAST тестирует работающее приложение снаружи.

> [!question]- Что такое SBOM и зачем он нужен?
> Список компонентов и версий в артефакте (CycloneDX/SPDX). Позволяет быстро определить, какие сборки затронуты новой уязвимостью, и требуется клиентами и регуляторами.

> [!question]- Как убедиться в Kubernetes, что запускаются только доверенные образы?
> Подписывать образы в CI (cosign), а admission-политика (Kyverno/policy-controller) проверяет подпись и издателя перед запуском; плюс SBOM и provenance.
