---
type: topic
domain: frontend
stage: 2
section: "2.1"
order: 5
status: todo
level: middle
notion_id: 3ea33104867981b2b063f7aa36540971
tags: [domain/frontend, stage/2, level/middle, topic/javascript, topic/event-loop, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Event Loop: микро- и макрозадачи

↑ [[FE 2.1 JavaScript — продвинутый|2.1 JavaScript: продвинутый]] · ← [[FE 2.1.4 Асинхронность — callbacks, Promise, async-await|Предыдущая]] · → [[FE 2.1.6 Event Loop браузера|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->
























> [!info] Зачем это на собесе
> «Что выведет код?» с `setTimeout`, `Promise` и `async/await` — почти обязательная задача.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

JS однопоточный. **Event loop** координирует стек вызовов, очереди задач и среду (Web APIs/Node).

Цикл:

1. Выполнить текущую задачу (macro task) до опустошения стека.
2. **Выполнить все микрозадачи** (очередь полностью, включая добавленные по ходу).
3. (Браузер) при необходимости выполнить рендеринг.
4. Взять следующую макрозадачу.

| Макрозадачи | Микрозадачи |
|---|---|
| скрипт, `setTimeout`, `setInterval`, события UI, `MessageChannel`, I/O | `Promise.then/catch/finally`, продолжение после `await`, `queueMicrotask`, `MutationObserver` |

```js
console.log("1");
setTimeout(() => console.log("2"), 0);
Promise.resolve().then(() => console.log("3"));
queueMicrotask(() => console.log("4"));
(async () => { console.log("5"); await null; console.log("6"); })();
console.log("7");
// 1, 5, 7, 3, 4, 6, 2
```

Разбор: синхронно — `1, 5, 7`; микрозадачи по порядку постановки — `3`, `4`, `6`; затем макрозадача — `2`.

Следствия:

- Бесконечные микрозадачи блокируют рендер и таймеры.
- `setTimeout(fn, 0)` выполняется не мгновенно (минимальная задержка, после микрозадач и текущей задачи).
- Тяжёлый синхронный код блокирует всё: разбивайте на части (`setTimeout`/`scheduler.yield`), выносите в Web Workers.

В Node.js фазы иные: `timers → pending → poll → check (setImmediate) → close`, между фазами — `process.nextTick` и микрозадачи.

## Нюансы и подводные камни

- `await x` эквивалентен `Promise.resolve(x).then(...)`: продолжение — микрозадача (число тиков зависит от типа значения).
- Рендер не происходит между микрозадачами.
- `setInterval` не гарантирует точный интервал.
- Порядок `setTimeout` и `setImmediate` в главном модуле Node не определён.

## Практика

1. Решите 10 задач «что выведет код» и объясните порядок вслух.
2. Разбейте тяжёлый цикл на части, чтобы страница оставалась отзывчивой.
3. Перенесите вычисление в Web Worker.

## Вопросы с ответами

> [!question]- Чем микрозадачи отличаются от макрозадач?
> Очередь микрозадач полностью выполняется после каждой макрозадачи и до рендера; макрозадачи берутся по одной.

> [!question]- Что раньше: `setTimeout(0)` или `Promise.then`?
> `Promise.then` — микрозадача выполнится до макрозадачи `setTimeout`.

## Связанные темы

- [[N:3ea3310486798125aed9f655f8593986]]
- [[N:3ea33104867981438159d8a46581a7a5]]
