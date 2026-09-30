---
type: topic
domain: frontend
stage: 5
section: "5.4"
order: 11
status: todo
level: middle
notion_id: cbd9f4bed053472fbe6ce5ef68d5cd7b
tags: [domain/frontend, stage/5, level/middle, topic/api, topic/openapi, topic/contracts, topic/testing, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# API-контракты: OpenAPI, codegen и contract testing

↑ [[FE 5.4 Работа с API — REST, GraphQL, WebSocket|5.4 Работа с API: REST, GraphQL, WebSocket]] · ← [[FE 5.4.10 Слой API в приложении — сервисы и типизация|Предыдущая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->








> [!info] Зачем это на собесе
> Как фронт и бэк не расходятся в понимании API: схема как источник истины и автоматические проверки.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

**OpenAPI** — машиночитаемое описание REST API (пути, параметры, схемы, ошибки). Источник истины: бэкенд генерирует спецификацию из кода (см. [[N:3ea331048679816ca2a9e01efe418d51]]) или команда пишет «schema-first».

Генерация клиента:

| Инструмент | Результат |
|---|---|
| `openapi-typescript` | только типы (`paths`, `components`), лёгкий; с `openapi-fetch` — типизированный клиент |
| Orval | типы + хуки Vue Query/Axios + моки MSW |
| `@hey-api/openapi-ts` | клиент и SDK |
| Kiota, NSwag | клиенты (в том числе для .NET) |
| `openapi-zod-client` | Zod-схемы для runtime-валидации |

```bash
npx openapi-typescript https://api.example.com/openapi.json -o src/api/schema.d.ts
```

```ts
import createClient from "openapi-fetch";
import type { paths } from "./schema";
const client = createClient<paths>({ baseUrl: "/api" });
const { data, error } = await client.GET("/orders/{id}", { params: { path: { id: "42" } } });   // типы параметров и ответа выведены
```

**Contract testing** — проверка соглашений без интеграционных стендов:

| Подход | Суть |
|---|---|
| Проверка совместимости схемы (`oasdiff breaking`) | в CI бэкенда: изменения не ломают потребителей |
| Consumer-driven (Pact) | фронтенд описывает ожидания; бэкенд проверяет их в CI |
| Mock-сервер по схеме (Prism, MSW + схема) | фронтенд разрабатывается без бэкенда, ответы валидируются схемой |
| Валидация ответов на стенде (Schemathesis, Dredd) | автоматическое тестирование API по схеме (property-based) |
| Runtime-валидация на клиенте (Zod) | обнаружение расхождения в проде (с логированием) |

CI фронтенда: `generate` → `git diff --exit-code` (типы актуальны) → `vue-tsc` (компиляция ловит несовместимости после обновления схемы).

Процесс: изменение API → обновлённая схема в репозитории/артефакте → PR на фронт с регенерацией типов → совместимые изменения (добавление полей) деплоятся независимо, ломающие — по правилам версионирования (см. [[N:3ea33104867981a78f21d0e71de5ad83]]).

## Нюансы и подводные камни

- Схема не отражает семантику (бизнес-правила), только форму.
- Сгенерированный код не правят вручную; расширения — обёртками.
- Устаревшая схема хуже её отсутствия: автоматизируйте публикацию.
- Nullable/optional в разных генераторах трактуются по-разному — договоритесь.
- Большие спецификации замедляют генерацию: разбивайте по тегам.

## Практика

1. Сгенерируйте типы и клиент из OpenAPI и замените ручные типы.
2. Добавьте проверку актуальности сгенерированного кода в CI.
3. Настройте Prism/MSW для разработки без бэкенда.

## Вопросы с ответами

> [!question]- Зачем OpenAPI фронтенду?
> Единый контракт: типы и клиент генерируются автоматически, изменения API видны при компиляции.

> [!question]- Что такое contract testing?
> Автоматическая проверка того, что потребитель и поставщик придерживаются согласованного контракта, без полного интеграционного стенда.

## Связанные темы

- [[N:3ea331048679812caa72d90b8bef45f7]]
- [[N:3ea33104867981bba291d38dfa496b93]]
