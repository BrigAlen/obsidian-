---
type: topic
domain: frontend
stage: 7
section: "7.3"
order: 5
status: todo
level: senior
notion_id: 3ea33104867981c49947d137f472eb68
tags: [domain/frontend, stage/7, level/senior, topic/security, topic/tokens, topic/jwt, topic/cookies, priority/should]
reviewed:
next_review:
priority: should
time: 3
---

# Безопасное хранение токенов

↑ [[FE 7.3 Безопасность фронтенда|7.3 Безопасность фронтенда]] · ← [[FE 7.3.4 Clickjacking|Предыдущая]] · → [[FE 7.3.6 Уязвимости зависимостей и npm audit|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: senior</span></div>
<!-- meta:end -->






> [!info] Зачем это на собесе
> Один из самых обсуждаемых вопросов: «где хранить JWT». Нужно взвесить компромиссы.

## Варианты

| Место | Плюсы | Минусы |
|---|---|---|
| `localStorage` | просто | доступен любому скрипту → украдут через XSS |
| `sessionStorage` | живёт до закрытия вкладки | та же XSS-уязвимость |
| Память (переменная) | недоступна после XSS-сессии в другой вкладке | теряется при перезагрузке |
| Cookie `HttpOnly; Secure; SameSite` | JS токен не прочитает | нужна CSRF-защита |

## Рекомендуемая схема

- **access-токен** — короткоживущий (5–15 минут), держим в памяти;
- **refresh-токен** — в `HttpOnly; Secure; SameSite=Strict/Lax` cookie, путь `/auth/refresh`;
- при перезагрузке страницы запрашиваем новый access по refresh;
- **rotation refresh-токенов** и детект повторного использования на сервере;
- выход: сервер отзывает refresh, cookie удаляется.

```ts
let accessToken: string | null = null

export async function refresh() {
  const r = await fetch('/auth/refresh', { method: 'POST', credentials: 'include' })
  accessToken = (await r.json()).accessToken
}
```

## OIDC и SPA

Для SPA: Authorization Code Flow с **PKCE**, без implicit flow. Библиотеки: `oidc-client-ts`, `keycloak-js`. Либо паттерн **BFF** (Backend for Frontend): токены живут на сервере, браузер получает только сессионную cookie.

## Что ещё

- не класть чувствительные данные в JWT (он читаем, не шифруется);
- не логировать токены, скрывать из URL и `Referer`;
- короткий TTL и проверка `aud`, `iss`, `exp` на бэкенде.

## Вопросы с ответами

> [!question]- Где хранить JWT в SPA?
> Access-токен в памяти, refresh-токен в HttpOnly cookie с ротацией. localStorage уязвим для XSS. Наиболее защищённый вариант — BFF.

> [!question]- Зачем PKCE?
> Защищает Authorization Code от перехвата в публичных клиентах: связывает запрос кода и обмен на токен одноразовым секретом.
