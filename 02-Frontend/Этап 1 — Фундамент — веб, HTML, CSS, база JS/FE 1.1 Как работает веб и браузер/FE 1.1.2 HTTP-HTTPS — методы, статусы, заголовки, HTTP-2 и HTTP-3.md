---
type: topic
domain: frontend
stage: 1
section: "1.1"
order: 2
status: todo
level: junior
notion_id: 3ea331048679817ab843d2d18cee2479
tags: [domain/frontend, stage/1, level/junior, topic/web, topic/http, priority/should]
reviewed:
next_review:
priority: should
time: 3
---

# HTTP/HTTPS: методы, статусы, заголовки, HTTP/2 и HTTP/3

↑ [[FE 1.1 Как работает веб и браузер|1.1 Как работает веб и браузер]] · ← [[FE 1.1.1 DNS, TCP, TLS|Предыдущая]] · → [[FE 1.1.3 Хранилища — Cookies, localStorage, sessionStorage, IndexedDB|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: junior</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> HTTP — язык общения фронта и бэка; вопросы про методы, идемпотентность, коды и кэширование задают всем.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

Запрос: метод + URL + заголовки + тело. Ответ: код статуса + заголовки + тело.

| Метод | Назначение | Идемпотентен | Безопасен |
|---|---|---|---|
| GET | получить | да | да |
| POST | создать/выполнить действие | нет | нет |
| PUT | заменить | да | нет |
| PATCH | изменить часть | нет (обычно) | нет |
| DELETE | удалить | да | нет |
| OPTIONS | что разрешено (CORS preflight) | да | да |

| Классы кодов | Примеры |
|---|---|
| 2xx | 200 OK, 201 Created, 204 No Content |
| 3xx | 301/308 постоянный, 302/307 временный, 304 Not Modified |
| 4xx | 400, 401 (не аутентифицирован), 403 (нет прав), 404, 409, 422, 429 |
| 5xx | 500, 502, 503, 504 |

Важные заголовки: `Content-Type`, `Accept`, `Authorization`, `Cache-Control`, `ETag`/`If-None-Match`, `Set-Cookie`/`Cookie`, `Origin`, `Content-Security-Policy`, `Location`.

Версии протокола:

| Версия | Особенности |
|---|---|
| HTTP/1.1 | текстовый, keep-alive, до ~6 соединений на домен, head-of-line blocking |
| HTTP/2 | бинарный, мультиплексирование, сжатие заголовков (HPACK), server push (почти не используется) |
| HTTP/3 | QUIC поверх UDP, нет HOL-blocking транспорта, быстрая установка |

HTTPS = HTTP поверх TLS: шифрование, целостность, аутентификация сервера.

```js
const res = await fetch("/api/orders", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(order) });
if (!res.ok) throw new Error(`HTTP ${res.status}`);   // fetch не бросает исключение на 4xx/5xx
```

## Нюансы и подводные камни

- `fetch` отклоняется только при сетевой ошибке; статусы 4xx/5xx нужно проверять вручную.
- 401 и 403 путают: 401 — «кто вы?», 403 — «вам нельзя».
- Кэширование GET-запросов: не кладите чувствительные данные в URL.
- При HTTP/2 «спрайты» и склейка файлов уже не нужны в прежнем виде.
- `301` кэшируется браузером надолго.

## Практика

1. Посмотрите заголовки запроса и ответа для 3 сайтов в DevTools.
2. Отправьте POST через `fetch` и обработайте 400/500.
3. Проверьте условный запрос с ETag: 304 в Network.

## Вопросы с ответами

> [!question]- Чем PUT отличается от PATCH?
> PUT заменяет ресурс целиком, PATCH меняет часть.

> [!question]- Что такое идемпотентность?
> Повтор запроса даёт то же состояние, что и одиночный.

> [!question]- В чём выигрыш HTTP/2?
> Мультиплексирование запросов в одном соединении и сжатие заголовков.

## Связанные темы

- [[N:3ea3310486798116a40fe7fca0db88e4]]
- [[N:3ea3310486798147bcb9d8a88f44b639]]
