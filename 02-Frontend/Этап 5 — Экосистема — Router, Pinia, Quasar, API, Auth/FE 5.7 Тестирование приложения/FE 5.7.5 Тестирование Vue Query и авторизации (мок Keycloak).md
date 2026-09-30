---
type: topic
domain: frontend
stage: 5
section: "5.7"
order: 5
status: todo
level: middle
notion_id: 3ea33104867981c0b163f7c428eb6b11
tags: [domain/frontend, stage/5, level/middle, topic/testing, topic/vue-query, topic/keycloak, priority/must]
reviewed:
next_review:
priority: must
time: 5
---

# Тестирование Vue Query и авторизации (мок Keycloak)

↑ [[FE 5.7 Тестирование приложения|5.7 Тестирование приложения]] · ← [[FE 5.7.4 Тестирование компонентов с Quasar|Предыдущая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~5 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->



> [!info] Зачем это на собесе
> Тесты кэша запросов и защищённых экранов без реального провайдера идентичности.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

### Vue Query

```ts
import { VueQueryPlugin, QueryClient } from "@tanstack/vue-query";

function makeQueryClient() {
  return new QueryClient({ defaultOptions: { queries: { retry: false, gcTime: Infinity, staleTime: 0 }, mutations: { retry: false } } });   // без ретраев и общего кэша
}

function renderWithQuery(component: Component, opts = {}) {
  const queryClient = makeQueryClient();
  return { queryClient, ...render(component, { global: { plugins: [[VueQueryPlugin, { queryClient }], pinia, router] }, ...opts }) };
}

it("показывает заказы", async () => {
  renderWithQuery(OrdersPage);
  expect(screen.getByText(/загрузка/i)).toBeInTheDocument();
  expect(await screen.findByText("A-1")).toBeInTheDocument();                       // данные пришли из MSW
});

it("после создания заказа список обновляется (инвалидация)", async () => {
  const { queryClient } = renderWithQuery(OrdersPage);
  const spy = vi.spyOn(queryClient, "invalidateQueries");
  await user.click(screen.getByRole("button", { name: /создать/i }));
  await waitFor(() => expect(spy).toHaveBeenCalledWith({ queryKey: ["orders"] }));
});

// Composable с Query
const [{ data, isSuccess }] = withSetup(() => useOrders(ref({ page: 1 })), { plugins: [[VueQueryPlugin, { queryClient }]] });
await vi.waitFor(() => expect(isSuccess.value).toBe(true));
```

Оптимистичное обновление: MSW возвращает ошибку → проверяем откат состояния списка.

### Авторизация (мок Keycloak)

```ts
// test/mocks/keycloak.ts
export const keycloakMock = { authenticated: true, token: "test-token", tokenParsed: { sub: "1", preferred_username: "anna", realm_access: { roles: ["user"] } },
  login: vi.fn(), logout: vi.fn(), updateToken: vi.fn().mockResolvedValue(true), init: vi.fn().mockResolvedValue(true), onTokenExpired: undefined };
vi.mock("@/auth/keycloak", () => ({ keycloak: keycloakMock, initAuth: vi.fn() }));

it("добавляет Bearer в запросы", async () => {
  let auth = "";
  server.use(http.get("/api/me", ({ request }) => { auth = request.headers.get("authorization") ?? ""; return HttpResponse.json({}); }));
  await api.get("/me");
  expect(auth).toBe("Bearer test-token");
});

it("без роли admin — кнопка скрыта", () => {
  keycloakMock.tokenParsed.realm_access.roles = ["user"];
  render(UsersPage, ...); expect(screen.queryByRole("button", { name: /удалить/i })).toBeNull();
});
it("401 → обновление токена → повтор", async () => { /* MSW: первый запрос 401, второй 200; проверяем updateToken и результат */ });
```

Практика: выделяйте слой аутентификации за интерфейсом (`useAuth`) — в тестах подменяется стор/composable, не библиотека.

## Нюансы и подводные камни

- Новый `QueryClient` на каждый тест, иначе кэш протекает.
- `retry: false` в тестах, иначе ошибки «зависают» на повторах.
- Не забывайте очищать моки Keycloak между тестами (`vi.clearAllMocks()`).
- Токены в реальном формате JWT не нужны; важна форма `tokenParsed`.
- Асинхронные проверки — `findBy`/`waitFor`, а не `setTimeout`.

## Практика

1. Напишите `renderWithQuery` и протестируйте состояния загрузки, успеха и ошибки.
2. Смоделируйте мок Keycloak и проверьте матрицу ролей.
3. Протестируйте обновление токена при 401 с MSW.

## Вопросы с ответами

> [!question]- Почему в тестах Vue Query отключают retry?
> Чтобы ошибки не откладывались повторами и тест не «висел» до исчерпания попыток.

> [!question]- Как тестировать авторизованные экраны без Keycloak?
> Замокать модуль аутентификации (или `useAuth`) с нужными claims/ролями и проверять поведение UI и заголовки запросов.

## Связанные темы

- [[N:3ea33104867981d68446c879a4fae8c5]]
- [[N:3ea3310486798198b18efa0927c00f99]]
