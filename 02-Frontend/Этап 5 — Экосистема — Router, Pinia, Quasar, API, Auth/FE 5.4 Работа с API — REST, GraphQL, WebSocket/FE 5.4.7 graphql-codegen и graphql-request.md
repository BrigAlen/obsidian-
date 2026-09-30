---
type: topic
domain: frontend
stage: 5
section: "5.4"
order: 7
status: todo
level: middle
notion_id: 3ea331048679818eacacea12f103344c
tags: [domain/frontend, stage/5, level/middle, topic/api, topic/graphql, topic/codegen, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# graphql-codegen и graphql-request

↑ [[FE 5.4 Работа с API — REST, GraphQL, WebSocket|5.4 Работа с API: REST, GraphQL, WebSocket]] · ← [[FE 5.4.6 GraphQL и REST — сравнение|Предыдущая]] · → [[FE 5.4.8 WebSocket|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->









> [!info] Зачем это на собесе
> Типобезопасный GraphQL-клиент: как получить типы из схемы и документов.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

**GraphQL Code Generator** читает схему (`schema.graphql` или URL/introspection) и документы (`*.graphql`, `gql` в коде) и генерирует TypeScript-типы и типизированные операции.

```yaml
# codegen.ts
import type { CodegenConfig } from "@graphql-codegen/cli";
const config: CodegenConfig = {
  schema: "http://localhost:5000/graphql",
  documents: ["src/**/*.graphql", "src/**/*.vue"],
  generates: {
    "src/gql/": { preset: "client", presetConfig: { fragmentMasking: false } },
    // либо: "src/generated.ts": { plugins: ["typescript", "typescript-operations", "typed-document-node"] },
  },
  config: { scalars: { DateTime: "string", Decimal: "string" } },
};
export default config;
```

```graphql
# src/orders/orders.graphql
query Orders($first: Int!, $after: String) { orders(first: $first, after: $after) { edges { node { id number status } } pageInfo { hasNextPage endCursor } } }
```

```ts
import { graphql } from "@/gql";                                  // preset client: типизированная функция gql
const OrdersQuery = graphql(`query Orders($first: Int!) { orders(first: $first) { edges { node { id number } } } }`);

const client = new GraphQLClient("/graphql");
const data = await client.request(OrdersQuery, { first: 20 });    // data и variables типизированы
const { data: q } = useQuery({ queryKey: ["orders"], queryFn: () => client.request(OrdersQuery, { first: 20 }) });
```

`graphql-request` — минимальный клиент (fetch), не имеет кэша (кэшем занимается Vue Query). Поддерживает заголовки, middleware, `rawRequest`, `batchRequests`, загрузку файлов.

Практика:

- Скрипт `codegen` (`graphql-codegen --watch` в dev), генерация в CI; артефакты не коммитить или коммитить осознанно.
- Скалярные типы (`DateTime`, `Decimal`, `Upload`) мапить явно.
- Фрагменты рядом с компонентами; типы `FragmentType` для маскирования данных.
- Проверка запросов относительно схемы (`graphql-eslint`).
- Валидация ответов не нужна для типов, но контракт должен проверяться (сравнение схем в CI).

## Нюансы и подводные камни

- Схема на сервере меняется: генерация должна быть частью пайплайна.
- Сгенерированные типы описывают запрошенные поля; лишние поля недоступны.
- `any` в скалярах при отсутствии маппинга.
- Скачивание схемы с продовой среды в CI — используйте зафиксированный файл схемы.

## Практика

1. Настройте codegen и типизированные операции для 2–3 запросов.
2. Подключите `graphql-request` к Vue Query.
3. Добавьте проверку схемы и запросов в CI.

## Вопросы с ответами

> [!question]- Что делает GraphQL Code Generator?
> Генерирует TypeScript-типы и типизированные документы из схемы и запросов.

> [!question]- Чем `graphql-request` отличается от Apollo?
> Это минимальный клиент без нормализованного кэша; кэш делегируется Vue Query.

## Связанные темы

- [[N:3ea33104867981b396cddabaf563379e]]
- [[N:3ea33104867981cebb9ce4aaf0305137]]
