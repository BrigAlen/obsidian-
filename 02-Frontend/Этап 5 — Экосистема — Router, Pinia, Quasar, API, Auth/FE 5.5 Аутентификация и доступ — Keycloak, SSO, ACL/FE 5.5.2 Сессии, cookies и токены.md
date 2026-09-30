---
type: topic
domain: frontend
stage: 5
section: "5.5"
order: 2
status: todo
level: middle
notion_id: 3ea3310486798172bf0eddbc19555afa
tags: [domain/frontend, stage/5, level/middle, topic/auth, topic/cookies, topic/sessions, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Сессии, cookies и токены

↑ [[FE 5.5 Аутентификация и доступ — Keycloak, SSO, ACL|5.5 Аутентификация и доступ: Keycloak, SSO, ACL]] · ← [[FE 5.5.1 Аутентификация и авторизация — различия|Предыдущая]] · → [[FE 5.5.3 JWT — access и refresh токены|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->





> [!info] Зачем это на собесе
> Сессия против токена, флаги cookie и CSRF — классика веб-безопасности.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

| Модель | Как работает | Плюсы | Минусы |
|---|---|---|---|
| Серверная сессия | сервер хранит состояние, клиенту отдаёт `session_id` в cookie | легко отозвать, данные на сервере | состояние на сервере (хранилище, масштабирование) |
| Токен (JWT, opaque) | клиент хранит токен и отправляет в заголовке/cookie | stateless, удобно для API и микросервисов | сложнее отзыв, риск при краже |
| Cookie-based token | токен в `HttpOnly` cookie | недоступен JS (защита от XSS-кражи) | нужна защита от CSRF |

Флаги cookie:

| Флаг | Смысл |
|---|---|
| `HttpOnly` | недоступна из JS |
| `Secure` | только HTTPS |
| `SameSite=Lax/Strict/None` | ограничение кросс-сайтовой отправки (CSRF) |
| `Path`, `Domain`, `Max-Age` | область и срок |
| `__Host-` префикс | жёсткие ограничения (Secure, Path=/, без Domain) |

**Атаки и защита**:

| Атака | Защита |
|---|---|
| XSS (внедрение скрипта) → кража токена из `localStorage` | `HttpOnly` cookie, CSP, экранирование, санитайзинг |
| CSRF (запрос от чужого сайта с cookie) | `SameSite`, CSRF-токены, проверка `Origin`, кастомные заголовки |
| Session fixation | новая сессия после входа |
| Перехват | HTTPS, HSTS |
| Кража refresh-токена | ротация, привязка к устройству, обнаружение повторного использования |

Сценарии:

- **SPA + собственный бэкенд на том же сайте**: сессионная cookie (`HttpOnly; Secure; SameSite=Lax`) — простой и надёжный вариант.
- **SPA + внешний API (другой origin)**: OIDC + токены; BFF-паттерн (Backend For Frontend), где токены хранит сервер, а браузеру выдаётся сессионная cookie — рекомендуется для повышенной безопасности.

```ts
await fetch("/api/orders", { credentials: "include" });        // отправка cookie
```

## Нюансы и подводные камни

- `SameSite=None` требует `Secure`.
- CORS с credentials: конкретный origin, `Allow-Credentials: true`.
- `SameSite=Lax` не защищает от CSRF для «безопасных» методов (GET) с побочными эффектами.
- Сторонние cookie блокируются браузерами: влияет на встроенные виджеты и кросс-доменный SSO.
- Время жизни и «выйти везде» — продумайте.

## Практика

1. Настройте cookie-сессию с флагами и проверьте в DevTools.
2. Воспроизведите CSRF на тестовом стенде и защитите.
3. Сравните хранение токена в `localStorage` и в `HttpOnly` cookie.

## Вопросы с ответами

> [!question]- Сессия или токен?
> Сессия проще отзывается и хранится на сервере; токены удобны для stateless API, но требуют защиты и стратегии отзыва.

> [!question]- Зачем `HttpOnly` и `SameSite`?
> `HttpOnly` защищает от чтения cookie JS (XSS), `SameSite` — от CSRF.

## Связанные темы

- [[N:3ea33104867981bba291d38dfa496b93]]
- [[N:3ea33104867981368d3fd6c3d4da9d62]]
