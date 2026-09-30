---
type: topic
domain: frontend
stage: 1
section: "1.4"
order: 3
status: todo
level: junior
notion_id: 3ea33104867981dc8665de8df9c3f74d
tags: [domain/frontend, stage/1, level/junior, topic/javascript, topic/scope, topic/hoisting, priority/should]
reviewed:
next_review:
priority: should
time: 3
---

# var, let, const, hoisting, TDZ

↑ [[FE 1.4 JavaScript — основы|1.4 JavaScript: основы]] · ← [[FE 1.4.2 Сравнение — == и ===, Object.is, NaN|Предыдущая]] · → [[FE 1.4.4 Строгий режим|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: junior</span></div>
<!-- meta:end -->
























> [!info] Зачем это на собесе
> Вопросы про «всплытие» и временную мёртвую зону — обязательная часть собеседования по JS.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

| | `var` | `let` | `const` |
|---|---|---|---|
| Область | функция | блок | блок |
| Hoisting | поднимается, инициализируется `undefined` | поднимается, но недоступна до объявления (**TDZ**) | как `let` |
| Повторное объявление | разрешено | нет | нет |
| Переприсваивание | да | да | нет (но объект внутри изменяем) |
| Свойство `window` | да (глобально) | нет | нет |

**Hoisting** — объявления обрабатываются при создании контекста выполнения до выполнения кода.

```js
console.log(a);   // undefined  (var поднята)
var a = 1;

console.log(b);   // ReferenceError: Cannot access 'b' before initialization  (TDZ)
let b = 2;

hello();          // работает: Function Declaration поднимается целиком
function hello() { console.log("hi"); }

bye();            // TypeError: bye is not a function (var поднята как undefined)
var bye = function () {};

for (var i = 0; i < 3; i++) setTimeout(() => console.log(i));   // 3 3 3
for (let j = 0; j < 3; j++) setTimeout(() => console.log(j));   // 0 1 2 (новая привязка на итерацию)

const user = { name: "A" };
user.name = "B";   // ок: изменяется содержимое
// user = {};      // TypeError
Object.freeze(user);   // мелкая неизменяемость
```

**TDZ** (Temporal Dead Zone) — период от начала блока до строки объявления `let/const/class`, когда обращение к переменной вызывает `ReferenceError`.

## Нюансы и подводные камни

- Используйте `const` по умолчанию, `let` при переприсваивании, `var` не используйте.
- `const` не делает объект неизменяемым: нужен `Object.freeze` (мелко) или иммутабельные подходы.
- `typeof` в TDZ тоже бросает исключение.
- Function Declaration в блоках имеет особенности в нестрогом режиме.
- Глобальные `var` создают свойства `window` и могут конфликтовать со сторонним кодом.

## Практика

1. Предскажите вывод 6 фрагментов с `var/let` и `setTimeout` в цикле.
2. Найдите в коде `var` и замените.
3. Объясните, почему `let` в цикле работает иначе.

## Вопросы с ответами

> [!question]- Что такое hoisting?
> Подъём объявлений в начало области видимости при создании контекста выполнения.

> [!question]- Что такое TDZ?
> Промежуток до инициализации `let/const`, в котором обращение вызывает ReferenceError.

> [!question]- Почему `const` объект можно менять?
> `const` запрещает переприсваивание привязки, но не изменение содержимого объекта.

## Связанные темы

- [[N:3ea33104867981669b6bd6f060aa0c30]]
- [[N:3ea33104867981699af8deffb5430c6b]]
