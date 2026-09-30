---
type: topic
domain: frontend
stage: 3
section: "3.1"
order: 7
status: todo
level: middle
notion_id: 3ea3310486798167b6ffeadd14bf3dcd
tags: [domain/frontend, stage/3, level/middle, topic/typescript, topic/classes, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Классы в TS: модификаторы, abstract, implements

↑ [[FE 3.1 TypeScript — от базовых типов к продвинутым|3.1 TypeScript: от базовых типов к продвинутым]] · ← [[FE 3.1.6 Narrowing и type guards|Предыдущая]] · → [[FE 3.1.8 Enum и as const|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->









> [!info] Зачем это на собесе
> Объектная модель TS: модификаторы доступа, абстрактные классы, отличие TS `private` от `#private`.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

```ts
abstract class Shape {
  protected constructor(readonly name: string) {}          // parameter property
  abstract area(): number;
  describe() { return `${this.name}: ${this.area().toFixed(2)}`; }
}

class Circle extends Shape {
  constructor(private radius: number) { super("circle"); }
  area() { return Math.PI * this.radius ** 2; }
}

interface Serializable { toJSON(): string }
class User implements Serializable {
  static count = 0;
  #secret = "x";                          // приватное поле рантайма (JS)
  private legacy = 1;                     // TS private: только проверка компилятора
  constructor(public id: number, public readonly name: string) { User.count++; }
  toJSON() { return JSON.stringify({ id: this.id }); }
}
```

| Модификатор | Смысл |
|---|---|
| `public` (по умолчанию) | доступ отовсюду |
| `protected` | класс и наследники |
| `private` | только класс (проверка в TS) |
| `#name` | настоящая приватность в JS |
| `readonly` | присваивание только в конструкторе/инициализаторе |
| `static` | член класса |
| `abstract` | без реализации, нельзя создать экземпляр |
| `override` | явно переопределяет (ошибка, если родителя нет) |
| `declare` | объявление поля без эмита |

`implements` проверяет соответствие классу интерфейса (структуры не наследует). `extends` наследует реализацию.

Классы структурно типизированы: объект, соответствующий форме, совместим (кроме классов с `private/protected` членами — номинальная привязка).

## Нюансы и подводные камни

- TS `private` доступен в рантайме (`obj["legacy"]`): для настоящей приватности — `#`.
- Parameter properties (`constructor(private x)`) удобны, но могут ухудшать читаемость и конфликтуют с `erasableSyntaxOnly`.
- Поле без инициализации при `strictPropertyInitialization` требует `!` или инициализации.
- Включайте `noImplicitOverride`.

## Практика

1. Смоделируйте иерархию `Shape` с абстрактным классом.
2. Проверьте разницу `private` и `#private` в рантайме.
3. Реализуйте интерфейс и добавьте `override`.

## Вопросы с ответами

> [!question]- Чем TS `private` отличается от `#private`?
> `private` проверяется только компилятором, `#private` защищён на уровне JS-рантайма.

> [!question]- Чем `implements` отличается от `extends`?
> `implements` только проверяет соответствие контракту, `extends` наследует реализацию.

## Связанные темы

- [[N:3ea331048679812694a2d2a4ca78bc40]]
- [[N:3ea33104867981b6ac0bf52e95f84990]]
