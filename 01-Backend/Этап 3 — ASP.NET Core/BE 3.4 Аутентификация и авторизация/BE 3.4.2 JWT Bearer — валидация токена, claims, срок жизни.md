---
type: topic
domain: backend
stage: 3
section: "3.4"
order: 2
status: todo
level: middle
notion_id: 3ea33104867981f7801ef26a713b2fd5
tags: [domain/backend, stage/3, level/middle, topic/aspnet, topic/security, topic/jwt, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# JWT Bearer: валидация токена, claims, срок жизни

↑ [[BE 3.4 Аутентификация и авторизация|3.4 Аутентификация и авторизация]] · ← [[BE 3.4.1 Аутентификация и авторизация в ASP.NET Core — схемы, handlers|Предыдущая]] · → [[BE 3.4.3 OAuth 2.0, OpenID Connect и Keycloak на бэкенде|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->























































> [!info] Зачем это на собесе
> JWT спрашивают везде: структура, что проверяется, где хранить, как отзывать.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

JWT = `header.payload.signature` (Base64Url). Подпись гарантирует целостность, **но не секретность**: payload читается любым.

| Часть | Содержимое |
|---|---|
| Header | алгоритм (`RS256`, `HS256`), `kid` |
| Payload | claims: `iss`, `sub`, `aud`, `exp`, `nbf`, `iat`, роли и т.п. |
| Signature | подпись header+payload ключом |

```csharp
builder.Services.AddAuthentication().AddJwtBearer(o =>
{
    o.Authority = "https://keycloak.example.com/realms/app";   // ключи из JWKS
    o.Audience = "orders-api";
    o.TokenValidationParameters = new()
    {
        ValidateIssuer = true, ValidateAudience = true,
        ValidateLifetime = true, ClockSkew = TimeSpan.FromSeconds(30),
        ValidAlgorithms = ["RS256"],
    };
});
```

| Схема | Плюсы | Минусы |
|---|---|---|
| HS256 (общий секрет) | просто | секрет знают все проверяющие |
| RS256/ES256 (пара ключей) | проверка по публичному ключу (JWKS) | сложнее управление ключами |

### Access и Refresh

Access-токен короткоживущий (5–15 минут), refresh — долгоживущий, хранится защищённо, ротируется, отзывается на сервере.

## Нюансы и подводные камни

- Проверять нужно подпись, `iss`, `aud`, `exp`; отключение любой проверки — уязвимость.
- Не кладите секреты и персональные данные в payload.
- Отзыв: JWT сам по себе нельзя «отозвать» — короткий срок жизни, denylist по `jti`, introspection.
- `alg: none` и подмена алгоритма — известные атаки; фиксируйте `ValidAlgorithms`.
- Хранение в браузере: `localStorage` уязвим к XSS, `HttpOnly` cookie — к CSRF; выбирайте осознанно.

## Практика

1. Подключите Keycloak и валидацию через `Authority`.
2. Декодируйте токен на jwt.io и найдите claims.
3. Реализуйте refresh с ротацией токенов.

## Вопросы с ответами

> [!question]- Что проверяет JwtBearer?
> Подпись, издателя, аудиторию, срок действия (`exp`/`nbf`) и алгоритм.

> [!question]- Как отозвать JWT?
> Короткий срок, denylist/`jti`, ротация ключей, введение introspection; сам токен не отзывается.

> [!question]- HS256 или RS256?
> RS256/ES256 для распределённых систем: сервисы проверяют по публичному ключу без общего секрета.

## Связанные темы

- [[N:3ea331048679811a91f1da415f818e6a]]
- [[N:3ea33104867981eab521e5a0dd217b96]]
