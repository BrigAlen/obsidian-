---
type: topic
domain: frontend
stage: 5
section: "5.1"
order: 5
status: todo
level: middle
notion_id: 3ea331048679819fbff4e2f18f924db2
tags: [domain/frontend, stage/5, level/middle, topic/vue, topic/router, topic/acl, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Meta-поля маршрутов и доступ по ролям

↑ [[FE 5.1 Vue Router|5.1 Vue Router]] · ← [[FE 5.1.4 Navigation guards|Предыдущая]] · → [[FE 5.1.6 Lazy loading маршрутов|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->









> [!info] Зачем это на собесе
> Декларативная конфигурация доступа к маршрутам и типизация `meta`.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

Маршрут может нести произвольные данные в `meta`.

```ts
// Типизация
declare module "vue-router" {
  interface RouteMeta { requiresAuth?: boolean; roles?: string[]; title?: string; layout?: "default" | "blank"; keepAlive?: boolean }
}

const routes: RouteRecordRaw[] = [
  { path: "/login", component: LoginPage, meta: { layout: "blank", title: "Вход" } },
  {
    path: "/admin", component: AdminLayout, meta: { requiresAuth: true, roles: ["admin"] },
    children: [{ path: "users", component: UsersPage, meta: { title: "Пользователи" } }],
  },
];

// meta наследуется по вложенности: используйте matched
router.beforeEach((to) => {
  const needsAuth = to.matched.some(r => r.meta.requiresAuth);
  const roles = to.matched.flatMap(r => r.meta.roles ?? []);
  if (needsAuth && !auth.user) return { name: "login", query: { redirect: to.fullPath } };
  if (roles.length && !roles.some(r => auth.user?.roles.includes(r))) return { name: "forbidden" };
});
```

Применения `meta`:

| Поле | Использование |
|---|---|
| `requiresAuth`, `roles`, `permissions` | доступ |
| `title`, `breadcrumb` | заголовок страницы и хлебные крошки |
| `layout` | выбор шаблона (`<component :is>` в `App.vue`) |
| `keepAlive` | кэширование страницы |
| `transition` | анимация перехода |

ACL: вместо ролей лучше **права (permissions)**: `permissions: ["orders:read"]`; роль → набор прав определяется на бэкенде. Меню генерируется из маршрутов (видимость по правам), кнопки — директивой `v-can`.

Динамические маршруты: после логина `router.addRoute(...)` только для доступных модулей (уменьшает бандл и раскрытие структуры).

## Нюансы и подводные камни

- `meta` не наследуется автоматически в `to.meta` (в v4 «слито» из совпавших записей, но лучше использовать `matched`).
- Проверка ролей на клиенте — UX; сервер должен отклонять запросы.
- Хардкод строк ролей размазывается по проекту: соберите в константы/перечисление.
- Прямой заход по ссылке: пользователь ещё не загружен — дождитесь инициализации.

## Практика

1. Типизируйте `RouteMeta` и настройте guard по `matched`.
2. Сгенерируйте меню из маршрутов с учётом прав.
3. Добавьте `layout` в meta и выбирайте шаблон в `App.vue`.

## Вопросы с ответами

> [!question]- Как защитить группу маршрутов?
> Указать `meta.requiresAuth`/`roles` на родителе и проверять `to.matched` в глобальном guard.

> [!question]- Роли или права?
> Права (permissions) гибче: роли — набор прав, приложение проверяет конкретные права.

## Связанные темы

- [[N:3ea33104867981d095e9fddd500a9f0e]]
- [[N:3ea331048679813ebd28c2768696b2fc]]
