---
type: topic
domain: frontend
stage: 1
section: "1.4"
order: 6
status: todo
level: junior
notion_id: 3ea3310486798128ae5ce7936d799a28
tags: [domain/frontend, stage/1, level/junior, topic/javascript, topic/this, priority/should]
reviewed:
next_review:
priority: should
time: 3
---

# this, call, apply, bind, стрелочные функции

↑ [[FE 1.4 JavaScript — основы|1.4 JavaScript: основы]] · ← [[FE 1.4.5 Scope и замыкания|Предыдущая]] · → [[FE 1.4.7 Объекты — копирование, сравнение, дескрипторы|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: junior</span></div>
<!-- meta:end -->












> [!info] Зачем это на собесе
> «Чему равен `this`?» — обязательная задача. Знайте четыре правила и особенности стрелочных функций.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

`this` определяется **способом вызова**, а не местом объявления (кроме стрелочных функций).

| Правило (по приоритету) | `this` |
|---|---|
| `new Foo()` | новый объект |
| `call/apply/bind` | указанный объект |
| `obj.method()` | `obj` |
| простой вызов `fn()` | `undefined` (strict) / `window` |

```js
const user = { name: "A", hi() { return this.name; } };
user.hi();                  // "A"
const f = user.hi;
f();                        // undefined: контекст потерян

f.call(user);               // "A"
f.apply(user, [arg1]);      // аргументы массивом
const bound = f.bind(user); // новая функция с привязанным this
bound();                    // "A"

class Btn {
  label = "OK";
  onClick = () => console.log(this.label);   // стрелка: this от класса
  handle() { console.log(this.label); }
}
btn.addEventListener("click", new Btn().handle);   // this потерян (будет элемент)
```

**Стрелочные функции**: своего `this`, `arguments`, `super`, `new.target` нет — берут из внешней лексической области. Нельзя вызывать через `new`, `call/apply/bind` не меняют `this`.

Во Vue `this` в Options API — инстанс компонента (автобиндинг методов); в Composition API `this` не используется.

## Нюансы и подводные камни

- Коллбэки (`setTimeout(obj.method)`, `arr.map(this.fn)`) теряют контекст.
- Стрелка как метод объекта берёт `this` внешнего контекста (не объект).
- `bind` создаёт новую функцию каждый раз — сравнивайте и снимайте обработчики с сохранённой ссылкой.
- В обработчиках DOM для обычных функций `this` — элемент (`currentTarget`).

## Практика

1. Определите `this` в 10 примерах вызовов.
2. Реализуйте свой `bind` (см. полифиллы).
3. Исправьте потерю контекста в классе тремя способами.

## Вопросы с ответами

> [!question]- Чем стрелочная функция отличается от обычной по `this`?
> У неё нет собственного `this`: она берёт его из внешнего контекста в момент создания.

> [!question]- Чем `call` отличается от `apply` и `bind`?
> `call` вызывает сразу с аргументами по одному, `apply` — с массивом, `bind` возвращает новую функцию с привязанным `this`.

## Связанные темы

- [[N:3ea3310486798116b0c9e2e1ab363feb]]
- [[N:3ea33104867981228603ca7fc9b662f2]]
