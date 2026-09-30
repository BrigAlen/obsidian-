---
type: topic
domain: devops
stage: 2
order: 11
status: todo
level: junior
tags: [domain/devops, stage/2, level/junior, priority/must]
reviewed: 
next_review: 
priority: must
time: 5
---

# Container registry: теги, версионирование, GitLab Registry

↑ [[DO Этап 2 · Контейнеры — Docker, docker-compose, Makefile|Этап 2 · Контейнеры: Docker, docker-compose, Makefile]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~5 мин чтения</span><span class="chip">Уровень: junior</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> Реестр — «склад» образов в пайплайне; спрашивают схему тегов, хранение, очистку и аутентификацию.

## Что такое реестр

Сервис, реализующий OCI Distribution API: хранит образы (манифесты и слои-блобы) и отдаёт их по `pull`/`push`. Адрес образа: `registry.example.com:5000/team/app:1.4.2` = `host[:port]/namespace/repo:tag` (или `@sha256:digest`).

| Реестр | Особенности |
|---|---|
| **Docker Hub** | публичный по умолчанию, лимиты pull для анонимов |
| **GitLab Container Registry** | встроен в GitLab; права наследуются от проекта; переменные CI (`CI_REGISTRY`, `CI_REGISTRY_IMAGE`, `CI_JOB_TOKEN`) |
| **GitHub Container Registry** (ghcr.io), **GHCR** | интеграция с Actions |
| **Harbor** | self-hosted: RBAC, сканирование (Trivy), репликация, подпись, квоты, прокси-кэш |
| **Nexus / Artifactory** | универсальные репозитории артефактов (образы + пакеты) |
| **AWS ECR, Google Artifact Registry, Azure ACR, Yandex Container Registry** | облачные, IAM, сканирование |
| **registry:2 (distribution)** | минимальный self-hosted реестр |

## Работа

```bash
docker login registry.example.com -u user --password-stdin < token.txt
docker build -t registry.example.com/clinic/api:1.4.2 .
docker push registry.example.com/clinic/api:1.4.2
docker pull registry.example.com/clinic/api:1.4.2
docker tag clinic/api:1.4.2 registry.example.com/clinic/api:latest
skopeo copy docker://src/app:1.0 docker://dst/app:1.0         # перенос между реестрами без локального Docker
crane ls registry.example.com/clinic/api; crane digest ...
```

Аутентификация: токены доступа/deploy tokens (с минимальными правами, `read_registry` для деплоя, `write_registry` для CI), job token в GitLab CI, IAM-роли в облаке. **Не использовать личные пароли**; в CI — временные токены. На нодах Kubernetes — `imagePullSecrets` (`kubectl create secret docker-registry`).

## Теги и версионирование

Схема (ориентир):

| Тег | Пример | Назначение |
|---|---|---|
| **Неизменяемая версия** | `1.4.2` | релиз (по git-тегу) |
| **Версия + коммит** | `1.4.2-a1b2c3d` | трассировка до коммита |
| **Коммит** | `a1b2c3d` | сборки веток/MR |
| **Скользящие** | `1.4`, `1`, `latest`, `main`, `staging` | удобные «указатели» (подвижные) |
| **Ветка/MR** | `mr-123`, `feature-x` | ревью-стенды (с TTL) |

Правила:

- **не деплоить `latest`** в прод: невоспроизводимо, откат невозможен, неясно, что запущено;
- теги релизов — **неизменяемые** (запрет перезаписи в реестре: immutable tags в Harbor/ECR);
- **digest** — истинный идентификатор (`@sha256:...`); в манифестах GitOps можно фиксировать digest;
- один образ для всех окружений (**build once, deploy many**): различается только конфигурация; продвижение образа — повторный тег (`docker buildx imagetools create`, `crane tag`), а не пересборка;
- метаданные: OCI-лейблы (`org.opencontainers.image.source`, `revision`, `version`, `created`), SBOM и подпись (cosign) связывают образ с коммитом и сборкой.

```bash
docker buildx build \
  --label org.opencontainers.image.revision=$CI_COMMIT_SHA \
  --label org.opencontainers.image.version=$VERSION \
  -t $CI_REGISTRY_IMAGE/api:$VERSION -t $CI_REGISTRY_IMAGE/api:$CI_COMMIT_SHORT_SHA --push .
```

## Политики хранения и очистка

Без очистки реестр разрастается. Политики:

- удалять теги веток/MR старше N дней; хранить последние K релизов; **никогда не удалять** то, что запущено в проде;
- GitLab: Cleanup policies (regex для хранения/удаления, срок, количество), `gitlab-ctl registry-garbage-collect`;
- Harbor: retention policy + garbage collection; ECR: lifecycle policy;
- удаление тега не освобождает место до **garbage collection** (слои общие).

## Безопасность реестра

- приватные репозитории по умолчанию, права по принципу наименьших привилегий;
- **сканирование** уязвимостей (Trivy в Harbor/CI), блокировка pull образов с критичными CVE (политики);
- **подпись** (cosign/Notation) и проверка при деплое (Kyverno, policy controller);
- TLS обязательно; доступ по сети ограничен;
- **proxy-cache** (Harbor, Nexus, ECR pull-through): кэш Docker Hub, обход лимитов и отказоустойчивость, контроль источников;
- зеркало базовых образов (внутренний «золотой» набор).

## Надёжность и скорость

- реплицируйте реестр (мультирегион), CDN/кэш на нодах; мониторинг доступности: недоступность реестра блокирует деплой и масштабирование;
- близость к кластеру (в том же регионе/сети) — скорость pull;
- квоты и алерты на заполнение.

## Типичные проблемы

| Симптом | Причина |
|---|---|
| `unauthorized: authentication required` | нет/истёк токен, нет прав, неверный `imagePullSecret` |
| `manifest unknown` | нет такого тега/архитектуры |
| `toomanyrequests` (Docker Hub) | лимит анонимных pull: логин или зеркало |
| `x509: certificate signed by unknown authority` | self-hosted реестр с внутренним CA: добавить CA на хост/ноды |
| `ImagePullBackOff` в Kubernetes | любое из выше + неверное имя/тег/сеть |
| Образ «не обновляется» | подвижный тег и `IfNotPresent`; пинуйте digest/версию |

## Вопросы с ответами

> [!question]- Почему не стоит использовать тег latest в продакшне?
> Он подвижный: нельзя определить, какая версия запущена, невозможно воспроизвести и откатиться. Нужны неизменяемые версионные теги или digest.

> [!question]- Что значит «build once, deploy many»?
> Образ собирается один раз в CI и продвигается по окружениям (dev → staging → prod) без пересборки; различается только конфигурация. Так в прод попадает ровно то, что тестировали.

> [!question]- Как организовать очистку реестра?
> Политики хранения (по возрасту, количеству, regex тегов), защита релизных/запущенных тегов, регулярный garbage collection, теги MR с коротким сроком жизни.
