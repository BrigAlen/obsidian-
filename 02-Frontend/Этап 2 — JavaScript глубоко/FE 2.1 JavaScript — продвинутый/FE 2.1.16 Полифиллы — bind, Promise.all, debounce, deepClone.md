---
type: topic
domain: frontend
stage: 2
section: "2.1"
order: 16
status: todo
level: middle
notion_id: 3ea331048679812294bdeb38bfb575f8
tags: [domain/frontend, stage/2, level/middle, topic/javascript, topic/interview, topic/polyfills, priority/must]
reviewed:
next_review:
priority: must
time: 5
---

# Полифиллы: bind, Promise.all, debounce, deepClone

↑ [[FE 2.1 JavaScript — продвинутый|2.1 JavaScript: продвинутый]] · ← [[FE 2.1.15 Задачи на JS — замыкания, this, Event Loop|Предыдущая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~5 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->













> [!info] Зачем это на собесе
> Реализация встроенных функций — частое задание live coding. Проверяет знание `this`, замыканий и промисов.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

```js
// bind
Function.prototype.myBind = function (ctx, ...bound) {
  const fn = this;
  return function bound_(...args) {
    return fn.apply(this instanceof bound_ ? this : ctx, [...bound, ...args]);   // поддержка new
  };
};

// Promise.all
function promiseAll(items) {
  return new Promise((resolve, reject) => {
    const results = []; let left = 0, i = 0;
    for (const item of items) {
      const idx = i++; left++;
      Promise.resolve(item).then(v => { results[idx] = v; if (--left === 0) resolve(results); }, reject);
    }
    if (left === 0) resolve(results);
  });
}

// deepClone (циклы, Date, Map, Set)
function deepClone(x, seen = new WeakMap()) {
  if (x === null || typeof x !== "object") return x;
  if (seen.has(x)) return seen.get(x);
  if (x instanceof Date) return new Date(x);
  if (x instanceof Map) { const m = new Map(); seen.set(x, m); x.forEach((v, k) => m.set(deepClone(k, seen), deepClone(v, seen))); return m; }
  if (x instanceof Set) { const s = new Set(); seen.set(x, s); x.forEach(v => s.add(deepClone(v, seen))); return s; }
  const out = Array.isArray(x) ? [] : Object.create(Object.getPrototypeOf(x));
  seen.set(x, out);
  for (const k of Reflect.ownKeys(x)) out[k] = deepClone(x[k], seen);
  return out;
}

// once, memoize, flatten, curry, EventEmitter
const once = (fn) => { let done = false, res; return (...a) => done ? res : (done = true, res = fn(...a)); };
const flat = (arr, d = Infinity) => arr.reduce((acc, x) => Array.isArray(x) && d > 0 ? acc.concat(flat(x, d - 1)) : acc.concat(x), []);

class Emitter {
  #h = new Map();
  on(e, f) { (this.#h.get(e) ?? this.#h.set(e, new Set()).get(e)).add(f); return () => this.off(e, f); }
  off(e, f) { this.#h.get(e)?.delete(f); }
  emit(e, ...a) { this.#h.get(e)?.forEach(f => f(...a)); }
}

// Promise-пул с ограничением параллелизма
async function pool(tasks, limit) {
  const results = []; let i = 0;
  const worker = async () => { while (i < tasks.length) { const idx = i++; results[idx] = await tasks[idx](); } };
  await Promise.all(Array.from({ length: limit }, worker));
  return results;
}
```

(Реализации `debounce` и `throttle` — в [[N:3ea3310486798141ac16e74c3bd7c467]].)

Как реализовывать на интервью: уточнить контракт (поведение на ошибках, порядок результатов, `this`), написать базовый вариант, затем обработать крайние случаи и назвать сложность.

## Нюансы и подводные камни

- `Promise.all` сохраняет порядок результатов, а не порядок завершения.
- `deepClone` должен обрабатывать циклические ссылки, `Date`, `RegExp`, `Map/Set`.
- `bind`: результат должен поддерживать вызов через `new`.
- Не забывайте про пустой ввод и нестандартные итерируемые.

## Практика

1. Реализуйте `myCall`, `myApply`, `myBind`, `promiseAny`, `promiseRace`.
2. Реализуйте `LRUCache`, `EventEmitter`, `pool` и напишите тесты.
3. Сравните свой `deepClone` с `structuredClone`.

## Вопросы с ответами

> [!question]- Как реализовать `bind`?
> Вернуть функцию, вызывающую оригинал через `apply` с сохранённым контекстом и предустановленными аргументами.

> [!question]- Как обработать циклические ссылки при копировании?
> Хранить уже скопированные объекты в `WeakMap` и возвращать копию при повторной встрече.

## Связанные темы

- [[N:3ea331048679815f9d17e64def8d245c]]
- [[N:3ea3310486798198b292ca6f533bfc9f]]
