---
type: topic
domain: devops
stage: 4
order: 1
status: todo
level: middle
tags: [domain/devops, stage/4, level/middle, priority/should]
reviewed: 
next_review: 
priority: should
time: 8
---

# Nginx: конфигурация, server, location, upstream

↑ [[DO Этап 4 · Веб-серверы и сеть в проде — Nginx, TLS|Этап 4 · Веб-серверы и сеть в проде: Nginx, TLS]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~8 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> Nginx — точка входа почти любого веб-проекта. Нужно понимать структуру конфигурации и правила выбора location.

## Архитектура

Событийная модель: **master** процесс (чтение конфигурации, управление) + **worker**-процессы (по одному на ядро, `worker_processes auto`), каждый обрабатывает тысячи соединений неблокирующе (epoll). Малое потребление памяти, высокая производительность; используется как веб-сервер, reverse proxy, балансировщик, TLS-терминатор, кэш.

## Структура конфигурации

`/etc/nginx/nginx.conf` (+ `conf.d/*.conf`, `sites-enabled/*`). Контексты: `main` → `events` → `http` → `server` → `location` (директивы наследуются вниз).

```nginx
user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log warn;
pid /run/nginx.pid;

events { worker_connections 4096; multi_accept on; }

http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;
    sendfile on; tcp_nopush on; tcp_nodelay on;
    keepalive_timeout 65;
    server_tokens off;                       # не раскрывать версию
    client_max_body_size 20m;

    log_format main '$remote_addr - $remote_user [$time_local] "$request" $status $body_bytes_sent '
                    '"$http_referer" "$http_user_agent" rt=$request_time urt=$upstream_response_time';
    access_log /var/log/nginx/access.log main;

    include /etc/nginx/conf.d/*.conf;
}
```

## server и server_name

```nginx
server {
    listen 80;
    listen [::]:80;
    server_name example.com www.example.com;
    return 301 https://example.com$request_uri;
}

server {
    listen 443 ssl;
    http2 on;
    server_name example.com;
    root /var/www/example;
    index index.html;
    # ...
}
```

Выбор виртуального хоста: по `listen` (адрес:порт), затем по заголовку `Host` и `server_name` (точное → `*.` префикс → суффикс → regex → `default_server`). Без совпадения — `default_server` (полезно отдавать 444/закрыть для неизвестных хостов).

## location: порядок выбора

| Синтаксис | Тип | Приоритет |
|---|---|---|
| `location = /path` | точное совпадение | 1 (наивысший) |
| `location ^~ /static/` | префикс; при совпадении regex не проверяются | 2 |
| `location ~ \.php$` | regex, чувствительный к регистру | 3 (по порядку в файле) |
| `location ~* \.(jpg\|png)$` | regex без учёта регистра | 3 |
| `location /prefix/` | обычный префикс (берётся самый длинный) | 4 |
| `location /` | запасной | |

Алгоритм: найти самый длинный префикс → если `=` или `^~` — выбрать → иначе проверить regex по порядку; первое совпадение выигрывает, иначе — запомненный префикс.

```nginx
location = /health { return 200 "ok\n"; add_header Content-Type text/plain; }
location ^~ /assets/ { expires 1y; add_header Cache-Control "public, immutable"; }
location ~* \.(?:css|js|woff2?|png|jpg|svg)$ { expires 30d; }
location / { try_files $uri $uri/ /index.html; }
```

## root, alias, try_files, return, rewrite

```nginx
location /img/ { root /var/www; }          # /img/a.png → /var/www/img/a.png
location /img/ { alias /data/images/; }     # /img/a.png → /data/images/a.png (alias заменяет префикс; завершающий / одинаковый!)
location / { try_files $uri $uri/ =404; }   # последовательная проверка файлов
return 301 https://$host$request_uri;       # редирект
rewrite ^/old/(.*)$ /new/$1 permanent;      # перезапись (предпочитайте return)
```

**`if` в location опасен** («if is evil») — используйте `map`, `try_files`, отдельные location.

## upstream (пул серверов)

```nginx
upstream api_backend {
    least_conn;                              # round-robin по умолчанию; ip_hash; hash $request_uri consistent; random
    server 10.0.1.10:8080 weight=3 max_fails=3 fail_timeout=10s;
    server 10.0.1.11:8080;
    server 10.0.1.12:8080 backup;
    keepalive 32;                            # пул keep-alive соединений к бэкендам
}

server {
    location /api/ {
        proxy_pass http://api_backend;
        proxy_http_version 1.1;
        proxy_set_header Connection "";      # для keepalive к upstream
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Пассивные проверки здоровья: `max_fails`/`fail_timeout`; активные — Nginx Plus или сторонние модули.

## map и переменные

```nginx
map $http_upgrade $connection_upgrade { default upgrade; '' close; }
map $status $loggable { ~^[23] 0; default 1; }          # не логировать 2xx/3xx
```

Встроенные переменные: `$host`, `$uri` (нормализованный), `$request_uri` (исходный), `$args`, `$remote_addr`, `$scheme`, `$request_time`, `$upstream_addr`, `$upstream_status`, `$http_*` (заголовки), `$cookie_*`.

## Проверка и управление

```bash
sudo nginx -t                        # проверка синтаксиса
sudo nginx -T | less                 # полная итоговая конфигурация
sudo nginx -s reload                 # перечитать без разрыва соединений
sudo systemctl reload nginx
curl -I -H "Host: example.com" http://127.0.0.1/
```

Типичные ошибки: забытый `;`, `proxy_pass` со слешем (`http://up/` и `http://up` ведут себя по-разному: с URI — заменяется префикс location), конфликт `server_name`, неправильный `root`/`alias`, права доступа к файлам (`403`), `502` — бэкенд недоступен, `413` — `client_max_body_size`, `504` — таймаут upstream.

## Вопросы с ответами

> [!question]- Как Nginx выбирает location?
> Находит самый длинный префикс; точное совпадение `=` и префикс `^~` выбираются сразу; иначе проверяются regex по порядку, первый подошедший выигрывает, иначе используется найденный префикс.

> [!question]- Чем root отличается от alias?
> `root` добавляет URI к пути (`root + uri`), `alias` заменяет часть URI, соответствующую location, на указанный путь.

> [!question]- Почему в Nginx не рекомендуют if?
> В контексте location он работает неинтуитивно (создаёт вложенный контекст, не все директивы совместимы), лучше использовать `map`, `try_files`, `return`.
