---
type: topic
domain: frontend
stage: 5
section: "5.1"
order: 4
status: todo
level: middle
notion_id: 3ea33104867981d095e9fddd500a9f0e
tags: [domain/frontend, stage/5, level/middle, topic/vue, topic/router, topic/guards, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Navigation guards

↑ [[FE 5.1 Vue Router|5.1 Vue Router]] · ← [[FE 5.1.3 Программная навигация|Предыдущая]] · → [[FE 5.1.5 Meta-поля маршрутов и доступ по ролям|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->

















> [!info] Зачем это на собесе
> Защита маршрутов и логика перед переходом; частый вопрос про порядок guard-ов.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

Guard решает: разрешить, отменить или перенаправить навигацию.

```ts
router.beforeEach(async (to, from) => {
  const auth = useAuthStore();                              // Pinia доступна после app.use(pinia)
  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    return { name: "login", query: { redirect: to.fullPath } };     // редирект
  }
  if (to.meta.roles && !auth.hasAnyRole(to.meta.roles)) return { name: "forbidden" };
  // return true / undefined — разрешить; return false — отменить
});
router.afterEach((to, from, failure) => { document.title = to.meta.title ?? "App"; analytics.page(to.fullPath); });
router.onError((err) => report(err));
```

| Уровень | Хук |
|---|---|
| Глобальные | `beforeEach`, `beforeResolve`, `afterEach` |
| На маршруте | `beforeEnter` |
| В компоненте | `onBeforeRouteUpdate`, `onBeforeRouteLeave`, (Options: `beforeRouteEnter`) |

Порядок: `beforeRouteLeave` (уходящий компонент) → глобальный `beforeEach` → `beforeRouteUpdate` (переиспользуемые) → `beforeEnter` (маршрут) → разрешение асинхронных компонентов → `beforeRouteEnter` → глобальный `beforeResolve` → навигация подтверждена → `afterEach` → обновление DOM.

```ts
onBeforeRouteLeave(() => {
  if (form.isDirty && !confirm("Есть несохранённые изменения. Уйти?")) return false;    // защита от потери данных
});
```

Использования: аутентификация и роли, загрузка обязательных данных (`await`), несохранённые изменения, аналитика, лоадер навигации, смена `document.title`.

Guards выполняются последовательно; `async` guard блокирует переход до завершения.

## Нюансы и подводные камни

- Старая сигнатура с `next()` устарела: используйте возвращаемое значение; нельзя вызывать `next` дважды.
- Бесконечные редиректы (логин → главная → логин): проверяйте условие.
- Клиентские guards — UX, а не безопасность: права проверяются на сервере.
- Тяжёлые запросы в `beforeEach` тормозят каждый переход: кэшируйте.
- Инициализация состояния (например, восстановление сессии) должна завершиться до первой навигации.

## Практика

1. Реализуйте guard авторизации и ролей с редиректом на логин.
2. Добавьте предупреждение о несохранённых изменениях.
3. Покажите глобальный индикатор загрузки на время навигации.

## Вопросы с ответами

> [!question]- Какие бывают navigation guards?
> Глобальные (`beforeEach/beforeResolve/afterEach`), на маршруте (`beforeEnter`) и в компоненте (`onBeforeRouteLeave/Update`).

> [!question]- Защищают ли guards от доступа к данным?
> Нет, они ограничивают только интерфейс: доступ к API должен проверять сервер.

## Связанные темы

- [[N:3ea3310486798194982ef8547def2804]]
- [[N:3ea331048679819fbff4e2f18f924db2]]
