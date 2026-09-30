---
type: topic
domain: devops
stage: 2
order: 9
status: todo
level: junior
tags: [domain/devops, stage/2, level/junior, priority/must]
reviewed: 
next_review: 
priority: must
time: 10
---

# docker-compose: сервисы, depends_on, healthcheck, profiles, extends, env-файлы

↑ [[DO Этап 2 · Контейнеры — Docker, docker-compose, Makefile|Этап 2 · Контейнеры: Docker, docker-compose, Makefile]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~10 мин чтения</span><span class="chip">Уровень: junior</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> Compose — основной инструмент локальной разработки и небольших деплоев. Проверяют depends_on с healthcheck, profiles, переменные окружения.

## Идея

Декларативное описание многоконтейнерного приложения в `compose.yaml` (раньше `docker-compose.yml`): сервисы, сети, тома, конфигурации. Команды: `docker compose up -d`, `down`, `logs`, `ps`, `exec`, `build`, `pull`, `config`.

## Структура

```yaml
name: clinic
services:
  db:
    image: postgres:17
    environment:
      POSTGRES_DB: clinic
      POSTGRES_USER: clinic
      POSTGRES_PASSWORD_FILE: /run/secrets/db_password
    secrets: [db_password]
    volumes: [pgdata:/var/lib/postgresql/data]
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U clinic -d clinic"]
      interval: 5s
      timeout: 3s
      retries: 10
      start_period: 10s
    networks: [backend]

  api:
    build:
      context: ./src
      dockerfile: Api/Dockerfile
      args: { BUILD_CONFIGURATION: Release }
    image: registry.example.com/clinic/api:${TAG:-dev}
    env_file: [.env]
    environment:
      ConnectionStrings__Default: Host=db;Database=clinic;Username=clinic;Password=${DB_PASSWORD}
    depends_on:
      db: { condition: service_healthy }
      migrate: { condition: service_completed_successfully }
    ports: ["8080:8080"]
    networks: [backend, frontend]
    restart: unless-stopped

  migrate:
    image: registry.example.com/clinic/migrator:${TAG:-dev}
    depends_on: { db: { condition: service_healthy } }
    restart: "no"

  web:
    build: ./web
    ports: ["80:8080"]
    depends_on: [api]
    networks: [frontend]

  adminer:
    image: adminer
    profiles: ["debug"]
    ports: ["8081:8080"]

volumes:
  pgdata:
networks:
  frontend:
  backend:
secrets:
  db_password:
    file: ./secrets/db_password.txt
```

## depends_on и готовность

`depends_on` по умолчанию определяет только **порядок запуска**, а не готовность. Условия:

| condition | Значение |
|---|---|
| `service_started` | контейнер запущен (по умолчанию) |
| `service_healthy` | healthcheck зависимости успешен |
| `service_completed_successfully` | разовая задача завершилась с кодом 0 (миграции, инициализация) |

Без healthcheck приложение может стартовать раньше БД. Приложение **всё равно должно** уметь переподключаться (retry): это устойчивее, чем полагаться на порядок.

## Profiles

Опциональные сервисы включаются по профилю:

```bash
docker compose up -d                        # без профилей: db, api, web
docker compose --profile debug up -d        # + adminer
COMPOSE_PROFILES=debug,monitoring docker compose up -d
```

Применение: отладочные утилиты, мониторинг, тестовые данные, e2e-окружение.

## Переменные и env-файлы

Приоритет (от высшего): `docker compose run -e` → переменные оболочки → `environment:` → `env_file:` → `Dockerfile ENV`. Подстановка `${VAR}` в самом compose-файле берётся из окружения оболочки и файла **`.env`** рядом (либо `--env-file`).

```yaml
image: app:${TAG:-latest}                 # значение по умолчанию
password: ${DB_PASSWORD:?DB_PASSWORD не задан}   # обязательная
```

```text
# .env (в .gitignore!)
TAG=1.4.2
DB_PASSWORD=change-me
```

Различайте: `.env` — подстановка в compose-файл; `env_file:` — переменные внутри контейнера. Для секретов лучше `secrets:` (файлы в `/run/secrets`), а не переменные окружения (видны в `docker inspect`).

## Extends, include, override, fragments

**Override**: `compose.yaml` + `compose.override.yaml` автоматически объединяются (разработка), для прода: `-f compose.yaml -f compose.prod.yaml`.

```bash
docker compose -f compose.yaml -f compose.prod.yaml up -d
docker compose -f compose.yaml -f compose.prod.yaml config      # итоговая конфигурация после слияния
```

**YAML anchors** для повторов:

```yaml
x-common: &common
  restart: unless-stopped
  logging: { driver: json-file, options: { max-size: "20m", max-file: "3" } }
services:
  api:    { <<: *common, image: api }
  worker: { <<: *common, image: worker }
```

**`extends`**: наследование конфигурации сервиса из другого файла/сервиса. **`include`**: подключение целых compose-файлов (модульность для больших систем).

## Полезные поля

- `restart`: `no`, `on-failure[:N]`, `always`, `unless-stopped`;
- `healthcheck`, `init: true` (tini как PID 1: сбор зомби, сигналы), `stop_grace_period`, `stop_signal`;
- `deploy.resources.limits/reservations` (`cpus`, `memory`) — работают и в обычном compose;
- `user`, `read_only: true`, `tmpfs`, `cap_drop: [ALL]`, `security_opt: ["no-new-privileges:true"]`;
- `ulimits`, `sysctls`, `extra_hosts`, `dns`, `hostname`;
- `configs`, `secrets`; `volumes` (short/long синтаксис, `type: bind`, `read_only`);
- `develop.watch`: авто-синхронизация/пересборка при изменении файлов (`docker compose watch`);
- `scale`/`--scale api=3` (без `container_name` и фиксированных портов).

## Полезные команды

```bash
docker compose up -d --build --remove-orphans
docker compose up -d --wait                # ждать healthy
docker compose logs -f --tail 100 api
docker compose exec api sh; docker compose run --rm api dotnet ef ...
docker compose ps -a; docker compose top; docker compose config --services
docker compose pull && docker compose up -d      # обновление образов
docker compose down -v                     # с удалением томов (ОСТОРОЖНО: данные)
docker compose restart api; docker compose stop
docker compose cp api:/app/file ./
```

## Практика

- в проде фиксируйте теги/digest, не `latest`;
- один проект — свои сети; не публикуйте порты БД;
- healthcheck для всех важных сервисов;
- лимиты ресурсов и ротация логов;
- compose — для одного хоста (dev, малые нагрузки), для кластера — Kubernetes/Swarm;
- файл валидируйте: `docker compose config -q` в CI.

## Вопросы с ответами

> [!question]- Гарантирует ли depends_on, что БД готова принимать подключения?
> Нет: по умолчанию только порядок запуска. Для готовности используют `condition: service_healthy` вместе с healthcheck, а приложение всё равно должно повторять подключение.

> [!question]- Чем .env отличается от env_file?
> `.env` подставляет значения в сам compose-файл (`${VAR}`), а `env_file` передаёт переменные в окружение контейнера.

> [!question]- Для чего профили (profiles)?
> Чтобы опциональные сервисы (отладка, мониторинг, тестовые данные) запускались только по явному запросу, а не всегда.
