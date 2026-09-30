---
type: topic
domain: devops
stage: 4
order: 4
status: todo
level: middle
tags: [domain/devops, stage/4, level/middle, priority/should]
reviewed: 
next_review: 
priority: should
time: 7
---

# TLS в проде: Let's Encrypt, certbot, HSTS

↑ [[DO Этап 4 · Веб-серверы и сеть в проде — Nginx, TLS|Этап 4 · Веб-серверы и сеть в проде: Nginx, TLS]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~7 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> TLS — обязательный минимум. Спрашивают выпуск сертификатов, автоматическое продление и HSTS.

## Как работает TLS (кратко)

1. **ClientHello**: версии, шифры, SNI (имя хоста), расширения.
2. **ServerHello** + **сертификат** (цепочка: листовой → промежуточные CA).
3. Клиент проверяет подпись цепочки до доверенного корня, срок, **имя** (SAN), отзыв (OCSP).
4. Обмен ключами (**ECDHE**, forward secrecy) → общий сессионный ключ.
5. Шифрованный обмен (AES-GCM/ChaCha20). TLS 1.3 — 1 RTT, упрощённый набор шифров.

Сертификат связывает **открытый ключ** с **доменом**, подписан **CA**. Типы: DV (домен), OV/EV (организация), wildcard (`*.example.com`), multi-SAN, самоподписанные (только внутри, с доверенным корнем).

## Let's Encrypt и ACME

Бесплатный CA; сертификаты живут **90 дней**, автоматически продлеваются по протоколу **ACME**.

Проверки владения доменом (challenge):

| Challenge | Как | Когда |
|---|---|---|
| **HTTP-01** | файл по `http://domain/.well-known/acme-challenge/<token>` (порт 80) | один домен на сервере с доступом из интернета |
| **DNS-01** | TXT `_acme-challenge.domain` | **wildcard**, серверы без публичного порта 80, внутренние сервисы; нужен API DNS-провайдера |
| **TLS-ALPN-01** | на 443 | реже |

## certbot

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d example.com -d www.example.com          # получить и настроить nginx
sudo certbot certonly --webroot -w /var/www/certbot -d example.com   # только выпуск (webroot)
sudo certbot certonly --dns-cloudflare --dns-cloudflare-credentials /etc/cf.ini -d '*.example.com' -d example.com
sudo certbot renew --dry-run                                     # проверка автопродления
sudo certbot certificates
systemctl list-timers | grep certbot                             # таймер продления (дважды в день)
```

Сертификаты: `/etc/letsencrypt/live/<домен>/` (`fullchain.pem`, `privkey.pem`); **hook** после продления: `--deploy-hook "systemctl reload nginx"` (`/etc/letsencrypt/renewal-hooks/deploy/`).

Для HTTP-01 в nginx:

```nginx
server {
    listen 80;
    server_name example.com;
    location /.well-known/acme-challenge/ { root /var/www/certbot; }
    location / { return 301 https://$host$request_uri; }
}
```

В контейнерах: `certbot/certbot` + общий том, **Caddy** (автоматический TLS «из коробки»), **Traefik** (встроенный ACME), **cert-manager** в Kubernetes, `acme.sh`, `lego`. Лимиты Let's Encrypt (rate limits): не делать частых перевыпусков; staging-среда для тестов (`--staging`).

## Конфигурация Nginx для TLS

```nginx
server {
    listen 443 ssl;
    http2 on;
    server_name example.com;

    ssl_certificate     /etc/letsencrypt/live/example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/example.com/privkey.pem;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 1d;
    ssl_session_tickets off;
    ssl_stapling on; ssl_stapling_verify on;           # OCSP stapling
    resolver 1.1.1.1 8.8.8.8 valid=300s;

    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
}
```

Рекомендации профилей: генератор **Mozilla SSL Configuration** (Intermediate), проверка — **SSL Labs**, `testssl.sh`. Отключить SSLv3, TLS 1.0/1.1.

## HSTS

`Strict-Transport-Security: max-age=31536000; includeSubDomains; preload` заставляет браузер **всегда** использовать HTTPS для домена (защита от downgrade и SSL stripping).

- включать **после** проверки, что HTTPS работает везде (ошибка = недоступность сайта на срок `max-age`);
- начинать с малого `max-age` (300) и увеличивать;
- `includeSubDomains` — осторожно (все поддомены должны работать по HTTPS);
- `preload` — список в браузерах (hstspreload.org), откат сложен;
- заголовок действует только при доставке по HTTPS.

## Редирект HTTP → HTTPS

`return 301 https://$host$request_uri;` на порту 80. Внутренний трафик за прокси: терминация TLS на edge и `X-Forwarded-Proto`.

## Внутренние сервисы и mTLS

- внутренний CA (step-ca, Vault PKI, cert-manager `ClusterIssuer` CA) для сервисов без публичного доступа;
- **mTLS**: сервер проверяет клиентский сертификат (`ssl_verify_client on; ssl_client_certificate ca.pem;`), аутентификация сервис-сервис; service mesh (Istio/Linkerd) автоматизирует;
- **TLS до бэкенда** (`proxy_ssl_*`, re-encrypt) при требованиях безопасности.

## Мониторинг и эксплуатация

- **срок действия**: алерты за 14/7 дней (blackbox_exporter `probe_ssl_earliest_cert_expiry`, `x509-certificate-exporter`);
- тест продления (`--dry-run`) и после смены инфраструктуры; проверка, что **reload** подхватывает новый сертификат;
- защита `privkey.pem` (права 0600, владелец root), отдельные ключи на сервис, ротация при компрометации;
- цепочка сертификатов: использовать `fullchain.pem` (иначе ошибки у некоторых клиентов);
- **CAA**-записи DNS: ограничить, какие CA могут выпускать сертификаты;
- Certificate Transparency: мониторинг выпуска сертификатов на ваши домены (crt.sh).

## Диагностика

```bash
openssl s_client -connect example.com:443 -servername example.com -showcerts </dev/null | openssl x509 -noout -dates -subject -issuer -ext subjectAltName
curl -vI https://example.com
echo | openssl s_client -connect example.com:443 -tls1_3 2>/dev/null | grep -E "Protocol|Cipher"
```

| Ошибка | Причина |
|---|---|
| `certificate has expired` | не продлился: таймер, hook, DNS/порт 80 недоступны |
| `unable to get local issuer certificate` | не передана промежуточная цепочка (нужен fullchain) |
| `hostname mismatch` | домен не в SAN, SNI, default_server с другим сертификатом |
| Challenge failed | порт 80 закрыт/редирект, DNS указывает не туда, WAF, лимиты |
| Браузер «не защищено» | смешанный контент (HTTP-ресурсы на HTTPS-странице) |
| Старые клиенты не подключаются | отключены старые протоколы/шифры (компромисс) |

## Вопросы с ответами

> [!question]- Как автоматизировать продление сертификатов Let's Encrypt?
> `certbot` с таймером/cron (`certbot renew`), deploy-hook для reload nginx, мониторинг срока действия; в Kubernetes — cert-manager; Caddy/Traefik делают это сами.

> [!question]- Когда нужен DNS-01 challenge?
> Для wildcard-сертификатов и серверов, недоступных из интернета по порту 80: подтверждение через TXT-запись в DNS через API провайдера.

> [!question]- Что такое HSTS и чем он опасен?
> Заголовок, обязывающий браузер использовать только HTTPS на заданный срок. Ошибка конфигурации HTTPS при включённом HSTS делает сайт недоступным, а preload трудно откатить.
