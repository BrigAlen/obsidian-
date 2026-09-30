---
type: topic
domain: frontend
stage: 5
section: "5.7"
order: 3
status: todo
level: middle
notion_id: 3ea33104867981a18b7bf87480a1b51f
tags: [domain/frontend, stage/5, level/middle, topic/testing, topic/router, topic/guards, priority/must]
reviewed:
next_review:
priority: must
time: 4
---

# Тестирование роутера и navigation guards

↑ [[FE 5.7 Тестирование приложения|5.7 Тестирование приложения]] · ← [[FE 5.7.2 Мокирование API — MSW, моки Axios и GraphQL|Предыдущая]] · → [[FE 5.7.4 Тестирование компонентов с Quasar|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~4 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->





> [!info] Зачем это на собесе
> Guards содержат критичную логику доступа: их нужно проверять отдельно от UI.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

Используйте настоящий роутер с `createMemoryHistory`, а не мок.

```ts
import { createRouter, createMemoryHistory } from "vue-router";
import { routes, installGuards } from "@/router";

function makeRouter() {
  const router = createRouter({ history: createMemoryHistory(), routes });
  installGuards(router);                                    // guards вынесены в функцию для тестируемости
  return router;
}

it("неавторизованного перенаправляет на логин с redirect", async () => {
  setActivePinia(createTestingPinia({ initialState: { auth: { user: null } }, stubActions: false }));
  const router = makeRouter();
  await router.push("/orders/5");
  await router.isReady();
  expect(router.currentRoute.value.name).toBe("login");
  expect(router.currentRoute.value.query.redirect).toBe("/orders/5");
});

it("пользователь без роли попадает на forbidden", async () => {
  useAuthStore().user = { roles: ["user"] };
  await router.push("/admin");
  expect(router.currentRoute.value.name).toBe("forbidden");
});

it("предупреждает при уходе с несохранённой формой", async () => {
  const w = mount(EditPage, { global: { plugins: [router, pinia] } });
  await router.push("/orders/1/edit"); w.vm.dirty = true;
  vi.spyOn(window, "confirm").mockReturnValue(false);
  await router.push("/orders");
  expect(router.currentRoute.value.path).toBe("/orders/1/edit");           // переход отменён
});
```

Компоненты, зависящие от роутера:

```ts
const wrapper = mount(Nav, { global: { plugins: [router] } });
await router.push("/orders"); await router.isReady();
expect(wrapper.get("a.active").text()).toBe("Заказы");
// или мок: global: { mocks: { $route, $router }, stubs: { RouterLink: RouterLinkStub } }
```

Что проверять: редиректы, доступ по ролям/правам, `meta`, преобразование `props`, загрузка данных в guards, `onBeforeRouteLeave`, ленивые компоненты (`await flushPromises()`), 404.

Практика: guards — отдельные функции с явными зависимостями (стор передаётся параметром) — их можно тестировать без роутера как обычные функции.

## Нюансы и подводные камни

- Ждите `await router.push(...)` и `router.isReady()` перед проверками.
- Для guards, использующих Pinia, активируйте Pinia до вызова.
- Ленивые компоненты загружаются асинхронно: `flushPromises`.
- Глобальный роутер, разделяемый между тестами, — источник зависимости: создавайте новый на тест.

## Практика

1. Протестируйте guard авторизации и ролей матрицей «маршрут × роль».
2. Проверьте защиту от потери несохранённых данных.
3. Вынесите guards в чистые функции и покройте unit-тестами.

## Вопросы с ответами

> [!question]- Как тестировать navigation guards?
> Создать роутер с `createMemoryHistory`, установить guards и проверить итоговый маршрут после `router.push`.

> [!question]- Что важно перед проверкой маршрута?
> Дождаться завершения навигации (`await router.push`, `router.isReady()`).

## Связанные темы

- [[N:3ea33104867981b78458edabcd0ef13e]]
- [[N:3ea33104867981d68446c879a4fae8c5]]
