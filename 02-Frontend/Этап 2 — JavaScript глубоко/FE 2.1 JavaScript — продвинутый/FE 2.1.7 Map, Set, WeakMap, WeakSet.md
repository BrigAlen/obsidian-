---
type: topic
domain: frontend
stage: 2
section: "2.1"
order: 7
status: todo
level: middle
notion_id: 3ea33104867981bbab02d2b18bd7ffe9
tags: [domain/frontend, stage/2, level/middle, topic/javascript, topic/collections, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Map, Set, WeakMap, WeakSet

↑ [[FE 2.1 JavaScript — продвинутый|2.1 JavaScript: продвинутый]] · ← [[FE 2.1.6 Event Loop браузера|Предыдущая]] · → [[FE 2.1.8 Symbol и BigInt|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->







> [!info] Зачем это на собесе
> Когда `Map` лучше объекта и зачем нужны слабые ссылки.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

| Структура | Особенности |
|---|---|
| `Map` | ключи любых типов, сохраняет порядок вставки, `size`, итерация, быстрая частая вставка/удаление |
| `Set` | уникальные значения, `has` O(1) |
| `WeakMap` | ключи — только объекты, слабые ссылки (не мешают GC), не итерируется, нет `size` |
| `WeakSet` | множество объектов со слабыми ссылками |
| `Object` | ключи — строки/символы, прототипные ключи, порядок сложнее |

```js
const m = new Map([["a", 1]]);
m.set({ id: 1 }, "obj").get("a"); m.has("a"); m.delete("a"); [...m.entries()];

const s = new Set([1, 2, 2, 3]); s.add(4).has(2);
const union = new Set([...a, ...b]);           // + Set.union/intersection/difference (новые версии)

// WeakMap: приватные данные и кэш без утечек
const cache = new WeakMap();
function compute(obj) { if (!cache.has(obj)) cache.set(obj, heavy(obj)); return cache.get(obj); }   // запись исчезнет вместе с obj

const seen = new WeakSet();   // отметки «уже обработан» для DOM-узлов
```

Когда `Map` вместо `{}`: ключи не строки (объекты, числа), частые добавления/удаления, нужен размер и порядок, нет риска конфликта с прототипом. Когда `Object`: фиксированная структура, JSON.

`Map` не сериализуется `JSON.stringify` напрямую (`Object.fromEntries(map)`).

## Нюансы и подводные камни

- Ключи `Map` сравниваются по SameValueZero (`NaN` равен `NaN`), объекты — по ссылке.
- Во Vue `reactive(new Map())` поддерживается, но `WeakMap` не итерируется.
- `WeakMap` ключ — только объект (или незарегистрированный символ).
- Порядок итерации `Map` — по вставке.
- `Set` сравнивает объекты по ссылке — дубликаты «равных» объектов не удаляются.

## Практика

1. Реализуйте LRU-кэш на `Map`.
2. Сохраните метаданные DOM-узлов в `WeakMap` и проверьте отсутствие утечки.
3. Посчитайте частоты слов через `Map`.

## Вопросы с ответами

> [!question]- Чем Map отличается от Object?
> Ключи любого типа, порядок вставки, `size`, нет унаследованных ключей.

> [!question]- Зачем WeakMap?
> Хранить данные, связанные с объектом, не удерживая его в памяти.

## Связанные темы

- [[N:3ea33104867981438159d8a46581a7a5]]
- [[N:3ea331048679816aba5dc2f30dead79a]]
