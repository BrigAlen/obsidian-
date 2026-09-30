---
type: topic
domain: frontend
stage: 5
section: "5.5"
order: 3
status: todo
level: middle
notion_id: 3ea33104867981368d3fd6c3d4da9d62
tags: [domain/frontend, stage/5, level/middle, topic/auth, topic/jwt, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# JWT: access и refresh токены

↑ [[FE 5.5 Аутентификация и доступ — Keycloak, SSO, ACL|5.5 Аутентификация и доступ: Keycloak, SSO, ACL]] · ← [[FE 5.5.2 Сессии, cookies и токены|Предыдущая]] · → [[FE 5.5.4 OAuth 2.0 и OpenID Connect|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->















> [!info] Зачем это на собесе
> JWT спрашивают везде: структура, что проверять, зачем refresh и как хранить.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

Подробно серверная сторона — [[N:3ea33104867981f7801ef26a713b2fd5]]. Клиентская перспектива:

**JWT** = `header.payload.signature` (Base64Url). Payload (claims: `sub`, `iss`, `aud`, `exp`, `iat`, роли) **читается любым**; подпись защищает от подделки, но не скрывает содержимое.

```ts
function parseJwt(t: string) {
  const [, p] = t.split(".");
  return JSON.parse(decodeURIComponent(escape(atob(p.replace(/-/g, "+").replace(/_/g, "/")))));     // только для чтения claims; проверка подписи — на сервере
}
const { exp } = parseJwt(token); const expiresInMs = exp * 1000 - Date.now();
```

| Токен | Назначение | Срок | Хранение |
|---|---|---|---|
| **Access** | доступ к API (`Authorization: Bearer`) | 5–15 минут | в памяти (переменная/стор) |
| **Refresh** | получение нового access | часы–дни | `HttpOnly` cookie (или защищённо на сервере в BFF) |
| **ID token** (OIDC) | сведения о пользователе для клиента | короткий | не отправляют в API |

Обновление:

- Проактивно: по таймеру за 30–60 секунд до `exp` (`setTimeout`, `keycloak.updateToken(30)`).
- Реактивно: при 401 (см. интерсептор в [[N:3ea331048679812ba856e1ba38a2e798]]) с единым запросом обновления.
- **Ротация refresh-токена**: каждый refresh выдаёт новый; повторное использование старого → отзыв всей цепочки (защита от кражи).
- Выход: отзыв refresh на сервере (`logout` endpoint), очистка состояния и кэша Query.

Ограничения JWT:

- Невозможно «отозвать» access до `exp` без списка отзыва/introspection — поэтому короткий срок.
- Размер (заголовок `Authorization` в каждом запросе).
- Не кладите чувствительные данные в payload.
- Проверка `exp` на клиенте — только для UX; сервер решает.

Проверка на сервере: подпись (JWKS), `iss`, `aud`, `exp`, `nbf`, алгоритм (запрет `none`).

## Нюансы и подводные камни

- Смещение часов клиента: не полагайтесь на локальные часы точно (запас по времени).
- Несколько вкладок одновременно обновляют токен: синхронизируйте (BroadcastChannel/Web Locks).
- Потеря состояния при перезагрузке страницы: access в памяти → восстановление через refresh cookie (silent refresh).
- Токен в URL попадает в логи и историю.

## Практика

1. Реализуйте проактивное и реактивное обновление токена с единым запросом.
2. Синхронизируйте обновление между вкладками.
3. Опишите поведение при истёкшем refresh.

## Вопросы с ответами

> [!question]- Зачем два токена?
> Access — короткоживущий для запросов (минимизирует ущерб при краже), refresh — для получения нового access без повторного ввода пароля.

> [!question]- Можно ли доверять данным из JWT на клиенте?
> Читать для UX можно, но проверка подписи и решения по доступу — на сервере.

## Связанные темы

- [[N:3ea3310486798172bf0eddbc19555afa]]
- [[N:3ea33104867981c5b486ef23f5f8b4d5]]
