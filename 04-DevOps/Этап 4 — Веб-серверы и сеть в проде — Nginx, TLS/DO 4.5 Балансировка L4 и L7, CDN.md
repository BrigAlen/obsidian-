---
type: topic
domain: devops
stage: 4
order: 5
status: todo
level: middle
tags: [domain/devops, stage/4, level/middle, priority/should]
reviewed: 
next_review: 
priority: should
time: 6
---

# Балансировка L4 и L7, CDN

↑ [[DO Этап 4 · Веб-серверы и сеть в проде — Nginx, TLS|Этап 4 · Веб-серверы и сеть в проде: Nginx, TLS]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~6 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> Балансировка — основа отказоустойчивости и масштабирования. Нужно различать L4 и L7 и знать алгоритмы и health-checks.

## Зачем

Распределение нагрузки между экземплярами, **отказоустойчивость** (исключение упавших), масштабирование (добавление узлов), обновления без простоя, терминация TLS, единая точка входа.

## L4 и L7

| | L4 (транспортный) | L7 (прикладной) |
|---|---|---|
| Видит | IP, порт, TCP/UDP | HTTP: путь, заголовки, cookie, метод, хост |
| Работа | пересылка соединений (NAT/прокси) | разбор HTTP, маршрутизация по содержимому |
| Производительность | очень высокая, малая задержка | выше нагрузка на CPU |
| Возможности | балансировка TCP (БД, SMTP, gRPC-passthrough), TLS passthrough | маршрутизация по URL/Host, TLS termination, WAF, кэш, rate limit, rewrite, canary |
| Примеры | LVS/IPVS, HAProxy (mode tcp), AWS NLB, Nginx `stream`, MetalLB, kube-proxy | Nginx, HAProxy (mode http), Envoy, Traefik, AWS ALB, Ingress |

Часто комбинация: L4 на входе (NLB) → L7 (Nginx/Envoy) → сервисы.

## Алгоритмы

| Алгоритм | Суть | Когда |
|---|---|---|
| **Round robin** | по кругу | одинаковые узлы и запросы |
| **Weighted RR** | с весами | разная мощность |
| **Least connections** | узел с наименьшим числом соединений | запросы разной длительности |
| **IP hash / consistent hash** | один клиент/ключ → один узел | sticky sessions, кэши |
| **Random (power of two choices)** | два случайных, выбрать менее загруженный | большие пулы |
| **Least time** | минимальное время ответа (Nginx Plus, HAProxy) | |
| **Geo / latency-based** | по региону | DNS/GSLB |

## Sticky sessions (сессионная привязка)

Направление пользователя на один и тот же узел (cookie, ip_hash). Минусы: неравномерность, потеря сессии при падении узла, мешает масштабированию. **Предпочтительнее stateless-сервисы** и внешнее хранилище сессий (Redis) или JWT.

## Health checks

- **пассивные**: по ошибкам реальных запросов (`max_fails`, `fail_timeout` в Nginx);
- **активные**: периодический запрос `/health` (HAProxy `option httpchk`, Envoy, облачные LB, Nginx Plus);
- критерии: код 200, время ответа, содержимое; пороги `rise`/`fall`;
- различать **liveness** и **readiness**: узел выводится из пула, пока не готов; graceful drain при деплое.

```nginx
# Nginx: балансировка L7
upstream api { least_conn; server 10.0.1.10:8080 max_fails=3 fail_timeout=10s; server 10.0.1.11:8080; keepalive 32; }

# Nginx stream: L4 для PostgreSQL/TCP
stream {
    upstream pg { server 10.0.2.10:5432; server 10.0.2.11:5432 backup; }
    server { listen 5432; proxy_pass pg; proxy_connect_timeout 3s; }
}
```

```text
# HAProxy
frontend https_in
    bind *:443 ssl crt /etc/haproxy/certs/site.pem alpn h2,http/1.1
    acl is_api path_beg /api
    use_backend api_be if is_api
    default_backend web_be
backend api_be
    balance leastconn
    option httpchk GET /health/ready
    http-check expect status 200
    default-server inter 3s fall 3 rise 2 maxconn 500
    server api1 10.0.1.10:8080 check
    server api2 10.0.1.11:8080 check
```

## Отказоустойчивость самого балансировщика

Балансировщик — потенциальная единая точка отказа:

- **пара в HA**: **keepalived** (VRRP) с плавающим **VIP**; активный/пассивный или активный/активный (DNS round robin, ECMP);
- управляемые облачные LB (многозонные);
- **Anycast** и BGP (MetalLB в BGP-режиме);
- DNS-балансировка и **GSLB** (Route 53, Cloudflare Load Balancing): health checks, geo-routing, failover между регионами (ограничено TTL).

## Kubernetes

- **Service** (ClusterIP): L4 балансировка kube-proxy (iptables/IPVS) по подам с Ready;
- **Service type LoadBalancer**: облачный L4 LB; `MetalLB` на bare metal;
- **Ingress / Gateway API**: L7 маршрутизация;
- внешняя политика трафика (`externalTrafficPolicy: Local` сохраняет IP клиента);
- **service mesh** (Envoy): клиентская балансировка, retries, circuit breaker; gRPC требует L7/клиентской балансировки (долгие HTTP/2-соединения «прилипают» к одному поду при L4).

## CDN

**Content Delivery Network**: распределённые edge-серверы кэшируют контент ближе к пользователю.

- статика (js/css/изображения/видео), иногда API-ответы; снижение задержек и нагрузки на origin;
- **DDoS-защита, WAF, TLS-терминация, HTTP/3, сжатие**, оптимизация изображений;
- кэширование: `Cache-Control`, `s-maxage`, `Vary`, **инвалидация** (purge по URL/тегу) или версионирование имён;
- защита origin: принимать трафик только от CDN (ip allowlist, секретный заголовок, mTLS/authenticated origin pulls);
- `stale-while-revalidate`, `stale-if-error` — устойчивость при недоступности origin;
- поставщики: Cloudflare, Fastly, Akamai, CloudFront, Яндекс CDN/Cloud CDN; self-hosted: Nginx cache, Varnish.
- внимание: корректный `Host`, реальный IP клиента (`CF-Connecting-IP`, `X-Forwarded-For` доверенные диапазоны), cookies и персональные ответы не кэшировать.

## Практика

- обновления без простоя: drain (вывод узла, ожидание завершения запросов), `maxUnavailable`, readiness;
- **connection draining/ deregistration delay**;
- лимиты: `maxconn`, очереди, `queue timeout`, защита от перегрузки (load shedding, 503 Retry-After);
- **ретраи** осторожно (идемпотентные, бюджеты, backoff) — риск шторма повторов;
- **circuit breaker**, таймауты на всех уровнях;
- мониторинг: RPS, латентность p95/p99, 5xx, активные соединения, состояния backend'ов, насыщение.

## Вопросы с ответами

> [!question]- Чем L4 балансировка отличается от L7?
> L4 работает на уровне TCP/UDP без разбора содержимого (быстро, универсально); L7 разбирает HTTP и маршрутизирует по URL, заголовкам, cookie, умеет TLS termination, кэш, WAF.

> [!question]- Как обеспечить отказоустойчивость самого балансировщика?
> Пара узлов с keepalived (VRRP) и плавающим VIP, управляемые многозонные облачные балансировщики, Anycast/ECMP или DNS/GSLB с health checks.

> [!question]- Зачем нужен CDN и какие риски?
> Кэширует контент рядом с пользователями, снижает задержку и нагрузку на origin, защищает от DDoS. Риски: устаревший кэш (нужна инвалидация/версионирование), утечка персональных ответов при неверном кэшировании, необходимость защитить origin.
