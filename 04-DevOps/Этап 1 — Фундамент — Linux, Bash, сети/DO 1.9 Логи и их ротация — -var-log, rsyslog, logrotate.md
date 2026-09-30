---
type: topic
domain: devops
stage: 1
order: 9
status: todo
level: junior
tags: [domain/devops, stage/1, level/junior, priority/should]
group: Скрипты и автоматизация
reviewed: 
next_review: 
priority: should
time: 6
---

# Логи и их ротация: /var/log, rsyslog, logrotate

↑ [[DO Этап 1 · Фундамент — Linux, Bash, сети|Этап 1 · Фундамент: Linux, Bash, сети]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~6 мин чтения</span><span class="chip">Уровень: junior</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> Логи — главный источник диагностики; переполнение диска логами — классический инцидент. Нужны ротация и понимание пути логов.

## Где лежат логи

| Путь | Что |
|---|---|
| `/var/log/syslog` (Debian) / `/var/log/messages` (RHEL) | общие сообщения |
| `/var/log/auth.log` / `/var/log/secure` | аутентификация, sudo, ssh |
| `/var/log/kern.log`, `dmesg` | ядро |
| `/var/log/nginx/access.log`, `error.log` | веб-сервер |
| `/var/log/postgresql/` | БД |
| `/var/log/journal/` | журнал systemd (бинарный) |
| `/var/log/apt/`, `dpkg.log` | пакеты |
| `/var/lib/docker/containers/<id>/<id>-json.log` | логи контейнеров |

## syslog и rsyslog

**Syslog** — стандарт сообщений: **facility** (auth, kern, daemon, local0–7) и **severity** (0 emerg … 3 err, 4 warning, 6 info, 7 debug). **rsyslog** — демон: принимает сообщения (из `/dev/log`, по сети UDP/TCP 514), фильтрует и маршрутизирует по правилам.

```text
# /etc/rsyslog.d/30-myapp.conf
if $programname == 'myapp' then /var/log/myapp/app.log
& stop

# отправка на центральный сервер по TCP
*.* @@logs.internal:514
```

```bash
logger -p local0.info -t myapp "deploy started"     # записать сообщение из скрипта
```

Современные дистрибутивы: журнал **journald** собирает stdout/stderr сервисов и syslog; rsyslog может читать из него (`imjournal`) и пересылать дальше.

## Ротация логов: logrotate

Без ротации файлы растут бесконечно. `logrotate` запускается по cron/systemd timer, по политикам `/etc/logrotate.d/*`.

```text
/var/log/myapp/*.log {
    daily                 # weekly, monthly или size 100M
    rotate 14             # хранить 14 архивов
    compress
    delaycompress         # сжимать со второго цикла (приложение ещё может писать в предыдущий)
    missingok
    notifempty
    create 0640 myapp myapp
    sharedscripts
    postrotate
        systemctl reload myapp >/dev/null 2>&1 || true     # переоткрыть файл логов
    endscript
}
```

Варианты обработки открытого файла:

- **`postrotate` с reload/HUP**: приложение переоткрывает файл (nginx: `nginx -s reopen` или `kill -USR1`);
- **`copytruncate`**: копирует и обнуляет файл, не требует сигнала, но возможна потеря строк между копированием и усечением.

Проверка: `logrotate -d /etc/logrotate.d/myapp` (dry-run), `logrotate -f` (принудительно). Состояние — `/var/lib/logrotate/status`.

## Ротация journald

```ini
# /etc/systemd/journald.conf
Storage=persistent
SystemMaxUse=1G
MaxRetentionSec=14day
```

```bash
journalctl --disk-usage; sudo journalctl --vacuum-size=500M
```

## Логи контейнеров

Драйвер `json-file` по умолчанию **без лимита**: безлимитный рост.

```json
// /etc/docker/daemon.json
{ "log-driver": "json-file", "log-opts": { "max-size": "50m", "max-file": "5" } }
```

```yaml
# docker-compose
logging:
  driver: json-file
  options: { max-size: "50m", max-file: "5" }
```

Другие драйверы: `local` (компактный с ротацией), `journald`, `fluentd`, `syslog`, `gelf`. Приложение в контейнере пишет в **stdout/stderr** (12-factor), а сбор — на уровне платформы.

## Рекомендации по логированию

- **структурированные логи** (JSON) — удобно искать и агрегировать;
- уровни (`DEBUG/INFO/WARN/ERROR`), в проде по умолчанию INFO;
- **корреляция**: `trace_id`, `request_id`, пользователь (не PII);
- **не логировать** пароли, токены, персональные данные;
- время в UTC, ISO 8601;
- централизованный сбор (Loki, ELK, ClickHouse) — логи не теряются при смерти хоста;
- мониторинг объёма и ошибок, алерты на всплески `ERROR`;
- хранить в соответствии с политикой (ретенция, закон).

## Диагностика

```bash
tail -f /var/log/myapp/app.log
grep -c ERROR /var/log/myapp/app.log
journalctl -u myapp -p err --since today
du -sh /var/log/* | sort -h | tail
ls -lh /var/log | sort -k5 -h | tail
lsof +L1     # удалённые логи, которые процесс держит открытыми
```

Типичная проблема: логи удалили (`rm`), но процесс держит дескриптор — место не освободилось; правильно ротировать (reopen) или обнулять (`: > file`, `truncate -s 0`).

## Вопросы с ответами

> [!question]- Зачем postrotate в logrotate?
> После переименования файла приложение продолжает писать в старый дескриптор. `postrotate` отправляет сигнал или reload, чтобы оно открыло новый файл.

> [!question]- Чем copytruncate отличается от обычной ротации?
> Копирует файл и обнуляет исходный, не требуя переоткрытия приложением; но между копированием и усечением могут потеряться записи.

> [!question]- Как ограничить логи Docker-контейнеров?
> Настроить `log-opts` (`max-size`, `max-file`) в `daemon.json` или для каждого сервиса в compose; либо драйвер `local`/внешний сборщик.
