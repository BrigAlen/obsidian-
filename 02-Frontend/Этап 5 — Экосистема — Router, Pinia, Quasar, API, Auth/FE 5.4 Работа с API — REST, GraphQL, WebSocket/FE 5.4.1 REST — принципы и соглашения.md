---
type: topic
domain: frontend
stage: 5
section: "5.4"
order: 1
status: todo
level: middle
notion_id: 3ea3310486798111bac4ca5217597700
tags: [domain/frontend, stage/5, level/middle, topic/api, topic/rest, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# REST: принципы и соглашения

↑ [[FE 5.4 Работа с API — REST, GraphQL, WebSocket|5.4 Работа с API: REST, GraphQL, WebSocket]] · → [[FE 5.4.2 Fetch API и Axios|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->


> [!info] Зачем это на собесе
> Фронтендер должен понимать REST со стороны клиента: методы, коды, идемпотентность, формат ошибок.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

Серверная сторона REST разобрана в [[N:3ea33104867981beb645e6208a37200e]]. Что важно клиенту:

| Тема | Клиентская практика |
|---|---|
| Методы | GET безопасен и кэшируется, POST не идемпотентен (защита от двойного клика, `Idempotency-Key`), PUT/DELETE идемпотентны |
| Коды | 2xx — успех, 401 → обновить токен/логин, 403 → сообщение о правах, 404, 409 (конфликт версий), 422 (валидация → поля формы), 429 (повтор позже, `Retry-After`), 5xx (ретрай/сообщение) |
| Формат ошибок | `ProblemDetails` (`type`, `title`, `detail`, `errors`, `traceId`) — единый разбор на клиенте |
| Пагинация | `page/size` или cursor; ссылки/`total`; бесконечный скролл |
| Фильтры и сортировка | query-параметры, синхронизация с URL |
| Условные запросы | ETag/`If-None-Match` (304), `If-Match` для оптимистичной блокировки |
| Версионирование | заголовок/URL; учитывать в клиенте |
| Даты и числа | ISO 8601 UTC, деньги как строки/минимальные единицы |
| Идентификаторы | строки (id > 2⁵³ теряют точность в JS числом) |
| Кэширование | `Cache-Control`, серверный кэш + клиентский (Vue Query) |

```ts
// Единый разбор ошибки
export class ApiError extends Error {
  constructor(public status: number, public problem?: ProblemDetails, public fieldErrors: Record<string, string[]> = {}) { super(problem?.title ?? `HTTP ${status}`); }
}
async function parse(res: Response) {
  if (res.ok) return res.status === 204 ? undefined : res.json();
  const problem = await res.json().catch(() => undefined);
  throw new ApiError(res.status, problem, problem?.errors);
}
```

Идемпотентность и повторы: безопасно повторять GET/PUT/DELETE; POST — только с ключом идемпотентности.

Именование клиента: ресурсо-ориентированные модули (`ordersApi.list/get/create/update/remove`), а не разрозненные вызовы.

## Нюансы и подводные камни

- `200` с ошибкой в теле — антипаттерн: договоритесь о коде и формате.
- Не парсите `error.message` бэкенда для UI-логики — используйте коды.
- Не храните токены и не логируйте их в URL.
- CORS и preflight добавляют задержку.
- Большие числа и денежные значения — не `number` без осторожности.

## Практика

1. Опишите единый разбор ошибок и покажите ошибки валидации на полях.
2. Реализуйте `Idempotency-Key` для создания заказа.
3. Настройте обработку 401 с обновлением токена.

## Вопросы с ответами

> [!question]- Как клиенту обрабатывать статус 401 и 403?
> 401 — сессия недействительна (обновить токен/перейти на логин), 403 — недостаточно прав (сообщение, без логина).

> [!question]- Какие запросы можно безопасно повторять?
> Идемпотентные (GET/PUT/DELETE); POST — с ключом идемпотентности.

## Связанные темы

- [[N:c0b760520d08405aa560ec038f0c7d5a]]
- [[N:3ea33104867981e4b92aed4daaecffce]]
