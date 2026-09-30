---
type: topic
domain: devops
stage: 3
order: 2
status: todo
level: middle
tags: [domain/devops, stage/3, level/middle, priority/must]
reviewed: 
next_review: 
priority: must
time: 5
---

# Версионирование и артефакты: SemVer, теги, Nexus и Harbor

↑ [[DO Этап 3 · CI-CD|Этап 3 · CI-CD]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~5 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> Без внятного версионирования нельзя воспроизвести релиз и откатиться. Спрашивают SemVer, схему тегов и хранилища артефактов.

## Semantic Versioning

`MAJOR.MINOR.PATCH[-prerelease][+build]`

| Часть | Когда увеличивается |
|---|---|
| **MAJOR** | несовместимые изменения API |
| **MINOR** | новая функциональность, обратно совместимая |
| **PATCH** | исправления ошибок |
| `-rc.1`, `-beta.2` | предрелизы (ниже релиза: `1.0.0-rc.1 < 1.0.0`) |
| `+sha.a1b2c3d` | метаданные сборки (не влияют на порядок) |

Для сервисов «API» = публичный контракт (REST/gRPC, схема событий, БД-контракты); для библиотек — публичный API. Версия `0.y.z` — нестабильная разработка.

## Автоматизация версий

- **Conventional Commits** (`feat:`, `fix:`, `feat!:` / `BREAKING CHANGE:`) → версия и changelog вычисляются автоматически: `semantic-release`, `release-please`, `git-cliff`, `standard-version`, `changesets` (monorepo);
- **GitVersion**, **MinVer**, **Nerdbank.GitVersioning** (.NET): версия из тегов git;
- версия как единый источник истины: тег `v1.4.2` в git → пайплайн публикует артефакты с той же версией.

```bash
git tag -a v1.4.2 -m "Release 1.4.2" && git push origin v1.4.2
# в пайплайне:
VERSION=${CI_COMMIT_TAG#v}
dotnet publish -p:Version=$VERSION -p:InformationalVersion=$VERSION+$CI_COMMIT_SHORT_SHA
docker buildx build -t $IMAGE:$VERSION -t $IMAGE:$CI_COMMIT_SHORT_SHA --push .
```

## Схема тегов образов

| Событие | Теги |
|---|---|
| коммит в `main` | `main`, `sha-a1b2c3d`, `1.5.0-dev.17` |
| MR | `mr-123`, `sha-...` |
| релиз (тег git) | `1.4.2`, `1.4`, `1` (подвижные), `latest` (по политике) |
| hotfix | `1.4.3` |

Правила: релизные теги **неизменяемые**; `latest` не использовать для деплоев; всегда связывайте образ с коммитом (тег SHA + OCI-лейблы); для воспроизводимости деплоя — версия или digest.

## Хранилища артефактов

| Тип | Примеры |
|---|---|
| Образы | GitLab Registry, Harbor, ECR/ACR/GAR, Docker Hub |
| Пакеты .NET | **NuGet**: GitLab/GitHub Packages, Azure Artifacts, **Nexus**, Artifactory, BaGet |
| Пакеты JS | **npm**: Verdaccio, Nexus, GitLab/GitHub Packages |
| Универсальные | Nexus Repository, **JFrog Artifactory** (Maven, npm, NuGet, PyPI, Docker, Helm, generic) |
| Helm-чарты | OCI-реестр, ChartMuseum, Harbor |
| Бинарники релизов | GitLab/GitHub Releases, S3/MinIO |

### Nexus Repository

Репозитории трёх видов:

- **hosted** — собственные артефакты (релизы, снапшоты);
- **proxy** — кэширующий прокси публичных реестров (nuget.org, npmjs, Docker Hub, Maven Central): ускорение, отказоустойчивость, аудит и контроль зависимостей, работа в закрытом контуре;
- **group** — единая точка доступа, объединяющая hosted + proxy.

Политики: очистка (cleanup policies по возрасту/версиям), права (роли), блокировка перезаписи релизов (*disable redeploy*), хранилище blob (S3/файловое).

```xml
<!-- NuGet.config -->
<configuration>
  <packageSources>
    <clear/>
    <add key="nexus" value="https://nexus.example.com/repository/nuget-group/index.json" />
  </packageSources>
  <packageSourceMapping>
    <packageSource key="nexus"><package pattern="*" /></packageSource>
  </packageSourceMapping>
</configuration>
```

### Harbor

Self-hosted **реестр образов** (CNCF): проекты и RBAC, **сканирование Trivy**, **подпись** (cosign/Notation), репликация между реестрами, **retention** и garbage collection, квоты, immutable tags, прокси-кэш Docker Hub, вебхуки, аудит, OIDC (Keycloak). Часто: Harbor для образов + Nexus/Artifactory для пакетов.

## Практики

- **immutable releases**: нельзя перезаписать опубликованную версию;
- **метаданные**: коммит, пайплайн, SBOM, подпись, provenance (SLSA);
- **promotion**: продвижение между репозиториями/тегами (dev → staging → prod) вместо пересборки;
- **retention**: очистка снапшотов и feature-сборок, хранение релизов;
- **кэш зависимостей через прокси**: защита от удаления пакетов (left-pad), недоступности внешних реестров и подмены;
- **приватные пакеты и scope** (dependency confusion): `@company/*`, `packageSourceMapping`;
- **lock-файлы** (`packages.lock.json`, `package-lock.json`) и `npm ci`, `dotnet restore --locked-mode`;
- **ревизия лицензий** и уязвимостей.

## Версионирование БД и API

- миграции БД с версиями (Flyway/EF), обратная совместимость (expand/contract);
- API: `/v1/`, заголовок версии, депрекейшн и политика поддержки; контракты (OpenAPI) проверяются на breaking changes (`oasdiff`).

## Вопросы с ответами

> [!question]- Как связать релиз, тег git, образ и пакет?
> Версия берётся из git-тега (`v1.4.2`): пайплайн собирает пакеты и образы с той же версией, добавляет тег `sha` и OCI-лейблы коммита; всё публикуется в реестры как неизменяемые артефакты.

> [!question]- Зачем proxy-репозиторий в Nexus?
> Кэширует внешние зависимости: быстрее сборки, работа при недоступности внешних реестров и в изолированных сетях, контроль и аудит используемых пакетов.

> [!question]- Что делает Conventional Commits полезными для релизов?
> По типам коммитов автоматически определяется следующая версия по SemVer и генерируется changelog.
