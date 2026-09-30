---
type: topic
domain: backend
stage: 3
section: "3.1"
order: 3
status: todo
level: middle
notion_id: 3ea33104867981bf8a02c3a4b52c7ec7
tags: [domain/backend, stage/3, level/middle, topic/aspnet, topic/configuration, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Конфигурация: appsettings, окружения, переменные, секреты

↑ [[BE 3.1 Хост, конфигурация и middleware pipeline|3.1 Хост, конфигурация и middleware pipeline]] · ← [[BE 3.1.2 Middleware — конвейер, порядок, свои middleware|Предыдущая]] · → [[BE 3.1.4 Options pattern — IOptions, IOptionsSnapshot, IOptionsMonitor, валидация|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->























> [!info] Зачем это на собесе
> Спрашивают приоритет источников, как хранить секреты и как переопределять настройки в Docker/Kubernetes.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

`IConfiguration` объединяет несколько провайдеров в один ключ-значение. Поздние источники **переопределяют** ранние.

| Порядок (по умолчанию) | Источник |
|---|---|
| 1 | `appsettings.json` |
| 2 | `appsettings.{Environment}.json` |
| 3 | User Secrets (только Development) |
| 4 | Переменные окружения |
| 5 | Аргументы командной строки |

Иерархия ключей разделяется двоеточием: `ConnectionStrings:Default`. В переменных окружения используют двойное подчёркивание: `ConnectionStrings__Default`.

```json
{
  "ConnectionStrings": { "Default": "Host=localhost;Database=app" },
  "Kafka": { "Brokers": ["k1:9092", "k2:9092"] }
}
```

```csharp
var cs = builder.Configuration.GetConnectionString("Default");
var brokers = builder.Configuration.GetSection("Kafka:Brokers").Get<string[]>();
```

### Окружения

`ASPNETCORE_ENVIRONMENT` (Development / Staging / Production) выбирает `appsettings.{env}.json` и поведение (`app.Environment.IsDevelopment()`), например страницу ошибок разработчика.

### Секреты

- Локально: `dotnet user-secrets set "Jwt:Key" "..."` — хранится вне репозитория.
- Прод: переменные окружения, Kubernetes Secrets, Azure Key Vault, HashiCorp Vault, AWS Secrets Manager (провайдеры конфигурации).
- Никогда: секреты в репозитории или в образе Docker.

## Нюансы и подводные камни

- Значения из переменных окружения всегда строки; массивы задаются индексами: `Kafka__Brokers__0`.
- Конфигурация в целом не типизирована: для использования в коде применяйте Options (см. [[N:3ea331048679814dbaadc2a67ef314e5]]).
- Изменения файлов подхватываются (`reloadOnChange`), но значения, уже прочитанные в singleton-е, не обновятся автоматически.
- Опечатка в ключе даёт `null` без ошибки: используйте валидацию Options при старте.
- `launchSettings.json` работает только при запуске из IDE/`dotnet run`, не в Docker.

## Практика

1. Переопределите строку подключения переменной окружения в `docker run`.
2. Настройте User Secrets для JWT-ключа и убедитесь, что он не попал в git.
3. Подключите Azure Key Vault или Vault-провайдер в тестовом окружении.

## Вопросы с ответами

> [!question]- Каков порядок приоритета источников конфигурации?
> appsettings → appsettings.{env} → user secrets → переменные окружения → командная строка; последний побеждает.

> [!question]- Как безопасно хранить секреты?
> Вне репозитория: user-secrets локально, секрет-хранилище и переменные окружения в проде, доступ по принципу наименьших прав.

> [!question]- Как задать вложенный ключ в переменной окружения?
> Заменить двоеточие на двойное подчёркивание: `Section__Key`.

## Связанные темы

- [[N:3ea331048679810f8b4def6f1c5f7146]]
- [[N:3ea331048679814dbaadc2a67ef314e5]]
