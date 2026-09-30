---
type: topic
domain: devops
stage: 9
order: 10
status: todo
level: final
tags: [domain/devops, stage/9, level/final, priority/must]
reviewed: 
next_review: 
priority: must
time: 5
---

# Чек-лист готовности к Middle DevOps и план финального повторения

↑ [[DO Этап 9 · Собес Middle DevOps — вопросы, практика, деплой систем|Этап 9 · Собес Middle DevOps: вопросы, практика, деплой систем]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~5 мин чтения</span><span class="chip">Уровень: final</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> Перед интервью — проверить пробелы и распланировать повторение. Отмечайте только то, что можете объяснить вслух без подсказок.

## Linux и сети

- [ ] Файловая система, права, sudo/capabilities, пользователи и группы;
- [ ] процессы, сигналы, systemd (unit, журнал, отладка), cron и timers;
- [ ] диагностика ресурсов: load average, память/swap/OOM, диск, inode, I/O;
- [ ] Bash (кавычки, пайпы, `set -euo pipefail`, trap), grep/sed/awk/find/jq/curl;
- [ ] OSI/TCP-IP, TCP-рукопожатие, состояния сокетов, UDP;
- [ ] IP, CIDR, подсети, NAT, маршруты, порты;
- [ ] DNS (записи, резолвинг, TTL, `dig`), firewall (iptables/nftables/ufw), SSH (ключи, туннели, hardening);
- [ ] диагностика сети: ping, mtr, nc, curl, tcpdump, ss.

## Контейнеры

- [ ] namespaces/cgroups, отличие от ВМ; OCI, containerd, runc, Podman;
- [ ] слои, кэш сборки, Dockerfile (ENTRYPOINT/CMD, ARG/ENV, exec-форма), multi-stage, оптимизация образов, non-root;
- [ ] сети и volumes, compose (depends_on+healthcheck, profiles, env), compose в проде;
- [ ] registry и теги, безопасность контейнеров, жизненный цикл (PID 1, SIGTERM, graceful shutdown);
- [ ] отладка: logs, exec, inspect, stats, коды выхода (137/143).

## CI/CD

- [ ] CI vs CD (Delivery/Deployment), стадии, артефакты, build once deploy many;
- [ ] GitLab CI: stages, jobs, rules, needs, cache/artifacts, runners, variables (masked/protected), environments;
- [ ] версионирование (SemVer), теги, Nexus/Harbor;
- [ ] качество в пайплайне (тесты, линтеры, SonarQube, quality gates), DevSecOps (SAST/SCA/Trivy, SBOM, подписи);
- [ ] секреты и окружения, миграции БД в CD;
- [ ] стратегии деплоя (rolling, blue-green, canary, feature flags), откат; метрики DORA.

## Nginx и сеть в проде

- [ ] server/location (порядок выбора), upstream, `proxy_pass` и слеш, заголовки `X-Forwarded-*`;
- [ ] раздача SPA (history fallback, кэш, сжатие), TLS (Let's Encrypt, certbot, HSTS);
- [ ] L4/L7 балансировка, CDN; HTTP/1.1-2-3, keep-alive, таймауты, буферы;
- [ ] WebSocket/SSE/gRPC через nginx; безопасность edge (headers, rate limiting, WAF);
- [ ] диагностика 4xx/5xx, reload без простоя; OTel-трассировка nginx.

## Kubernetes

- [ ] архитектура (control plane, etcd, kubelet), Pod/ReplicaSet/Deployment, rolling update и откат;
- [ ] Service (типы), Ingress, DNS, cert-manager, NetworkPolicy;
- [ ] ConfigMap/Secret/Namespace; probes; requests/limits, HPA; StatefulSet, PV/PVC, Jobs/CronJobs;
- [ ] Helm и Kustomize; RBAC и ServiceAccount; отладка (describe/logs/events/debug);
- [ ] эксплуатация: drain, PDB, affinity, taints; безопасность workloads (securityContext, PSS, политики);
- [ ] observability кластера (metrics-server, kube-state-metrics, Prometheus, логи, аудит); etcd backup.

## IaC и облака

- [ ] принципы IaC: декларативность, идемпотентность, immutable, drift;
- [ ] Ansible: inventory, playbooks, roles, handlers, Jinja2, Vault; генерация конфигураций;
- [ ] Terraform: providers, resources, state, modules, plan/apply; remote state, блокировки, окружения, drift, CI;
- [ ] облака: IaaS/PaaS/SaaS, VPC, подсети, SG, VM, S3, IAM, стоимость.

## Observability и эксплуатация

- [ ] Prometheus (pull, типы метрик, PromQL, кардинальность), экспортеры, Grafana;
- [ ] логи (структурированные, Loki/ELK), OpenTelemetry Collector;
- [ ] SLI/SLO/SLA, error budget, burn rate; алертинг (Alertmanager, шум);
- [ ] инциденты: on-call, runbook, blameless постмортем.

## Senior-блок (для Middle+)

- [ ] HA, SPOF, расчёт доступности, паттерны устойчивости;
- [ ] Trivy/supply chain, Vault/секреты, GitOps (ArgoCD/Flux);
- [ ] DR (RPO/RTO, стратегии), capacity planning, FinOps;
- [ ] platform engineering, chaos engineering.

## Практика и проекты

- [ ] есть рабочий проект (homelab) и схема архитектуры;
- [ ] 4–6 историй STAR с метриками;
- [ ] рассказ о своём опыте (2–3 мин) и о проекте (10 мин);
- [ ] решены типовые практические задания (Dockerfile, compose, `.gitlab-ci.yml`, nginx, Ansible, K8s манифест, PromQL);
- [ ] отработаны сценарии: «сайт не открывается», «диск заполнен», «контейнер падает», «502/504», «сертификат истёк», «под в CrashLoopBackOff»;
- [ ] проектирование: CI/CD, деплой без простоя, мониторинг, миграция в Kubernetes.

## План финального повторения (7–10 дней)

| День | Фокус |
|---|---|
| 1 | Linux, процессы, диагностика, Bash; сети, DNS, TLS |
| 2 | Docker, образы, compose; отладка контейнеров |
| 3 | CI/CD: GitLab CI, стратегии деплоя, DevSecOps |
| 4 | Nginx, reverse proxy, TLS, балансировка, диагностика 502/504 |
| 5 | Kubernetes: объекты, probes, ресурсы, сеть, отладка |
| 6 | Ansible/Terraform, облака; IaC-практика |
| 7 | Наблюдаемость: Prometheus, логи, OTel, SLO, алерты, инциденты |
| 8 | Сценарии troubleshooting вслух; практические задания |
| 9 | Рассказ об опыте, STAR-истории, проектирование |
| 10 | Mock-интервью, слабые места, отдых |

## Приёмы подготовки

- **объясняйте вслух** (как будто новичку), записывайте на диктофон;
- **mock-интервью** с коллегой/ИИ; задавайте себе вопросы из разделов с ответами в этом хранилище;
- **повторение интервалами** (шаги 1–3–7–14 дней), возврат к слабым темам;
- **делайте руками**: поднимите стенд, сломайте и почините (диск, сертификат, под, миграцию);
- **читайте публичные постмортемы** (Cloudflare, GitHub, AWS) и разбирайте причины;
- **следите за формулировками**: «что сделал я», метрики, компромиссы.

## Организационно

- [ ] резюме и проекты актуальны, ссылки работают;
- [ ] вопросы работодателю подготовлены (процессы, стек, on-call, зрелость);
- [ ] техника: камера, микрофон, доступ к терминалу/документации;
- [ ] отдых накануне; готовность честно сказать «не знаю, но вот как разберусь».

## Вопросы с ответами

> [!question]- Что делать, если по части тем большие пробелы?
> Приоритизировать по частоте вопросов и вакансии (Linux, Docker, CI/CD, nginx, Kubernetes, мониторинг), закрыть практикой на стенде, а по остальным подготовить честный ответ о понимании принципов и плане изучения.

> [!question]- Как оценить готовность?
> Если можете за 2 минуты объяснить тему без подсказок и воспроизвести типовую практику (конфиг/команду) и диагностический сценарий — тема закрыта.

> [!question]- Что самое важное в последний день?
> Повторить сценарии troubleshooting и истории STAR вслух, проверить технику и выспаться.
