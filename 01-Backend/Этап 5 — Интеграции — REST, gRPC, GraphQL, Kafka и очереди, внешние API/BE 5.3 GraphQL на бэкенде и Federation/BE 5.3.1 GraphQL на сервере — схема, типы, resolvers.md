---
type: topic
domain: backend
stage: 5
section: "5.3"
order: 1
status: todo
level: middle
notion_id: 3ea3310486798175b3a6d2f428a4a9d4
tags: [domain/backend, stage/5, level/middle, topic/api, topic/graphql, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# GraphQL на сервере: схема, типы, resolvers

↑ [[BE 5.3 GraphQL на бэкенде и Federation|5.3 GraphQL на бэкенде и Federation]] · → [[BE 5.3.2 Hot Chocolate — queries, mutations, фильтрация, пагинация|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->



































> [!info] Зачем это на собесе
> Ждут понимания, чем GraphQL отличается от REST и где он оправдан.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

GraphQL — язык запросов и рантайм: клиент **сам описывает нужную форму данных**, сервер отвечает ровно ей через один endpoint (`POST /graphql`).

```graphql
type Query { order(id: ID!): Order  orders(first: Int, after: String): OrderConnection! }
type Mutation { cancelOrder(id: ID!): Order! }
type Subscription { orderUpdated(id: ID!): Order! }

type Order { id: ID!  number: String!  customer: Customer!  items: [Item!]!  total: Decimal! }
```

| Понятие | Смысл |
|---|---|
| Schema | строго типизированный контракт |
| Query / Mutation / Subscription | чтение / изменение / поток событий |
| Resolver | функция, получающая значение поля |
| Scalar, Enum, Interface, Union, Input | типы |

Клиент запрашивает только нужное:

```graphql
query { order(id: "42") { number customer { name } items { title price } } }
```

| Плюсы | Минусы |
|---|---|
| нет over/under-fetching | сложнее кэширование HTTP |
| один запрос вместо нескольких | N+1 в resolvers |
| самодокументируемая схема | нужны лимиты сложности |
| удобно для разных клиентов (web, mobile) | больше инфраструктуры |

Resolvers выполняются на каждом поле: поле `customer` вызовет свой resolver для каждого заказа — источник N+1 (см. [[N:3ea331048679815caa34c14a7c942c60]]).

## Нюансы и подводные камни

- Всегда 200 OK: ошибки лежат в поле `errors`, а не в HTTP-статусе.
- Схема — публичный контракт: устаревшие поля помечайте `@deprecated`, не удаляйте.
- Не отдавайте сущности БД как есть: проектируйте схему вокруг клиентов.
- Авторизация — на уровне полей и типов, а не только endpoint.
- GraphQL не заменяет REST везде: для простых CRUD и публичных API REST проще.

## Практика

1. Опишите схему магазина и запросите вложенные данные одним запросом.
2. Найдите N+1 в логах SQL.
3. Сравните число запросов клиента для REST и GraphQL на экране заказа.

## Вопросы с ответами

> [!question]- Чем GraphQL отличается от REST?
> Один endpoint и клиентское описание формы ответа против набора ресурсов с фиксированными представлениями.

> [!question]- Что такое resolver?
> Функция, вычисляющая значение конкретного поля схемы.

> [!question]- Почему в GraphQL всегда 200?
> Транспорт и результат разделены: частичные данные и список `errors` возвращаются вместе.

## Связанные темы

- [[N:3ea33104867981bf90d1f3ec3e986fe2]]
- [[N:3ea331048679815caa34c14a7c942c60]]
