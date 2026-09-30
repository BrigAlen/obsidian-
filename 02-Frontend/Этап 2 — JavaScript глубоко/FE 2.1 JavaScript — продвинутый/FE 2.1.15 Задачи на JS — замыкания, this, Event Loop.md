---
type: topic
domain: frontend
stage: 2
section: "2.1"
order: 15
status: todo
level: middle
notion_id: 3ea331048679815f9d17e64def8d245c
tags: [domain/frontend, stage/2, level/middle, topic/javascript, topic/interview, topic/practice, priority/must]
reviewed:
next_review:
priority: must
time: 4
---

# Задачи на JS: замыкания, this, Event Loop

↑ [[FE 2.1 JavaScript — продвинутый|2.1 JavaScript: продвинутый]] · ← [[FE 2.1.14 Даты, часовые пояса, Intl|Предыдущая]] · → [[FE 2.1.16 Полифиллы — bind, Promise.all, debounce, deepClone|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~4 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->













> [!info] Зачем это на собесе
> Типовые задачи «что выведет код». Решайте, проговаривая правила: hoisting, замыкания, `this`, порядок очередей.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Задачи

```js
// 1. Замыкания и var
for (var i = 0; i < 3; i++) setTimeout(() => console.log(i), 0);
```

> [!question]- Ответ
> `3 3 3`. Один `var i` на всю функцию, коллбэки выполняются после цикла. С `let` — `0 1 2`.

```js
// 2. this
const obj = { name: "A", regular() { return this.name; }, arrow: () => typeof this };
const f = obj.regular;
console.log(obj.regular(), f(), obj.arrow());
```

> [!question]- Ответ
> `"A"`, `undefined` (потерян контекст; в нестрогом — `window.name`), `"object"`/`"undefined"` (стрелка берёт `this` внешнего контекста: модуль — `undefined`).

```js
// 3. Event loop
console.log("A");
setTimeout(() => console.log("B"), 0);
Promise.resolve().then(() => console.log("C"));
(async () => { console.log("D"); await 0; console.log("E"); })();
console.log("F");
```

> [!question]- Ответ
> `A D F C E B`: синхронно `A, D, F`; микрозадачи `C, E`; затем макрозадача `B`.

```js
// 4. Hoisting
console.log(typeof f1, typeof f2);
function f1() {}
var f2 = function () {};
```

> [!question]- Ответ
> `"function" "undefined"`: function declaration поднимается целиком, `var f2` — со значением `undefined`.

```js
// 5. Приведение типов
console.log([] + [], [] + {}, 1 + "2", "3" - 1, true + true, [] == false, null == undefined, NaN == NaN);
```

> [!question]- Ответ
> `""`, `"[object Object]"`, `"12"`, `2`, `2`, `true`, `true`, `false`.

```js
// 6. Замыкание-счётчик
const make = () => { let n = 0; return () => ++n; };
const a = make(), b = make();
console.log(a(), a(), b());
```

> [!question]- Ответ
> `1 2 1` — у каждого замыкания своё окружение.

```js
// 7. Promise-цепочка
Promise.resolve(1).then(v => { throw new Error("x"); }).then(() => console.log("A")).catch(() => console.log("B")).then(() => console.log("C"));
```

> [!question]- Ответ
> `B C` — ошибка пропускает `then`, ловится `catch`, цепочка продолжается.

```js
// 8. Порядок
setTimeout(() => console.log(1));
new Promise((res) => { console.log(2); res(); }).then(() => console.log(3));
console.log(4);
```

> [!question]- Ответ
> `2 4 3 1` — тело промиса выполняется синхронно.

## Как решать

1. Разделите синхронный код, микрозадачи и макрозадачи.
2. Определите значение `this` по способу вызова.
3. Учитывайте hoisting и TDZ.
4. Проговаривайте правила вслух: интервьюеру важен ход рассуждений.

## Практика

1. Составьте ещё 10 задач на каждый пункт и решите без запуска.
2. Разберите ответы с помощью визуализатора (loupe, JS Visualizer).

## Связанные темы

- [[N:3ea331048679819ab2eff856ad1072b9]]
- [[N:3ea331048679812294bdeb38bfb575f8]]
