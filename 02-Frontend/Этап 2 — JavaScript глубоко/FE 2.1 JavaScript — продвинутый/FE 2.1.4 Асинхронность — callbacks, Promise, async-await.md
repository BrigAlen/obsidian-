---
type: topic
domain: frontend
stage: 2
section: "2.1"
order: 4
status: todo
level: middle
notion_id: 3ea3310486798125aed9f655f8593986
tags: [domain/frontend, stage/2, level/middle, topic/javascript, topic/async, topic/promise, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Асинхронность: callbacks, Promise, async/await

↑ [[FE 2.1 JavaScript — продвинутый|2.1 JavaScript: продвинутый]] · ← [[FE 2.1.3 Классы|Предыдущая]] · → [[FE 2.1.5 Event Loop — микро- и макрозадачи|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->






> [!info] Зачем это на собесе
> Асинхронность — основа фронтенда. Ждут понимания состояний Promise, комбинаторов и обработки ошибок.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

**Callbacks** приводят к «аду колбэков» и сложной обработке ошибок. **Promise** — объект будущего результата: `pending → fulfilled | rejected` (состояние необратимо).

```js
const p = new Promise((resolve, reject) => setTimeout(() => resolve(42), 100));
p.then(v => v * 2).then(console.log).catch(console.error).finally(cleanup);

fetch("/api").then(r => r.json());     // цепочка: then возвращает новый Promise
```

| Комбинатор | Результат |
|---|---|
| `Promise.all([...])` | все успешны (или первая ошибка) |
| `Promise.allSettled` | результаты всех со статусами |
| `Promise.race` | первый завершившийся |
| `Promise.any` | первый успешный (или `AggregateError`) |
| `Promise.withResolvers()` | внешние `resolve/reject` |

**async/await** — синтаксис над Promise:

```js
async function load(ids, signal) {
  try {
    const [user, orders] = await Promise.all([api.user(ids.u, { signal }), api.orders(ids.u, { signal })]);   // параллельно
    for (const id of ids.items) await process(id);                                                              // последовательно
    return { user, orders };
  } catch (e) {
    if (e.name === "AbortError") return null;
    throw e;
  }
}
```

Правила:

- `async`-функция всегда возвращает Promise; `await` приостанавливает функцию (не поток).
- `await` в цикле выполняет последовательно; для параллельности — `Promise.all`.
- Ошибка в `async` — отклонённый Promise; `try/catch` вокруг `await`.
- Продолжение после `await` — **микрозадача** (см. [[N:3ea33104867981b2b063f7aa36540971]]).

## Нюансы и подводные камни

- Забытый `await` — «плавающий» промис без обработки ошибок (`unhandledrejection`).
- `forEach(async …)` не ждёт завершения.
- `Promise.all` отклоняется при первой ошибке, остальные продолжают выполняться.
- Отмена промисов невозможна: используйте `AbortController` и передавайте `signal`.
- `return await` внутри `try` нужен для перехвата ошибки; вне `try` избыточен.

## Практика

1. Перепишите вложенные коллбэки на Promise, затем на async/await.
2. Реализуйте `retry(fn, n)` и `timeout(promise, ms)`.
3. Распараллельте три независимых запроса и обработайте частичные ошибки через `allSettled`.

## Вопросы с ответами

> [!question]- Чем `Promise.all` отличается от `allSettled`?
> `all` падает при первой ошибке, `allSettled` ждёт все и возвращает статусы каждого.

> [!question]- Что делает `await`?
> Приостанавливает выполнение async-функции до завершения промиса; главный поток при этом свободен.

> [!question]- Как отменить запрос?
> `AbortController`: передать `signal` в `fetch` и вызвать `abort()`.

## Связанные темы

- [[N:3ea3310486798130b7fece73b6a6d5cb]]
- [[N:3ea33104867981b2b063f7aa36540971]]
