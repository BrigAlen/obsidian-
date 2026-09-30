---
type: topic
domain: frontend
stage: 2
section: "2.1"
order: 3
status: todo
level: middle
notion_id: 3ea3310486798130b7fece73b6a6d5cb
tags: [domain/frontend, stage/2, level/middle, topic/javascript, topic/classes, topic/oop, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Классы

↑ [[FE 2.1 JavaScript — продвинутый|2.1 JavaScript: продвинутый]] · ← [[FE 2.1.2 Прототипы и наследование|Предыдущая]] · → [[FE 2.1.4 Асинхронность — callbacks, Promise, async-await|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->










> [!info] Зачем это на собесе
> `class` — синтаксический сахар над прототипами; важно знать, что происходит под капотом и как работают `#private`, `static`, `super`.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

```js
class Account {
  #balance = 0;                     // приватное поле
  static count = 0;                 // статическое поле
  static { Account.count = 0; }     // статический блок

  constructor(owner) { this.owner = owner; Account.count++; }

  get balance() { return this.#balance; }
  deposit(x) { if (x <= 0) throw new RangeError("x"); this.#balance += x; return this; }
  #audit() { /* приватный метод */ }
  static from(obj) { return new Account(obj.owner); }
}

class Savings extends Account {
  constructor(owner, rate) { super(owner); this.rate = rate; }   // super() перед this
  deposit(x) { super.deposit(x); return this; }
}
```

Особенности:

| Особенность | Пояснение |
|---|---|
| Методы на прототипе | не создаются для каждого экземпляра |
| Поля класса | создаются для каждого экземпляра (стрелочные методы-поля — тоже, дороже по памяти, но привязывают `this`) |
| `#private` | недоступны снаружи, даже через `Object.keys`, проверка `#x in obj` |
| `class` не hoisted как функция | обращение до объявления — TDZ |
| Код в классе — строгий режим | |
| Вызов без `new` | `TypeError` |
| `super` | доступ к прототипу родителя |
| `extends` | наследование, включая встроенные (`Array`, `Error`) |
| `instanceof`, `Symbol.hasInstance` | проверка типа |

Композиция vs наследование: предпочитайте композицию/миксины; глубокие иерархии хрупки.

```js
const CanFly = (Base) => class extends Base { fly() {} };   // миксин
class Bird extends CanFly(Animal) {}
```

## Нюансы и подводные камни

- Потеря `this` при передаче метода как коллбэка (см. [[N:3ea3310486798128ae5ce7936d799a28]]).
- Стрелочные методы-поля нельзя переопределить через `super` и они не на прототипе.
- В конструкторе наследника нельзя использовать `this` до `super()`.
- Приватные поля не наследуются в смысле доступа: доступны только внутри объявившего класса.
- Классы во Vue-компонентах и стейте — редкость; чаще функции и композиция.

## Практика

1. Реализуйте иерархию `Shape → Circle/Rect` с полиморфным `area()`.
2. Добавьте приватное состояние и статический фабричный метод.
3. Сравните метод на прототипе и стрелочное поле по памяти.

## Вопросы с ответами

> [!question]- Что такое class в JavaScript?
> Синтаксический сахар над функциями-конструкторами и прототипами с дополнениями (`#private`, `static`, `super`).

> [!question]- Зачем `super()`?
> Вызывает конструктор родителя и инициализирует `this`; без него в наследнике `this` недоступен.

## Связанные темы

- [[N:3ea33104867981c7890ad0da3eea40ca]]
- [[N:3ea3310486798125aed9f655f8593986]]
