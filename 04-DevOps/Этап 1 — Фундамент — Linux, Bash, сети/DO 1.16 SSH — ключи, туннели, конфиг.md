---
type: topic
domain: devops
stage: 1
order: 16
status: todo
level: junior
tags: [domain/devops, stage/1, level/junior, priority/should]
group: Сети
reviewed: 
next_review: 
priority: should
time: 7
---

# SSH: ключи, туннели, конфиг

↑ [[DO Этап 1 · Фундамент — Linux, Bash, сети|Этап 1 · Фундамент: Linux, Bash, сети]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~7 мин чтения</span><span class="chip">Уровень: junior</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> SSH — главный инструмент доступа к серверам: ключи, туннели, hardening и удобная конфигурация.

## Принцип

**Secure Shell**: шифрованный канал (TCP/22) для удалённого доступа, передачи файлов и туннелей. Аутентификация: пароль (избегать) или **ключи**.

## Ключи

```bash
ssh-keygen -t ed25519 -C "alex@laptop" -f ~/.ssh/id_ed25519     # современный алгоритм; пароль на ключ (passphrase)
ssh-copy-id -i ~/.ssh/id_ed25519.pub user@host                  # добавить публичный ключ в ~/.ssh/authorized_keys
ssh -i ~/.ssh/id_ed25519 user@host
ssh-add ~/.ssh/id_ed25519; ssh-add -l                            # ssh-agent: ключ в памяти
```

- **приватный ключ** никому не передаётся (`600`); **публичный** размещается на серверах;
- права: `~/.ssh` `700`, `authorized_keys` `600`;
- **`known_hosts`**: отпечатки серверов (защита от MITM); предупреждение «REMOTE HOST IDENTIFICATION HAS CHANGED» — повод проверить, а не просто удалить запись (`ssh-keygen -R host`);
- **`ssh-agent` forwarding** (`-A`) удобен, но небезопасен на недоверенных серверах; предпочитайте `ProxyJump`.

## Клиентский конфиг `~/.ssh/config`

```text
Host bastion
    HostName 203.0.113.10
    User ops
    IdentityFile ~/.ssh/id_ed25519
    IdentitiesOnly yes

Host prod-*
    User deploy
    ProxyJump bastion                      # через бастион
    ServerAliveInterval 30
    ServerAliveCountMax 3

Host prod-api
    HostName 10.0.1.15
    LocalForward 5433 10.0.2.20:5432       # проброс порта БД

Host *
    AddKeysToAgent yes
    ControlMaster auto                     # мультиплексирование: последующие подключения мгновенные
    ControlPath ~/.ssh/cm-%r@%h:%p
    ControlPersist 10m
```

`ssh prod-api` — короткое имя вместо длинной команды.

## Туннели (проброс портов)

```bash
# Local: локальный порт → через SSH-сервер → цель (доступ к БД во внутренней сети)
ssh -L 5433:db.internal:5432 user@bastion        # затем psql -h localhost -p 5433

# Remote: порт на сервере → обратно к вам (выставить локальный сервис наружу)
ssh -R 8080:localhost:3000 user@server

# Dynamic: SOCKS5-прокси через сервер
ssh -D 1080 user@bastion                         # браузер/curl --socks5-hostname localhost:1080

ssh -N -f -L ...                                 # без shell, в фоне
ssh -J bastion user@internal-host                # ProxyJump: прыжок через бастион
```

Постоянные туннели: `autossh`, systemd unit.

## Передача файлов

```bash
scp file user@host:/path/; scp -r dir user@host:/path/
rsync -avz --progress -e ssh ./dist/ user@host:/var/www/app/     # дельта-синхронизация; --delete, --dry-run
sftp user@host
ssh host 'tar czf - /data' > backup.tgz                          # поток через ssh
```

## Hardening sshd (`/etc/ssh/sshd_config`)

```text
Port 22                          # смена порта — не защита, лишь снижает шум
PermitRootLogin no
PasswordAuthentication no        # только ключи
PubkeyAuthentication yes
KbdInteractiveAuthentication no
AllowUsers deploy ops            # или AllowGroups ssh-users
MaxAuthTries 3
LoginGraceTime 30
ClientAliveInterval 300
ClientAliveCountMax 2
X11Forwarding no
AllowTcpForwarding no            # включать только где нужно
AuthenticationMethods publickey  # или publickey,keyboard-interactive для 2FA
```

```bash
sudo sshd -t                     # проверка конфигурации ПЕРЕД перезагрузкой
sudo systemctl reload ssh        # не закрывайте текущую сессию, проверьте вход во второй
```

Дополнительно: **fail2ban**/`sshguard` (блокировка перебора), firewall по источникам, **2FA** (TOTP через PAM), **SSH-сертификаты** (подписанные CA, короткий срок жизни: масштабируемая альтернатива раздаче ключей), **bastion host**/**ssh over SSM/Teleport/Boundary**, аудит входов (`last`, `journalctl -u ssh`), ротация ключей, удаление ключей уволенных сотрудников (управление через Ansible/IAM).

## Диагностика

```bash
ssh -vvv user@host               # подробный вывод
sudo journalctl -u ssh -f        # на сервере (auth.log)
sudo ss -tlnp | grep :22
```

| Ошибка | Причина |
|---|---|
| `Permission denied (publickey)` | нет ключа в `authorized_keys`, неверные права, не тот пользователь, `AllowUsers`, ключ не загружен в агент |
| `Connection refused` | sshd не запущен, другой порт, firewall |
| `Connection timed out` | сеть, firewall, security group |
| `Host key verification failed` | изменился ключ сервера (переустановка, MITM) |
| `Too many authentication failures` | слишком много ключей в агенте: `IdentitiesOnly yes`, `-o IdentityFile` |
| Зависает сессия | `ServerAliveInterval` |

## Вопросы с ответами

> [!question]- Чем Local Port Forwarding отличается от Remote?
> Local (`-L`) открывает порт у клиента и пересылает на цель через сервер (доступ к внутренним ресурсам). Remote (`-R`) открывает порт на сервере и пересылает на клиента (выставление локального сервиса).

> [!question]- Как безопасно настроить доступ по SSH к продакшн-серверам?
> Только ключи (пароли выключены), запрет root-входа, бастион/ProxyJump, ограничение источников и пользователей, fail2ban, 2FA или SSH-сертификаты, регулярная ротация и аудит.

> [!question]- Что делать при предупреждении о смене host key?
> Не игнорировать: выяснить причину (переустановка сервера, смена IP) по независимому каналу, и только после проверки обновить запись `known_hosts`.
