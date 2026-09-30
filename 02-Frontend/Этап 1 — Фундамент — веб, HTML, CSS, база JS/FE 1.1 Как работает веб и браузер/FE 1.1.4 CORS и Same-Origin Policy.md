---
type: topic
domain: frontend
stage: 1
section: "1.1"
order: 4
status: todo
level: junior
notion_id: 3ea33104867981018b3ad263fdb490a3
tags: [domain/frontend, stage/1, level/junior, topic/web, topic/security, topic/cors, priority/should]
reviewed:
next_review:
priority: should
time: 3
---

# CORS и Same-Origin Policy

↑ [[FE 1.1 Как работает веб и браузер|1.1 Как работает веб и браузер]] · ← [[FE 1.1.3 Хранилища — Cookies, localStorage, sessionStorage, IndexedDB|Предыдущая]] · → [[FE 1.1.5 Что происходит при вводе URL|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: junior</span></div>
<!-- meta:end -->





















> [!info] Зачем это на собесе
> Ошибка CORS видит каждый фронтендер; нужно уметь объяснить её причину и решение.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

**Origin** = схема + хост + порт. **Same-Origin Policy (SOP)**: скрипт с одного origin не может читать ответы с другого. Это защита от чтения данных чужого сайта от имени пользователя.

**CORS** — механизм, которым сервер **разрешает** чтение своих ответов другим origin через заголовки:

```http
Access-Control-Allow-Origin: https://app.example.com
Access-Control-Allow-Methods: GET, POST, PUT
Access-Control-Allow-Headers: Authorization, Content-Type
Access-Control-Allow-Credentials: true
Access-Control-Max-Age: 600
```

| Тип запроса | Поведение |
|---|---|
| «Простой» (GET/POST с простыми заголовками) | выполняется сразу, браузер проверяет ответ |
| «Непростой» (JSON, `Authorization`, PUT/DELETE) | сначала preflight `OPTIONS`, затем основной запрос |
| С credentials (`credentials: "include"`) | `Allow-Origin` не может быть `*`, нужен `Allow-Credentials: true` |

```js
fetch("https://api.example.com/orders", { credentials: "include", headers: { Authorization: `Bearer ${t}` } });
```

Решения проблемы в разработке: прокси dev-сервера (Vite `server.proxy`), корректные заголовки на бэкенде, общий домен через reverse proxy.

## Нюансы и подводные камни

- CORS блокирует **чтение ответа** браузером; сам запрос (для простых) до сервера доходит.
- CORS не защита API: curl и серверные клиенты его игнорируют.
- `Access-Control-Allow-Origin: *` вместе с credentials недопустим.
- Ошибка preflight (неверный ответ на `OPTIONS`) — частая причина «не работает».
- Разные порты и поддомены — разные origin.

## Практика

1. Воспроизведите CORS-ошибку, обращаясь с `localhost:5173` к API на другом порту.
2. Настройте прокси в Vite и уберите ошибку.
3. Настройте CORS на бэкенде с allowlist origin.

## Вопросы с ответами

> [!question]- Что такое Same-Origin Policy?
> Правило браузера, запрещающее скриптам одного origin читать ресурсы другого.

> [!question]- Для чего preflight?
> Браузер спрашивает разрешение у сервера, прежде чем отправлять «опасный» кросс-доменный запрос.

> [!question]- Защищает ли CORS сервер?
> Нет, он ограничивает браузер, а не серверные клиенты.

## Связанные темы

- [[N:3ea3310486798147bcb9d8a88f44b639]]
- [[N:3ea33104867981f3bab7cc9fe3d82992]]
