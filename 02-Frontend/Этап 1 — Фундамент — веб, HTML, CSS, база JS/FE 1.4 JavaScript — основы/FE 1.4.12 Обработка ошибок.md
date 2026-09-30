---
type: topic
domain: frontend
stage: 1
section: "1.4"
order: 12
status: todo
level: junior
notion_id: 3ea331048679816da10fe17794cbb365
tags: [domain/frontend, stage/1, level/junior, topic/javascript, topic/errors, priority/should]
reviewed:
next_review:
priority: should
time: 3
---

# Обработка ошибок

↑ [[FE 1.4 JavaScript — основы|1.4 JavaScript: основы]] · ← [[FE 1.4.11 DOM и события — всплытие, погружение, делегирование|Предыдущая]] · → [[FE 1.4.13 Модули — ESM и CommonJS|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: junior</span></div>
<!-- meta:end -->






> [!info] Зачем это на собесе
> Как правильно бросать и ловить ошибки, особенно в асинхронном коде и на уровне приложения.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

```js
try {
  const data = JSON.parse(text);
  await save(data);
} catch (err) {
  if (err instanceof SyntaxError) showMessage("Некорректный JSON");
  else throw err;                   // неизвестное — пробрасываем
} finally {
  hideLoader();                     // выполняется всегда
}

class ApiError extends Error {
  constructor(message, { status, code, cause } = {}) {
    super(message, { cause });
    this.name = "ApiError"; this.status = status; this.code = code;
  }
}
throw new ApiError("Не найдено", { status: 404 });
```

| Тип | Причина |
|---|---|
| `Error` | базовый |
| `TypeError` | неверный тип/`undefined.x` |
| `ReferenceError` | необъявленная переменная |
| `SyntaxError` | синтаксис, `JSON.parse` |
| `RangeError` | значение вне диапазона, переполнение стека |
| `AggregateError` | несколько ошибок (`Promise.any`) |

Асинхронные ошибки:

- В Promise — `.catch()` или `try/await/catch`.
- `try/catch` не ловит ошибки внутри асинхронных коллбэков `setTimeout`.
- Глобальные: `window.onerror`, `window.addEventListener("unhandledrejection", …)`.

```js
window.addEventListener("unhandledrejection", (e) => report(e.reason));
const results = await Promise.allSettled(tasks);      // не падает из-за одной ошибки
```

Практики: единая обработка ошибок HTTP (интерсептор), понятные сообщения пользователю, логирование (Sentry) с контекстом, `cause` для цепочки причин, не глотать ошибки (`catch {}`), не использовать исключения для обычного потока.

Во Vue: `errorCaptured`, `app.config.errorHandler`; ErrorBoundary-подобные компоненты.

## Нюансы и подводные камни

- `throw` строки/объектов — плохо: теряется стек; бросайте `Error`.
- `fetch` не бросает ошибку на 4xx/5xx.
- `finally` с `return` переопределяет результат.
- Без `await` внутри `try` промис не будет пойман.
- Слишком общий `catch` скрывает баги.

## Практика

1. Создайте иерархию ошибок API и единый обработчик.
2. Настройте глобальные обработчики и отправку в Sentry.
3. Обработайте `Promise.allSettled` с частичными ошибками.

## Вопросы с ответами

> [!question]- Ловит ли `try/catch` ошибки в `setTimeout`?
> Нет: коллбэк выполняется позже; обработку нужно ставить внутри коллбэка.

> [!question]- Как поймать необработанные ошибки промисов?
> Событие `unhandledrejection` и `.catch` на цепочках.

## Связанные темы

- [[N:3ea33104867981e090f1cd2ad6c856f0]]
- [[N:3ea33104867981daa8b5d128045f2f66]]
