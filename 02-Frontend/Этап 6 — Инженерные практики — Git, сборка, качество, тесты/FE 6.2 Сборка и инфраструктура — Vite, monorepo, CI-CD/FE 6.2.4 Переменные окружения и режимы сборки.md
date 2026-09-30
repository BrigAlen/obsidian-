---
type: topic
domain: frontend
stage: 6
section: "6.2"
order: 4
status: todo
level: middle
notion_id: 3ea33104867981ae9b4bf9d29143eb13
tags: [domain/frontend, stage/6, level/middle, topic/build, topic/env, topic/vite, priority/should]
reviewed:
next_review:
priority: should
time: 3
---

# Переменные окружения и режимы сборки

↑ [[FE 6.2 Сборка и инфраструктура — Vite, monorepo, CI-CD|6.2 Сборка и инфраструктура: Vite, monorepo, CI/CD]] · ← [[FE 6.2.3 Webpack — основы и отличия от Vite|Предыдущая]] · → [[FE 6.2.5 Пакетные менеджеры — npm, yarn, pnpm, lock-файлы, semver|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->














> [!info] Зачем это на собесе
> Разница build-time и runtime конфигурации и то, что переменные клиента — публичны.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

Vite читает `.env`-файлы по режиму:

```text
.env                # всегда
.env.local          # всегда, не в git
.env.development    # режим development (vite dev)
.env.production     # режим production (vite build)
.env.staging        # vite build --mode staging
```

```ts
// доступны только переменные с префиксом VITE_ (защита от утечек серверных секретов)
const api = import.meta.env.VITE_API_URL;
import.meta.env.MODE;          // "development" | "production" | свой режим
import.meta.env.DEV / PROD / BASE_URL / SSR;
```

```ts
// Типизация: env.d.ts
interface ImportMetaEnv { readonly VITE_API_URL: string; readonly VITE_SENTRY_DSN?: string }
```

**Ключевой момент**: `import.meta.env.*` подставляется **на этапе сборки** (build-time). Значит, один и тот же артефакт нельзя использовать для разных окружений без пересборки. Решение — **runtime-конфигурация** (см. [[N:71baa0cafa97476da6dc9a5a3b7bb970]]): файл `config.json`/`window.__CONFIG__`, генерируемый контейнером при старте.

Режимы сборки: `--mode staging` меняет набор `.env` и `MODE`; условная логика (`if (import.meta.env.DEV)`) удаляется из prod-бандла (dead code elimination).

| Тема | Правило |
|---|---|
| Секреты | **Никогда** в клиентских переменных: любая `VITE_*` попадает в бандл и видна пользователю |
| Публичные значения | URL API, DSN Sentry, ключи публичных сервисов, флаги |
| `define` | подстановка констант (`__APP_VERSION__`) |
| Различия окружений | URL, аналитика, флаги, уровни логов |
| CI | переменные передаются на этапе сборки; для runtime — при запуске контейнера |
| Валидация | проверять обязательные переменные при старте (Zod) |
| Node-переменные в конфиге Vite | `loadEnv(mode, process.cwd(), "")` |

Quasar: `build.env` в `quasar.config`, `process.env.*`.

## Нюансы и подводные камни

- «Секретный» ключ в `VITE_*` = публичный ключ.
- Сборка для stage и prod отдельно нарушает принцип «один артефакт» — используйте runtime-конфигурацию.
- Опечатка в имени переменной даёт `undefined` без ошибки: валидируйте при старте.
- Изменение `.env` требует перезапуска dev-сервера.
- Значения — строки: приводите типы (`"false"` — truthy).

## Практика

1. Настройте `.env.development/.env.production/.env.staging` и типизацию.
2. Добавьте валидацию переменных при старте приложения.
3. Убедитесь, что серверных секретов нет в `dist`.

## Вопросы с ответами

> [!question]- Почему `VITE_` префикс?
> Чтобы в клиентский бандл попадали только явно публичные переменные, а не всё окружение.

> [!question]- Можно ли хранить секрет в переменной окружения фронтенда?
> Нет: она встраивается в бандл и доступна любому пользователю.

## Связанные темы

- [[N:3ea331048679819ebc53c4173bc9fc78]]
- [[N:3ea33104867981a0ade9f88b2d4cc268]]
