---
type: topic
domain: devops
stage: 1
order: 3
status: todo
level: junior
tags: [domain/devops, stage/1, level/junior, priority/should]
group: Linux
reviewed: 
next_review: 
priority: should
time: 4
---

# sudo, PAM и Linux capabilities: управление привилегиями

↑ [[DO Этап 1 · Фундамент — Linux, Bash, сети|Этап 1 · Фундамент: Linux, Bash, сети]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~4 мин чтения</span><span class="chip">Уровень: junior</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> Управление привилегиями — основа безопасности: принцип наименьших привилегий, аудит, отказ от работы под root.

## sudo

Позволяет пользователю выполнять команды от имени другого (обычно root) с аудитом в журнале.

```bash
sudo systemctl restart nginx
sudo -u postgres psql
sudo -l                      # что мне разрешено
sudo visudo                  # безопасное редактирование /etc/sudoers
```

Конфигурация `/etc/sudoers` и `/etc/sudoers.d/*`:

```text
# пользователь/группа  хосты=(от кого) [опции] команды
deploy   ALL=(root) NOPASSWD: /usr/bin/systemctl restart myapp, /usr/bin/systemctl status myapp
%devops  ALL=(ALL:ALL) ALL
Defaults  logfile="/var/log/sudo.log"
Defaults  requiretty, use_pty
```

Принципы:

- **точечные права**: конкретные команды с полными путями, а не `ALL`;
- `NOPASSWD` только для автоматизации и узких команд;
- не давать `sudo` на интерпретаторы, редакторы, `less`, `find`, `vi` (выход в shell — повышение привилегий);
- файлы в `/etc/sudoers.d/` с правами `0440`, проверка `visudo -c`;
- журналирование (`journalctl _COMM=sudo`, `/var/log/auth.log`).

## PAM (Pluggable Authentication Modules)

Подсистема аутентификации: программы (login, sshd, sudo) обращаются к PAM, который по конфигурации `/etc/pam.d/<сервис>` вызывает модули.

Четыре группы:

| Тип | Задача |
|---|---|
| `auth` | проверка личности (пароль, ключ, 2FA) |
| `account` | разрешён ли доступ (срок, время, доступ к сервису) |
| `password` | смена пароля, политика сложности |
| `session` | действия при входе/выходе (лимиты, монтирование, журнал) |

Флаги управления: `required` (итог провал, но остальные модули выполняются), `requisite` (провал — сразу отказ), `sufficient` (успех — достаточно), `optional`.

```text
auth     required   pam_faillock.so preauth deny=5 unlock_time=900
auth     sufficient pam_unix.so
session  required   pam_limits.so
```

Примеры применения: блокировка после неудачных попыток (`pam_faillock`), политика паролей (`pam_pwquality`), 2FA (`pam_google_authenticator`, `pam_u2f`), LDAP/SSSD/Kerberos, лимиты ресурсов (`pam_limits`, `/etc/security/limits.conf`).

## Linux capabilities

Root разбит на ~40 **привилегий** (capabilities), которые можно выдавать по отдельности.

| Capability | Что даёт |
|---|---|
| `CAP_NET_BIND_SERVICE` | слушать порты < 1024 |
| `CAP_NET_ADMIN` | настройка сети, iptables |
| `CAP_NET_RAW` | raw-сокеты (ping) |
| `CAP_SYS_ADMIN` | «новый root»: огромный набор операций (избегать) |
| `CAP_CHOWN`, `CAP_DAC_OVERRIDE` | менять владельца, обход прав файлов |
| `CAP_SYS_PTRACE` | отладка чужих процессов |
| `CAP_KILL`, `CAP_SETUID` | сигналы, смена UID |

```bash
getcap -r /usr/bin 2>/dev/null
sudo setcap 'cap_net_bind_service=+ep' /usr/local/bin/myapp   # порт 80 без root
capsh --print
cat /proc/<pid>/status | grep Cap
```

Наборы: permitted, effective, inheritable, bounding, ambient.

В systemd: `AmbientCapabilities=CAP_NET_BIND_SERVICE`, `CapabilityBoundingSet=`, `NoNewPrivileges=true`.

В Docker/Kubernetes контейнер по умолчанию получает урезанный набор; правильно — `drop: ["ALL"]` и добавлять нужные:

```yaml
securityContext:
  allowPrivilegeEscalation: false
  capabilities: { drop: ["ALL"], add: ["NET_BIND_SERVICE"] }
```

## Другие механизмы

- **SELinux / AppArmor**: обязательный контроль доступа (MAC) поверх обычных прав;
- **seccomp**: фильтр системных вызовов;
- **user namespaces / rootless**: root внутри контейнера не root на хосте;
- **setuid-программы**: минимизировать, аудит `find / -perm -4000`.

## Вопросы с ответами

> [!question]- Зачем capabilities, если есть root и обычный пользователь?
> Чтобы выдать процессу только нужную привилегию (например, порт 80), не давая полного root. Снижает ущерб при компрометации.

> [!question]- Как дать сервису возможность слушать порт 443 без root?
> `setcap cap_net_bind_service=+ep` на бинарь, `AmbientCapabilities=CAP_NET_BIND_SERVICE` в unit systemd или `sysctl net.ipv4.ip_unprivileged_port_start=0`, либо слушать высокий порт за reverse proxy.

> [!question]- Чем опасен sudo на vim или find?
> Из них можно запустить shell (`:!sh`, `find -exec`), получив root без ограничений.
