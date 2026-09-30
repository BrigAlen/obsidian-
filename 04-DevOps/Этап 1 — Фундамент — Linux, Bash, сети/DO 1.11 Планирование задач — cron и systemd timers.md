---
type: topic
domain: devops
stage: 1
order: 11
status: todo
level: junior
tags: [domain/devops, stage/1, level/junior, priority/should]
group: Скрипты и автоматизация
reviewed: 
next_review: 
priority: should
time: 6
---

# Планирование задач: cron и systemd timers

↑ [[DO Этап 1 · Фундамент — Linux, Bash, сети|Этап 1 · Фундамент: Linux, Bash, сети]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~6 мин чтения</span><span class="chip">Уровень: junior</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> Регулярные задачи (бэкапы, очистка, отчёты) — обычная задача; спрашивают cron-синтаксис и преимущества systemd timers.

## cron

Демон `cron` выполняет команды по расписанию.

```bash
crontab -e            # редактировать задачи пользователя
crontab -l            # показать
sudo crontab -u deploy -l
```

Формат записи:

```text
# ┌ минута (0-59)
# │ ┌ час (0-23)
# │ │ ┌ день месяца (1-31)
# │ │ │ ┌ месяц (1-12)
# │ │ │ │ ┌ день недели (0-7, 0 и 7 — воскресенье)
# │ │ │ │ │
  */15 * * * *  /opt/scripts/sync.sh           # каждые 15 минут
  0 3 * * *     /opt/scripts/backup.sh         # каждый день в 03:00
  30 2 * * 1-5  /opt/scripts/report.sh         # по будням в 02:30
  0 0 1 * *     /opt/scripts/monthly.sh        # первого числа
  @reboot       /opt/scripts/on_boot.sh        # при загрузке
```

Системный cron: `/etc/crontab` и `/etc/cron.d/*` (с дополнительным полем «пользователь»), каталоги `/etc/cron.daily|hourly|weekly|monthly`.

### Типичные ловушки cron

- **пустое окружение**: `PATH` минимальный, нет ваших переменных: используйте полные пути (`/usr/bin/docker`), задайте `PATH=` и `SHELL=` вверху crontab;
- **вывод** уходит на почту пользователя или теряется: перенаправляйте `>> /var/log/job.log 2>&1` или логируйте через `logger`;
- **символ `%`** в команде должен экранироваться (`\%`);
- **пересечение запусков**: задача ещё идёт, а следующая уже стартует: `flock -n /var/lock/job.lock cmd`;
- **часовой пояс** сервера (обычно UTC): учитывайте; летнее время;
- **нет мониторинга**: молчаливые сбои; нужны heartbeat (healthchecks.io, Pushgateway) и алерты;
- **изменение crontab без контроля версий**: храните в репозитории и раскатывайте Ansible;
- **рассинхронизация при нескольких серверах**: задача выполнится на каждом (нужен лидер или распределённая блокировка).

```text
MAILTO=""
PATH=/usr/local/bin:/usr/bin:/bin
0 3 * * * flock -n /var/lock/backup.lock /opt/scripts/backup.sh >> /var/log/backup.log 2>&1 && curl -fsS https://hc-ping.com/UUID
```

`anacron` — для машин, которые выключаются: догоняет пропущенные задачи.

## systemd timers

Задача состоит из двух unit: `.service` (что делать) и `.timer` (когда).

```ini
# /etc/systemd/system/backup.service
[Unit]
Description=Nightly DB backup
[Service]
Type=oneshot
User=backup
ExecStart=/opt/scripts/backup.sh
```

```ini
# /etc/systemd/system/backup.timer
[Unit]
Description=Run backup nightly
[Timer]
OnCalendar=*-*-* 03:00:00
RandomizedDelaySec=10min       # разброс, чтобы не нагружать всех сразу
Persistent=true                # догнать пропущенный запуск после простоя
[Install]
WantedBy=timers.target
```

```bash
sudo systemctl enable --now backup.timer
systemctl list-timers --all
systemctl status backup.service
journalctl -u backup.service
systemd-analyze calendar "Mon..Fri 02:30"     # проверить выражение
sudo systemctl start backup.service             # запустить вручную
```

Другие триггеры: `OnBootSec=`, `OnUnitActiveSec=` (через интервал после предыдущего запуска), `OnStartupSec=`.

### Преимущества timers над cron

| | cron | systemd timer |
|---|---|---|
| Логи | почта/файл вручную | journald автоматически |
| Зависимости | нет | `After=`, `Requires=` |
| Ресурсы, безопасность | нет | cgroup, `MemoryMax`, sandboxing |
| Пропущенные запуски | нет (кроме anacron) | `Persistent=true` |
| Повторы | вручную | `Restart=`, лимиты |
| Перекрытие запусков | нужен flock | сервис не запустится второй раз, пока идёт |
| Статус и история | нет | `systemctl status`, `list-timers` |
| Простота | очень просто | два файла |

## Другие варианты

- **Kubernetes CronJob**: расписание для контейнеров (`concurrencyPolicy: Forbid`, `startingDeadlineSeconds`, `successfulJobsHistoryLimit`);
- CI по расписанию (GitLab schedules);
- планировщики задач: Hangfire, Quartz.NET, Airflow, Temporal — для приложений со сложными графами;
- `at` — разовые задачи.

## Практика

- задача должна быть **идемпотентной** и устойчивой к повтору;
- **таймаут**: `timeout 30m cmd`;
- логирование + метрика успеха/времени/последнего успешного запуска; алерт, если задача не выполнялась дольше N;
- не запускать тяжёлые задачи одновременно (разброс `RandomizedDelaySec`);
- код возврата ≠ 0 при ошибке.

## Вопросы с ответами

> [!question]- Почему скрипт работает из терминала, но не из cron?
> В cron другое окружение: минимальный PATH, нет переменных и рабочего каталога, нет TTY. Используйте полные пути и задавайте окружение явно.

> [!question]- Как предотвратить параллельный запуск одной задачи?
> `flock -n lockfile cmd` для cron; для systemd достаточно `.service` (повторно он не стартует, пока активен).

> [!question]- Что делает Persistent=true?
> Если система была выключена в момент запуска, systemd выполнит задачу сразу после старта.
