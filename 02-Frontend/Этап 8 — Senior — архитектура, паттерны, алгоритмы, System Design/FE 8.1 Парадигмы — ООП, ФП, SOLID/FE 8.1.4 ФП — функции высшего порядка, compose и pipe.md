---
type: topic
domain: frontend
stage: 8
section: "8.1"
order: 4
status: todo
level: senior
notion_id: 3ea331048679818882abe94dcdf33229
tags: [domain/frontend, stage/8, level/senior, topic/functional, topic/hof, topic/typescript, priority/should]
reviewed:
next_review:
priority: should
time: 3
---

# ФП: функции высшего порядка, compose и pipe

↑ [[FE 8.1 Парадигмы — ООП, ФП, SOLID|8.1 Парадигмы: ООП, ФП, SOLID]] · ← [[FE 8.1.3 SOLID подробно с примерами|Предыдущая]] · → [[FE 8.1.5 Декларативный и императивный подход|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: senior</span></div>
<!-- meta:end -->


> [!info] Зачем это на собесе
> ФП-подход лежит в основе Vue composition API, Redux, RxJS; просят реализовать compose/pipe/curry.

## Ключевые идеи

- **чистые функции**: результат зависит только от аргументов, без побочных эффектов;
- **иммутабельность**: новое значение вместо изменения старого;
- **функции — значения**: передаём, возвращаем, композируем;
- **функции высшего порядка** (HOF): принимают или возвращают функции.

## HOF

```ts
const withLogging = <A extends unknown[], R>(fn: (...a: A) => R) =>
  (...args: A): R => { console.log('call', fn.name, args); return fn(...args) }

const debounce = <A extends unknown[]>(fn: (...a: A) => void, ms: number) => {
  let t: ReturnType<typeof setTimeout>
  return (...args: A) => { clearTimeout(t); t = setTimeout(() => fn(...args), ms) }
}
```

`map`, `filter`, `reduce`, `sort`, `Array.from` — тоже HOF.

## pipe и compose

```ts
const pipe = <T>(...fns: Array<(x: T) => T>) => (x: T) => fns.reduce((acc, fn) => fn(acc), x)
const compose = <T>(...fns: Array<(x: T) => T>) => (x: T) => fns.reduceRight((acc, fn) => fn(acc), x)

const slugify = pipe<string>(
  s => s.trim(),
  s => s.toLowerCase(),
  s => s.replace(/\s+/g, '-'),
)
slugify('  Hello World ')   // 'hello-world'
```

`pipe` читается слева направо, `compose` — справа налево.

## Каррирование и частичное применение

```ts
const curry = (fn: Function) => function c(...a: any[]): any {
  return a.length >= fn.length ? fn(...a) : (...b: any[]) => c(...a, ...b)
}
const add = curry((a: number, b: number, c: number) => a + b + c)
add(1)(2)(3); add(1, 2)(3)
```

## Иммутабельность

```ts
const next = { ...state, user: { ...state.user, name: 'Аня' } }
const list2 = [...list, item]
const list3 = list.filter(x => x.id !== id)
structuredClone(obj)   // глубокая копия
```

Библиотеки: Immer (мутирующий синтаксис поверх неизменяемости).

## Во фронтенде

Редьюсеры, селекторы, computed, чистые преобразования данных, RxJS-операторы, мемоизация.

## Вопросы с ответами

> [!question]- Что такое чистая функция и зачем она?
> Функция без побочных эффектов, результат зависит только от аргументов. Проще тестировать, кэшировать, распараллеливать и рассуждать о ней.

> [!question]- Разница между pipe и compose?
> Порядок применения: pipe — слева направо, compose — справа налево.
