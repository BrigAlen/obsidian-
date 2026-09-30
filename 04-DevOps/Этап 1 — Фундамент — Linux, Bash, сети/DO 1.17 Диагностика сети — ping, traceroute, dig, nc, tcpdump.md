---
type: topic
domain: devops
stage: 1
order: 17
status: todo
level: junior
tags: [domain/devops, stage/1, level/junior, priority/should]
group: Сети
reviewed: 
next_review: 
priority: should
time: 5
---

# Диагностика сети: ping, traceroute, dig, nc, tcpdump

↑ [[DO Этап 1 · Фундамент — Linux, Bash, сети|Этап 1 · Фундамент: Linux, Bash, сети]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~5 мин чтения</span><span class="chip">Уровень: junior</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> «Сайт не открывается» — основа сценарного интервью. Важна последовательность проверок и знание инструментов каждого уровня.

## Алгоритм

1. **Воспроизвести** и уточнить: кому и откуда недоступно, что именно (ошибка/таймаут), когда началось, что менялось.
2. **Сузить уровень**: DNS → маршрут → порт → TLS → HTTP → приложение.
3. **Проверить с разных точек** (клиент, сервер, другая сеть).
4. Собрать доказательства (вывод команд, пакеты), зафиксировать.

## ping и traceroute/mtr

```bash
ping -c 4 8.8.8.8            # доступность по ICMP и RTT (ICMP может быть закрыт — «нет ping» ≠ «недоступно»)
ping -c 4 example.com        # отличить DNS от сети
ping -M do -s 1472 host      # проверка MTU (DF-бит, 1472 + 28 = 1500)
traceroute example.com       # маршрут по TTL; traceroute -T -p 443 (по TCP)
mtr -rwzbc 100 example.com   # комбинированно: потери и задержка по каждому хопу
```

Чтение mtr: потери **на промежуточном хопе, не продолжающиеся дальше** — ограничение ICMP на роутере, не проблема; потери, сохраняющиеся до конечного узла — реальная проблема.

## dig и DNS

```bash
dig +short example.com
dig @1.1.1.1 example.com
dig +trace example.com
resolvectl query example.com; getent hosts example.com
```

## nc (netcat) и порты

```bash
nc -vz host 443                 # TCP: открыт ли порт
nc -vzu host 53                 # UDP (менее надёжно)
nc -l 9000                      # слушать порт (проверка firewall на приёмной стороне)
echo "GET / HTTP/1.0\r\n\r\n" | nc host 80
# bash без nc
timeout 3 bash -c '</dev/tcp/host/443' && echo open || echo closed
```

Интерпретация: `Connection refused` — хост достижим, порт никто не слушает (или RST от firewall); `timed out` — пакеты теряются/DROP (firewall, маршрут, хост недоступен); `No route to host` — ICMP unreachable.

## curl для L7

```bash
curl -v https://example.com                # TLS, заголовки, статус
curl -I https://example.com                # только заголовки
curl -w "@format.txt" -o /dev/null -s URL  # тайминги
curl --resolve example.com:443:203.0.113.10 https://example.com    # конкретный IP (обход DNS/балансировщика)
curl -H "Host: example.com" http://203.0.113.10/
openssl s_client -connect example.com:443 -servername example.com -showcerts </dev/null   # сертификат, цепочка, срок
openssl x509 -noout -dates -subject -issuer -in cert.pem
```

## tcpdump и Wireshark

Перехват пакетов — «правда на проводе».

```bash
sudo tcpdump -ni any port 443 and host 203.0.113.10
sudo tcpdump -ni eth0 -w capture.pcap 'tcp port 5432'        # в файл → Wireshark
sudo tcpdump -ni any 'tcp[tcpflags] & (tcp-syn|tcp-rst) != 0'     # только SYN и RST
sudo tcpdump -ni any udp port 53
sudo tcpdump -A -s0 port 80                                      # содержимое HTTP (незашифрованное)
```

Что искать:

- **SYN без SYN-ACK** — пакет не доходит или DROP на пути;
- **SYN → RST** — порт закрыт;
- повторные передачи (`retransmission`), нулевое окно (`zero window`) — проблемы пропускной способности/получателя;
- неполное TLS-рукопожатие;
- разные IP в запросе и ответе (асимметрия, NAT);
- большие пакеты не проходят (MTU).

Правила: фильтровать по хосту/порту, ограничивать время и объём (`-c 1000`), не захватывать чувствительные данные без необходимости; `-n` без резолвинга.

## ss, ip, ethtool

```bash
ss -tulpn; ss -tan state established '( dport = :443 )'; ss -ti dst host     # метрики TCP: rtt, cwnd, retrans
ip -s link show eth0                    # ошибки и drops интерфейса
ip route get 203.0.113.10; ip neigh
ethtool eth0; ethtool -S eth0 | grep -i -E 'err|drop'
```

## Другие инструменты

- `nmap -sT -p 1-1000 host`: сканирование портов (только со своими системами!);
- `iperf3 -s` / `iperf3 -c host`: пропускная способность;
- `nslookup`, `host`, `whois`;
- `arping`, `ip neigh`: L2;
- `ss -s`, `netstat -s`: статистика протоколов;
- `iftop`, `nethogs`, `bmon`: кто использует канал;
- `curl -w` и `httpstat`; `hey`, `wrk`, `k6`: нагрузка.

## Сценарий: «сайт не открывается»

| Шаг | Проверка | Вывод |
|---|---|---|
| 1 | `dig site.com` | нет ответа → DNS |
| 2 | `ping IP` / `mtr IP` | нет → сеть/маршрут |
| 3 | `nc -vz IP 443` | refused → сервис не слушает/закрыт; timeout → firewall/SG |
| 4 | `openssl s_client` | ошибка → сертификат/TLS |
| 5 | `curl -v` | 502/503/504 → бэкенд/прокси; 404 → маршрутизация; 403 → права/WAF |
| 6 | на сервере: `ss -tulpn`, логи nginx/приложения, ресурсы | сервис упал, перегружен |
| 7 | изменения: деплой, сертификат, DNS, firewall | откат/исправление |

## Вопросы с ответами

> [!question]- Чем отличается «Connection refused» от «timed out»?
> Refused — пакет дошёл, но на порту никто не слушает (RST). Timed out — ответа нет: пакеты отбрасываются (firewall, SG, маршрут) или хост недоступен.

> [!question]- Почему потери на промежуточных хопах mtr не всегда проблема?
> Многие роутеры ограничивают ответы ICMP для самих себя, хотя транзитный трафик пропускают. Проблема, если потери сохраняются до конечного узла.

> [!question]- Как проверить, что сертификат на сервере корректен и не истёк?
> `openssl s_client -connect host:443 -servername host` и `openssl x509 -noout -dates`, либо `curl -v`.
