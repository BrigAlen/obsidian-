---
type: topic
domain: devops
stage: 1
order: 14
status: todo
level: junior
tags: [domain/devops, stage/1, level/junior, priority/should]
group: Сети
reviewed: 
next_review: 
priority: should
time: 5
---

# DNS для DevOps: записи, резолвинг, /etc/hosts, resolv.conf

↑ [[DO Этап 1 · Фундамент — Linux, Bash, сети|Этап 1 · Фундамент: Linux, Bash, сети]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~5 мин чтения</span><span class="chip">Уровень: junior</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> «Это всегда DNS». Нужно понимать записи, процесс резолвинга, кэши и как диагностировать проблемы.

## Как работает DNS

Иерархическая распределённая БД имён: `www.example.com.` = корень `.` → TLD `com` → домен `example` → хост `www`.

**Резолвинг** (упрощённо):

1. Приложение обращается к **stub resolver** (libc, systemd-resolved): кэш и `/etc/hosts`.
2. Запрос уходит **рекурсивному резолверу** (провайдер, `8.8.8.8`, внутренний).
3. Резолвер, если нет в кэше, опрашивает **корневые серверы** → серверы TLD (`com`) → **авторитетный сервер** домена.
4. Ответ кэшируется на время **TTL**.

Транспорт: UDP/53 (и TCP/53 для больших ответов, зонных трансферов, DNSSEC); DoT (853), DoH (443).

## Типы записей

| Запись | Назначение | Пример |
|---|---|---|
| **A** | имя → IPv4 | `api A 203.0.113.10` |
| **AAAA** | имя → IPv6 | |
| **CNAME** | алиас на другое имя | `www CNAME example.com.` (нельзя на корне зоны и вместе с другими записями) |
| **MX** | почтовые серверы (приоритет) | `MX 10 mail.example.com.` |
| **TXT** | текст: SPF, DKIM, DMARC, подтверждение домена, ACME | `TXT "v=spf1 include:_spf.google.com ~all"` |
| **NS** | авторитетные серверы зоны | |
| **SOA** | параметры зоны (serial, refresh, TTL) | |
| **PTR** | обратная запись IP → имя | `10.113.0.203.in-addr.arpa` |
| **SRV** | сервис, порт, вес | `_sip._tcp SRV 10 60 5060 sip.example.com.` |
| **CAA** | какие CA могут выпускать сертификаты | |
| **ALIAS/ANAME** | CNAME на корне (у провайдера) | |

**TTL**: время кэширования. Перед миграцией за дни **снижайте TTL** (до 60–300 с), после — возвращайте.

## Инструменты

```bash
dig example.com                       # полный ответ
dig +short A example.com
dig @8.8.8.8 example.com MX           # конкретный резолвер
dig +trace example.com                # проход от корня
dig -x 203.0.113.10                   # PTR
dig +noall +answer +ttlunits api.example.com
nslookup example.com; host example.com
resolvectl status; resolvectl query example.com       # systemd-resolved
getent hosts example.com              # как видит приложение (учитывает /etc/hosts и nsswitch)
```

В ответе `dig`: `status: NOERROR / NXDOMAIN (нет имени) / SERVFAIL (ошибка сервера) / REFUSED`, флаги (`aa` — авторитетный), `ANSWER SECTION`, время запроса.

## Локальные файлы

**`/etc/hosts`**: статические соответствия (приоритетнее DNS по `nsswitch`):

```text
127.0.0.1   localhost
10.0.0.15   db.internal db
```

**`/etc/resolv.conf`**: резолверы и поиск:

```text
nameserver 10.0.0.2
nameserver 1.1.1.1
search internal.example.com example.com
options timeout:2 attempts:2 ndots:1
```

- `search` — домены для дополнения коротких имён (`db` → `db.internal.example.com`);
- `ndots` — порог точек, при котором имя считается абсолютным (в **Kubernetes `ndots:5`** приводит к множеству лишних запросов — оптимизируют через FQDN с точкой на конце или `dnsConfig`);
- на современных системах `resolv.conf` управляется **systemd-resolved** (`127.0.0.53`) или NetworkManager: правьте через их конфигурацию.

`/etc/nsswitch.conf`: порядок источников имён (`hosts: files dns`).

## DNS в контейнерах и Kubernetes

- Docker: встроенный DNS (`127.0.0.11`) резолвит имена сервисов в пользовательских сетях;
- Kubernetes: CoreDNS; имена `<svc>.<ns>.svc.cluster.local`, поды получают `search` домены кластера;
- проблемы: перегрузка CoreDNS, `ndots`, отсутствие кэширования → NodeLocal DNSCache.

## Балансировка и отказоустойчивость

- несколько A-записей (round-robin DNS), **GeoDNS**, weighted, health-checked (Route 53, Cloudflare);
- failover через DNS ограничен TTL и кэшами клиентов;
- split-horizon DNS: разные ответы для внутренних и внешних клиентов.

## Типовые проблемы

| Симптом | Причина и проверка |
|---|---|
| После смены записи старый адрес | кэш: TTL, кэш резолвера/браузера/приложения (Java кэширует JVM, .NET `DnsRefreshTimeout`) |
| Работает по IP, не по имени | DNS недоступен, неверный `resolv.conf`, firewall на 53 |
| Внутреннее имя не резолвится | нет записи, неверный search-домен, split-horizon |
| Медленные запросы, задержка 5 с | недоступный первый resolver (timeout), IPv6/AAAA, `ndots` |
| Разные ответы на разных серверах | не завершилась репликация зон, разные кэши |
| NXDOMAIN | имя не существует (опечатка, запись не создана) |
| Сертификат Let's Encrypt не выдаётся | DNS-01: TXT `_acme-challenge` не опубликован |

Порядок диагностики: `getent hosts name` (как видит система) → `dig name` (резолвер по умолчанию) → `dig @авторитетный name` → `dig +trace` → сравнить с ожиданиями, TTL.

## Безопасность

DNSSEC (подписи зон), DoT/DoH, защита от cache poisoning, ограничение рекурсии (open resolver → DDoS amplification), внимание к dangling CNAME (subdomain takeover).

## Вопросы с ответами

> [!question]- Что происходит, когда вы набираете example.com в браузере (DNS-часть)?
> Проверяется кэш браузера/ОС и `/etc/hosts`, затем запрос рекурсивному резолверу, который при отсутствии кэша обходит корень → TLD → авторитетный сервер; ответ кэшируется на время TTL.

> [!question]- Чем CNAME отличается от A?
> A указывает имя на IP-адрес, CNAME — на другое имя (алиас). CNAME нельзя ставить на корень зоны и совмещать с другими записями того же имени.

> [!question]- Почему после смены DNS-записи часть пользователей видит старый адрес?
> Из-за кэширования: TTL записи, кэши резолверов, ОС, браузеров и приложений. Перед миграцией понижают TTL заранее.
