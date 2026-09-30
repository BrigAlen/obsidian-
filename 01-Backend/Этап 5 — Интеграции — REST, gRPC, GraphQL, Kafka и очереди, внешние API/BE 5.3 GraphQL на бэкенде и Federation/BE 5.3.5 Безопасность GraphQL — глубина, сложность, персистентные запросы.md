---
type: topic
domain: backend
stage: 5
section: "5.3"
order: 5
status: todo
level: middle
notion_id: 3ea3310486798105bb21fdc37191b769
tags: [domain/backend, stage/5, level/middle, topic/api, topic/graphql, topic/security, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Безопасность GraphQL: глубина, сложность, персистентные запросы

↑ [[BE 5.3 GraphQL на бэкенде и Federation|5.3 GraphQL на бэкенде и Federation]] · ← [[BE 5.3.4 Federation и gateway — Hot Chocolate Fusion|Предыдущая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->






> [!info] Зачем это на собесе
> Гибкость GraphQL — и уязвимость: без ограничений один запрос может положить сервер.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

Клиент строит запросы сам, поэтому сервер обязан ограничивать ресурсы.

| Угроза | Защита |
|---|---|
| Глубокие вложенные запросы (`a{b{a{b...}}}`) | ограничение глубины (`AddMaxExecutionDepthRule`) |
| Дорогие запросы | анализ стоимости/сложности, лимиты |
| Огромные списки | `MaxPageSize`, обязательный `first` |
| Batching/alias-атаки (100 логинов в одном запросе) | лимит алиасов/операций, rate limiting по стоимости |
| Introspection в проде | отключить или ограничить |
| Неавторизованный доступ к полям | `[Authorize]` на полях, политики |
| Инъекции | параметры/переменные, валидация входа |
| Утечка ошибок | скрывать детали исключений |

```csharp
builder.Services.AddGraphQLServer()
    .AddMaxExecutionDepthRule(8)
    .ModifyCostOptions(o => { o.MaxFieldCost = 1000; o.EnforceCostLimits = true; })
    .AddAuthorization()
    .DisableIntrospection(!builder.Environment.IsDevelopment());
```

### Persisted queries

Клиенты заранее регистрируют запросы (по хэшу), а в проде принимаются **только известные** запросы. Это снижает трафик и полностью исключает произвольные тяжёлые запросы (allowlist).

## Нюансы и подводные камни

- Введите тайм-аут выполнения запроса.
- Ограничивайте не только количество запросов, но и их стоимость.
- Subscription-соединения требуют лимитов и аутентификации.
- Схема раскрывает структуру данных: отключайте introspection и подсказки полей в проде для публичных API.

## Практика

1. Включите лимит глубины и проверьте рекурсивный запрос.
2. Настройте persisted queries и allowlist.
3. Добавьте авторизацию на конфиденциальное поле.

## Вопросы с ответами

> [!question]- Как защитить GraphQL от тяжёлых запросов?
> Лимиты глубины и стоимости, ограничение размера страниц, таймауты, persisted queries.

> [!question]- Зачем persisted queries?
> Сервер выполняет только заранее известные запросы: меньше трафика и нет произвольных запросов от клиента.

## Связанные темы

- [[N:3ea331048679810ab845d7cf86845ccc]]
- [[N:3ea33104867981a88b97d7b7124a6163]]
