---
type: topic
domain: devops
stage: 4
order: 7
status: todo
level: middle
tags: [domain/devops, stage/4, level/middle, priority/should]
reviewed: 
next_review: 
priority: should
time: 5
---

# Эксплуатация Nginx: reload без простоя, диагностика 4xx и 5xx

↑ [[DO Этап 4 · Веб-серверы и сеть в проде — Nginx, TLS|Этап 4 · Веб-серверы и сеть в проде: Nginx, TLS]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~5 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> Типовой сценарий: «пользователи получают 502/504, что делать?» Нужно знать reload без простоя и методичную диагностику.

## Управление

```bash
sudo nginx -t                        # проверка конфигурации (ВСЕГДА перед reload)
sudo nginx -T                        # вывести итоговую конфигурацию со всеми include
sudo systemctl reload nginx          # = nginx -s reload (HUP мастеру)
sudo nginx -s reopen                 # переоткрыть логи (после logrotate)
sudo nginx -s quit                   # graceful остановка; stop — немедленная
sudo nginx -V                        # версия и модули сборки
```

## Reload без простоя

При `reload` master-процесс:

1. проверяет новую конфигурацию (при ошибке остаётся старая);
2. запускает **новые worker** с новой конфигурацией;
3. посылает **старым worker** сигнал graceful shutdown: они **дорабатывают текущие запросы** и завершаются;
4. новые соединения обслуживают новые worker.

Поэтому reload не рвёт соединения. Замечания:

- `restart` останавливает всё: короткий простой; используйте `reload`;
- долгие соединения (WebSocket, SSE, стриминг) удерживают старые worker'ы; `worker_shutdown_timeout 30s;` принудительно завершит;
- сертификаты подхватываются при reload;
- изменения порта/бинарного файла — `upgrade` (USR2) или перезапуск;
- в Kubernetes/compose при смене конфигурации пересоздаётся контейнер: обеспечить rolling.

Безопасный паттерн деплоя конфигурации: `nginx -t && nginx -s reload || откат` (хранить предыдущую версию, выкатывать через Ansible с валидацией: `validate: nginx -t -c %s`).

## Логи

- `error_log` с уровнем (`warn` по умолчанию; `debug` временно, требует сборки с `--with-debug`); `error_log /dev/stderr` в контейнерах;
- `access_log` с полезными полями (время, upstream, `$request_time`, `$upstream_response_time`, `$request_id`, `$trace_id`), отключать для health-check;
- **ротация**: logrotate + `nginx -s reopen` (или `USR1`);
- условное логирование: `map` + `access_log ... if=$loggable`.

## Диагностика 4xx

| Код | Причина | Проверка |
|---|---|---|
| **400** Bad Request | некорректный запрос/заголовки, слишком большие cookie (`large_client_header_buffers`), HTTP на HTTPS-порт | error.log, `curl -v` |
| **401/403** | авторизация, права файла (`403` при отсутствии `x` на каталоге/индексе), `deny`, WAF, `autoindex off` без index | права `namei -l path`, `allow/deny` |
| **404** | нет файла/маршрута, неверные `root`/`alias`, `proxy_pass` со слешем, fallback SPA | `try_files`, лог `open() failed` |
| **405** | метод запрещён (статика не принимает POST) | конфигурация |
| **408** | клиент слишком долго отправлял запрос | `client_body_timeout` |
| **413** | тело больше `client_max_body_size` | увеличить |
| **414/431** | слишком длинный URI/заголовки | буферы |
| **429** | сработал `limit_req`/лимит бэкенда | `limit_req_status` |
| **499** | клиент закрыл соединение, не дождавшись ответа (нестандартный код nginx) | медленный бэкенд, таймаут клиента/LB |

## Диагностика 5xx

| Код | Причина | Что смотреть |
|---|---|---|
| **500** | ошибка приложения/конфигурации (цикл rewrite) | error.log nginx, логи приложения |
| **502 Bad Gateway** | upstream недоступен или закрыл соединение, невалидный ответ | `connect() failed (111: Connection refused)`, `upstream prematurely closed connection`, упал процесс, неверный порт/сокет, SELinux (`setsebool -P httpd_can_network_connect 1`), DNS/IP контейнера изменился, `recv() failed (104: Connection reset)` |
| **503** | нет живых upstream, `limit_conn`, сервис перегружен/на обслуживании | `no live upstreams`, health, лимиты |
| **504 Gateway Timeout** | upstream не ответил за `proxy_read_timeout` | медленный запрос в приложении/БД, блокировки, нехватка ресурсов |
| **520–530** (Cloudflare) | проблемы origin | логи origin и CDN |

Пошагово для 502/504:

1. **error.log**: точное сообщение (`upstream timed out while reading response header`; `connect() failed`; `no live upstreams`).
2. **Обращение к бэкенду напрямую**: `curl -v http://10.0.1.10:8080/health` с сервера nginx.
3. **Состояние бэкенда**: процесс жив (`systemctl status`, `docker ps`), порт слушает (`ss -tulpn`), ресурсы (CPU, память, OOM, соединения).
4. **Логи приложения и БД** в то же время (по `trace_id`/`request_id`).
5. **Таймауты**: нормальное ли время ответа? Сравнить `$upstream_response_time` и `proxy_read_timeout`.
6. **Сеть/DNS/firewall** между nginx и бэкендом, лимиты `worker_connections`, `ulimit -n`.
7. **Недавние изменения**: деплой, конфигурация, сертификаты, обновления.

## Ресурсы и лимиты

- `worker_connections` × `worker_processes` ≥ нужное число соединений (учитывайте **два соединения на проксируемый запрос**);
- `worker_rlimit_nofile`, `ulimit -n`, `LimitNOFILE` в systemd (ошибка `Too many open files`);
- `error_log`: `worker_connections are not enough`, `socket() failed`;
- память: буферы, кэш (`proxy_cache_path` с `max_size`); диск: логи, кэш, временные файлы;
- `net.core.somaxconn`, `net.ipv4.ip_local_port_range`, TIME_WAIT (`keepalive` к upstream снижает число новых соединений);
- CPU: TLS handshake, gzip высокого уровня.

## Мониторинг

`stub_status`, nginx-exporter, логи → метрики; алерты: рост 5xx, p95 латентности, активные соединения около предела, ошибки reload, срок сертификатов, недоступность upstream, `worker_connections are not enough`.

## Обновление и безопасность

- обновления безопасности Nginx (CVE), актуальные модули; `nginx -V` для проверки;
- минимальные права (`user nginx`), права на конфигурацию и ключи (600), скрыть версию;
- конфигурация в Git, валидация в CI (`nginx -t` в контейнере: `docker run --rm -v $PWD:/etc/nginx:ro nginx nginx -t`), линтеры (gixy);
- управление через Ansible/шаблоны; аудит изменений.

## Вопросы с ответами

> [!question]- Что происходит при nginx -s reload?
> Master проверяет конфигурацию, запускает новых worker'ов, старым посылает сигнал graceful shutdown: они доводят текущие запросы и завершаются. Соединения не рвутся, при ошибке остаётся старая конфигурация.

> [!question]- Как отличить 502 от 504 и что проверять?
> 502 — upstream недоступен или оборвал соединение (проверить процесс, порт, сеть, падения). 504 — upstream не ответил вовремя (медленные запросы, БД, ресурсы, таймаут). Начинать с error.log nginx и прямого запроса к бэкенду.

> [!question]- Что означает код 499 в логах nginx?
> Клиент закрыл соединение до получения ответа (нестандартный код nginx): бэкенд слишком медленный или клиентский/балансировщик таймаут короче.
