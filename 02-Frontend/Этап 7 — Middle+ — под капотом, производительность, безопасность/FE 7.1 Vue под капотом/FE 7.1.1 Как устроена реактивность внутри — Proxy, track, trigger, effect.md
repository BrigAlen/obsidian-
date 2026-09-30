---
type: topic
domain: frontend
stage: 7
section: "7.1"
order: 1
status: todo
level: senior
notion_id: 3ea331048679810e8db6cbb8453bc6a4
tags: [domain/frontend, stage/7, level/senior, topic/vue, topic/reactivity, topic/proxy, priority/should]
reviewed:
next_review:
priority: should
time: 4
---

# Как устроена реактивность внутри: Proxy, track, trigger, effect

↑ [[FE 7.1 Vue под капотом|7.1 Vue под капотом]] · → [[FE 7.1.2 Scheduler — батчинг обновлений, flush pre-post-sync|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~4 мин чтения</span><span class="chip">Уровень: senior</span></div>
<!-- meta:end -->




> [!info] Зачем это на собесе
> Классический вопрос middle+: «как Vue узнаёт, что данные изменились». Нужно уверенно назвать Proxy, track/trigger и effect.

## Идея

Vue 3 оборачивает объект в `Proxy`. При **чтении** свойства он запоминает, какой эффект (`effect`) сейчас выполняется (**track**). При **записи** — находит подписанные эффекты и запускает их (**trigger**).

## Мини-реализация

```ts
let activeEffect: (() => void) | null = null
const targetMap = new WeakMap<object, Map<PropertyKey, Set<() => void>>>()

function track(target: object, key: PropertyKey) {
  if (!activeEffect) return
  let deps = targetMap.get(target)
  if (!deps) targetMap.set(target, (deps = new Map()))
  let dep = deps.get(key)
  if (!dep) deps.set(key, (dep = new Set()))
  dep.add(activeEffect)
}

function trigger(target: object, key: PropertyKey) {
  targetMap.get(target)?.get(key)?.forEach(fn => fn())
}

function reactive<T extends object>(obj: T): T {
  return new Proxy(obj, {
    get(t, k, r) { track(t, k); return Reflect.get(t, k, r) },
    set(t, k, v, r) { const ok = Reflect.set(t, k, v, r); trigger(t, k); return ok },
  })
}

function effect(fn: () => void) {
  activeEffect = fn
  fn()
  activeEffect = null
}
```

## Структура

| Понятие | Роль |
|---|---|
| `reactive` | Proxy над объектом (глубокий) |
| `ref` | контейнер `{ value }` с геттером и сеттером, для примитивов |
| `computed` | ленивый эффект с кэшем, инвалидируется при смене зависимостей |
| `watchEffect`, render | эффекты, подписанные на реактивные данные |

## Vue 2 vs Vue 3

Vue 2 использовал `Object.defineProperty`: не видел добавление и удаление свойств, индексы массивов (`Vue.set`). Proxy перехватывает всё: добавление, удаление, `in`, итерацию, `Map` и `Set`.

## Нюансы

- деструктуризация `reactive` теряет реактивность — используйте `toRefs`;
- `ref` в шаблоне разворачивается автоматически, в `reactive` тоже (unwrap);
- Proxy создаётся лениво при первом обращении к вложенному объекту;
- начиная с Vue 3.5 реактивная система переписана: двусвязный список зависимостей и версии счётчиков, потребление памяти на ~56% меньше.

## Вопросы с ответами

> [!question]- Как Vue понимает, какие данные использует компонент?
> Рендер выполняется внутри эффекта. Каждое чтение реактивного свойства вызывает `track`, запоминая зависимость. При записи вызывается `trigger`, и компонент перерисовывается.

> [!question]- Почему не работает деструктуризация reactive?
> Значения копируются как примитивы и отвязываются от прокси. Нужны `toRefs` или `toRef`.

> [!question]- Чем Proxy лучше defineProperty?
> Видит добавление и удаление ключей, индексы массивов, работает с Map/Set, не требует обхода всех свойств заранее.
