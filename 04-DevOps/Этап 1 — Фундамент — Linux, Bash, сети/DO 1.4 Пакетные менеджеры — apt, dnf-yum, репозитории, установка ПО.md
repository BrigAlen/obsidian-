---
type: topic
domain: devops
stage: 1
order: 4
status: todo
level: junior
tags: [domain/devops, stage/1, level/junior, priority/should]
group: Скрипты и автоматизация
reviewed: 
next_review: 
priority: should
time: 4
---

# Пакетные менеджеры: apt, dnf-yum, репозитории, установка ПО

↑ [[DO Этап 1 · Фундамент — Linux, Bash, сети|Этап 1 · Фундамент: Linux, Bash, сети]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~4 мин чтения</span><span class="chip">Уровень: junior</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> Установка и обновление ПО, репозитории и подписи — повседневная работа; важны воспроизводимость и безопасность.

## Семейства

| Семейство | Формат | Инструменты | Дистрибутивы |
|---|---|---|---|
| Debian | `.deb` | `apt`, `apt-get`, `dpkg` | Debian, Ubuntu |
| Red Hat | `.rpm` | `dnf` (ранее `yum`), `rpm` | RHEL, Rocky, AlmaLinux, Fedora |
| Alpine | `.apk` | `apk` | Alpine (контейнеры) |
| Arch | pkg.tar | `pacman` | Arch |

Пакетный менеджер решает **зависимости**, ведёт базу установленного, проверяет **подписи** и **контрольные суммы**, умеет обновлять и удалять.

## apt (Debian/Ubuntu)

```bash
sudo apt update                          # обновить индекс пакетов (не сами пакеты)
sudo apt install -y nginx=1.24.0-1ubuntu1    # конкретная версия
sudo apt upgrade                         # обновить установленные
sudo apt full-upgrade                    # с удалением/заменой зависимостей
sudo apt remove nginx                    # удалить, конфиги остаются
sudo apt purge nginx                     # удалить вместе с конфигурацией
sudo apt autoremove
apt search nginx; apt show nginx; apt list --installed
apt-cache policy nginx                   # доступные версии и приоритеты
dpkg -l | grep nginx; dpkg -L nginx; dpkg -S /usr/sbin/nginx   # файлы пакета, чей файл
sudo apt-mark hold nginx                 # зафиксировать версию
```

## dnf/yum (RHEL)

```bash
sudo dnf install -y nginx
sudo dnf update; sudo dnf remove nginx
dnf search|info|list installed nginx
dnf history; sudo dnf history undo 12
dnf provides /usr/sbin/nginx
sudo dnf versionlock add nginx           # плагин versionlock
rpm -qa; rpm -ql nginx; rpm -qf /usr/sbin/nginx; rpm -V nginx   # проверка целостности
```

## Репозитории

- **Debian**: `/etc/apt/sources.list`, `/etc/apt/sources.list.d/*.list` (или `.sources` — deb822);
- **RHEL**: `/etc/yum.repos.d/*.repo`.

Подписи: ключи GPG, современный способ — отдельный keyring и `signed-by`:

```bash
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo "deb [arch=amd64 signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu jammy stable" \
  | sudo tee /etc/apt/sources.list.d/docker.list
sudo apt update && sudo apt install docker-ce
```

`apt-key` устарел. Не отключайте проверку подписи (`--allow-unauthenticated`, `gpgcheck=0`).

## Практика в DevOps

- **Воспроизводимость**: фиксировать версии (`apt install pkg=version`, `hold`/`versionlock`), в Dockerfile — конкретные теги;
- **Зеркала и кэш**: внутренний репозиторий (Nexus, Artifactory, apt-cacher-ng) — скорость и отказоустойчивость;
- **Автоматические обновления безопасности**: `unattended-upgrades`, `dnf-automatic`; тесты перед применением в проде;
- **Минимум пакетов** на сервере и в образах: меньше уязвимостей;
- **Чистка кэша в Dockerfile** в том же слое:

```dockerfile
RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates \
 && rm -rf /var/lib/apt/lists/*
```

- Конфигурационное управление (Ansible: модули `apt`, `dnf`, `package`) вместо ручной установки;
- Установка из исходников/бинарников — в `/opt` или `/usr/local`, по возможности упаковать (`fpm`), чтобы не терять управление.

Другие менеджеры: **snap**, **flatpak**, **pip/npm/cargo** (языковые, отдельно), **Homebrew**, **Nix** (декларативно и воспроизводимо).

## Проблемы

- «Unable to acquire the dpkg lock» — другой процесс apt/unattended-upgrades;
- сломанные зависимости: `apt --fix-broken install`, `dpkg --configure -a`;
- конфликт версий из разных репозиториев: приоритеты (`apt_preferences`), pinning;
- `apt update` падает по подписи: просроченный или отсутствующий ключ.

## Вопросы с ответами

> [!question]- Чем apt update отличается от apt upgrade?
> `update` обновляет индекс доступных пакетов из репозиториев; `upgrade` ставит новые версии уже установленных пакетов.

> [!question]- Как зафиксировать версию пакета?
> Установить конкретную версию (`apt install pkg=ver`) и поставить `apt-mark hold`; в RHEL — `dnf versionlock`. В контейнерах — пиннинг версий в Dockerfile.

> [!question]- Зачем remove и purge различаются?
> `remove` оставляет конфигурационные файлы (удобно при переустановке), `purge` удаляет и их.
