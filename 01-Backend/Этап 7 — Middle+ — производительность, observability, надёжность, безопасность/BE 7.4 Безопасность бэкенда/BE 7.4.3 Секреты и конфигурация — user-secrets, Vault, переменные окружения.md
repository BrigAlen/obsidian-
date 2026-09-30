---
type: topic
domain: backend
stage: 7
section: "7.4"
order: 3
status: todo
level: senior
notion_id: 3ea331048679819c9bb7c741225859ca
tags: [domain/backend, stage/7, level/senior, topic/security, topic/secrets, priority/should]
reviewed:
next_review:
priority: should
time: 3
---

# Секреты и конфигурация: user-secrets, Vault, переменные окружения

↑ [[BE 7.4 Безопасность бэкенда|7.4 Безопасность бэкенда]] · ← [[BE 7.4.2 Инъекции — SQL, командные, LDAP, десериализация|Предыдущая]] · → [[BE 7.4.4 Криптография — хэши, соль, шифрование, Data Protection API|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: senior</span></div>
<!-- meta:end -->

































> [!info] Зачем это на собесе
> «Где хранить пароли к БД и ключи?» — базовый вопрос по безопасности эксплуатации.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

Секрет — пароль, токен, ключ, сертификат. Он **не хранится** в репозитории, образе Docker, логах и клиентском коде.

| Место | Когда |
|---|---|
| User Secrets (`dotnet user-secrets`) | локальная разработка |
| Переменные окружения | простые окружения, Docker/Kubernetes (Secret → env) |
| Kubernetes Secrets (+ шифрование etcd, External Secrets) | кластеры |
| HashiCorp Vault, Azure Key Vault, AWS Secrets Manager | централизованное хранение, аудит, ротация, динамические секреты |
| CI/CD-секреты (masked variables) | сборка/деплой |

Принципы:

- **Наименьшие привилегии**: у каждого сервиса свои учётные записи с минимальными правами.
- **Ротация**: регулярная смена, возможность быстрого отзыва.
- **Динамические секреты**: Vault выдаёт временные учётные данные БД.
- **Раздельные окружения**: dev/staging/prod с разными секретами.
- **Аудит доступа**.
- **Сканирование репозитория** на утечки (gitleaks, trufflehog, GitHub secret scanning); утёкший секрет считается скомпрометированным — его отзывают, а не только удаляют из истории.

```bash
dotnet user-secrets init
dotnet user-secrets set "Jwt:Key" "..."
```

```yaml
env:
  - name: ConnectionStrings__Default
    valueFrom: { secretKeyRef: { name: orders-db, key: connection } }
```

## Нюансы и подводные камни

- Переменные окружения видны в `/proc`, `docker inspect`, дампах и иногда логах старта.
- Base64 в Kubernetes Secret — не шифрование.
- Секреты в `appsettings.json`, Dockerfile (`ENV`, `ARG`) и истории git.
- `.env` не должен попадать в git (`.gitignore`).
- Для доступа приложения к хранилищу используйте workload identity/IAM-роли, а не ещё один статический секрет.

## Практика

1. Уберите секреты из репозитория и настройте user-secrets + переменные окружения.
2. Запустите gitleaks по истории репозитория.
3. Подключите Vault и получите динамические креды БД.

## Вопросы с ответами

> [!question]- Что делать, если секрет попал в git?
> Считать его скомпрометированным: отозвать и перевыпустить, только потом чистить историю.

> [!question]- Почему Base64 в Kubernetes Secret небезопасен?
> Это кодирование, а не шифрование; нужны RBAC и шифрование хранилища.

## Связанные темы

- [[N:3ea3310486798151bdfce23ff2d8a287]]
- [[N:3ea331048679818080eee95e1cd52107]]
