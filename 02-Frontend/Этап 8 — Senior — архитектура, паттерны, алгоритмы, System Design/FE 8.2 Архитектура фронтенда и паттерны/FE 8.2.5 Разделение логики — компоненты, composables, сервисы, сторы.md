---
type: topic
domain: frontend
stage: 8
section: "8.2"
order: 5
status: todo
level: senior
notion_id: 3ea3310486798115a437ec9eda2acc96
tags: [domain/frontend, stage/8, level/senior, topic/architecture, topic/composables, topic/pinia, priority/should]
reviewed:
next_review:
priority: should
time: 3
---

# Разделение логики: компоненты, composables, сервисы, сторы

↑ [[FE 8.2 Архитектура фронтенда и паттерны|8.2 Архитектура фронтенда и паттерны]] · ← [[FE 8.2.4 Feature-Sliced Design|Предыдущая]] · → [[FE 8.2.6 Дизайн-система и UI-kit|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: senior</span></div>
<!-- meta:end -->




> [!info] Зачем это на собесе
> Главный практический вопрос: где что должно лежать во Vue-приложении.

## Слои

| Слой | Ответственность | Знает о |
|---|---|---|
| **Компонент** | отображение, обработка пользовательского ввода | props, composables, store |
| **Composable** | переиспользуемая реактивная логика (UI и данные) | сервисы, другие composables |
| **Store (Pinia)** | общее состояние приложения, кэш данных | сервисы |
| **Service / API** | обмен с бэкендом, преобразование DTO | HTTP-клиент |
| **Utils** | чистые функции | ничего |

## Как решать, где хранить

- локально нужное одному компоненту → `ref` в компоненте;
- переиспользуемая логика с реактивностью → composable;
- разделяется между несколькими страницами или переживает навигацию → Pinia;
- данные с сервера с кэшем, повторной загрузкой, инвалидацией → TanStack Query (Vue Query);
- состояние в URL (фильтры, страница) → query-параметры роутера;
- форма → локально (vee-validate, FormKit).

## Пример

```ts
// services/orders.ts
export const ordersApi = {
  list: (params: OrdersQuery) => http.get<OrderDto[]>('/orders', { params }).then(r => r.data.map(toOrder)),
}

// composables/useOrders.ts
export function useOrders(query: Ref<OrdersQuery>) {
  return useQuery({ queryKey: ['orders', query], queryFn: () => ordersApi.list(query.value) })
}
```

```vue
<script setup lang="ts">
const filters = ref<OrdersQuery>({ page: 1 })
const { data: orders, isLoading } = useOrders(filters)
</script>
<template><OrdersTable :rows="orders" :loading="isLoading" /></template>
```

## Антипаттерны

- HTTP-запросы прямо в компонентах;
- вся логика в store, включая локальную;
- store как кэш серверных данных вручную (без инвалидации);
- «умные» компоненты, влезающие в глобальное состояние без нужды;
- события `emit` через 5 уровней вместо `provide/inject` или стора.

## Тестируемость

Логика в composables и сервисах тестируется без DOM, компоненты — через Testing Library.

## Вопросы с ответами

> [!question]- Когда данные класть в Pinia, а когда использовать Vue Query?
> Серверные данные (кэш, refetch, инвалидация, состояние загрузки) — Vue Query. Клиентское глобальное состояние (пользователь, настройки, UI) — Pinia.

> [!question]- Чем composable отличается от store?
> Composable создаёт независимое состояние на каждый вызов (если не вынесено наружу), store — единый общий экземпляр.
