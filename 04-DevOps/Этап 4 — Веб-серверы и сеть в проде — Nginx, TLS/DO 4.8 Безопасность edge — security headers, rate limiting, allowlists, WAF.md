---
type: topic
domain: devops
stage: 4
order: 8
status: todo
level: middle
tags: [domain/devops, stage/4, level/middle, priority/should]
reviewed: 
next_review: 
priority: should
time: 7
---

# Безопасность edge: security headers, rate limiting, allowlists, WAF

↑ [[DO Этап 4 · Веб-серверы и сеть в проде — Nginx, TLS|Этап 4 · Веб-серверы и сеть в проде: Nginx, TLS]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~7 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> Edge — первая линия защиты: заголовки безопасности, ограничение частоты, allowlists, WAF.

## Заголовки безопасности

```nginx
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-Frame-Options "DENY" always;                         # или CSP frame-ancestors
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
add_header Permissions-Policy "geolocation=(), microphone=(), camera=()" always;
add_header Cross-Origin-Opener-Policy "same-origin" always;
add_header Cross-Origin-Resource-Policy "same-origin" always;
add_header Content-Security-Policy "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self' https://api.example.com; frame-ancestors 'none'; base-uri 'self'; form-action 'self'" always;
server_tokens off;
```

| Заголовок | Защита |
|---|---|
| **HSTS** | принудительный HTTPS |
| **CSP** | ограничение источников скриптов/стилей/запросов: защита от XSS, инъекций. Внедрять через `Content-Security-Policy-Report-Only` |
| **X-Content-Type-Options** | запрет угадывания MIME (MIME sniffing) |
| **X-Frame-Options / frame-ancestors** | защита от clickjacking |
| **Referrer-Policy** | утечка URL в Referer |
| **Permissions-Policy** | отключение возможностей браузера |
| **COOP/COEP/CORP** | изоляция контекстов, защита от Spectre-подобных атак |
| Cookie-флаги | `Secure; HttpOnly; SameSite` |

Проверка: securityheaders.com, Mozilla Observatory. `add_header ... always` — чтобы заголовки были и в ответах с ошибками; помните про наследование `add_header` (в location переопределяют, а не дополняют): выносите в `include snippets/security-headers.conf` и подключайте в каждом location с собственными `add_header`.

## Rate limiting и ограничение соединений

```nginx
http {
    limit_req_zone  $binary_remote_addr zone=perip:10m  rate=10r/s;
    limit_req_zone  $http_x_api_key      zone=perkey:10m rate=100r/s;
    limit_req_zone  $binary_remote_addr zone=login:10m  rate=5r/m;
    limit_conn_zone $binary_remote_addr zone=connperip:10m;
    limit_req_status 429; limit_conn_status 429;

    server {
        location /api/ {
            limit_req  zone=perip burst=20 nodelay;     # допускает всплеск 20 запросов сверх rate
            limit_conn connperip 20;
            proxy_pass http://api;
        }
        location = /auth/login {
            limit_req zone=login burst=5;               # защита от перебора паролей
            proxy_pass http://api;
        }
    }
}
```

- алгоритм **leaky bucket**; `burst` — очередь всплесков; `nodelay` — обслужить всплеск сразу, но ограничить дальнейшие;
- ключ: IP (`$binary_remote_addr`), API-ключ, пользователь; **за CDN/прокси** использовать реальный IP (`real_ip_header`, `set_real_ip_from` доверенных адресов), иначе лимит применяется к IP прокси;
- NAT и корпоративные сети: много пользователей на одном IP → мягкие пороги;
- лимиты для дорогих эндпоинтов отдельно; `Retry-After`; дополнительно лимиты в приложении/шлюзе (по пользователю/тарифу), защита от медленных атак: `client_header_timeout`, `client_body_timeout`, `send_timeout`, `limit_conn`.

## Allowlist / denylist

```nginx
location /admin/ { allow 10.0.0.0/8; allow 203.0.113.5; deny all; proxy_pass http://admin; }
location /metrics { allow 10.0.0.0/8; deny all; }
geo $blocked { default 0; 198.51.100.0/24 1; }
if ($blocked) { return 403; }                       # допустимое использование if: return
```

Доступ к внутренним эндпоинтам (`/metrics`, `/actuator`, `/swagger`, админ-панели) — только из доверенных сетей/через VPN; базовая аутентификация (`auth_basic`) как минимум; mTLS для админ-интерфейсов; блокировка по GeoIP (с оговорками), списки плохих ботов, фильтрация User-Agent (слабая мера).

## Защита от распространённых атак

- **Слабый TLS**: только TLS 1.2/1.3, современные шифры, HSTS;
- **Скрытие технологий**: `server_tokens off`, удаление `X-Powered-By` (`proxy_hide_header`);
- **Запрещённые методы**: `if ($request_method !~ ^(GET|POST|PUT|DELETE|OPTIONS)$) { return 405; }` (или `limit_except`);
- **Размеры**: `client_max_body_size`, `large_client_header_buffers`, `client_body_buffer_size`;
- **Path traversal**: корректный `alias` (завершающий слеш), `merge_slashes`;
- **Скрытые файлы**: `location ~ /\.(?!well-known) { deny all; }`, запрет `.git`, `.env`, бэкапов;
- **Open redirect / Host-header атаки**: `default_server` возвращает 444 для неизвестных Host;
- **SSRF через прокси**: не проксировать произвольные пользовательские адреса;
- **Slowloris**: таймауты, лимиты соединений;
- **Кэш-отравление**: осторожно с `proxy_cache_key` и `Vary`.

## WAF (Web Application Firewall)

Фильтрует L7-трафик по правилам: SQL-инъекции, XSS, RCE, path traversal, сканеры.

| Решение | Примечание |
|---|---|
| **ModSecurity** + **OWASP Core Rule Set (CRS)** | модуль Nginx (ModSecurity-nginx, libmodsecurity3), «SecRule», режимы DetectionOnly / On |
| **Coraza** | современный WAF на Go, совместим с CRS (модуль для Caddy, Envoy, Traefik) |
| **NAXSI** | Nginx: на основе whitelist/scoring |
| **Облачные WAF** | Cloudflare, AWS WAF, Yandex Smart Web Security, Akamai |
| **NGINX App Protect** | коммерческий |

Внедрение: сначала **DetectionOnly**, собрать ложные срабатывания, настроить исключения по правилам (`SecRuleRemoveById`), затем блокирующий режим; уровень параноидальности CRS (PL1–PL4); логирование в SIEM; обновление правил. WAF не заменяет безопасный код и валидацию, а снижает риск известных атак и даёт «виртуальные патчи».

```nginx
modsecurity on;
modsecurity_rules_file /etc/nginx/modsec/main.conf;    # включает CRS и SecRuleEngine DetectionOnly|On
```

## DDoS и боты

- CDN/защитный сервис (Cloudflare, Qrator, DDoS-Guard) перед origin; origin доступен только с адресов CDN;
- rate limiting, `limit_conn`, кэширование, отдача статики из CDN, автоматические челленджи (captcha), bot management;
- SYN-flood: `net.ipv4.tcp_syncookies`, лимиты на уровне L3/L4 (провайдер, iptables/nftables connlimit, XDP);
- мониторинг аномалий трафика и автоматические правила.

## Логи безопасности и реагирование

- логировать отказы (403/429/WAF), аномальные UA и пути (`/wp-login.php`, `/.env`), отправлять в SIEM;
- **fail2ban** по логам nginx (повторные 401/403/404, сканеры) → блокировка в firewall;
- алерты на всплески 4xx/5xx, рост запросов к служебным путям;
- регулярные тесты (`nikto`, `nmap`, `testssl.sh`, OWASP ZAP), своевременные обновления nginx и ОС.

## Вопросы с ответами

> [!question]- Как работает limit_req и что такое burst?
> Алгоритм «дырявого ведра»: запросы обслуживаются с заданной скоростью, `burst` позволяет временно принять всплеск сверх нормы; `nodelay` обрабатывает всплеск сразу, а превышение отклоняется (429).

> [!question]- Зачем Content-Security-Policy?
> Ограничивает источники скриптов, стилей, запросов и фреймов, снижая последствия XSS и инъекций; внедряют через Report-Only, затем блокирующий режим.

> [!question]- Как внедрять WAF без нарушения работы сайта?
> Включить в режиме обнаружения (DetectionOnly), проанализировать логи и настроить исключения для ложных срабатываний, затем перейти в блокирующий режим с мониторингом.
