---
type: topic
domain: devops
stage: 9
order: 7
status: todo
level: final
tags: [domain/devops, stage/9, level/final, priority/must]
reviewed: 
next_review: 
priority: must
time: 12
---

# Разбор: развёртывание Clinic end-to-end (Makefile, Ansible, compose, nginx, Keycloak, телеметрия)

↑ [[DO Этап 9 · Собес Middle DevOps — вопросы, практика, деплой систем|Этап 9 · Собес Middle DevOps: вопросы, практика, деплой систем]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~12 мин чтения</span><span class="chip">Уровень: final</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> Разбор «учебной» системы от начала до конца (вымышленный проект Clinic — запись пациентов на приём) показывает, как все инструменты связаны. Используйте как шаблон рассказа о собственном проекте.

## Система Clinic (пример)

Состав:

- **Frontend**: Vue 3 + Quasar (SPA), статика в nginx;
- **Backend**: ASP.NET Core API (REST), фоновые воркеры;
- **Аутентификация**: Keycloak (OIDC, Authorization Code + PKCE);
- **Данные**: PostgreSQL (основные), Redis (кэш, сессии), ClickHouse (аналитика и телеметрия), MinIO (документы, снимки);
- **Телеметрия**: OpenTelemetry (SDK в сервисах) → OpenTelemetry Collector → ClickHouse, Grafana;
- **Edge**: Nginx (TLS, reverse proxy, SPA fallback, rate limiting).

Окружения: `dev` (локально, compose), `staging`, `prod`.

## Архитектура и путь запроса

```text
Браузер ──HTTPS──▶ Nginx ──/──────▶ web (nginx со статикой SPA)
                      ├─/api/────▶ api (.NET) ──▶ PostgreSQL / Redis / MinIO
                      └─/auth/───▶ keycloak ─────▶ PostgreSQL (keycloak DB)
api / keycloak / nginx ──OTLP──▶ otel-collector ──▶ ClickHouse ──▶ Grafana
```

Путь кода: `commit → GitLab CI (тесты, образы) → Registry → Ansible/compose на сервере → smoke-test`.

## Структура репозитория

```text
clinic/
  Makefile
  compose.yaml                 # базовое описание (dev)
  compose.prod.yaml            # переопределения для сервера
  src/{Api,Worker,Migrator}/   # .NET
  web/                         # Vue/Quasar
  deploy/
    ansible/
      inventories/{staging,prod}/{hosts.yml,group_vars/,host_vars/}
      roles/{common,docker,nginx,clinic_stack,keycloak,otel}/
      playbooks/{site.yml,deploy.yml,backup.yml}
    nginx/templates/*.j2
    otel/collector.yaml.j2
    keycloak/realm-clinic.json
  .gitlab-ci.yml
```

## Makefile — точка входа

```make
ENV     ?= dev
TAG     ?= $(shell git rev-parse --short HEAD)
COMPOSE := docker compose -f compose.yaml $(if $(filter-out dev,$(ENV)),-f compose.$(ENV).yaml)

.DEFAULT_GOAL := help
.PHONY: help up down logs build test migrate deploy backup
help:    ## Справка
	@grep -E '^[a-z-]+:.*## ' $(MAKEFILE_LIST) | awk -F':.*## ' '{printf "%-10s %s\n",$$1,$$2}'
up:      ## Запустить окружение
	$(COMPOSE) up -d --build --wait
down:    ## Остановить
	$(COMPOSE) down
logs:    ## Логи (S=сервис)
	$(COMPOSE) logs -f --tail=100 $(S)
build:   ## Собрать образы
	docker buildx build -t registry/clinic/api:$(TAG) -f src/Api/Dockerfile .
test:    ## Тесты
	dotnet test && npm --prefix web run test
migrate: ## Применить миграции
	$(COMPOSE) run --rm migrate
deploy:  ## Деплой: make deploy ENV=staging TAG=1.4.2
	cd deploy/ansible && ansible-playbook -i inventories/$(ENV) playbooks/deploy.yml -e tag=$(TAG)
backup:  ## Бэкап БД
	cd deploy/ansible && ansible-playbook -i inventories/$(ENV) playbooks/backup.yml
```

## Docker: образы

- **api/worker**: multi-stage (`sdk` → `aspnet:9.0-noble-chiseled`), non-root, порт 8080, `HEALTHCHECK` снаружи (compose/оркестратор), переменные окружения для конфигурации;
- **web**: `node` → сборка Quasar → `nginx-unprivileged` с SPA fallback; **runtime-конфигурация** `config.json` из переменных окружения (один образ на все окружения);
- **migrator**: отдельный образ/бандл EF Core — запускается одноразово;
- теги: `sha` и релизная версия, OCI-метки; все образы в GitLab Registry.

## compose (прод): фрагмент

```yaml
name: clinic
x-common: &common
  restart: unless-stopped
  logging: { driver: json-file, options: { max-size: "20m", max-file: "5" } }
  networks: [backend]
services:
  postgres:
    <<: *common
    image: postgres:17
    environment: { POSTGRES_DB: clinic, POSTGRES_USER: clinic, POSTGRES_PASSWORD_FILE: /run/secrets/pg_password }
    secrets: [pg_password]
    volumes: [pgdata:/var/lib/postgresql/data]
    healthcheck: { test: ["CMD-SHELL", "pg_isready -U clinic -d clinic"], interval: 10s, retries: 10 }
  migrate:
    image: ${REGISTRY}/clinic/migrator:${TAG}
    env_file: [.env]
    depends_on: { postgres: { condition: service_healthy } }
    restart: "no"
    networks: [backend]
  api:
    <<: *common
    image: ${REGISTRY}/clinic/api:${TAG}
    env_file: [.env]
    depends_on: { migrate: { condition: service_completed_successfully }, redis: { condition: service_started } }
    deploy: { resources: { limits: { memory: 768M } } }
    read_only: true
    tmpfs: [/tmp]
    cap_drop: [ALL]
  keycloak:
    <<: *common
    image: quay.io/keycloak/keycloak:26.0
    command: [start, --optimized, --import-realm]
    environment: { KC_DB: postgres, KC_DB_URL: "jdbc:postgresql://postgres:5432/keycloak", KC_HOSTNAME: "https://${DOMAIN}/auth", KC_PROXY_HEADERS: xforwarded, KC_HTTP_ENABLED: "true" }
    volumes: [./keycloak/realm-clinic.json:/opt/keycloak/data/import/realm-clinic.json:ro]
  otel-collector:
    <<: *common
    image: otel/opentelemetry-collector-contrib:0.110.0
    volumes: [./otel/collector.yaml:/etc/otelcol-contrib/config.yaml:ro]
    depends_on: [clickhouse]
  nginx:
    <<: *common
    image: nginx:1.27-alpine
    ports: ["80:80", "443:443"]
    volumes: [./nginx/conf.d:/etc/nginx/conf.d:ro, /etc/letsencrypt:/etc/letsencrypt:ro]
    depends_on: { api: { condition: service_healthy } }
networks: { backend: { internal: false } }
volumes: { pgdata: {} }
secrets: { pg_password: { file: ./secrets/pg_password } }
```

Принципы: БД не публикуется наружу, внутренние сети, лимиты ресурсов, read-only и `cap_drop`, `restart: unless-stopped`, ротация логов, секреты файлами.

## Ansible: фабрика конфигураций

- **inventory** по окружениям, `group_vars/{all,staging,prod}`, секреты в **Ansible Vault**;
- роль `clinic_stack`: шаблоны `.env.j2`, `compose.prod.yaml.j2`, `nginx/*.conf.j2`, `otel/collector.yaml.j2`; `validate:` для конфигов; handlers для `compose up` и `nginx -s reload`;
- роль `common`: пользователи, SSH hardening, `ufw`, `fail2ban`, `unattended-upgrades`, `node_exporter`;
- роль `docker`: Docker Engine, `daemon.json` (`log-opts`, `live-restore`), права;
- **Certbot**: выпуск и автопродление, deploy-hook `nginx -s reload`;
- деплой: `docker login` → `compose pull` → `up -d --wait` → smoke-тест (`uri`) → при неудаче откат на прежний тег; `serial: 1` для нескольких серверов.

## Nginx

- TLS (Let's Encrypt), HTTP→HTTPS, HSTS, заголовки безопасности;
- `/` → SPA (`try_files … /index.html`), кэш ассетов; `/api/` → API (`proxy_pass`, заголовки `X-Forwarded-*`, таймауты, `limit_req`); `/auth/` → Keycloak (увеличенные буферы); `/ws/` → WebSocket (Upgrade);
- внутренние пути (`/metrics`, `/health`) закрыты для внешнего доступа;
- сжатие, HTTP/2; access-лог в JSON с `trace_id`; `otel_trace` для трассировки.

## Keycloak

- realm `clinic`, клиенты: `clinic-web` (public, PKCE), `clinic-api` (bearer), сервисный клиент для воркера; роли `doctor`, `registrar`, `admin`;
- конфигурация — realm JSON (импорт при первом старте), изменения — Terraform provider/keycloak-config-cli;
- БД Keycloak — отдельная база в PostgreSQL, бэкапы;
- за nginx: `KC_PROXY_HEADERS`, `KC_HOSTNAME`, админ-консоль закрыта по IP/VPN;
- API валидирует JWT по JWKS (`iss`, `aud`, `exp`, роли).

## Телеметрия

- .NET: OpenTelemetry SDK (ASP.NET Core, HttpClient, Npgsql, Redis), OTLP → Collector (`otel-collector:4317`); `service.name`, `deployment.environment`, `service.version`;
- Collector: receivers `otlp`, `filelog` (nginx); processors `memory_limiter`, `batch`, `attributes` (удаление чувствительных), `tail_sampling`; exporters `clickhouse` (traces/logs/metrics), при необходимости Prometheus remote write;
- ClickHouse: `otel_traces`, `otel_logs`, TTL 14 дней, пользователь на запись;
- Grafana: дашборды RED по API, запросы к ClickHouse; связь лог ↔ трейс по `trace_id`; алерты (5xx, p95, доступность);
- Prometheus + blackbox для внешней проверки доступности и срока TLS.

## Бэкапы и эксплуатация

- PostgreSQL: `pg_dump`/WAL-G по расписанию (systemd timer) в MinIO/S3, шифрование, ротация; **регулярная проверка восстановления**;
- ClickHouse: `BACKUP` или TTL (данные телеметрии воспроизводимы);
- тома Keycloak/MinIO: бэкапы и репликация;
- runbook'и: недоступность сайта, заполнение диска, падение контейнера, истёкший сертификат, откат релиза;
- мониторинг: узлы (node_exporter), контейнеры (cAdvisor), БД, блэкбокс, SLO API 99.9%.

## Безопасность

- SSH по ключам, фаервол (22/80/443), fail2ban; порты БД закрыты;
- TLS везде; секреты — Ansible Vault/файлы, не в Git; non-root контейнеры, read-only, `cap_drop`;
- сканирование образов (Trivy) и зависимостей в CI; gitleaks;
- CORS отсутствует (единый домен), CSP/HSTS/заголовки; rate limiting на `/auth` и `/api`;
- принцип минимальных прав у БД-пользователей (`migrator` и `app`).

## Что сказать о слабых местах и развитии

- один сервер = SPOF → несколько узлов, репликация PostgreSQL, балансировщик;
- релизы с кратким простоем → blue-green/rolling (Kubernetes);
- ручные ротации секретов → Vault/динамические секреты;
- compose на сервере → **Kubernetes + GitOps** (см. следующую тему);
- мониторинг по SLO и burn rate, DR-план с учениями.

## Вопросы с ответами

> [!question]- Почему выбрали docker compose, а не Kubernetes?
> Небольшое число сервисов, одна команда и одна-две ВМ: compose проще и дешевле в эксплуатации. Kubernetes оправдан при росте числа сервисов, требований к HA, автоскейлу и частым релизам.

> [!question]- Как гарантируется одинаковая конфигурация окружений?
> Ansible генерирует `.env`, compose и nginx из общих шаблонов по inventory; различаются только переменные; применение идемпотентно и проверяется `--check --diff`.

> [!question]- Как проследить запрос от браузера до БД?
> По `trace_id`: Nginx/API/воркеры передают контекст W3C `traceparent`, трассы и логи хранятся в ClickHouse и связаны в Grafana.
