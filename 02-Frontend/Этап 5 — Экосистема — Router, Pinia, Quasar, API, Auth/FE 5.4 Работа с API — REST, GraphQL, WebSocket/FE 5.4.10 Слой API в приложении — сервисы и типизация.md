---
type: topic
domain: frontend
stage: 5
section: "5.4"
order: 10
status: todo
level: middle
notion_id: 3ea331048679812caa72d90b8bef45f7
tags: [domain/frontend, stage/5, level/middle, topic/api, topic/architecture, topic/typescript, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Слой API в приложении: сервисы и типизация

↑ [[FE 5.4 Работа с API — REST, GraphQL, WebSocket|5.4 Работа с API: REST, GraphQL, WebSocket]] · ← [[FE 5.4.9 Long polling и SSE|Предыдущая]] · → [[FE 5.4.11 API-контракты — OpenAPI, codegen и contract testing|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->










> [!info] Зачем это на собесе
> Как организовать обращения к API, чтобы код был типобезопасным и легко тестируемым.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

Компоненты не вызывают `fetch/axios` напрямую: между ними и сетью стоит **слой API**.

```text
src/api/
  client.ts        # axios/ky-инстанс, интерсепторы, ApiError
  orders.ts        # ordersApi: list/get/create/update/remove
  schemas/         # Zod-схемы ответов (по необходимости)
  types.ts         # DTO / сгенерированные типы
  queries/         # useOrdersQuery, useCreateOrder (Vue Query)
```

```ts
// api/orders.ts
export const ordersApi = {
  list: (params: OrdersFilter, signal?: AbortSignal) => http.get<Page<OrderDto>>("/orders", { params, signal }).then(r => r.data),
  get: (id: string, signal?: AbortSignal) => http.get<OrderDto>(`/orders/${id}`, { signal }).then(r => r.data),
  create: (dto: CreateOrderDto, key = crypto.randomUUID()) => http.post<OrderDto>("/orders", dto, { headers: { "Idempotency-Key": key } }).then(r => r.data),
};

// api/queries/orders.ts
export const orderKeys = { all: ["orders"] as const, list: (f: OrdersFilter) => [...orderKeys.all, "list", f] as const, detail: (id: string) => [...orderKeys.all, id] as const };
export const useOrders = (filter: MaybeRefOrGetter<OrdersFilter>) =>
  useQuery({ queryKey: computed(() => orderKeys.list(toValue(filter))), queryFn: ({ signal }) => ordersApi.list(toValue(filter), signal), select: mapOrders });
export const useCreateOrder = () => { const qc = useQueryClient(); return useMutation({ mutationFn: ordersApi.create, onSuccess: () => qc.invalidateQueries({ queryKey: orderKeys.all }) }); };
```

Принципы:

| Принцип | Зачем |
|---|---|
| Один слой доступа | замена библиотеки/URL в одном месте, единые интерсепторы |
| DTO ↔ доменные модели (мапперы) | UI не зависит от формы ответа сервера (переименования, даты в `Date`, деньги) |
| Типы из контракта (OpenAPI/GraphQL codegen) | синхронизация с бэкендом |
| Ключи запросов — фабрики | предсказуемая инвалидация |
| Ошибки нормализованы | UI работает с `ApiError` |
| Отмена (`signal`) | без гонок |
| Тестируемость | подмена слоя (MSW / моки модулей) |
| Runtime-валидация на границе | защита от неожиданных ответов (Zod) |

Не смешивайте: слой API (транспорт) → Vue Query хуки (кэш) → компоненты (UI). Логика форматирования и бизнес-правила — в мапперах/доменных функциях.

## Нюансы и подводные камни

- «Умный» слой с бизнес-логикой становится вторым бэкендом.
- Дублирование типов вручную расходится с сервером — генерируйте.
- Мапперы должны быть чистыми и покрытыми тестами.
- Жёсткая связь компонентов и структуры ответа мешает эволюции API.

## Практика

1. Вынесите вызовы API из компонентов в `api/*.ts` и хуки Query.
2. Добавьте маппер DTO → модель (даты, деньги).
3. Настройте MSW и протестируйте слой без реального сервера.

## Вопросы с ответами

> [!question]- Зачем отдельный слой API?
> Единая точка изменений, общая обработка ошибок/авторизации, типизация и лёгкое тестирование.

> [!question]- Зачем мапперы DTO?
> Изолируют UI от формы ответа сервера и преобразуют данные (даты, деньги) в удобные модели.

## Связанные темы

- [[N:3ea3310486798173bebcd71df11c13c6]]
- [[N:cbd9f4bed053472fbe6ce5ef68d5cd7b]]
