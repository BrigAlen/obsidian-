---
type: topic
domain: backend
stage: 7
section: "7.6"
order: 3
status: todo
level: senior
notion_id: 3ea33104867981a9874fd15bb01e9c43
tags: [domain/backend, stage/7, level/senior, topic/devops, topic/docker, topic/compose, priority/nice]
reviewed:
next_review:
priority: nice
time: 4
---

# Как поднимается Clinic: docker compose, Makefile, порядок запуска, healthcheck

↑ [[BE 7.6 DevOps для бэкенд-разработчика — деплой наших систем и CI-CD|7.6 DevOps для бэкенд-разработчика: деплой наших систем и CI/CD]] · ← [[BE 7.6.2 Dockerfile для .NET-микросервисов — общий core-образ, multi-stage, как у нас|Предыдущая]] · → [[BE 7.6.4 Конфигурация и секреты — env-файлы, Ansible-фабрика, окружения dev-staging-prod|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge nice">По желанию</span><span class="chip">~4 мин чтения</span><span class="chip">Уровень: senior</span></div>
<!-- meta:end -->



























> [!info] Зачем это на собесе
> Умение поднять многосервисное окружение одной командой и объяснить порядок запуска.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново; пример обобщён (сервисы `api`, `worker`, `postgres`, `kafka`).

## Объяснение

Docker Compose описывает набор сервисов в одном файле, `Makefile` даёт короткие команды для команды.

```yaml
services:
  postgres:
    image: postgres:16
    environment: { POSTGRES_PASSWORD_FILE: /run/secrets/pg_pass }
    volumes: [pgdata:/var/lib/postgresql/data]
    healthcheck: { test: ["CMD-SHELL", "pg_isready -U postgres"], interval: 5s, retries: 10 }
  migrate:
    image: registry.example.com/orders-migrations:${TAG}
    depends_on: { postgres: { condition: service_healthy } }
  api:
    image: registry.example.com/orders-api:${TAG}
    env_file: [.env]
    depends_on:
      migrate: { condition: service_completed_successfully }
      kafka:   { condition: service_healthy }
    ports: ["8080:8080"]
    healthcheck: { test: ["CMD", "wget", "-qO-", "http://localhost:8080/health/ready"], interval: 10s }
    restart: unless-stopped
volumes: { pgdata: {} }
```

```make
up:        ; docker compose up -d
down:      ; docker compose down
logs:      ; docker compose logs -f --tail=200 api
migrate:   ; docker compose run --rm migrate
reset-db:  ; docker compose down -v && docker compose up -d postgres migrate
```

Порядок запуска: инфраструктура (БД, брокер, хранилище) → миграции (одноразовая задача) → сервисы → шлюз/фронтенд.

`depends_on` с `condition: service_healthy` ждёт **готовности**, а не просто запуска контейнера; при этом приложение всё равно должно уметь переподключаться к зависимостям.

## Нюансы и подводные камни

- Только `depends_on` без healthcheck не гарантирует готовность БД.
- Данные в volumes переживают `down`, но не `down -v`.
- `latest`-теги и «плавающие» образы делают окружение невоспроизводимым.
- Compose подходит для dev/staging и небольших продов; для масштабирования — Kubernetes.
- Порядок запуска ≠ надёжность: сервисы должны переживать перезапуск зависимостей.

## Практика

1. Соберите compose-окружение: БД, брокер, API с миграциями и health checks.
2. Добавьте `make up/down/logs/reset-db`.
3. Остановите БД и проверьте, что API восстанавливается сам.

## Вопросы с ответами

> [!question]- Гарантирует ли depends_on готовность зависимости?
> Только с `condition: service_healthy` и настроенным healthcheck.

> [!question]- Зачем отдельный сервис миграций?
> Схема применяется один раз до запуска приложения, независимо от числа реплик.

## Связанные темы

- [[N:3ea33104867981548b3aef7030878932]]
- [[N:3ea33104867981c0a409c221b337c688]]
