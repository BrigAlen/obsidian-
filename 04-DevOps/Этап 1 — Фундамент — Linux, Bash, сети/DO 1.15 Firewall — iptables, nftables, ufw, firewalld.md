---
type: topic
domain: devops
stage: 1
order: 15
status: todo
level: junior
tags: [domain/devops, stage/1, level/junior, priority/should]
group: Сети
reviewed: 
next_review: 
priority: should
time: 6
---

# Firewall: iptables, nftables, ufw, firewalld

↑ [[DO Этап 1 · Фундамент — Linux, Bash, сети|Этап 1 · Фундамент: Linux, Bash, сети]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~6 мин чтения</span><span class="chip">Уровень: junior</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> Сетевая безопасность хоста — обязательный навык: открыть нужные порты, закрыть остальное, не потеряв доступ к серверу.

## Принципы

- **default deny**: по умолчанию всё запрещено, явно разрешаем нужное;
- **stateful** фильтрация: состояния соединений (`NEW`, `ESTABLISHED`, `RELATED`) — ответы на разрешённые исходящие соединения проходят автоматически;
- порядок правил важен: первое подошедшее срабатывает;
- не запирайте себя: правила для SSH до смены политики по умолчанию; тестируйте с отложенным откатом (`at`/`sleep && iptables-restore`).

## Netfilter

Подсистема ядра Linux для фильтрации пакетов. Фронтенды: **iptables** (классика), **nftables** (современная замена), **ufw** и **firewalld** (упрощённые оболочки).

Цепочки (hooks): `PREROUTING` → (маршрутизация) → `INPUT` (локальные) / `FORWARD` (транзитные) → `OUTPUT` → `POSTROUTING`. Таблицы: `filter` (фильтрация), `nat`, `mangle`, `raw`.

## iptables

```bash
sudo iptables -L -n -v --line-numbers          # список правил со счётчиками
sudo iptables -P INPUT DROP                    # политика по умолчанию (осторожно!)

sudo iptables -A INPUT -i lo -j ACCEPT
sudo iptables -A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 22 -s 203.0.113.0/24 -j ACCEPT      # SSH только с доверенной сети
sudo iptables -A INPUT -p tcp -m multiport --dports 80,443 -j ACCEPT
sudo iptables -A INPUT -p icmp --icmp-type echo-request -m limit --limit 5/s -j ACCEPT
sudo iptables -A INPUT -j LOG --log-prefix "DROP: " --log-level 4
sudo iptables -D INPUT 5                       # удалить правило №5
sudo iptables-save > /etc/iptables/rules.v4    # сохранить (iptables-persistent)
sudo iptables-restore < /etc/iptables/rules.v4
```

## nftables

Единый синтаксис для IPv4/IPv6, наборы (`set`), карты, атомарное применение правил.

```bash
sudo nft list ruleset
```

```text
# /etc/nftables.conf
table inet filter {
  set trusted { type ipv4_addr; flags interval; elements = { 203.0.113.0/24 } }
  chain input {
    type filter hook input priority 0; policy drop;
    iif lo accept
    ct state established,related accept
    ct state invalid drop
    tcp dport 22 ip saddr @trusted accept
    tcp dport { 80, 443 } accept
    icmp type echo-request limit rate 5/second accept
  }
  chain forward { type filter hook forward priority 0; policy drop; }
  chain output  { type filter hook output priority 0; policy accept; }
}
```

```bash
sudo nft -f /etc/nftables.conf; sudo systemctl enable --now nftables
```

`iptables-nft` — совместимая оболочка поверх nftables (на новых дистрибутивах).

## ufw (Ubuntu)

```bash
sudo ufw default deny incoming; sudo ufw default allow outgoing
sudo ufw allow 22/tcp                       # либо limit 22/tcp (защита от перебора)
sudo ufw allow from 203.0.113.0/24 to any port 5432 proto tcp
sudo ufw allow 80,443/tcp
sudo ufw enable; sudo ufw status verbose numbered
sudo ufw delete 3
```

## firewalld (RHEL)

Понятие **зон** (public, internal, trusted) и сервисов.

```bash
sudo firewall-cmd --state
sudo firewall-cmd --get-active-zones
sudo firewall-cmd --zone=public --add-service=https --permanent
sudo firewall-cmd --zone=public --add-port=8080/tcp --permanent
sudo firewall-cmd --permanent --add-rich-rule='rule family="ipv4" source address="203.0.113.0/24" port port="5432" protocol="tcp" accept'
sudo firewall-cmd --reload
sudo firewall-cmd --list-all
```

`--permanent` сохраняет в конфигурацию, без него — до перезагрузки.

## Docker и firewall

Docker сам добавляет правила в iptables (цепочка `DOCKER`, NAT для `-p`). **Опубликованные порты обходят ufw/firewalld** (правила Docker применяются раньше). Защита: слушать на `127.0.0.1` (`-p 127.0.0.1:5432:5432`), использовать цепочку `DOCKER-USER` для своих ограничений, не публиковать порты БД наружу, размещать БД во внутренней сети.

## Kubernetes

Сетевую политику между подами задают **NetworkPolicy** (реализует CNI: Calico, Cilium). kube-proxy формирует правила iptables/IPVS для сервисов.

## Облачный уровень

Security Groups / NSG / сетевые ACL: stateful/stateless фильтры на уровне инстанса/подсети; принцип минимальных портов и источников; `0.0.0.0/0` на SSH и БД — недопустимо.

## Диагностика

```bash
sudo iptables -L -n -v | head; sudo nft list ruleset
sudo tcpdump -ni eth0 port 443 and host 1.2.3.4
nc -vz host port; nmap -sT -p 1-1024 host        # что видно снаружи (из другой сети!)
ss -tulpn                                        # слушает ли сервис
sudo dmesg | grep "DROP:"
conntrack -L | wc -l
```

Порядок: сервис слушает? → firewall хоста пропускает? → security group? → сетевой маршрут/ACL? → NAT/балансировщик.

## Вопросы с ответами

> [!question]- Что такое stateful firewall?
> Межсетевой экран, отслеживающий состояние соединений: разрешённые исходящие соединения автоматически пропускают ответный трафик без отдельных правил.

> [!question]- Почему порты Docker доступны снаружи, хотя ufw их закрывает?
> Docker вносит свои правила NAT и FORWARD в iptables раньше ufw. Публикуйте порты на `127.0.0.1` или фильтруйте в `DOCKER-USER`.

> [!question]- Как безопасно менять правила firewall по SSH?
> Сначала разрешить SSH, применять изменения с отложенным откатом (таймер), проверять вторым соединением и только потом закреплять.
