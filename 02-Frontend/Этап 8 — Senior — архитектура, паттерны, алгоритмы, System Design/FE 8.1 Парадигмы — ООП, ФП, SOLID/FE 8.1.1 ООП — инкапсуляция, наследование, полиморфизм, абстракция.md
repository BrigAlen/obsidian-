---
type: topic
domain: frontend
stage: 8
section: "8.1"
order: 1
status: todo
level: senior
notion_id: 3ea3310486798104b276c6e96ee73fc6
tags: [domain/frontend, stage/8, level/senior, topic/oop, topic/typescript, topic/design, priority/should]
reviewed:
next_review:
priority: should
time: 3
---

# ООП: инкапсуляция, наследование, полиморфизм, абстракция

↑ [[FE 8.1 Парадигмы — ООП, ФП, SOLID|8.1 Парадигмы: ООП, ФП, SOLID]] · → [[FE 8.1.2 Композиция вместо наследования|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: senior</span></div>
<!-- meta:end -->


> [!info] Зачем это на собесе
> Базовые принципы проверяют на любом уровне; для senior важнее показать, где ООП помогает, а где во фронтенде лучше функции и композиция.

## Четыре принципа

| Принцип | Суть | Пример на TS |
|---|---|---|
| **Инкапсуляция** | скрыть внутреннее состояние, дать узкий интерфейс | `private`, `#field`, замыкания |
| **Наследование** | новый тип расширяет существующий | `class Admin extends User` |
| **Полиморфизм** | один интерфейс, разные реализации | `interface Storage` → `Local`, `Session` |
| **Абстракция** | выделить существенное, скрыть детали | интерфейс `PaymentProvider` |

```ts
interface Notifier { send(message: string): Promise<void> }

class EmailNotifier implements Notifier {
  #smtp: SmtpClient
  constructor(smtp: SmtpClient) { this.#smtp = smtp }
  async send(message: string) { await this.#smtp.send(message) }
}

class SmsNotifier implements Notifier {
  async send(message: string) { /* ... */ }
}

// потребитель зависит от абстракции
async function alert(n: Notifier) { await n.send('Заказ создан') }
```

## Особенности JS/TS

- наследование **прототипное**, `class` — синтаксический сахар;
- `private` в TS — только проверка типов, `#field` — настоящая приватность в рантайме;
- структурная типизация: совместимость по форме, а не по имени;
- методы теряют `this` при передаче как колбэк (нужен `bind` или стрелка).

## Где ООП уместно во фронтенде

- модели предметной области с поведением (валидация, вычисления);
- адаптеры и сервисы над API;
- иерархии виджетов сторонних библиотек (Canvas, карты).

Во Vue компоненты и composables — это **функции и композиция**, а не иерархии классов. Классовые компоненты (vue-class-component) вышли из практики.

## Типичные проблемы

- глубокие иерархии наследования: хрупкий базовый класс;
- «божественные» классы;
- наследование ради переиспользования кода вместо композиции.

## Вопросы с ответами

> [!question]- Чем полиморфизм в TypeScript отличается от Java или C#?
> Структурная типизация: тип подходит, если у него есть нужные члены, явное `implements` необязательно. Полиморфизм достигается через интерфейсы, дженерики и union-типы.

> [!question]- Почему во Vue не используют наследование компонентов?
> Композиция (composables, slots, props) гибче: нет скрытых зависимостей от родителя и конфликтов имён.
