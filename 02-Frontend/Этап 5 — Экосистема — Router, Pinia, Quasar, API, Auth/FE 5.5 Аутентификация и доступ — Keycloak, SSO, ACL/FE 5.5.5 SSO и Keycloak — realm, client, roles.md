---
type: topic
domain: frontend
stage: 5
section: "5.5"
order: 5
status: todo
level: middle
notion_id: 3ea33104867981ab949ccb7b17f78719
tags: [domain/frontend, stage/5, level/middle, topic/auth, topic/keycloak, topic/sso, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# SSO и Keycloak: realm, client, roles

↑ [[FE 5.5 Аутентификация и доступ — Keycloak, SSO, ACL|5.5 Аутентификация и доступ: Keycloak, SSO, ACL]] · ← [[FE 5.5.4 OAuth 2.0 и OpenID Connect|Предыдущая]] · → [[FE 5.5.6 keycloak-js — интеграция во Vue|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->


> [!info] Зачем это на собесе
> Что такое SSO и как в Keycloak настраивают realm, клиентов и роли.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

**SSO (Single Sign-On)** — один вход для многих приложений: сессия живёт у провайдера идентичности (IdP), приложения доверяют ему.

**Keycloak** — open-source IdP (OIDC, SAML, OAuth 2.0): SSO, MFA, федерация с LDAP/AD и соцсетями, управление пользователями и ролями, админ-консоль.

| Понятие | Смысл |
|---|---|
| **Realm** | изолированное пространство: пользователи, клиенты, роли, настройки (обычно один realm на продукт/тенанта) |
| **Client** | приложение, использующее Keycloak; типы: public (SPA) и confidential (бэкенд, с secret) |
| **User / Group** | пользователи и их группировка |
| **Realm roles / Client roles** | роли на уровне realm или конкретного клиента |
| **Composite roles** | роль, включающая другие |
| **Client scopes / Mappers** | какие claims попадут в токен (роли, группы, атрибуты, audience) |
| **Identity providers** | внешние IdP (Google, AD/LDAP, SAML) |
| **Authentication flows** | цепочки шагов входа (пароль, OTP, WebAuthn) |
| **Sessions** | SSO-сессия, offline-токены |
| **Themes** | брендирование страницы входа |
| **Service accounts** | client credentials для сервисов |

Настройка SPA-клиента: Client type OpenID Connect, Public, `Standard flow` + PKCE (S256), Valid redirect URIs, Web origins (CORS), Front-channel logout.

Роли в токене: `realm_access.roles` и `resource_access.<client>.roles`; mapper «audience» добавляет `aud` для API; при необходимости «flat» claim `roles`.

```json
{ "sub": "…", "preferred_username": "anna", "email": "a@x.ru", "realm_access": { "roles": ["user"] }, "resource_access": { "orders-api": { "roles": ["orders:write"] } }, "aud": ["orders-api"] }
```

Логаут: `/logout` с `id_token_hint` и `post_logout_redirect_uri` завершает SSO-сессию (иначе вход произойдёт автоматически).

Многопользовательская схема: realm на клиента (полная изоляция) или organizations внутри realm.

## Нюансы и подводные камни

- Неверные `redirect_uri`/Web origins — типичная причина ошибок входа и CORS.
- Роли в токене раздувают его: используйте client roles и только нужные scopes.
- Настройка Keycloak «руками» не воспроизводима: экспортируйте realm/используйте Terraform или `keycloak-config-cli`.
- Время жизни токенов и сессий настраивается отдельно (Access Token Lifespan, SSO Session Idle/Max).
- Обновление Keycloak меняет поведение: следите за релизами.

## Практика

1. Поднимите Keycloak в Docker, создайте realm, client (public, PKCE) и роли.
2. Добавьте mapper для audience и ролей в токен.
3. Проверьте logout и SSO между двумя клиентами.

## Вопросы с ответами

> [!question]- Что такое realm в Keycloak?
> Изолированное пространство с собственными пользователями, клиентами, ролями и настройками.

> [!question]- Чем public client отличается от confidential?
> Public не имеет secret (SPA, мобильные, PKCE), confidential — имеет и хранится на бэкенде.

## Связанные темы

- [[N:3ea33104867981c5b486ef23f5f8b4d5]]
- [[N:3ea3310486798174b39ee7d325d982cd]]
