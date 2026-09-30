---
type: topic
domain: devops
stage: 1
order: 7
status: todo
level: junior
tags: [domain/devops, stage/1, level/junior, priority/should]
group: Скрипты и автоматизация
reviewed: 
next_review: 
priority: should
time: 6
---

# Процессы, systemd, сервисы, journalctl

↑ [[DO Этап 1 · Фундамент — Linux, Bash, сети|Этап 1 · Фундамент: Linux, Bash, сети]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~6 мин чтения</span><span class="chip">Уровень: junior</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> Запуск, перезапуск и диагностика сервисов через systemd — ежедневная работа; спрашивают unit-файлы и работу с журналом.

## Процессы

```bash
ps aux; ps -ef --forest; pstree -p
top; htop
pgrep -af nginx; pkill -f worker
kill PID        # SIGTERM (15): просьба завершиться (graceful)
kill -9 PID     # SIGKILL: немедленно, без очистки (крайняя мера)
kill -HUP PID   # SIGHUP: перечитать конфигурацию (у многих демонов)
nice -n 10 cmd; renice 5 -p PID
```

Состояния: **R** (выполняется), **S** (спит), **D** (непрерываемый сон, ждёт I/O), **T** (остановлен), **Z** (зомби: завершился, родитель не прочитал код возврата).

Сигналы: `SIGTERM` (15), `SIGKILL` (9, нельзя перехватить), `SIGINT` (2, Ctrl+C), `SIGHUP` (1), `SIGSTOP/SIGCONT`, `SIGUSR1/2`. Зомби не «убить» — решается завершением родителя.

**PID 1** — init (systemd): усыновляет сирот; в контейнерах PID 1 — ваше приложение (нужно обрабатывать сигналы и собирать зомби).

## systemd

Менеджер системы и сервисов: запуск, зависимости, перезапуск при падении, cgroups, журналы.

```bash
systemctl status nginx
sudo systemctl start|stop|restart|reload nginx
sudo systemctl enable --now nginx        # автозапуск + запуск
sudo systemctl disable nginx; systemctl is-active nginx; systemctl is-enabled nginx
systemctl list-units --type=service --state=failed
systemctl list-unit-files | grep enabled
sudo systemctl daemon-reload             # после изменения unit-файлов
systemctl cat myapp; systemctl show myapp -p MainPID,MemoryCurrent
systemd-analyze blame; systemd-analyze critical-chain
```

## Unit-файл сервиса

`/etc/systemd/system/myapp.service`:

```ini
[Unit]
Description=My .NET API
After=network-online.target postgresql.service
Wants=network-online.target
Requires=postgresql.service

[Service]
Type=notify                    # simple | exec | forking | oneshot | notify
User=myapp
Group=myapp
WorkingDirectory=/opt/myapp
EnvironmentFile=/etc/myapp/env
ExecStart=/usr/bin/dotnet /opt/myapp/Api.dll
ExecReload=/bin/kill -HUP $MAINPID
Restart=on-failure
RestartSec=5
TimeoutStopSec=30
LimitNOFILE=65535

# безопасность (hardening)
NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=true
PrivateTmp=true
ReadWritePaths=/var/lib/myapp
CapabilityBoundingSet=
MemoryMax=1G

[Install]
WantedBy=multi-user.target
```

- **`After`** — порядок запуска; **`Requires`/`Wants`** — зависимость (жёсткая/мягкая);
- **`Restart=`**: `no`, `on-failure`, `always`; с `StartLimitBurst` и `StartLimitIntervalSec` защита от бесконечных перезапусков;
- drop-in переопределения: `systemctl edit myapp` (файл `override.conf`), не правьте файлы пакетов;
- `systemd-analyze security myapp` — оценка безопасности unit.

Другие типы unit: `.timer` (замена cron), `.socket` (активация по сокету), `.mount`, `.target`, `.path`.

## journalctl

```bash
journalctl -u myapp -f                     # follow
journalctl -u myapp --since "1 hour ago" --until "10 min ago"
journalctl -u myapp -p err -b              # только ошибки с текущей загрузки
journalctl -b -1                           # прошлая загрузка
journalctl -k                              # ядро
journalctl -o json-pretty -n 20
journalctl --disk-usage; sudo journalctl --vacuum-time=7d --vacuum-size=500M
```

Постоянное хранение: `Storage=persistent` в `/etc/systemd/journald.conf` (каталог `/var/log/journal`). Лимиты: `SystemMaxUse`, `MaxRetentionSec`.

## Диагностика упавшего сервиса

1. `systemctl status myapp` — состояние, код выхода, последние строки журнала;
2. `journalctl -u myapp -n 100 --no-pager`;
3. проверка конфигурации (`nginx -t`), прав, порта (`ss -tulpn`), переменных окружения;
4. запуск вручную под тем же пользователем;
5. `systemctl show myapp -p ExecMainStatus,Result` — почему завершился; `status=203/EXEC` — не найден или не исполняется бинарь, `217/USER` — нет пользователя, `200/CHDIR` — нет рабочего каталога;
6. OOM: `dmesg | grep -i oom`; лимиты: `LimitNOFILE`, `MemoryMax`.

## Вопросы с ответами

> [!question]- Чем SIGTERM отличается от SIGKILL?
> SIGTERM можно перехватить: процесс корректно завершает работу. SIGKILL ядро применяет немедленно, процесс не может его обработать — возможна потеря данных.

> [!question]- Что такое процесс-зомби?
> Завершённый процесс, код возврата которого не прочитал родитель; он занимает запись в таблице процессов. Убирается завершением или исправлением родителя (`wait`).

> [!question]- Зачем нужен daemon-reload?
> systemd кэширует unit-файлы; после их изменения нужно перечитать конфигурацию.
