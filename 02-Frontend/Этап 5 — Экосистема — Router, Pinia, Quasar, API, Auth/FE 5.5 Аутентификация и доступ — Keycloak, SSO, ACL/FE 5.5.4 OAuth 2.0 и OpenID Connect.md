---
type: topic
domain: frontend
stage: 5
section: "5.5"
order: 4
status: todo
level: middle
notion_id: 3ea33104867981c5b486ef23f5f8b4d5
tags: [domain/frontend, stage/5, level/middle, topic/auth, topic/oauth, topic/oidc, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# OAuth 2.0 и OpenID Connect

↑ [[FE 5.5 Аутентификация и доступ — Keycloak, SSO, ACL|5.5 Аутентификация и доступ: Keycloak, SSO, ACL]] · ← [[FE 5.5.3 JWT — access и refresh токены|Предыдущая]] · → [[FE 5.5.5 SSO и Keycloak — realm, client, roles|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->


> [!info] Зачем это на собесе
> Ждут: чем OAuth отличается от OIDC и почему для SPA нужен Authorization Code + PKCE.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

**OAuth 2.0** — протокол **делегирования доступа**: приложение получает токен на ограниченный доступ к ресурсам от имени пользователя. **OpenID Connect (OIDC)** — слой аутентификации поверх OAuth: добавляет `id_token` и `userinfo`.

Роли: пользователь (Resource Owner), приложение (Client), Authorization Server (Keycloak и др.), Resource Server (API).

| Flow | Когда |
|---|---|
| **Authorization Code + PKCE** | SPA, мобильные, web-приложения (стандарт) |
| Client Credentials | сервис-сервис |
| Device Code | ТВ, CLI |
| Refresh Token | обновление |
| ~~Implicit~~, ~~Password~~ | устарели, не используются |

**PKCE** защищает authorization code от перехвата у публичных клиентов (без client secret): клиент генерирует `code_verifier`, отправляет `code_challenge = SHA256(verifier)`, а при обмене кода предъявляет `verifier`.

```ts
// Упрощённо (вручную; в реальности — библиотека oidc-client-ts / keycloak-js)
const verifier = base64url(crypto.getRandomValues(new Uint8Array(32)));
const challenge = base64url(await crypto.subtle.digest("SHA-256", new TextEncoder().encode(verifier)));
sessionStorage.setItem("pkce_verifier", verifier);
location.href = `${issuer}/authorize?response_type=code&client_id=spa&redirect_uri=${cb}&scope=openid profile email&state=${state}&nonce=${nonce}&code_challenge=${challenge}&code_challenge_method=S256`;
// на /callback: проверить state → POST /token {grant_type: authorization_code, code, code_verifier, redirect_uri}
```

Параметры: `scope` (права доступа: `openid`, `profile`, `email`, свои), `state` (защита от CSRF при редиректе), `nonce` (защита от replay `id_token`), `redirect_uri` (строгое совпадение).

Токены: **id_token** (для клиента, содержит личность), **access_token** (для API), **refresh_token**. Endpoint-ы: `/.well-known/openid-configuration` (discovery), `/authorize`, `/token`, `/userinfo`, `/logout`, `/certs` (JWKS).

Библиотеки: `oidc-client-ts`, `keycloak-js`, `@auth0/auth0-vue`, `vue-oidc-client`.

## Нюансы и подводные камни

- Проверяйте `state` и `nonce`.
- Строгие `redirect_uri` без wildcard.
- Client secret не хранят в SPA: публичный клиент + PKCE.
- Не смешивайте `id_token` и `access_token`: API принимает access token.
- Silent renew через iframe ломается третьесторонними cookie: используйте refresh token rotation.

## Практика

1. Пройдите Authorization Code + PKCE вручную в Postman/curl и разберите токены.
2. Настройте `oidc-client-ts` или `keycloak-js` для SPA.
3. Найдите endpoint-ы в discovery-документе.

## Вопросы с ответами

> [!question]- Чем OIDC отличается от OAuth 2.0?
> OAuth даёт доступ к ресурсам, OIDC добавляет стандартную аутентификацию пользователя (`id_token`).

> [!question]- Что такое PKCE?
> Механизм защиты authorization code для публичных клиентов через одноразовую пару `code_verifier`/`code_challenge`.

## Связанные темы

- [[N:3ea33104867981368d3fd6c3d4da9d62]]
- [[N:3ea33104867981ab949ccb7b17f78719]]
