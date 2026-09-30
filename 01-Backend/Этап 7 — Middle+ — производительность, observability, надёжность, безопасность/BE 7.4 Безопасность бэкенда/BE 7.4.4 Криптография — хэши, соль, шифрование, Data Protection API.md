---
type: topic
domain: backend
stage: 7
section: "7.4"
order: 4
status: todo
level: senior
notion_id: 3ea331048679818080eee95e1cd52107
tags: [domain/backend, stage/7, level/senior, topic/security, topic/cryptography, priority/should]
reviewed:
next_review:
priority: should
time: 3
---

# Криптография: хэши, соль, шифрование, Data Protection API

↑ [[BE 7.4 Безопасность бэкенда|7.4 Безопасность бэкенда]] · ← [[BE 7.4.3 Секреты и конфигурация — user-secrets, Vault, переменные окружения|Предыдущая]] · → [[BE 7.4.5 Защита персональных данных, аудит и логирование доступа|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: senior</span></div>
<!-- meta:end -->









> [!info] Зачем это на собесе
> Ждут различения хэширования, шифрования и подписи и знания, что «своё» крипто не пишут.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

| Примитив | Назначение | Пример |
|---|---|---|
| Хэш (SHA-256/512) | отпечаток данных, целостность | контрольные суммы |
| Пароль-хэш (Argon2id, bcrypt, PBKDF2) | хранение паролей: медленный, с солью | см. [[N:3ea33104867981bfb755f29c6b1cd640]] |
| HMAC | целостность и аутентичность по общему ключу | подпись вебхука |
| Симметричное шифрование (AES-GCM, ChaCha20-Poly1305) | конфиденциальность + целостность (AEAD) | шифрование полей БД |
| Асимметричное (RSA, ECC) | обмен ключами, подписи, TLS | JWT RS256/ES256 |
| Подпись (ECDSA, Ed25519) | неотказуемость, подлинность | подпись документов |
| KDF (HKDF, PBKDF2) | получение ключей из секрета | |
| CSPRNG | случайные ключи, токены | `RandomNumberGenerator` |

```csharp
// AES-GCM (AEAD): уникальный nonce на каждое шифрование
var nonce = RandomNumberGenerator.GetBytes(AesGcm.NonceByteSizes.MaxSize);
var cipher = new byte[data.Length]; var tag = new byte[AesGcm.TagByteSizes.MaxSize];
using var aes = new AesGcm(key, tag.Length);
aes.Encrypt(nonce, data, cipher, tag);

// Токены и ключи — только криптостойкий генератор
var token = Convert.ToHexString(RandomNumberGenerator.GetBytes(32));
```

**Data Protection API** (ASP.NET Core) — управляемое шифрование для cookie, антифорджери и своих данных: `IDataProtector.Protect/Unprotect`; кольцо ключей нужно хранить общим (Redis, БД, файловая система) для нескольких реплик и защищать.

Правила: не изобретайте алгоритмы; используйте проверенные библиотеки и AEAD; ключи храните отдельно от данных; TLS 1.2+ везде; не используйте MD5/SHA-1/DES/ECB.

## Нюансы и подводные камни

- Повтор nonce в AES-GCM с тем же ключом — катастрофа.
- `Random` не подходит для секретов.
- Шифрование без аутентификации (AES-CBC без MAC) уязвимо к подмене.
- Сравнение MAC/токенов только за постоянное время (`FixedTimeEquals`).
- Потеря ключа = потеря данных: планируйте резервирование и ротацию ключей.

## Практика

1. Зашифруйте поле в БД AES-GCM и реализуйте ротацию ключа.
2. Настройте общее хранилище ключей Data Protection для нескольких реплик.
3. Проверьте подпись вебхука через HMAC.

## Вопросы с ответами

> [!question]- Хэширование или шифрование?
> Хэш необратим и служит для проверки целостности/паролей; шифрование обратимо ключом и защищает конфиденциальность.

> [!question]- Зачем соль?
> Делает хэши одинаковых паролей разными и не позволяет использовать радужные таблицы.

## Связанные темы

- [[N:3ea331048679819c9bb7c741225859ca]]
- [[N:3ea331048679810fb800c7dce192a1d4]]
