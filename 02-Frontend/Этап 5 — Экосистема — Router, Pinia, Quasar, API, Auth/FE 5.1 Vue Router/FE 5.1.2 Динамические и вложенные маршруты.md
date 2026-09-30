---
type: topic
domain: frontend
stage: 5
section: "5.1"
order: 2
status: todo
level: middle
notion_id: 3ea3310486798144b803e92c11aa8054
tags: [domain/frontend, stage/5, level/middle, topic/vue, topic/router, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Динамические и вложенные маршруты

↑ [[FE 5.1 Vue Router|5.1 Vue Router]] · ← [[FE 5.1.1 Настройка роутера, history-режимы|Предыдущая]] · → [[FE 5.1.3 Программная навигация|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->









> [!info] Зачем это на собесе
> Параметры маршрута, реакция на их изменение и вложенные layout-ы.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

```ts
const routes = [
  { path: "/orders/:id(\\d+)", name: "order", component: OrderPage, props: true },          // регулярное ограничение и params → props
  { path: "/files/:path(.*)*", component: FilesPage },                                       // catch-all
  {
    path: "/settings", component: SettingsLayout,                                            // вложенные маршруты
    children: [
      { path: "", redirect: { name: "profile" } },
      { path: "profile", name: "profile", component: ProfileTab },
      { path: "security", name: "security", component: SecurityTab },
    ],
  },
  { path: "/legacy", redirect: "/new" },
  { path: "/u/:name", alias: "/user/:name", component: UserPage },
  { path: "/search", component: SearchPage, props: (route) => ({ q: route.query.q, page: Number(route.query.page ?? 1) }) },
];
```

`SettingsLayout` содержит свой `<RouterView />` для дочернего маршрута.

Реакция на смену параметров: компонент **переиспользуется** (`/orders/1` → `/orders/2`), хуки `mounted` не вызываются повторно:

```ts
const route = useRoute();
watch(() => route.params.id, (id) => load(Number(id)), { immediate: true });
onBeforeRouteUpdate((to, from) => { /* реакция до обновления */ });
// или принудительно пересоздавать: <RouterView :key="$route.fullPath" />
```

Именованные виды: `components: { default: Main, sidebar: Sidebar }` и `<RouterView name="sidebar" />`.

Query и hash: `router.push({ path: "/orders", query: { status: "paid", page: 2 } })` → `/orders?status=paid&page=2`; типы значений — строки/массивы строк.

## Нюансы и подводные камни

- Параметры приходят строками: приводите к числу.
- Один и тот же компонент для разных параметров не перемонтируется — нужен `watch` или `key`.
- `props: true` делает компонент независимым от роутера (проще тесты).
- Порядок маршрутов важен для совпадения; более специфичные — выше.
- Пустой дочерний путь `""` даёт маршрут по умолчанию для родителя.

## Практика

1. Сделайте маршрут `/orders/:id` с проверкой числа и передачей в props.
2. Реализуйте страницу настроек с вложенными вкладками.
3. Загружайте данные при смене `id` через `watch`.

## Вопросы с ответами

> [!question]- Почему компонент не обновляется при смене `:id`?
> Vue Router переиспользует экземпляр; нужно отслеживать `route.params` или использовать `key`.

> [!question]- Как передать параметры маршрута в компонент как props?
> Опция `props: true` или функция `props: route => ({...})`.

## Связанные темы

- [[N:3ea331048679815f8ab2fd34e863ccd4]]
- [[N:3ea3310486798194982ef8547def2804]]
