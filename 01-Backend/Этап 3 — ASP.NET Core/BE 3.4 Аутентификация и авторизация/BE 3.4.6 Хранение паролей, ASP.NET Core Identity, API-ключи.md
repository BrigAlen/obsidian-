---
type: topic
domain: backend
stage: 3
section: "3.4"
order: 6
status: todo
level: middle
notion_id: 3ea33104867981bfb755f29c6b1cd640
tags: [domain/backend, stage/3, level/middle, topic/aspnet, topic/security, topic/identity, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Хранение паролей, ASP.NET Core Identity, API-ключи

↑ [[BE 3.4 Аутентификация и авторизация|3.4 Аутентификация и авторизация]] · ← [[BE 3.4.5 Контекст пользователя в сервисах (UserContext) и проброс токена между сервисами|Предыдущая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->























































> [!info] Зачем это на собесе
> «Как хранить пароли?» — вопрос-фильтр. Ответ «хэш с солью и медленный алгоритм» — минимум.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

Пароль нельзя хранить ни в открытом виде, ни зашифрованным обратимо. Хранится **хэш** медленным адаптивным алгоритмом с уникальной солью.

| Алгоритм | Комментарий |
|---|---|
| Argon2id | рекомендован OWASP |
| bcrypt | проверен, ограничение длины 72 байта |
| PBKDF2 (Identity по умолчанию) | стандарт, нужно много итераций |
| SHA-256/MD5 | не подходят: слишком быстрые |

```csharp
var hasher = new PasswordHasher<AppUser>();
var hash = hasher.HashPassword(user, password);
var result = hasher.VerifyHashedPassword(user, hash, input);   // Success / SuccessRehashNeeded / Failed
```

### ASP.NET Core Identity

Готовая система пользователей: `UserManager`, `SignInManager`, роли, lockout, 2FA, подтверждение email, хранение в EF Core.

```csharp
builder.Services.AddIdentityCore<AppUser>(o => { o.Password.RequiredLength = 12; o.Lockout.MaxFailedAccessAttempts = 5; })
    .AddEntityFrameworkStores<AppDbContext>();
```

Если есть внешний IdP (Keycloak), Identity часто не нужен: пароли хранит он.

### API-ключи

Генерируйте случайные (256 бит), показывайте один раз, храните только хэш (SHA-256), добавляйте префикс для идентификации, поддерживайте ротацию и отзыв, сравнивайте за постоянное время (`CryptographicOperations.FixedTimeEquals`).

## Нюансы и подводные камни

- Проверяйте пароль на утечки (HIBP k-anonymity).
- Одинаковые сообщения об ошибке для «нет пользователя» и «неверный пароль».
- Rate limiting и lockout на логин.
- Не логируйте пароли, ключи и токены.
- MFA/passkeys снижают риск кражи паролей.

## Практика

1. Замерьте время хэширования Argon2id/PBKDF2 при разных параметрах.
2. Реализуйте выдачу API-ключей с хранением хэша.
3. Настройте lockout и 2FA в Identity.

## Вопросы с ответами

> [!question]- Как правильно хранить пароли?
> Адаптивный хэш (Argon2id/bcrypt/PBKDF2) с уникальной солью и подходящей стоимостью, с возможностью перехэширования.

> [!question]- Зачем соль?
> Чтобы одинаковые пароли давали разные хэши и не работали радужные таблицы.

> [!question]- Как хранить API-ключи?
> Как пароли: только хэш, оригинал показывается один раз.

## Связанные темы

- [[N:3ea33104867981729109f1a011466c28]]
- [[N:3ea33104867981469ec0c25216311408]]
