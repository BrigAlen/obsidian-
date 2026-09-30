---
type: topic
domain: frontend
stage: 5
section: "5.4"
order: 6
status: todo
level: middle
notion_id: 3ea33104867981b396cddabaf563379e
tags: [domain/frontend, stage/5, level/middle, topic/api, topic/graphql, topic/rest, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# GraphQL и REST: сравнение

↑ [[FE 5.4 Работа с API — REST, GraphQL, WebSocket|5.4 Работа с API: REST, GraphQL, WebSocket]] · ← [[FE 5.4.5 GraphQL — query, mutation, subscription, fragments|Предыдущая]] · → [[FE 5.4.7 graphql-codegen и graphql-request|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->


> [!info] Зачем это на собесе
> Аргументированный выбор, а не «GraphQL современнее».

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

| Критерий | REST | GraphQL |
|---|---|---|
| Endpoint | много ресурсов | один `/graphql` |
| Форма ответа | фиксирована сервером | описывается клиентом |
| Over/under-fetching | возможны | нет |
| Количество запросов | несколько на экран | один |
| Типизация | OpenAPI (опционально) | строгая схема из коробки |
| Кэширование HTTP | нативное (GET, ETag, CDN) | сложно (POST) — persisted queries, клиентский кэш |
| Версионирование | версии API | эволюция схемы (`@deprecated`) |
| Ошибки | HTTP-коды | 200 + `errors` |
| Загрузка файлов | простая (multipart) | нестандартно |
| Реалтайм | SSE/WebSocket отдельно | subscriptions |
| Инструменты | Postman, OpenAPI | GraphiQL, Apollo Studio, codegen |
| Сложность сервера | ниже | выше (N+1, лимиты, безопасность) |
| Сложность клиента | ниже | выше (клиент, кэш, codegen) |
| Публичные API | стандарт | реже |
| Мобильные клиенты | лишний трафик | экономия |

Когда GraphQL: много разных клиентов (web/mobile) с разными потребностями данных; сложные связанные данные; быстрая итерация фронтенда; агрегация нескольких сервисов (federation).

Когда REST: простые CRUD, публичные API, кэширование на CDN, загрузка файлов, команда без опыта GraphQL, жёсткая простота эксплуатации.

Гибрид: REST для команд и файлов, GraphQL для чтения агрегатов; BFF; gRPC между сервисами.

## Нюансы и подводные камни

- GraphQL не устраняет N+1 — он переносит её на сервер (DataLoader).
- Безопасность: лимиты глубины/сложности обязательны.
- «Один запрос» не значит «быстрый запрос».
- REST + OpenAPI + codegen закрывает большую часть преимуществ типизации.

## Практика

1. Сравните количество запросов экрана заказа в REST и GraphQL.
2. Опишите критерии выбора для вашего проекта.

## Вопросы с ответами

> [!question]- Когда REST предпочтительнее GraphQL?
> Для простых CRUD, публичных и кэшируемых API, загрузки файлов и когда важна простота.

> [!question]- Основной плюс GraphQL для клиента?
> Клиент сам определяет форму данных и получает нужное за один запрос.

## Связанные темы

- [[N:3ea33104867981a8a3b1c57d5d9d9535]]
- [[N:3ea331048679818eacacea12f103344c]]
