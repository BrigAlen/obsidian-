---
type: topic
domain: frontend
stage: 2
section: "2.1"
order: 2
status: todo
level: middle
notion_id: 3ea33104867981c7890ad0da3eea40ca
tags: [domain/frontend, stage/2, level/middle, topic/javascript, topic/prototype, topic/oop, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Прототипы и наследование

↑ [[FE 2.1 JavaScript — продвинутый|2.1 JavaScript: продвинутый]] · ← [[FE 2.1.1 Execution context и call stack|Предыдущая]] · → [[FE 2.1.3 Классы|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->








> [!info] Зачем это на собесе
> «Как работает наследование в JS?» — обязательный вопрос. Нужно объяснить цепочку прототипов, а не только `class`.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

Каждый объект имеет скрытую ссылку `[[Prototype]]` (доступна через `Object.getPrototypeOf(o)` или `__proto__`). При обращении к свойству движок ищет его в объекте, затем по цепочке прототипов до `null`.

```js
const animal = { eats: true, walk() { return "walk"; } };
const dog = Object.create(animal);   // прототип dog = animal
dog.barks = true;
dog.eats;                            // true (из прототипа)
dog.hasOwnProperty("eats");          // false; Object.hasOwn(dog, "eats")
Object.getPrototypeOf(dog) === animal;   // true

function Person(name) { this.name = name; }
Person.prototype.hi = function () { return `Hi, ${this.name}`; };
const p = new Person("A");            // p.__proto__ === Person.prototype
p instanceof Person;                  // true
```

| Понятие | Смысл |
|---|---|
| `[[Prototype]]` / `__proto__` | ссылка объекта на прототип |
| `Function.prototype` | объект, который станет прототипом экземпляров при `new` |
| `obj.constructor` | ссылка на конструктор |
| `instanceof` | проверка наличия `Constructor.prototype` в цепочке |
| Shadowing | собственное свойство перекрывает прототипное |

Что делает `new Foo()`: создаёт пустой объект → устанавливает `[[Prototype]] = Foo.prototype` → вызывает `Foo` с `this` = объект → возвращает объект (если конструктор не вернул другой объект).

Наследование функциями-конструкторами:

```js
function Student(name, school) { Person.call(this, name); this.school = school; }
Student.prototype = Object.create(Person.prototype);
Student.prototype.constructor = Student;
```

Методы на прототипе разделяются всеми экземплярами (экономия памяти), собственные свойства — у каждого.

## Нюансы и подводные камни

- Изменение `__proto__` на лету замедляет оптимизации (используйте `Object.create`/`setPrototypeOf` осознанно).
- Модификация встроенных прототипов (`Array.prototype`) ломает чужой код.
- `for...in` обходит и унаследованные перечисляемые свойства: фильтруйте `Object.hasOwn`.
- Методы, вынесенные из объекта, теряют `this`.
- Объекты без прототипа: `Object.create(null)` — «чистый словарь».

## Практика

1. Постройте цепочку `Animal → Dog` без `class` и проверьте `instanceof`.
2. Реализуйте свой `new` и `instanceof`.
3. Найдите на схеме цепочку прототипов для массива и функции.

## Вопросы с ответами

> [!question]- Как работает наследование в JavaScript?
> Через цепочку прототипов: при отсутствии свойства у объекта поиск продолжается в его прототипе и выше.

> [!question]- Что делает оператор `new`?
> Создаёт объект с прототипом конструктора, вызывает конструктор с этим `this` и возвращает объект.

> [!question]- Чем `__proto__` отличается от `prototype`?
> `__proto__` — ссылка на прототип у экземпляра, `prototype` — свойство функции-конструктора, становящееся прототипом экземпляров.

## Связанные темы

- [[N:3ea33104867981789846e17e97e590c4]]
- [[N:3ea3310486798130b7fece73b6a6d5cb]]
