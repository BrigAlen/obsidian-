---
type: topic
domain: frontend
stage: 5
section: "5.7"
order: 1
status: todo
level: middle
notion_id: 3ea33104867981b5810dd862257958d2
tags: [domain/frontend, stage/5, level/middle, topic/testing, topic/pinia, topic/composables, priority/must]
reviewed:
next_review:
priority: must
time: 5
---

# Тестирование composables и Pinia-сторов

↑ [[FE 5.7 Тестирование приложения|5.7 Тестирование приложения]] · → [[FE 5.7.2 Мокирование API — MSW, моки Axios и GraphQL|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~5 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->













> [!info] Зачем это на собесе
> Как тестировать логику вне компонентов: composables с хуками и сторы Pinia.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

### Composables

Composable без хуков жизненного цикла — обычная функция:

```ts
it("useCounter увеличивает значение", () => {
  const { count, inc } = useCounter(1);
  inc();
  expect(count.value).toBe(2);
});
```

Composable, использующий `onMounted`, `provide/inject`, `useRoute`, требует контекста компонента — хелпер `withSetup`:

```ts
import { createApp } from "vue";
export function withSetup<T>(composable: () => T, { plugins = [] as any[] } = {}): [T, App] {
  let result!: T;
  const app = createApp({ setup() { result = composable(); return () => null; } });
  plugins.forEach(p => app.use(p));
  app.mount(document.createElement("div"));
  return [result, app];
}

it("useEventListener снимает слушатель при unmount", () => {
  const spy = vi.fn();
  const [, app] = withSetup(() => useEventListener(window, "resize", spy));
  window.dispatchEvent(new Event("resize")); expect(spy).toHaveBeenCalledTimes(1);
  app.unmount();
  window.dispatchEvent(new Event("resize")); expect(spy).toHaveBeenCalledTimes(1);
});
```

Асинхронные и с таймерами — `vi.useFakeTimers()`, `await nextTick()`, `flushPromises()`, `vi.waitFor`.

### Pinia

```ts
import { setActivePinia, createPinia } from "pinia";
beforeEach(() => setActivePinia(createPinia()));                       // чистый стор на каждый тест

it("cart: добавляет и считает сумму", () => {
  const cart = useCartStore();
  cart.add({ id: 1, price: 100, qty: 2 });
  expect(cart.total).toBe(200);
});

it("auth.login сохраняет пользователя", async () => {
  vi.mocked(api.login).mockResolvedValue({ user: { id: 1 }, token: "t" });
  const auth = useAuthStore();
  await auth.login("a@x.ru", "pwd");
  expect(auth.isAuthenticated).toBe(true);
});
```

Для компонентов: `createTestingPinia({ createSpy: vi.fn, initialState: { auth: { user } }, stubActions: false })` — подмена состояния и слежение за actions.

```ts
const wrapper = mount(Comp, { global: { plugins: [createTestingPinia({ createSpy: vi.fn })] } });
const store = useCartStore(); store.add = vi.fn();     // actions по умолчанию заглушены
await wrapper.get("button").trigger("click"); expect(store.add).toHaveBeenCalledWith(...)
```

Что тестировать: логику actions/getters, обработку ошибок, побочные эффекты (сохранение, вызовы API — замоканы), reset. Не тестируйте реализацию Pinia.

## Нюансы и подводные камни

- Без нового `createPinia()` между тестами состояние протекает.
- Composable с `inject` требует `provide` при монтировании.
- Забытая очистка (`app.unmount()`) оставляет слушатели.
- `createTestingPinia` по умолчанию заглушает actions: включайте `stubActions: false`, если нужна реальная логика.
- Сторы, зависящие от `localStorage`, требуют очистки между тестами.

## Практика

1. Напишите `withSetup` и протестируйте composable с `onMounted`.
2. Протестируйте стор корзины: getters, actions, ошибки.
3. Проверьте, что компонент вызывает action при клике (`createTestingPinia`).

## Вопросы с ответами

> [!question]- Как протестировать composable с хуками жизненного цикла?
> Смонтировать его в тестовом приложении/компоненте (хелпер `withSetup`) и, при необходимости, размонтировать.

> [!question]- Чем `createTestingPinia` полезен?
> Позволяет задать начальное состояние и следить за вызовами actions без реальных побочных эффектов.

## Связанные темы

- [[N:3ea33104867981b4b4fcc2eac6967d70]]
- [[N:3ea33104867981b78458edabcd0ef13e]]
