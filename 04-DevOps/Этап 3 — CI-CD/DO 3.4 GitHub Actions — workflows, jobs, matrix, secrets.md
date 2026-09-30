---
type: topic
domain: devops
stage: 3
order: 4
status: todo
level: middle
tags: [domain/devops, stage/3, level/middle, priority/must]
reviewed: 
next_review: 
priority: must
time: 10
---

# GitHub Actions: workflows, jobs, matrix, secrets

↑ [[DO Этап 3 · CI-CD|Этап 3 · CI-CD]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~10 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> GitHub Actions — самый распространённый CI для open-source и многих команд; важно знать workflow, matrix, secrets и безопасность.

## Структура

Файлы в `.github/workflows/*.yml`. **Workflow** запускается **событием** (`on`), содержит **jobs** (на **runners**), а те — **steps** (`run` команды или `uses` actions).

```yaml
name: CI
on:
  push: { branches: [main], tags: ["v*"] }
  pull_request: { branches: [main] }
  workflow_dispatch:
    inputs: { environment: { type: choice, options: [staging, prod] } }

permissions:                  # минимум прав для GITHUB_TOKEN
  contents: read

concurrency:
  group: ci-${{ github.ref }}
  cancel-in-progress: true

env:
  REGISTRY: ghcr.io
  IMAGE: ghcr.io/${{ github.repository }}/api

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        dotnet: ["8.0.x", "9.0.x"]
        os: [ubuntu-latest, windows-latest]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-dotnet@v4
        with: { dotnet-version: ${{ matrix.dotnet }} }
      - uses: actions/cache@v4
        with:
          path: ~/.nuget/packages
          key: nuget-${{ runner.os }}-${{ hashFiles('**/packages.lock.json') }}
      - run: dotnet test -c Release --logger trx
      - uses: actions/upload-artifact@v4
        if: always()
        with: { name: test-results-${{ matrix.os }}, path: "**/*.trx" }

  docker:
    needs: test
    if: github.ref == 'refs/heads/main' || startsWith(github.ref, 'refs/tags/v')
    runs-on: ubuntu-latest
    permissions: { contents: read, packages: write, id-token: write }
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3
      - uses: docker/login-action@v3
        with: { registry: ghcr.io, username: ${{ github.actor }}, password: ${{ secrets.GITHUB_TOKEN }} }
      - uses: docker/metadata-action@v5
        id: meta
        with: { images: "${{ env.IMAGE }}", tags: "type=semver,pattern={{version}}\ntype=sha" }
      - uses: docker/build-push-action@v6
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

  deploy:
    needs: docker
    runs-on: ubuntu-latest
    environment: { name: production, url: https://example.com }     # правила защиты: ревьюеры, ожидание
    steps:
      - run: ./scripts/deploy.sh ${{ needs.docker.outputs.version }}
        env: { SSH_KEY: ${{ secrets.DEPLOY_SSH_KEY }} }
```

## Ключевые понятия

| Понятие | Описание |
|---|---|
| **Events** | `push`, `pull_request`, `schedule` (cron), `workflow_dispatch`, `release`, `workflow_call` (вызываемый workflow), `repository_dispatch` |
| **Jobs** | независимые (по умолчанию параллельные); зависимость `needs`; `outputs` передают значения |
| **Steps** | последовательные в рамках job, общая файловая система раннера |
| **Actions** | переиспользуемые блоки (`uses: owner/repo@ref`): JS, Docker, composite |
| **Runners** | `ubuntu-latest`, `windows-latest`, `macos-latest` (GitHub-hosted) и **self-hosted** |
| **Matrix** | комбинации параметров (ОС, версии), `include`/`exclude` |
| **Contexts** | `${{ github.* }}`, `env`, `secrets`, `vars`, `needs`, `matrix`, `steps`, `runner` |
| **Expressions** | `if: ${{ success() }}`, `failure()`, `always()`, `contains()`, `hashFiles()` |
| **Artifacts** | `upload-artifact` / `download-artifact` между jobs |
| **Cache** | `actions/cache` (или встроенный кэш `setup-*`) |
| **Environments** | окружения с правилами (обязательные ревьюеры, таймер, ветки), секреты окружения, история деплоев |
| **Reusable workflows** | `uses: org/repo/.github/workflows/build.yml@v1` с `inputs`/`secrets` |

## Secrets и переменные

- **Secrets**: зашифрованные (repo, environment, organization); в логах маскируются; **не передаются** из форков в `pull_request`;
- **Variables** (`vars.*`) — несекретные настройки;
- **`GITHUB_TOKEN`**: автоматический короткоживущий токен; права задавайте `permissions:` (по умолчанию минимально `contents: read`);
- **OIDC** (`id-token: write`): получение временных облачных учётных данных (AWS/Azure/GCP/Vault) без долгоживущих ключей: рекомендуемый способ.

## Безопасность workflow

- **не доверять входным данным**: инъекции через `${{ github.event.pull_request.title }}` в `run:` — передавайте через `env:` и используйте как переменные оболочки;
- **pull_request_target** и `workflow_run` выполняются с секретами и правами — не запускать в них код из PR;
- **закреплять версии actions по SHA** (`uses: actions/checkout@<sha>`), особенно сторонние (цепочка поставок); Dependabot обновляет;
- минимальные `permissions`, environments с защитой для деплоев;
- self-hosted runners в публичных репозиториях опасны (код из PR);
- сканирование: CodeQL, Dependabot alerts, secret scanning, `step-security/harden-runner`;
- ограничить разрешённые actions в организации.

## Reusable workflows и composite actions

```yaml
# .github/workflows/build.yml (вызываемый)
on:
  workflow_call:
    inputs: { dotnet-version: { type: string, default: "9.0.x" } }
    secrets: { nuget-token: { required: false } }
jobs:
  build: { runs-on: ubuntu-latest, steps: [ ... ] }
```

```yaml
# вызов
jobs:
  ci:
    uses: my-org/.github/.github/workflows/build.yml@v1
    with: { dotnet-version: "9.0.x" }
    secrets: inherit
```

**Composite action** (`action.yml` с `runs: using: composite`) — набор шагов как один action.

## Сравнение с GitLab CI

| | GitHub Actions | GitLab CI |
|---|---|---|
| Конфиг | много файлов workflows | один `.gitlab-ci.yml` + include |
| Стадии | нет жёстких stages (jobs + `needs`) | stages + needs |
| Маркетплейс | богатый (actions) | меньше, но шаблоны и компоненты |
| Раннеры | hosted + self-hosted | shared/group/project, свои |
| Реестр образов | ghcr.io | встроенный Container Registry |
| Окружения/деплои | environments | environments + review apps, мощнее |
| Self-hosted | GitHub Enterprise Server | вся платформа self-hosted |

## Практика

- отмена устаревших запусков (`concurrency`), `timeout-minutes`;
- кэш зависимостей и Docker (`type=gha`);
- `paths`/`paths-ignore` для monorepo; `dorny/paths-filter`;
- теги релизов → `docker/metadata-action` → версии образа;
- `actions/attest-build-provenance` (подписи и provenance), cosign, SBOM;
- **`act`** для локального запуска; `actionlint` для проверки workflow.

## Вопросы с ответами

> [!question]- Как безопасно получить доступ к облаку из GitHub Actions?
> Через OIDC: workflow запрашивает токен у GitHub и обменивает его на временные учётные данные облака по доверительной политике; долгоживущие ключи в secrets не нужны.

> [!question]- Чем опасен pull_request_target?
> Выполняется в контексте базовой ветки с доступом к секретам; если он запускает код из PR-форка, злоумышленник получит секреты. Код из PR в нём запускать нельзя.

> [!question]- Что делает matrix?
> Запускает одно задание для каждой комбинации параметров (версия, ОС), параллельно; с `fail-fast` останавливает остальные при первой ошибке.
