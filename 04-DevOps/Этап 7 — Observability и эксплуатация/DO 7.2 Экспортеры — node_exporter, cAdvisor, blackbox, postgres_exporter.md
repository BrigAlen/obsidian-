---
type: topic
domain: devops
stage: 7
order: 2
status: todo
level: middle+
tags: [domain/devops, stage/7, level/middle+, priority/should]
reviewed: 
next_review: 
priority: should
time: 6
---

# Экспортеры: node_exporter, cAdvisor, blackbox, postgres_exporter

↑ [[DO Этап 7 · Observability и эксплуатация|Этап 7 · Observability и эксплуатация]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~6 мин чтения</span><span class="chip">Уровень: middle+</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> Экспортеры превращают состояние ОС, контейнеров и сервисов в метрики Prometheus. Нужно знать, какие использовать и как их безопасно развёртывать.

## Зачем

Не все системы отдают `/metrics`. **Экспортер** — промежуточный процесс: читает состояние (ОС, БД, очередь) и публикует в формате Prometheus. Принцип: метрики ближе к источнику; один экспортер на компонент.

## node_exporter (ОС хоста)

CPU, память, диски, файловые системы, сеть, нагрузка, `systemd`, температура, `textfile`.

```bash
docker run -d --name node-exporter --net host --pid host -v /:/host:ro,rslave prom/node-exporter --path.rootfs=/host
# или systemd-сервис/пакет; порт 9100
```

Ключевые метрики и запросы:

```promql
1 - avg by (instance) (rate(node_cpu_seconds_total{mode="idle"}[5m]))                          # загрузка CPU
1 - node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes                                 # использование памяти
node_load1 / count by (instance) (node_cpu_seconds_total{mode="idle"})                          # load на ядро
100 - node_filesystem_avail_bytes{fstype!~"tmpfs|overlay"} / node_filesystem_size_bytes * 100   # заполнение диска
predict_linear(node_filesystem_avail_bytes[6h], 24*3600) < 0                                    # закончится ли диск за сутки
rate(node_disk_io_time_seconds_total[5m])                                                       # насыщение диска (%util)
rate(node_network_receive_errors_total[5m])
node_systemd_unit_state{name="nginx.service",state="active"}
increase(node_vmstat_oom_kill[1h]) > 0                                                          # OOM на хосте
```

**textfile collector**: скрипты пишут метрики в `*.prom` (например, время последнего бэкапа, статус cron-задачи) — удобно для batch: `backup_last_success_timestamp_seconds`.

## cAdvisor (контейнеры)

Метрики контейнеров Docker/K8s: CPU, память (working set), сеть, диск, троттлинг. В Kubernetes встроен в kubelet (`/metrics/cadvisor`); для Docker — контейнер `gcr.io/cadvisor/cadvisor` (порт 8080).

```promql
sum by (name) (rate(container_cpu_usage_seconds_total{name!=""}[5m]))
container_memory_working_set_bytes{name="api"}
rate(container_cpu_cfs_throttled_periods_total[5m]) / rate(container_cpu_cfs_periods_total[5m])    # троттлинг
increase(container_oom_events_total[1h])
time() - container_start_time_seconds                                                              # аптайм, рестарты
```

Метрика `container_memory_working_set_bytes` — то, по чему OOM killer принимает решения (а не `usage`). Высокая кардинальность по `id`/`image` — фильтровать.

## blackbox_exporter (проверки снаружи)

Зондирование endpoint'ов: **HTTP(S), TCP, ICMP, DNS, gRPC** — «виден ли сервис пользователю»: доступность, код ответа, время, **срок действия TLS-сертификата**.

```yaml
# blackbox.yml
modules:
  http_2xx: { prober: http, timeout: 10s, http: { valid_status_codes: [], method: GET, follow_redirects: true, fail_if_not_ssl: true } }
  tcp_connect: { prober: tcp, timeout: 5s }
  icmp: { prober: icmp }
```

```yaml
# prometheus.yml
- job_name: blackbox-http
  metrics_path: /probe
  params: { module: [http_2xx] }
  static_configs: [{ targets: ["https://app.example.com", "https://api.example.com/health"] }]
  relabel_configs:
    - { source_labels: [__address__], target_label: __param_target }
    - { source_labels: [__param_target], target_label: instance }
    - { target_label: __address__, replacement: blackbox-exporter:9115 }
```

```promql
probe_success == 0                                          # недоступно
probe_http_status_code != 200
probe_duration_seconds > 2
(probe_ssl_earliest_cert_expiry - time()) / 86400 < 14       # сертификат истекает менее чем через 14 дней
```

Зондируйте **с разных точек** (внешние локации) и через публичный путь (DNS, CDN, LB) — это «то, что видит пользователь».

## postgres_exporter (БД)

Метрики PostgreSQL: соединения, транзакции, блокировки, репликация, размеры, cache hit, `pg_stat_*`, кастомные запросы.

```bash
DATA_SOURCE_NAME="postgresql://monitoring:***@db:5432/postgres?sslmode=require"
docker run -d -e DATA_SOURCE_NAME prometheuscommunity/postgres-exporter     # порт 9187
```

Пользователь с ролью `pg_monitor` (минимальные права).

```promql
pg_up == 0
sum(pg_stat_activity_count) by (datname, state); pg_settings_max_connections
pg_stat_database_xact_rollback / (pg_stat_database_xact_commit + pg_stat_database_xact_rollback)
pg_replication_lag_seconds; pg_stat_replication_replay_lag
rate(pg_stat_database_deadlocks[5m])
pg_stat_database_blks_hit / (pg_stat_database_blks_hit + pg_stat_database_blks_read)
pg_database_size_bytes
```

Другие экспортеры БД и систем: **redis_exporter**, **mysqld_exporter**, **mongodb_exporter**, **kafka_exporter / JMX**, **rabbitmq** (встроенный плагин Prometheus), **elasticsearch_exporter**, **nginx-prometheus-exporter** / **nginx vts**, **haproxy** (встроен), **ClickHouse** (встроенный `/metrics`), **MinIO** (`/minio/v2/metrics/cluster`), **snmp_exporter**, **windows_exporter**, **process-exporter**, **statsd_exporter**, **ipmi_exporter**, **smartctl_exporter** (здоровье дисков), **Keycloak** (метрики), **cloudwatch_exporter / yet-another-cloudwatch-exporter**.

## Развёртывание и безопасность экспортеров

- запуск под отдельным непривилегированным пользователем; минимальные права (например, `pg_monitor`, read-only);
- **не выставлять порты экспортеров в интернет**: firewall/NetworkPolicy, слушать внутренний интерфейс, при необходимости TLS и basic auth (`--web.config.file`);
- автоматизация установки (Ansible, Helm-чарты, `prometheus-community/*`), закрепление версий;
- sidecar-экспортеры в Kubernetes (Redis/Postgres) или центральные с обнаружением;
- **Service Discovery** вместо статических списков;
- ограничение кардинальности (`--collector.disable-defaults`, `--collector.*`), `metric_relabel_configs`;
- мониторинг самих экспортеров (`up`, `scrape_duration_seconds`).

## Написание своего экспортера

Когда нет готового: библиотеки `prometheus_client` (Python), `prometheus-net` (.NET), Go client; формат text exposition:

```text
# HELP backup_last_success_timestamp_seconds Время последнего успешного бэкапа
# TYPE backup_last_success_timestamp_seconds gauge
backup_last_success_timestamp_seconds{job="pg"} 1.7275e+09
```

Практика: `Collector` интерфейс (сбор при scrape, а не фоновое обновление), кэширование тяжёлых запросов, таймауты, метрика `*_up` и `*_scrape_duration_seconds`.

## Вопросы с ответами

> [!question]- Зачем blackbox_exporter, если есть метрики приложения?
> Он проверяет доступность и корректность сервиса **снаружи**, как пользователь (через DNS, балансировщик, TLS): выявляет проблемы, которых не видно изнутри, и следит за сроком сертификатов.

> [!question]- Какая метрика памяти контейнера важна для OOM?
> `container_memory_working_set_bytes` — именно по ней ядро/kubelet принимают решения об OOM и вытеснении.

> [!question]- Как безопасно развернуть экспортеры?
> Непривилегированный пользователь и минимальные права, закрытые от внешнего доступа порты (firewall, NetworkPolicy), при необходимости TLS/basic auth, автоматизация и закрепление версий.
