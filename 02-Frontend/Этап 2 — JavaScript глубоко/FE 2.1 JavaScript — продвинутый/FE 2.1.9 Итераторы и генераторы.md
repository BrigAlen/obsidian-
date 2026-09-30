---
type: topic
domain: frontend
stage: 2
section: "2.1"
order: 9
status: todo
level: middle
notion_id: 3ea33104867981e6b8fdfbbecd2a548e
tags: [domain/frontend, stage/2, level/middle, topic/javascript, topic/iterators, topic/generators, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Итераторы и генераторы

↑ [[FE 2.1 JavaScript — продвинутый|2.1 JavaScript: продвинутый]] · ← [[FE 2.1.8 Symbol и BigInt|Предыдущая]] · → [[FE 2.1.10 Proxy и Reflect|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->






> [!info] Зачем это на собесе
> Лежит в основе `for...of`, spread, `async/await`; спрашивают, как сделать объект итерируемым.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

**Итерируемый** объект имеет метод `[Symbol.iterator]()`, возвращающий **итератор** с методом `next()` → `{ value, done }`.

```js
const range = {
  from: 1, to: 3,
  [Symbol.iterator]() {
    let cur = this.from, end = this.to;
    return { next: () => cur <= end ? { value: cur++, done: false } : { value: undefined, done: true } };
  },
};
[...range];        // [1, 2, 3]
for (const x of range) console.log(x);
```

**Генератор** — функция с `function*`, приостанавливаемая `yield`; возвращает итератор.

```js
function* range(a, b) { for (let i = a; i <= b; i++) yield i; }
function* ids() { let id = 1; while (true) yield id++; }        // бесконечная последовательность, ленивость
const [a, b] = ids();                                            // берём нужное

function* dialog() {
  const name = yield "Как вас зовут?";       // yield принимает значение из next(value)
  return `Привет, ${name}`;
}
const g = dialog(); g.next(); g.next("Анна");   // { value: "Привет, Анна", done: true }
yield* otherGenerator();                          // делегирование
```

Асинхронные:

```js
async function* pages(url) { let next = url; while (next) { const r = await (await fetch(next)).json(); yield r.items; next = r.next; } }
for await (const items of pages("/api?page=1")) render(items);
```

Применения: ленивые последовательности, пагинация, пошаговые процессы, корутины (redux-saga), потоки данных (`ReadableStream` — async-итерируемый), кастомная итерация структур данных (деревья).

`async/await` исторически реализовывали на генераторах + Promise.

## Нюансы и подводные камни

- Генератор одноразовый: после `done: true` повторный обход даёт пустой результат.
- `return()` и `throw()` на итераторе позволяют завершать/прерывать (`break` в `for...of` вызывает `return`).
- Деструктуризация итерируемого потребляет его.
- Ленивые вычисления не выполняются, пока не запрошены.
- Итераторы-помощники (`Iterator.prototype.map/filter/take`) появляются в новых версиях.

## Практика

1. Реализуйте генератор Фибоначчи и `take(n)`.
2. Сделайте итерируемое бинарное дерево.
3. Постройте `for await` для постраничной загрузки.

## Вопросы с ответами

> [!question]- Что такое итерируемый объект?
> Объект с методом `[Symbol.iterator]`, возвращающим итератор с `next()`.

> [!question]- Чем генератор полезен?
> Упрощает создание итераторов, даёт ленивые последовательности и пошаговое выполнение.

## Связанные темы

- [[N:3ea331048679816aba5dc2f30dead79a]]
- [[N:3ea331048679817da316ca0ef842cabc]]
