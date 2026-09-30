---
type: topic
domain: frontend
stage: 5
section: "5.7"
order: 2
status: todo
level: middle
notion_id: 3ea33104867981b78458edabcd0ef13e
tags: [domain/frontend, stage/5, level/middle, topic/testing, topic/msw, topic/mocks, priority/must]
reviewed:
next_review:
priority: must
time: 4
---

# Мокирование API: MSW, моки Axios и GraphQL

↑ [[FE 5.7 Тестирование приложения|5.7 Тестирование приложения]] · ← [[FE 5.7.1 Тестирование composables и Pinia-сторов|Предыдущая]] · → [[FE 5.7.3 Тестирование роутера и navigation guards|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~4 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->













> [!info] Зачем это на собесе
> MSW — стандарт мокирования сети: тест видит настоящий HTTP-слой, а не подмену модулей.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

**MSW (Mock Service Worker)** перехватывает сетевые запросы на уровне сети: в браузере через Service Worker, в тестах (Node) — через `msw/node` (интерсепторы). Код приложения (Axios/fetch/Vue Query) работает как в реальности.

```ts
// test/mocks/handlers.ts
import { http, HttpResponse, graphql, delay } from "msw";
export const handlers = [
  http.get("/api/orders", ({ request }) => {
    const page = Number(new URL(request.url).searchParams.get("page") ?? 1);
    return HttpResponse.json({ items: makeOrders(20), total: 100, page });
  }),
  http.post("/api/orders", async ({ request }) => HttpResponse.json({ id: 1, ...(await request.json()) as object }, { status: 201 })),
  http.get("/api/orders/:id", ({ params }) => params.id === "404" ? new HttpResponse(null, { status: 404 }) : HttpResponse.json(makeOrder(Number(params.id)))),
  graphql.query("Orders", () => HttpResponse.json({ data: { orders: [] } })),
];

// test/setup.ts
import { setupServer } from "msw/node";
export const server = setupServer(...handlers);
beforeAll(() => server.listen({ onUnhandledRequest: "error" }));       // непредусмотренные запросы — ошибка
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

// переопределение в тесте
it("показывает ошибку при 500", async () => {
  server.use(http.get("/api/orders", () => new HttpResponse(null, { status: 500 })));
  render(OrdersPage, { global: { plugins: [queryPlugin] } });
  expect(await screen.findByText(/не удалось загрузить/i)).toBeInTheDocument();
});
server.use(http.get("/api/orders", async () => { await delay(200); return HttpResponse.json(...) }));   // задержки, состояния загрузки
```

Сравнение подходов:

| Подход | Плюсы | Минусы |
|---|---|---|
| `vi.mock("axios")` / мок API-модуля | быстро | тест связан с реализацией, не проверяет заголовки/URL/сериализацию |
| **MSW** | реалистично, не зависит от HTTP-клиента, переиспользуется в dev/Storybook | нужна настройка |
| Реальный тестовый стенд | максимальная реальность | медленно и нестабильно |
| Prism/mock-сервер по OpenAPI | контракт | внешний процесс |

Практика: общие моки для тестов, Storybook и режима разработки (`worker.start()`); данные — фабрики (`@faker-js/faker`, `@mswjs/data`); `onUnhandledRequest: "error"`; валидация запросов схемой OpenAPI.

Мок Axios: `axios-mock-adapter` (подходит для простых случаев), но MSW независим от клиента.

## Нюансы и подводные камни

- Vue Query кэширует между тестами: создавайте новый `QueryClient` на тест (`retry: false`).
- Относительные URL в Node-окружении требуют базового адреса (`jsdom` + `location`).
- Забытый `resetHandlers` протекает между тестами.
- Асинхронность: используйте `findBy…` и `waitFor`.
- Не мокайте то, что тестируете (собственный API-слой).

## Практика

1. Настройте MSW для Vitest и протестируйте загрузку списка и ошибку 500.
2. Используйте те же handlers в Storybook/dev.
3. Проверьте, что запрос содержит нужные заголовки и тело.

## Вопросы с ответами

> [!question]- Чем MSW лучше `vi.mock("axios")`?
> Тест не привязан к клиенту и проверяет реальный HTTP-слой (URL, заголовки, сериализацию), моки переиспользуются в разных окружениях.

> [!question]- Зачем `onUnhandledRequest: "error"`?
> Чтобы тест падал при запросах, для которых нет моков, а не уходил в сеть.

## Связанные темы

- [[N:3ea33104867981b5810dd862257958d2]]
- [[N:3ea33104867981a18b7bf87480a1b51f]]
