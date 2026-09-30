---
type: topic
domain: devops
stage: 6
order: 3
status: todo
level: middle
tags: [domain/devops, stage/6, level/middle, priority/nice]
reviewed: 
next_review: 
priority: nice
time: 12
---

# Ansible как фабрика конфигураций: генерация .env, compose и nginx

↑ [[DO Этап 6 · Infrastructure as Code — Ansible, Terraform|Этап 6 · Infrastructure as Code: Ansible, Terraform]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge nice">По желанию</span><span class="chip">~12 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> Практический приём: Ansible как генератор конфигураций и деплой-инструмент для систем на docker compose.

## Идея

Единый **источник параметров** (inventory + group_vars) и набор **шаблонов** Jinja2. Ansible формирует для каждого окружения/хоста готовые файлы (`.env`, `compose.yaml`, `nginx.conf`, конфиги приложений), раскладывает их на серверах и запускает сервисы. Так конфигурация окружений — **код**, а не ручные правки.

```text
inventories/prod/group_vars/all.yml   ─┐
inventories/prod/host_vars/app1.yml   ─┼─▶ Ansible (templates .j2) ─▶ /opt/clinic/{.env, compose.yaml, nginx/conf.d/*.conf}
vault (секреты)                       ─┘                          ─▶ docker compose up -d
```

## Структура

```text
roles/clinic_stack/
  defaults/main.yml
  tasks/main.yml
  templates/
    env.j2
    compose.yaml.j2
    nginx.conf.j2
    otel-collector.yaml.j2
  handlers/main.yml
```

### Переменные окружения

```yaml
# group_vars/prod/vars.yml
stack_dir: /opt/clinic
stack_version: "1.4.2"
domain: clinic.example.com
services:
  api:      { image: registry.example.com/clinic/api,      replicas: 2, port: 8080, memory: 768M }
  web:      { image: registry.example.com/clinic/web,      replicas: 1, port: 8080, memory: 128M }
  keycloak: { image: quay.io/keycloak/keycloak:26.0,       port: 8080, memory: 1G }
postgres: { host: db.internal, name: clinic, user: clinic }
otel: { endpoint: "http://otel-collector:4317", sampling: 0.1 }

# group_vars/prod/vault.yml (зашифрован ansible-vault)
vault_db_password: !vault |
  $ANSIBLE_VAULT;1.1;AES256 ...
vault_keycloak_admin_password: !vault | ...
```

### Шаблон `.env`

```jinja
# {{ ansible_managed }}
# Окружение: {{ env_name }}
TAG={{ stack_version }}
DOMAIN={{ domain }}
ASPNETCORE_ENVIRONMENT={{ 'Production' if env_name == 'prod' else 'Staging' }}
POSTGRES_HOST={{ postgres.host }}
POSTGRES_DB={{ postgres.name }}
POSTGRES_USER={{ postgres.user }}
POSTGRES_PASSWORD={{ vault_db_password }}
KEYCLOAK_ADMIN_PASSWORD={{ vault_keycloak_admin_password }}
OTEL_EXPORTER_OTLP_ENDPOINT={{ otel.endpoint }}
OTEL_TRACES_SAMPLER_ARG={{ otel.sampling }}
```

Права файла `0600`, владелец — пользователь деплоя; `no_log: true` для задач с секретами (чтобы значения не попадали в логи Ansible).

### Шаблон compose.yaml

```jinja
name: clinic
services:
{% for name, svc in services.items() %}
  {{ name }}:
    image: {{ svc.image }}{{ ':' ~ stack_version if ':' not in svc.image else '' }}
    restart: unless-stopped
    env_file: [.env]
    mem_limit: {{ svc.memory }}
    healthcheck:
      test: ["CMD", "wget", "-qO-", "http://localhost:{{ svc.port }}/health"]
      interval: 15s
      retries: 5
    logging: { driver: json-file, options: { max-size: "20m", max-file: "5" } }
    networks: [backend]
{% endfor %}
  nginx:
    image: nginx:1.27-alpine
    ports: ["80:80", "443:443"]
    volumes:
      - ./nginx/conf.d:/etc/nginx/conf.d:ro
      - /etc/letsencrypt:/etc/letsencrypt:ro
    depends_on:
{% for name in services %}
      {{ name }}: { condition: service_healthy }
{% endfor %}
    networks: [backend]
networks:
  backend:
```

### Задачи

```yaml
- name: Каталоги стека
  ansible.builtin.file: { path: "{{ stack_dir }}/{{ item }}", state: directory, mode: "0755" }
  loop: [nginx/conf.d, otel]

- name: Сформировать .env
  ansible.builtin.template: { src: env.j2, dest: "{{ stack_dir }}/.env", mode: "0600" }
  no_log: true
  notify: Apply stack

- name: Сформировать compose.yaml
  ansible.builtin.template:
    src: compose.yaml.j2
    dest: "{{ stack_dir }}/compose.yaml"
    mode: "0644"
    validate: docker compose -f %s config -q
  notify: Apply stack

- name: Сформировать конфигурацию nginx
  ansible.builtin.template: { src: nginx.conf.j2, dest: "{{ stack_dir }}/nginx/conf.d/clinic.conf", mode: "0644" }
  notify: Reload nginx

- name: Вход в реестр
  community.docker.docker_login: { registry_url: registry.example.com, username: "{{ registry_user }}", password: "{{ vault_registry_token }}" }
  no_log: true

- name: Запустить стек
  community.docker.docker_compose_v2:
    project_src: "{{ stack_dir }}"
    pull: always
    state: present
    wait: true
    wait_timeout: 180
  register: stack

- name: Smoke-тест
  ansible.builtin.uri: { url: "https://{{ domain }}/api/health", status_code: 200 }
  retries: 10
  delay: 6
  register: smoke
  until: smoke.status == 200
```

```yaml
# handlers/main.yml
- name: Apply stack
  community.docker.docker_compose_v2: { project_src: "{{ stack_dir }}", pull: always, state: present }
- name: Reload nginx
  community.docker.docker_container_exec:
    container: clinic-nginx-1
    command: nginx -s reload
```

## Преимущества подхода

- **одна модель данных на все окружения**: dev/stage/prod отличаются только переменными;
- **воспроизводимость**: любой сервер разворачивается одной командой;
- **валидация**: `validate:`, `docker compose config`, `nginx -t`, `--check --diff`;
- **секреты** в Vault, шаблоны их подставляют; файлы с секретами `0600`;
- **идемпотентность**: перезапуск происходит только при изменении файлов (handlers);
- **отсутствие дрейфа**: повторный запуск возвращает конфигурацию к эталону;
- **аудит**: изменения через Git/PR; AWX/Semaphore логируют запуски;
- **откат**: предыдущая версия переменных/тега (`stack_version`) и повторный запуск.

## Ограничения и практики

- шаблоны усложняются: держите логику в переменных, а не в Jinja; тесты (Molecule + `docker compose config`);
- **не раскатывайте напрямую на всё сразу**: `--limit`, `serial`, сначала staging;
- **секреты** не выводить (`no_log`), не хранить расшифрованными (`/tmp`), права; ротация;
- **drift-check**: `ansible-playbook --check --diff` по расписанию в CI;
- в Kubernetes такую же роль играет **Helm/Kustomize + GitOps**; Ansible остаётся для хостов и bootstrap;
- генерировать можно и другие конфигурации: Prometheus targets, `prometheus.yml`, `alert rules`, Grafana provisioning, Keycloak realm-импорт, logrotate, systemd unit-файлы.

## Вопросы с ответами

> [!question]- Зачем генерировать .env и compose через Ansible?
> Чтобы одна модель параметров и шаблоны давали согласованную конфигурацию всех окружений, исключали ручные правки и дрейф, безопасно подставляли секреты из Vault и позволяли проверять изменения до применения.

> [!question]- Как не раскрыть секреты в логах Ansible?
> Использовать `no_log: true` для задач с секретами, права файлов 0600, хранение значений в Ansible Vault/внешнем хранилище и запрет вывода переменных через `debug`.

> [!question]- Как перезапустить сервисы только при изменении конфигурации?
> Использовать `notify` на задачах `template/copy` и handlers: они выполнятся один раз, если файл действительно изменился.
