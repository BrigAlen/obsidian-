---
type: topic
domain: devops
stage: 3
order: 7
status: todo
level: middle
tags: [domain/devops, stage/3, level/middle, priority/must]
reviewed: 
next_review: 
priority: must
time: 5
---

# Качество в пайплайне: тесты, линтеры, coverage, SonarQube, quality gates

↑ [[DO Этап 3 · CI-CD|Этап 3 · CI-CD]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~5 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> «Как вы гарантируете качество в пайплайне?» — тесты, линтеры, покрытие, quality gates, SonarQube.

## Пирамида проверок в CI

| Уровень | Что | Где |
|---|---|---|
| Форматирование и стиль | `dotnet format`, Prettier, `editorconfig` | pre-commit + CI |
| Линтеры | ESLint, Roslyn-анализаторы (`-warnaserror`), hadolint, shellcheck, yamllint, `helm lint`, `terraform validate` | CI |
| Unit-тесты | xUnit/NUnit, Vitest | каждый коммит/MR |
| Интеграционные | Testcontainers, WebApplicationFactory | MR/main |
| Контрактные | Pact, OpenAPI diff | MR |
| E2E | Playwright/Cypress на review/staging | main/nightly |
| Нагрузочные, производительность | k6, JMeter | nightly/перед релизом |
| Безопасность | SAST, SCA, secrets, container scan, DAST | CI, расписание |

## Тесты и отчёты

```yaml
test:
  script:
    - dotnet test --logger "junit;LogFilePath=$CI_PROJECT_DIR/junit.xml"
        --collect:"XPlat Code Coverage" --results-directory coverage
    - reportgenerator -reports:"coverage/**/coverage.cobertura.xml" -targetdir:coverage/report -reporttypes:"Cobertura;TextSummary"
  coverage: '/Line coverage:\s*(\d+\.?\d*)%/'
  artifacts:
    when: always
    reports:
      junit: junit.xml
      coverage_report: { coverage_format: cobertura, path: coverage/report/Cobertura.xml }
```

Результаты отображаются в MR (упавшие тесты, изменение покрытия). **Flaky-тесты**: карантин с задачей на исправление, а не бесконечные перезапуски.

## Покрытие (coverage)

Метрики: строки, ветки. **Порог на новый код** (diff coverage), а не только общий процент. 100% — не цель; покрытие не заменяет качество assertions. Инструменты: Coverlet + ReportGenerator, Codecov, SonarQube.

## SonarQube / SonarCloud

Платформа статического анализа: баги, уязвимости, **security hotspots**, **code smells**, дублирование, технический долг, покрытие.

```yaml
sonar:
  image: { name: sonarsource/sonar-scanner-cli:latest, entrypoint: [""] }
  variables: { SONAR_USER_HOME: "${CI_PROJECT_DIR}/.sonar", GIT_DEPTH: "0" }    # полная история для blame и new code
  script:
    - sonar-scanner -Dsonar.projectKey=clinic-api -Dsonar.host.url=$SONAR_URL
        -Dsonar.token=$SONAR_TOKEN -Dsonar.qualitygate.wait=true
        -Dsonar.cs.opencover.reportsPaths=coverage/**/coverage.opencover.xml
```

Для .NET: `dotnet sonarscanner begin ... / build / end`. **New Code** — анализ только новых изменений (Clean as You Code): вместо «починить 5000 старых замечаний».

## Quality Gates

**Порог качества** — набор условий, при нарушении которых пайплайн/MR блокируется:

- все тесты зелёные;
- покрытие нового кода ≥ 80%;
- 0 новых критичных багов/уязвимостей/hotspots без ревью;
- дублирование нового кода < 3%;
- рейтинги надёжности/безопасности/сопровождаемости не ниже A;
- отсутствие уязвимых зависимостей уровня High/Critical;
- образ прошёл сканирование.

```yaml
# блокировка слияния: Settings → Merge requests → «Pipelines must succeed» + обязательные approvals
```

Правила должны быть **разумными и стабильными**: слишком строгие — обходят (`allow_failure`), слишком слабые — бесполезны. Исключения — с обоснованием и сроком.

## Безопасность в пайплайне (кратко)

- **SAST** (Semgrep, SonarQube, CodeQL, GitLab SAST);
- **SCA** (Dependency-Check, `dotnet list package --vulnerable --include-transitive`, `npm audit`, Trivy fs, Renovate/Dependabot);
- **secret detection** (gitleaks, GitLab Secret Detection);
- **container scanning** (Trivy/Grype), IaC-сканеры (Checkov, tfsec, Kubescape);
- **DAST** (OWASP ZAP) на стенде;
- **лицензии** (license scanning).

## Проверки инфраструктурного кода

```bash
hadolint Dockerfile
shellcheck scripts/*.sh
yamllint .
helm lint chart/ && helm template chart/ | kubeconform -strict
terraform fmt -check && terraform validate && tflint && checkov -d .
ansible-lint; docker compose config -q
```

## Обратная связь

- статус и отчёты прямо в MR/PR; комментарии бота (Sonar, coverage);
- быстрые проверки — сначала; тесты запускаются параллельно и с кэшем;
- уведомления об упавших сборках в чат, владелец пайплайна;
- метрики качества: доля flaky, время тестов, покрытие, MTTR пайплайна, «красные» main.

## Практики

- **pre-commit/Husky**: те же проверки локально до коммита;
- **required checks** в защищённой ветке;
- **Clean as You Code**: отвечать за новый код;
- **тест на каждый баг** (регрессионный);
- **мутационное тестирование** (Stryker) для оценки качества тестов;
- независимость тестов, детерминированные данные, время и случайность управляемы.

## Вопросы с ответами

> [!question]- Что такое quality gate?
> Набор критериев качества (тесты, покрытие нового кода, уязвимости, дублирование, рейтинги), при невыполнении которых слияние или релиз блокируются автоматически.

> [!question]- Почему «100% покрытия» — плохая цель?
> Покрытие показывает выполнение кода, а не проверку поведения; погоня за процентом порождает бессмысленные тесты. Лучше порог на новый код и контроль ключевых путей.

> [!question]- Как работать с flaky-тестами?
> Выявлять (метрики нестабильности), изолировать в карантин с задачей на исправление, искать причину (асинхронность, данные, время, окружение); не скрывать повторными запусками.
