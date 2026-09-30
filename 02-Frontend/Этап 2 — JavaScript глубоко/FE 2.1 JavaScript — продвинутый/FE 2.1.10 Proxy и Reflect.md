---
type: topic
domain: frontend
stage: 2
section: "2.1"
order: 10
status: todo
level: middle
notion_id: 3ea331048679817da316ca0ef842cabc
tags: [domain/frontend, stage/2, level/middle, topic/javascript, topic/proxy, topic/reflect, topic/reactivity, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Proxy и Reflect

↑ [[FE 2.1 JavaScript — продвинутый|2.1 JavaScript: продвинутый]] · ← [[FE 2.1.9 Итераторы и генераторы|Предыдущая]] · → [[FE 2.1.11 Память и сборщик мусора, утечки|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->









> [!info] Зачем это на собесе
> Proxy — основа реактивности Vue 3. Вопрос «как работает реактивность» требует понимания перехватчиков.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

`Proxy` оборачивает объект и перехватывает операции через **ловушки (traps)**; `Reflect` предоставляет методы стандартного поведения тех же операций.

```js
function reactive(target, onChange) {
  return new Proxy(target, {
    get(obj, key, receiver) {
      track(obj, key);                                  // зависимость (как во Vue)
      const v = Reflect.get(obj, key, receiver);
      return typeof v === "object" && v !== null ? reactive(v, onChange) : v;   // вложенная реактивность
    },
    set(obj, key, value, receiver) {
      const ok = Reflect.set(obj, key, value, receiver);
      onChange(key, value);
      return ok;                                        // в строгом режиме нужно вернуть true
    },
    has(obj, key) { return key in obj && !key.startsWith("_"); },
    deleteProperty(obj, key) { onChange(key); return Reflect.deleteProperty(obj, key); },
  });
}
```

| Ловушка | Перехватывает |
|---|---|
| `get`, `set`, `has`, `deleteProperty` | чтение, запись, `in`, `delete` |
| `ownKeys`, `getOwnPropertyDescriptor` | перечисление ключей |
| `apply`, `construct` | вызов функции, `new` |
| `getPrototypeOf` | прототип |

Применения: реактивность (Vue 3 `reactive`), валидация, логирование, значения по умолчанию, ленивые объекты, API-обёртки (`api.users.get(1)` → HTTP).

**Reflect** нужен, чтобы корректно пробросить `receiver` и `this`, вернуть булевый результат вместо исключения.

Vue 2 использовал `Object.defineProperty` (не видел добавление/удаление свойств и индексы массива), Vue 3 — `Proxy` (видит всё, но не поддерживается в IE).

## Нюансы и подводные камни

- Прокси не равен исходному объекту (`proxy !== target`): идентичность нарушается (проблема при сравнении, `Map`-ключах).
- Встроенные объекты с внутренними слотами (`Map`, `Date`) требуют привязки методов (`this` — прокси).
- Накладные расходы на каждую операцию: не оборачивайте горячие пути.
- Отмена доступа: `Proxy.revocable`.
- Во Vue деструктуризация реактивного объекта теряет реактивность (`toRefs`).

## Практика

1. Реализуйте мини-`reactive` с `track/trigger`.
2. Сделайте прокси для валидации присвоения типов.
3. Обёртка API-клиента через `Proxy`.

## Вопросы с ответами

> [!question]- Как Vue 3 реализует реактивность?
> Через `Proxy`: `get` отслеживает зависимости эффектов, `set` уведомляет подписчиков.

> [!question]- Зачем Reflect в ловушках?
> Для корректного стандартного поведения и проброса `receiver`.

## Связанные темы

- [[N:3ea33104867981e6b8fdfbbecd2a548e]]
- [[N:3ea33104867981dabc74d9f55baadb88]]
