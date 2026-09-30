---
type: topic
domain: devops
stage: 6
order: 2
status: todo
level: middle
tags: [domain/devops, stage/6, level/middle, priority/nice]
reviewed: 
next_review: 
priority: nice
time: 17
---

# Ansible: inventory, playbooks, tasks, roles, templates (Jinja2)

↑ [[DO Этап 6 · Infrastructure as Code — Ansible, Terraform|Этап 6 · Infrastructure as Code: Ansible, Terraform]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge nice">По желанию</span><span class="chip">~17 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> Ansible — основной инструмент конфигурации серверов в вашем стеке. Нужны inventory, playbooks, roles, Jinja2 и идемпотентность.

## Что такое Ansible

**Агентless** система автоматизации: подключается по **SSH** (Windows — WinRM), запускает небольшие модули на целевых хостах и возвращает результат; ничего не устанавливается на целевые узлы (кроме Python). Управляющая машина — **control node**; Декларативные модули, идемпотентность, YAML.

```bash
pip install ansible-core ansible-lint
ansible --version; ansible-galaxy collection install community.docker community.postgresql
```

## Inventory

Список хостов и групп.

```ini
# inventories/prod/hosts.ini
[web]
web1 ansible_host=10.0.1.11
web2 ansible_host=10.0.1.12

[db]
db1 ansible_host=10.0.2.10 ansible_user=admin

[app:children]
web

[prod:children]
web
db

[all:vars]
ansible_user=deploy
ansible_ssh_private_key_file=~/.ssh/id_ed25519
```

```yaml
# inventories/prod/hosts.yml
all:
  children:
    web: { hosts: { web1: { ansible_host: 10.0.1.11 }, web2: { ansible_host: 10.0.1.12 } } }
    db:  { hosts: { db1:  { ansible_host: 10.0.2.10 } } }
```

Переменные: `group_vars/<group>.yml`, `host_vars/<host>.yml`; **динамический inventory** из облаков/CMDB (`aws_ec2`, `yc`, `hcloud` плагины). Паттерны: `web:&prod`, `all:!db`.

## Ad-hoc команды

```bash
ansible all -i inventories/prod -m ping
ansible web -i inventories/prod -m ansible.builtin.service -a "name=nginx state=restarted" -b
ansible db -m shell -a "df -h" 
ansible all -m setup -a "filter=ansible_distribution*"      # факты
```

## Playbook

```yaml
# site.yml
- name: Настройка веб-серверов
  hosts: web
  become: true                     # sudo
  gather_facts: true
  vars:
    app_user: clinic
    nginx_port: 80
  vars_files: [vars/common.yml]
  pre_tasks:
    - name: Обновить кэш apt
      ansible.builtin.apt: { update_cache: true, cache_valid_time: 3600 }

  tasks:
    - name: Установить пакеты
      ansible.builtin.apt:
        name: [nginx, curl]
        state: present

    - name: Пользователь приложения
      ansible.builtin.user: { name: "{{ app_user }}", shell: /bin/bash, create_home: true }

    - name: Каталог приложения
      ansible.builtin.file: { path: /opt/clinic, state: directory, owner: "{{ app_user }}", mode: "0755" }

    - name: Конфигурация nginx из шаблона
      ansible.builtin.template:
        src: nginx.conf.j2
        dest: /etc/nginx/conf.d/clinic.conf
        owner: root
        mode: "0644"
        validate: nginx -t -c /etc/nginx/nginx.conf       # (для полного файла) или проверка в handler
      notify: Reload nginx

    - name: Сервис запущен и включён
      ansible.builtin.service: { name: nginx, state: started, enabled: true }

    - name: Проверка доступности
      ansible.builtin.uri: { url: "http://localhost/health", status_code: 200 }
      register: health
      retries: 5
      delay: 3
      until: health.status == 200

  handlers:
    - name: Reload nginx
      ansible.builtin.service: { name: nginx, state: reloaded }
```

```bash
ansible-playbook -i inventories/prod site.yml --check --diff          # dry-run с показом изменений
ansible-playbook -i inventories/prod site.yml --limit web1 --tags nginx -e "nginx_port=8080"
ansible-playbook site.yml --ask-vault-pass --start-at-task "Конфигурация nginx"
```

**Handlers** выполняются **один раз в конце** play и только если задача с `notify` сообщила об изменении (`changed`).

## Основные модули

| Категория | Модули |
|---|---|
| Пакеты | `apt`, `dnf`, `package`, `pip` |
| Файлы | `copy`, `template`, `file`, `lineinfile`, `blockinfile`, `synchronize`, `unarchive`, `fetch` |
| Сервисы | `service`, `systemd`, `cron` |
| Пользователи | `user`, `group`, `authorized_key` |
| Команды | `command`, `shell`, `script`, `raw` (не идемпотентны: использовать `creates`, `changed_when`) |
| Сеть/HTTP | `uri`, `get_url`, `wait_for`, `ufw`, `firewalld` |
| Docker | `community.docker.docker_compose_v2`, `docker_container`, `docker_image`, `docker_network` |
| Облака/БД | `amazon.aws.*`, `community.postgresql.postgresql_db`, `postgresql_user` |
| Отладка | `debug`, `assert`, `fail`, `set_fact` |

Предпочитайте **специализированные модули** вместо `shell`.

## Переменные, факты, условия, циклы

```yaml
- name: Пакеты по семейству ОС
  ansible.builtin.package: { name: "{{ item }}", state: present }
  loop: [git, curl, htop]
  when: ansible_os_family == "Debian"

- name: Создать несколько пользователей
  ansible.builtin.user: { name: "{{ item.name }}", groups: "{{ item.groups | default([]) }}" }
  loop: "{{ users }}"
  loop_control: { label: "{{ item.name }}" }

- name: Только если файл отсутствует
  ansible.builtin.command: /opt/init.sh
  args: { creates: /opt/.initialized }

- ansible.builtin.shell: grep -c foo /etc/bar || true
  register: res
  changed_when: false
  failed_when: res.rc > 1
```

**Факты** (`ansible_facts`): `ansible_hostname`, `ansible_default_ipv4.address`, `ansible_memtotal_mb`, `ansible_distribution`. **Приоритет переменных** (от низкого к высокому): role defaults → inventory/group_vars → host_vars → play vars → role vars → task vars → `set_fact` → `-e` extra vars (наивысший).

Фильтры Jinja2: `default`, `join`, `regex_replace`, `to_json`, `b64encode`, `ipaddr`, `password_hash`, `combine`, `selectattr`, `map`.

## Шаблоны Jinja2

```jinja
# nginx.conf.j2
{% for site in sites %}
server {
    listen {{ nginx_port | default(80) }};
    server_name {{ site.domain }};
    {% if site.tls | default(false) %}
    listen 443 ssl;
    ssl_certificate /etc/letsencrypt/live/{{ site.domain }}/fullchain.pem;
    {% endif %}
    location / { proxy_pass http://{{ site.backend }}; }
}
{% endfor %}
```

Синтаксис: `{{ var }}` — значение, `{% ... %}` — логика, `{# ... #}` — комментарий. Генерируемый файл помечайте `# Managed by Ansible`.

## Roles

Структурированная единица переиспользования.

```text
roles/nginx/
  defaults/main.yml      # значения по умолчанию (низкий приоритет)
  vars/main.yml          # внутренние переменные (высокий приоритет)
  tasks/main.yml
  handlers/main.yml
  templates/*.j2
  files/
  meta/main.yml          # зависимости
  molecule/              # тесты
```

```yaml
- hosts: web
  become: true
  roles:
    - common
    - { role: nginx, vars: { nginx_port: 8080 } }
    - role: clinic_app
      tags: [app]
```

Роли из **Ansible Galaxy** / коллекций (`ansible-galaxy install -r requirements.yml`); **коллекции** (`community.docker`, `ansible.posix`) — пакеты модулей и ролей. `include_role`/`import_role`, `include_tasks`/`import_tasks` (динамическое vs статическое).

## Структура репозитория

```text
ansible/
  ansible.cfg
  requirements.yml
  inventories/{dev,staging,prod}/{hosts.yml,group_vars/,host_vars/}
  playbooks/{site.yml,deploy.yml,backup.yml}
  roles/{common,docker,nginx,clinic_app}/
  collections/
  vault/  (зашифрованные переменные)
```

```ini
# ansible.cfg
[defaults]
inventory = inventories/dev
roles_path = roles
host_key_checking = True
forks = 20
stdout_callback = yaml
retry_files_enabled = False
[ssh_connection]
pipelining = True
ssh_args = -o ControlMaster=auto -o ControlPersist=60s
```

## Ansible Vault (секреты)

```bash
ansible-vault create group_vars/prod/vault.yml
ansible-vault edit|view|encrypt|decrypt|rekey group_vars/prod/vault.yml
ansible-vault encrypt_string 's3cret' --name 'db_password'
ansible-playbook site.yml --vault-password-file ~/.vault_pass       # пароль в файле (вне репозитория) / из менеджера секретов
```

Схема: открытый `vars.yml` ссылается на `vault_db_password` из зашифрованного файла. Альтернативы: SOPS, HashiCorp Vault lookup, облачные менеджеры (`community.hashi_vault`).

## Особенности и лучшие практики

- **идемпотентность**: используйте модули, `changed_when`, `creates`, `check_mode`; повторный запуск должен давать `changed=0`;
- **теги** (`tags`) и `--limit` для частичных запусков; `--check --diff` перед применением;
- **`serial`** для rolling-обновлений (`serial: 1` или `25%`), `max_fail_percentage`, `any_errors_fatal`;
- **`become`** только где нужно; отдельный deploy-пользователь с sudo по списку;
- **проверки**: `ansible-lint`, `yamllint`, **Molecule** (тест ролей в Docker), `--syntax-check`;
- **именование задач** понятное (вывод читается как лог); без `ignore_errors` без необходимости;
- **`block/rescue/always`** для обработки ошибок и отката;
- производительность: `pipelining`, `forks`, `gather_facts: false` (где не нужны), кэш фактов, `async`/`poll` для долгих задач, mitogen (опция);
- **AWX / Ansible Automation Platform / Semaphore** — веб-интерфейс, RBAC, расписания, аудит, credentials;
- **pull-режим** (`ansible-pull`) для автонастройки узлов;
- версии: фиксируйте `ansible-core` и коллекции (`requirements.yml`), запускайте в контейнере (execution environment).

```yaml
- name: Rolling-обновление
  hosts: web
  serial: 1
  tasks:
    - block:
        - name: Вывести из балансировщика
          ansible.builtin.uri: { url: "http://lb/api/drain/{{ inventory_hostname }}", method: POST }
        - name: Обновить приложение
          community.docker.docker_compose_v2: { project_src: /opt/clinic, pull: always, state: present }
        - name: Проверка здоровья
          ansible.builtin.uri: { url: "http://{{ inventory_hostname }}:8080/health", status_code: 200 }
          retries: 10
          delay: 5
          register: r
          until: r.status == 200
      rescue:
        - name: Откат
          ansible.builtin.debug: msg="Откат на предыдущую версию"
      always:
        - name: Вернуть в балансировщик
          ansible.builtin.uri: { url: "http://lb/api/enable/{{ inventory_hostname }}", method: POST }
```

## Вопросы с ответами

> [!question]- Почему Ansible называют агентless?
> Он подключается к хостам по SSH и запускает модули временно, без постоянного агента на целевых серверах.

> [!question]- Что такое handler и когда он выполняется?
> Задача-реакция, которая выполняется в конце play один раз и только если задача с `notify` изменила состояние (например, reload nginx после изменения конфигурации).

> [!question]- Как сделать задачу с shell идемпотентной?
> Использовать `creates`/`removes`, условие `when`, проверку состояния с `changed_when`/`failed_when`, либо заменить на специализированный модуль.
