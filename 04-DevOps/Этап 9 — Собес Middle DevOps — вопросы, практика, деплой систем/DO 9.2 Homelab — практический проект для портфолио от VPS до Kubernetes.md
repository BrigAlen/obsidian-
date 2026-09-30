---
type: topic
domain: devops
stage: 9
order: 2
status: todo
level: final
tags: [domain/devops, stage/9, level/final, priority/must]
reviewed: 
next_review: 
priority: must
time: 5
---

# Homelab: практический проект для портфолио от VPS до Kubernetes

↑ [[DO Этап 9 · Собес Middle DevOps — вопросы, практика, деплой систем|Этап 9 · Собес Middle DevOps: вопросы, практика, деплой систем]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~5 мин чтения</span><span class="chip">Уровень: final</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> Личный инфраструктурный проект — лучшее доказательство практического опыта. Показывает инициативу и позволяет рассказать о настоящих проблемах.

## Идея

Собрать собственную инфраструктуру «как в проде», но в малом: от одного VPS до маленького кластера Kubernetes. Каждый этап — отдельная история для собеседования.

**Правила**: всё **в Git** (код инфраструктуры), автоматизация вместо ручных действий, документация (README, схема), мониторинг, бэкапы, безопасность, **повторяемость** (можно снести и поднять заново одной командой).

## Этапы проекта

### Этап 1: VPS + приложение в Docker

- арендовать VPS (Hetzner, Timeweb, Selectel, Yandex Cloud; 2 vCPU/4 ГБ достаточно) или использовать локальную ВМ/мини-ПК/Raspberry Pi;
- **hardening**: пользователь не root, SSH по ключам, отключить пароли, `ufw` (22, 80, 443), `fail2ban`, автообновления безопасности;
- Docker + compose: своё приложение (например, .NET API + Vue SPA + PostgreSQL + Redis);
- **домен** + DNS; **Nginx** reverse proxy; **TLS** через Let's Encrypt (certbot/Caddy/Traefik), HSTS, заголовки безопасности;
- `Makefile` для операций (`make up`, `make logs`, `make backup`, `make deploy`).

### Этап 2: автоматизация (Ansible)

- **роли**: `common` (пользователи, SSH, firewall, unattended-upgrades), `docker`, `nginx`, `app` (шаблоны `.env`, `compose.yaml`, конфиги);
- inventory для нескольких хостов (dev/prod), Ansible Vault для секретов;
- идемпотентность (`--check --diff`, повторный запуск `changed=0`);
- разворачивание «с нуля» одной командой: `ansible-playbook site.yml`.

### Этап 3: CI/CD

- репозиторий в **GitLab** (gitlab.com или self-hosted runner) / GitHub;
- пайплайн: lint → test → build образов → push в Registry → деплой на стенд (SSH + compose или Ansible) → smoke-тест; теги релизов → прод (manual);
- кэш, артефакты, protected variables, environments, откат (предыдущий тег);
- сканирование образов (Trivy) и секретов (gitleaks).

### Этап 4: наблюдаемость

- **Prometheus + Grafana + Alertmanager** (compose/ Helm); node_exporter, cAdvisor, blackbox_exporter (HTTP + срок TLS), postgres_exporter;
- **логи**: Loki + Promtail/Alloy (или ELK/ClickHouse);
- **OpenTelemetry**: инструментирование приложения + Collector → Tempo/ClickHouse; корреляция лог ↔ трейс;
- дашборды (RED, USE), алерты (Telegram), **SLO** для основного сервиса;
- Uptime-проверки снаружи.

### Этап 5: надёжность и безопасность

- **бэкапы**: `pg_dump`/WAL-G в объектное хранилище (MinIO/S3) по расписанию, **проверка восстановления** (скрипт + отчёт);
- **Keycloak** для аутентификации (OIDC) + PKCE в SPA;
- секреты: SOPS/Ansible Vault/Vault; сеть: внутренние сети Docker, закрытые порты БД;
- Runbook'и для типовых инцидентов; **учения** (сломать БД, диск, сертификат — и восстановить).

### Этап 6: Kubernetes

- **k3s** на одном-трёх узлах (VPS или ВМ) либо kind/minikube локально;
- Helm-чарты для сервисов, Ingress-NGINX + cert-manager, ConfigMap/Secret, probes, ресурсы, HPA;
- мониторинг кластера (kube-prometheus-stack), логи (Loki), NetworkPolicy;
- **GitOps**: ArgoCD или Flux: репозиторий конфигурации окружений, автосинхронизация, откат через Git;
- хранилище (local-path/Longhorn), бэкапы (Velero), миграция из compose (см. отдельную тему).

### Этап 7: IaC и облако

- **Terraform**: создание VPS/сети/DNS/бакетов у провайдера (Yandex Cloud/Hetzner), remote state;
- Packer/cloud-init для образов; автоматическое создание окружения с нуля (**terraform apply → ansible → gitops sync**);
- отдельные окружения (staging/prod) на одном коде.

### Этап 8: дополнительно

- **Vault** (или облачный менеджер) для динамических секретов, **Trivy Operator**/Kyverno, **Chaos** (Chaos Mesh), нагрузочное тестирование (k6), FinOps-отчёт (стоимость стенда), **Backstage-lite** (каталог и шаблон сервиса), ClickHouse для аналитики.

## Пример структуры репозитория

```text
homelab/
  README.md                      # схема архитектуры, как запустить, решения и компромиссы
  docs/{architecture.md,runbooks/*.md,adr/*.md,postmortems/*.md}
  terraform/{modules,envs/{staging,prod}}
  ansible/{inventories,roles,playbooks}
  apps/clinic/{src,Dockerfile,compose.yaml,helm-chart/}
  gitops/{clusters,infra,apps}
  monitoring/{prometheus,grafana/dashboards,alerts,otel-collector}
  .gitlab-ci.yml
  Makefile
```

## Как использовать в собеседовании

- **Схема** архитектуры (одна картинка) и **ссылка на репозиторий**;
- **3–4 истории** со структурой STAR: «диск заполнился логами → нашёл → ротация, лимиты, алерты», «ошибка TLS → ... → автоматизация продления и мониторинг срока», «деплой ломал прод → blue/green/ откат → `--wait` и smoke», «Prometheus съел память → кардинальность меток → relabel»;
- **Метрики**: время развёртывания с нуля (был 2 часа → 7 минут), время деплоя, покрытие алертами, стоимость в месяц;
- **Решения и компромиссы**: почему compose, а не Kubernetes (и когда перешёл), почему Loki, а не ELK;
- **Что бы улучшил**: честный список (HA, multi-node, DR).

## Стоимость и безопасность проекта

- дёшево: VPS 500–1500 ₽/мес, домен; бесплатные тарифы облаков; локальные ВМ (Proxmox, VirtualBox, Multipass), старый ПК/mini-PC;
- **не публиковать секреты** (ключи, `.env`, state) в открытом репозитории: `.gitignore`, gitleaks, SOPS; публичный репозиторий — без реальных доменов/IP по необходимости;
- не оставлять открытыми админ-интерфейсы; регулярно обновлять; ограничивать расходы в облаке (бюджеты, алерты, удаление ресурсов).

## Идеи приложений для homelab

Блог/Wiki (Wiki.js), Nextcloud, Gitea/GitLab CE, Vaultwarden, Immich, Home Assistant, свой сервис (API записи на приём «Clinic», трекер задач), мониторинг-стек как продукт, Keycloak + приложения SSO. Лучше — **своё приложение с реальной архитектурой** (API + SPA + БД + очередь + авторизация).

## Вопросы с ответами

> [!question]- Как рассказать о homelab на собеседовании?
> Показать схему и репозиторий, описать стек и причины выбора, рассказать 3–4 инцидента или улучшения в формате проблема → диагностика → решение → результат и назвать метрики (время деплоя, развёртывания с нуля).

> [!question]- Что должно быть «обязательно» в таком проекте?
> Автоматизация (IaC, CI/CD), TLS и базовая безопасность, мониторинг с алертами, бэкапы с проверкой восстановления и документация — именно это отличает проект от «запустил контейнер».

> [!question]- Нужен ли Kubernetes в домашней лаборатории?
> Для портфолио — желательно (k3s), но начинать лучше с compose и Ansible, а переход на Kubernetes описывать как эволюцию с осознанными причинами.
