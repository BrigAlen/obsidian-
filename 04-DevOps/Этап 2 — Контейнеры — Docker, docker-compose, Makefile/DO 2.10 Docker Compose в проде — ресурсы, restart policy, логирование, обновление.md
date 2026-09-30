---
type: topic
domain: devops
stage: 2
order: 10
status: todo
level: junior
tags: [domain/devops, stage/2, level/junior, priority/must]
reviewed: 
next_review: 
priority: must
time: 6
---

# Docker Compose в проде: ресурсы, restart policy, логирование, обновление

↑ [[DO Этап 2 · Контейнеры — Docker, docker-compose, Makefile|Этап 2 · Контейнеры: Docker, docker-compose, Makefile]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~6 мин чтения</span><span class="chip">Уровень: junior</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> Compose часто используют на одном сервере в проде. Нужно знать ограничения и как сделать запуск надёжным и обновляемым.

## Когда Compose допустим в проде

Один сервер/ВМ, небольшой сервис, нет требований к автомасштабированию и мультихост-оркестрации. Ограничения: нет встроенного самовосстановления при падении хоста, нет rolling-обновлений «из коробки», нет распределения по нодам — всё на одном хосте (единая точка отказа). При росте требований — Kubernetes/Nomad/Swarm.

## Ресурсы

```yaml
services:
  api:
    deploy:
      resources:
        limits:   { cpus: "1.5", memory: 768M }
        reservations: { cpus: "0.5", memory: 256M }
    mem_swappiness: 0
    pids_limit: 512
    ulimits: { nofile: { soft: 65535, hard: 65535 } }
```

- лимит памяти → OOM kill при превышении; без лимитов один сервис может «съесть» хост;
- лимит CPU — троттлинг;
- подбор по метрикам (`docker stats`, Prometheus + cAdvisor).

## Restart policy

| Значение | Поведение |
|---|---|
| `no` | не перезапускать |
| `on-failure[:N]` | при ненулевом коде выхода (до N раз) |
| `always` | всегда, в том числе после перезагрузки Docker |
| `unless-stopped` | как always, кроме явной остановки вручную (**типовой выбор для продакшна**) |

Restart policy перезапускает контейнер при падении **процесса**, но не при зависании: нужен **healthcheck** + внешний механизм (autoheal, оркестратор). Для автозапуска после перезагрузки сервера Docker должен быть включён в systemd (`systemctl enable docker`). Цикл быстрых рестартов («crash loop») с backoff — исправлять причину.

## Healthcheck

```yaml
healthcheck:
  test: ["CMD", "curl", "-fsS", "http://localhost:8080/health/ready"]
  interval: 15s
  timeout: 3s
  retries: 3
  start_period: 30s
```

`start_period` — льготный период запуска. Compose не перезапускает unhealthy контейнер сам (это делают оркестраторы; можно добавить `willfarrell/autoheal`).

## Логирование

```yaml
logging:
  driver: json-file
  options: { max-size: "50m", max-file: "5", compress: "true" }
```

Без лимитов файл логов растёт бесконечно. Для централизации: драйверы `loki`, `fluentd`, `gelf`, `syslog` или агент (Promtail/Vector/OTel Collector), читающий логи контейнеров.

## Обновление (деплой) без лишнего простоя

Базовый:

```bash
docker compose pull
docker compose up -d --remove-orphans          # пересоздаст контейнеры с изменившимися образами
docker image prune -f
```

Минусы: краткая недоступность (контейнер пересоздаётся), нет автоматического отката.

Улучшения:

- **`--wait`**: ждать healthy; если нет — скрипт откатывает на предыдущий тег;
- **версионированные теги** (`TAG=1.4.3`): откат — возврат `TAG` и `up -d`;
- **blue-green/rolling вручную**: поднять вторую копию (`--scale api=2` без фиксированных портов за reverse proxy), дождаться healthy, убрать старую; инструмент **docker-rollout**;
- **reverse proxy** (nginx/Traefik/Caddy) с динамическим обнаружением сервисов;
- **миграции БД** отдельным сервисом/шагом до запуска новой версии (обратно совместимые);
- **`stop_grace_period`** и корректная обработка SIGTERM (graceful shutdown), иначе обрываются запросы;
- **бэкап** перед обновлением, проверка smoke-тестом после.

```bash
#!/usr/bin/env bash
set -euo pipefail
export TAG=${1:?usage: deploy.sh <tag>}
prev=$(cat .current_tag 2>/dev/null || true)
docker compose pull
if docker compose up -d --wait --remove-orphans && curl -fsS https://app.example.com/health; then
  echo "$TAG" > .current_tag
else
  echo "Деплой неуспешен, откат на $prev" >&2
  TAG=$prev docker compose up -d --wait
  exit 1
fi
```

## Безопасность в проде

- не публиковать порты БД/кэшей; внутренние сети (`internal: true`);
- секреты через `secrets:`/внешние хранилища, не в репозитории;
- `read_only: true`, `cap_drop: [ALL]`, `no-new-privileges`, non-root;
- фиксированные версии образов, сканирование;
- Docker socket не монтировать в приложения;
- TLS: reverse proxy (Caddy/Traefik/nginx + certbot);
- обновления хоста и Docker; firewall (учитывать обход ufw).

## Мониторинг и эксплуатация

- cAdvisor + node_exporter + Prometheus + Grafana; алерты на перезапуски, OOM, unhealthy, заполнение диска;
- регулярная очистка: `docker system prune`, логи, старые образы;
- бэкапы томов и БД;
- `docker compose config` как артефакт деплоя; инфраструктура в репозитории (Ansible раскатывает файлы и запускает `compose up`);
- автоматизация через CI/CD (SSH или runner на сервере), GitOps-подход: Watchtower/Renovate с осторожностью (автообновление без тестов опасно).

## Когда переходить на Kubernetes

Нужны: несколько хостов и отказоустойчивость, автомасштабирование, rolling/canary, декларативные секреты/конфиги, политики безопасности, множество сервисов и команд.

## Вопросы с ответами

> [!question]- Какая restart policy подходит для продакшна?
> `unless-stopped` (или `always`): контейнер поднимается после падения и перезагрузки хоста, но не запускается, если его намеренно остановили.

> [!question]- Как обновить сервисы в Compose с откатом?
> Версионированные теги образов, `pull` + `up -d --wait`, проверка здоровья и smoke-тест; при неуспехе — возврат на прежний тег; миграции БД обратно совместимы.

> [!question]- Почему важно ограничивать логи и ресурсы контейнеров?
> Без лимитов логи заполняют диск, а один сервис может исчерпать память/CPU хоста и повлиять на все остальные.
