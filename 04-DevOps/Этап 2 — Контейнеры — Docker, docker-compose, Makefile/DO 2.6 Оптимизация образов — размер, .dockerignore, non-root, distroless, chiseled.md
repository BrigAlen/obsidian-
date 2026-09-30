---
type: topic
domain: devops
stage: 2
order: 6
status: todo
level: junior
tags: [domain/devops, stage/2, level/junior, priority/must]
reviewed: 
next_review: 
priority: must
time: 5
---

# Оптимизация образов: размер, .dockerignore, non-root, distroless, chiseled

↑ [[DO Этап 2 · Контейнеры — Docker, docker-compose, Makefile|Этап 2 · Контейнеры: Docker, docker-compose, Makefile]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~5 мин чтения</span><span class="chip">Уровень: junior</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> Компактные и безопасные образы — признак зрелости. Спрашивают конкретные приёмы и инструменты проверки.

## Почему это важно

- **скорость** доставки (pull в CI, на ноды, при масштабировании);
- **стоимость** хранения и трафика;
- **безопасность**: меньше пакетов — меньше CVE;
- быстрый старт подов.

## Приёмы уменьшения размера

1. **Multi-stage build**: в финале только рантайм и артефакты.
2. **Минимальная база**: alpine, slim, distroless, chiseled, scratch.
3. **Очистка в том же слое**: `apt-get clean && rm -rf /var/lib/apt/lists/*`, `--no-install-recommends`, `apk add --no-cache`, `pip install --no-cache-dir`.
4. **`.dockerignore`**: не отправлять в контекст `.git`, `bin`, `obj`, `node_modules`, логи, `.env`.
5. **Только production-зависимости**: `npm ci --omit=dev`, `dotnet publish` без отладочных символов (`/p:DebugType=None`), trimming (`PublishTrimmed`), ReadyToRun.
6. **Не копировать лишнее**: точечный `COPY` вместо `COPY . .` в финальной стадии.
7. **Объединение `RUN`** для слоёв с временными файлами.
8. **Сжатие артефактов** и удаление документации/локалей.
9. **Native AOT / статические бинарники** (Go, Rust) на `scratch`.

```dockerfile
FROM python:3.12-slim
RUN apt-get update && apt-get install -y --no-install-recommends libpq5 \
 && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
```

Проверка: `docker images`, `docker history`, **dive** (неэффективные слои), `docker manifest inspect`.

## .dockerignore

```text
.git
.gitignore
**/bin
**/obj
**/node_modules
**/*.md
.env
.env.*
Dockerfile*
docker-compose*.yml
.vs
.vscode
coverage
```

Если всё игнорируется по умолчанию, используйте белый список (`*` затем `!src/`, `!package*.json`).

## Non-root

```dockerfile
RUN addgroup --system --gid 10001 app && adduser --system --uid 10001 --ingroup app app
COPY --chown=app:app . .
USER 10001:10001
```

- используйте **числовой UID**: Kubernetes проверяет `runAsNonRoot` по числу;
- порты выше 1024 (`8080`) — непривилегированному пользователю нельзя слушать < 1024 (или дать capability);
- права на каталоги записи (`/tmp`, `/app/data`) — только нужным;
- `readOnlyRootFilesystem: true` + `tmpfs` для временных файлов.

## Distroless и chiseled

**Distroless** (Google): образы без shell и пакетного менеджера, только рантайм (`gcr.io/distroless/static`, `base`, `cc`, `java`, `nodejs`, `python3`). **Chiseled** (Canonical/Microsoft): нарезанные Ubuntu-образы (`dotnet/aspnet:9.0-noble-chiseled`). **Chainguard/Wolfi**: минимальные образы с регулярными обновлениями (почти ноль CVE).

Плюсы: размер, поверхность атаки, non-root по умолчанию. Минусы: нет `sh` → отладка: `docker debug` (Docker Desktop), ephemeral containers в Kubernetes (`kubectl debug -it pod --image=busybox --target=app`), отладочные теги (`:debug` c busybox).

## Безопасность образов

- сканирование: **Trivy**, Grype, Docker Scout, Snyk (в CI, блокировать HIGH/CRITICAL с исправлениями);
- регулярная **пересборка** для подхвата патчей базового образа;
- фиксировать базовый образ по **digest** и обновлять автоматически (Renovate, Dependabot);
- **SBOM** (Syft), **подпись** образов (cosign), политики допуска (Kyverno, OPA Gatekeeper);
- не хранить секреты (BuildKit secrets), минимальные capabilities (`--cap-drop ALL`), `no-new-privileges`;
- линтер Dockerfile: **hadolint**.

## Скорость запуска

- малый размер и кэш на нодах (предзагрузка образов);
- ленивая загрузка слоёв (stargz/SOCI) в некоторых реестрах;
- для .NET: ReadyToRun, tiered compilation, AOT; для Java: CRaC, GraalVM;
- `imagePullPolicy: IfNotPresent` с неизменяемыми тегами.

## Таблица «было — стало»

| Приём | Эффект (типично) |
|---|---|
| SDK → runtime (multi-stage) | 900 МБ → 220 МБ |
| Debian → alpine/chiseled | 220 → 100–130 МБ |
| `PublishTrimmed`, отказ от символов | −20–40% |
| Native AOT + `runtime-deps` | 15–30 МБ |
| Go на `scratch` | 10–20 МБ |

## Вопросы с ответами

> [!question]- Как уменьшить размер Docker-образа?
> Multi-stage, минимальная база (alpine/distroless/chiseled), очистка кэшей в том же слое, `.dockerignore`, только production-зависимости и артефакты.

> [!question]- Зачем запускать контейнер не от root?
> При компрометации приложения у атакующего будут минимальные права, сложнее выход на хост; многие платформы (OpenShift, политики Kubernetes) требуют non-root.

> [!question]- Как отлаживать distroless-образ без shell?
> Временный отладочный контейнер в том же namespace (`kubectl debug` / `docker debug`), либо отладочный вариант образа с busybox.
