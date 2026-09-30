---
type: topic
domain: frontend
stage: 1
section: "1.4"
order: 7
status: todo
level: junior
notion_id: 3ea33104867981228603ca7fc9b662f2
tags: [domain/frontend, stage/1, level/junior, topic/javascript, topic/objects, priority/should]
reviewed:
next_review:
priority: should
time: 3
---

# Объекты: копирование, сравнение, дескрипторы

↑ [[FE 1.4 JavaScript — основы|1.4 JavaScript: основы]] · ← [[FE 1.4.6 this, call, apply, bind, стрелочные функции|Предыдущая]] · → [[FE 1.4.8 Массивы и их методы|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: junior</span></div>
<!-- meta:end -->


> [!info] Зачем это на собесе
> Разница поверхностного и глубокого копирования и работа с дескрипторами свойств.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

Объекты присваиваются и передаются **по ссылке**.

```js
const a = { n: 1, nested: { x: 1 } };
const b = a;              b.n = 2;            // a.n тоже 2
const shallow = { ...a }; // или Object.assign({}, a) — поверхностная копия
shallow.nested.x = 9;     // a.nested.x тоже 9
const deep = structuredClone(a);   // глубокая копия (Date, Map, Set, циклы), но не функции
JSON.parse(JSON.stringify(a));     // теряет функции, undefined, Date → строка, Map/Set
```

| Способ | Что копирует |
|---|---|
| Spread, `Object.assign` | верхний уровень (shallow) |
| `structuredClone` | глубоко, встроенные типы |
| JSON | только JSON-совместимое |
| `lodash.cloneDeep` | глубоко, включая многие типы |

**Дескрипторы свойств**:

```js
const o = {};
Object.defineProperty(o, "id", { value: 1, writable: false, enumerable: false, configurable: false });
Object.getOwnPropertyDescriptor(o, "id");   // { value: 1, writable: false, ... }
Object.defineProperty(o, "full", { get() { return `${this.a} ${this.b}`; }, enumerable: true });
```

| Флаг | Смысл |
|---|---|
| `writable` | можно менять значение |
| `enumerable` | видно в `for...in`, `Object.keys`, spread |
| `configurable` | можно удалить/переопределить |
| `get`/`set` | аксессоры |

Иммутабельность: `Object.freeze` (неизменяемый, мелко), `Object.seal` (нельзя добавлять/удалять), `Object.preventExtensions`.

Полезное: `Object.keys/values/entries`, `Object.fromEntries`, `in`, `hasOwn`, оператор `?.` и `??`, деструктуризация с переименованием, вычисляемые ключи.

## Нюансы и подводные камни

- Spread копирует только собственные перечисляемые свойства и не копирует прототип.
- `JSON`-копирование ломает `Date`, `undefined`, `NaN`, циклические ссылки.
- Порядок ключей: целочисленные по возрастанию, затем строковые в порядке добавления.
- `Object.freeze` не замораживает вложенные объекты.
- Во Vue реактивные прокси: `structuredClone` работает только над «сырыми» данными (`toRaw`).

## Практика

1. Реализуйте `deepClone` с обработкой циклических ссылок.
2. Создайте неизменяемое свойство через `defineProperty`.
3. Сравните способы копирования на сложном объекте.

## Вопросы с ответами

> [!question]- Как глубоко скопировать объект?
> `structuredClone` (или `lodash.cloneDeep`); JSON подходит только для простых данных.

> [!question]- Что делает `enumerable: false`?
> Свойство скрывается из перебора (`for...in`, `Object.keys`, spread).

## Связанные темы

- [[N:3ea3310486798128ae5ce7936d799a28]]
- [[N:3ea33104867981f9b32fe932432f0651]]
