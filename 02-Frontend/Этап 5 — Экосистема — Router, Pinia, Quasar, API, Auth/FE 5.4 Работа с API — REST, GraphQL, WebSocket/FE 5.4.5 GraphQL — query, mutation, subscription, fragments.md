---
type: topic
domain: frontend
stage: 5
section: "5.4"
order: 5
status: todo
level: middle
notion_id: 3ea33104867981a8a3b1c57d5d9d9535
tags: [domain/frontend, stage/5, level/middle, topic/api, topic/graphql, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# GraphQL: query, mutation, subscription, fragments

↑ [[FE 5.4 Работа с API — REST, GraphQL, WebSocket|5.4 Работа с API: REST, GraphQL, WebSocket]] · ← [[FE 5.4.4 Обработка ошибок, retry, отмена запросов (AbortController)|Предыдущая]] · → [[FE 5.4.6 GraphQL и REST — сравнение|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->













> [!info] Зачем это на собесе
> Клиентская сторона GraphQL: как писать запросы, использовать фрагменты и переменные.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

Серверная часть — в [[N:3ea3310486798175b3a6d2f428a4a9d4]]. Клиент отправляет `POST /graphql` с `{ query, variables, operationName }`.

```graphql
query GetOrder($id: ID!, $withItems: Boolean = false) {
  order(id: $id) {
    ...OrderFields
    items @include(if: $withItems) { sku qty }
  }
}
fragment OrderFields on Order { id number status total customer { id name } }

mutation CancelOrder($id: ID!) { cancelOrder(id: $id) { ...OrderFields } }

subscription OnOrderUpdated($id: ID!) { orderUpdated(id: $id) { id status } }
```

| Понятие | Смысл |
|---|---|
| Query | чтение, параллельное выполнение полей |
| Mutation | изменение, последовательное выполнение |
| Subscription | поток событий (WebSocket/SSE) |
| Variables | параметры вместо конкатенации строк (безопасность и кэш плана) |
| Fragments | переиспользуемые наборы полей; colocation с компонентом |
| Directives | `@include`, `@skip`, `@defer`, `@stream`, клиентские `@client` |
| Aliases | `a: order(id: 1) b: order(id: 2)` |
| Inline fragments, unions | `... on Photo { url }` |
| Introspection | получение схемы (генерация типов) |
| `__typename` | тип объекта для нормализованного кэша |

```ts
// graphql-request + Vue Query
const client = new GraphQLClient("/graphql", { headers: () => ({ Authorization: `Bearer ${token()}` }) });
const { data } = useQuery({ queryKey: ["order", id], queryFn: () => client.request(OrderDocument, { id: id.value }) });
```

Клиенты: Apollo Client (нормализованный кэш, `@vue/apollo-composable`), urql, `graphql-request` + Vue Query (проще, кэш по ключам). **Нормализованный кэш** по `__typename:id` автоматически обновляет одну сущность везде, где она показана.

Ошибки: HTTP 200 с полем `errors` (и, возможно, `data` частично) — обрабатывайте оба.

Подписки: `graphql-ws`; переподключение и повторная авторизация.

## Нюансы и подводные камни

- Нельзя конструировать запрос конкатенацией: используйте переменные.
- Кэширование HTTP затруднено (POST): нужны persisted queries/GET.
- Фрагменты «скрывают» зависимости: организуйте colocation и codegen.
- Избыточные запросы вложенности → тяжёлые запросы; ограничения на сервере.
- Ошибки на уровне полей приходят вместе с данными.

## Практика

1. Напишите запрос с переменными и фрагментом, выполните через `graphql-request`.
2. Подключите подписку через `graphql-ws`.
3. Сравните нормализованный кэш Apollo и кэш по ключам Vue Query.

## Вопросы с ответами

> [!question]- Чем query отличается от mutation?
> Query — чтение, поля выполняются параллельно; mutation — изменение, поля выполняются последовательно.

> [!question]- Зачем фрагменты?
> Переиспользование наборов полей и colocation данных с компонентами.

## Связанные темы

- [[N:3ea331048679814ea06ec88873e2751d]]
- [[N:3ea33104867981b396cddabaf563379e]]
