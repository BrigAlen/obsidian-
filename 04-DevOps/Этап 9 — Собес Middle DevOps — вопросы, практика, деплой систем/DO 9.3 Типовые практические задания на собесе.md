---
type: topic
domain: devops
stage: 9
order: 3
status: todo
level: final
tags: [domain/devops, stage/9, level/final, priority/must]
reviewed: 
next_review: 
priority: must
time: 11
---

# Типовые практические задания на собесе

↑ [[DO Этап 9 · Собес Middle DevOps — вопросы, практика, деплой систем|Этап 9 · Собес Middle DevOps: вопросы, практика, деплой систем]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~11 мин чтения</span><span class="chip">Уровень: final</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> Практическая часть интервью: нужно быстро и осмысленно написать конфиг или скрипт и объяснить каждую строку.

## Как подходить

1. **Уточнить требования** (окружение, нагрузка, безопасность, откат).
2. **Проговаривать** решение.
3. **Сначала работающий минимум**, потом улучшения (безопасность, наблюдаемость, идемпотентность).
4. **Проверка**: как убедиться, что работает; как откатить.
5. Указывать **компромиссы** и что сделали бы дальше.

## Задание: Dockerfile для .NET API

Требования: небольшой образ, не root, кэш зависимостей, healthcheck.

```dockerfile
# syntax=docker/dockerfile:1.7
FROM mcr.microsoft.com/dotnet/sdk:9.0 AS build
WORKDIR /src
COPY src/Api/Api.csproj src/Api/
RUN dotnet restore src/Api/Api.csproj
COPY . .
RUN dotnet publish src/Api/Api.csproj -c Release -o /app --no-restore /p:UseAppHost=false

FROM mcr.microsoft.com/dotnet/aspnet:9.0-noble-chiseled
WORKDIR /app
COPY --from=build /app .
ENV ASPNETCORE_HTTP_PORTS=8080
EXPOSE 8080
USER $APP_UID
ENTRYPOINT ["dotnet", "Api.dll"]
```

Пояснить: multi-stage (размер), порядок слоёв (кэш restore), chiseled (без shell, не root), `ASPNETCORE_HTTP_PORTS`, зависимость healthcheck (в chiseled нет curl → проверка снаружи/в оркестраторе).

## Задание: docker-compose с БД и миграциями

```yaml
services:
  db:
    image: postgres:17
    environment: { POSTGRES_PASSWORD_FILE: /run/secrets/pg_pass, POSTGRES_DB: app }
    secrets: [pg_pass]
    volumes: [pgdata:/var/lib/postgresql/data]
    healthcheck: { test: ["CMD-SHELL", "pg_isready -U postgres -d app"], interval: 5s, retries: 10 }
  migrate:
    image: app-migrator:${TAG}
    depends_on: { db: { condition: service_healthy } }
  api:
    image: app-api:${TAG}
    depends_on: { migrate: { condition: service_completed_successfully } }
    ports: ["127.0.0.1:8080:8080"]
    restart: unless-stopped
volumes: { pgdata: {} }
secrets: { pg_pass: { file: ./secrets/pg_pass } }
```

## Задание: .gitlab-ci.yml

Сборка, тесты, образ, деплой на стенд с ручным подтверждением на прод.

```yaml
stages: [test, build, deploy]
test:
  stage: test
  image: mcr.microsoft.com/dotnet/sdk:9.0
  script: [dotnet test -c Release]
build:
  stage: build
  image: docker:27
  services: [docker:27-dind]
  script:
    - echo "$CI_REGISTRY_PASSWORD" | docker login -u "$CI_REGISTRY_USER" --password-stdin "$CI_REGISTRY"
    - docker build -t $CI_REGISTRY_IMAGE:$CI_COMMIT_SHORT_SHA .
    - docker push $CI_REGISTRY_IMAGE:$CI_COMMIT_SHORT_SHA
  rules: [{ if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH }]
deploy-staging:
  stage: deploy
  environment: staging
  script: [./deploy.sh staging $CI_COMMIT_SHORT_SHA]
  rules: [{ if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH }]
deploy-prod:
  stage: deploy
  environment: production
  script: [./deploy.sh production $CI_COMMIT_SHORT_SHA]
  when: manual
  rules: [{ if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH }]
```

Расширения: кэш, `needs`, артефакты, сканирование Trivy, protected variables, откат.

## Задание: Nginx reverse proxy + SPA + TLS

```nginx
server { listen 80; server_name app.example.com; location /.well-known/acme-challenge/ { root /var/www/certbot; } location / { return 301 https://$host$request_uri; } }
server {
  listen 443 ssl; http2 on; server_name app.example.com;
  ssl_certificate /etc/letsencrypt/live/app.example.com/fullchain.pem;
  ssl_certificate_key /etc/letsencrypt/live/app.example.com/privkey.pem;
  add_header Strict-Transport-Security "max-age=31536000" always;
  location /api/ { proxy_pass http://api:8080/; proxy_set_header Host $host; proxy_set_header X-Forwarded-Proto $scheme; proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for; }
  location / { root /usr/share/nginx/html; try_files $uri /index.html; }
}
```

## Задание: Ansible playbook

Установить Docker, создать пользователя, развернуть стек из шаблона.

```yaml
- hosts: app
  become: true
  tasks:
    - name: Пользователь deploy
      ansible.builtin.user: { name: deploy, groups: docker, append: true, shell: /bin/bash }
    - name: Docker
      ansible.builtin.apt: { name: [docker.io, docker-compose-v2], state: present, update_cache: true }
    - name: Каталог
      ansible.builtin.file: { path: /opt/app, state: directory, owner: deploy, mode: "0755" }
    - name: compose.yaml
      ansible.builtin.template: { src: compose.yaml.j2, dest: /opt/app/compose.yaml, owner: deploy, mode: "0644" }
      notify: up
  handlers:
    - name: up
      community.docker.docker_compose_v2: { project_src: /opt/app, state: present, pull: always }
```

## Задание: Bash-скрипт

Бэкап БД с ротацией (см. тему про Bash): `set -euo pipefail`, `mktemp`, `trap`, `find -mtime`, проверки параметров, коды возврата.

## Задание: Kubernetes манифест

Deployment + Service + Ingress для приложения с probes и ресурсами (см. темы Kubernetes), HPA, ConfigMap/Secret.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata: { name: api }
spec:
  replicas: 3
  selector: { matchLabels: { app: api } }
  strategy: { rollingUpdate: { maxSurge: 1, maxUnavailable: 0 } }
  template:
    metadata: { labels: { app: api } }
    spec:
      containers:
        - name: app
          image: registry/api:1.0.0
          ports: [{ containerPort: 8080 }]
          resources: { requests: { cpu: 200m, memory: 256Mi }, limits: { memory: 512Mi } }
          readinessProbe: { httpGet: { path: /health/ready, port: 8080 } }
          livenessProbe:  { httpGet: { path: /health/live,  port: 8080 }, initialDelaySeconds: 15 }
          securityContext: { runAsNonRoot: true, allowPrivilegeEscalation: false, readOnlyRootFilesystem: true, capabilities: { drop: [ALL] } }
```

## Задание: Terraform

Создать сеть, подсеть и ВМ в облаке, вывести IP; state в удалённом backend; переменные; модуль.

## Задание: PromQL и алерт

- доля 5xx за 5 минут: `sum(rate(http_requests_total{status=~"5.."}[5m])) / sum(rate(http_requests_total[5m]))`;
- p95: `histogram_quantile(0.95, sum by (le)(rate(http_request_duration_seconds_bucket[5m])))`;
- алерт: заполнение диска за сутки: `predict_linear(node_filesystem_avail_bytes[6h], 24*3600) < 0` для 30 минут.

## Задание: разбор логов

Найти топ IP по 5xx, время ответов, количество запросов по статусам:

```bash
awk '$9 ~ /^5/ {print $1}' access.log | sort | uniq -c | sort -rn | head
awk '{print $9}' access.log | sort | uniq -c | sort -rn
awk '{sum+=$NF; n++} END {print sum/n}' access.log        # среднее время (если последнее поле — request_time)
grep -c "upstream timed out" error.log
```

## Задание: сеть

Вычислить подсети (`/26`), объяснить NAT, диагностика недоступности порта (`nc -vz`, `ss`, `tcpdump`), настроить `ufw` для веб-сервера.

## Задание: проектирование

- «Разверните сервис с БД в продакшне на одном сервере»: Docker compose + Nginx + TLS + бэкапы + мониторинг + hardening;
- «Как организовать деплой без простоя»: rolling/blue-green, миграции expand/contract, health checks;
- «Как организовать секреты»: Vault/SOPS/CI variables, ротация, минимальные права.

## Что оценивают в практике

| Критерий | Признаки |
|---|---|
| Корректность | конфиг работает, синтаксис верный |
| Безопасность | non-root, секреты вне кода, минимальные порты/права |
| Надёжность | healthcheck, restart policy, откат, идемпотентность |
| Читаемость | структура, комментарии по делу |
| Понимание | объяснение «почему» |
| Автоматизация | мыслит «скриптом», а не «руками» |
| Наблюдаемость | логи, метрики, проверки |

## Вопросы с ответами

> [!question]- Что делать, если не помните синтаксис?
> Сказать об этом, описать идею и структуру решения, использовать документацию/`--help` (обычно разрешено) и объяснить, как проверите результат.

> [!question]- Как сделать практическое решение «продовым»?
> Добавить безопасность (non-root, секреты, TLS), healthchecks и restart policy, логи и метрики, идемпотентность, автоматическую проверку и план отката.

> [!question]- Что делать при зависании в задаче?
> Проговаривать рассуждения, упростить до минимального работающего варианта, задавать уточняющие вопросы; молчание — худшая стратегия.
