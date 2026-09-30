---
type: topic
domain: frontend
stage: 3
section: "3.1"
order: 18
status: todo
level: middle
notion_id: 3ea331048679819c9b56f7afc4868cd5
tags: [domain/frontend, stage/3, level/middle, topic/typescript, topic/interview, topic/practice, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Задачи на TypeScript

↑ [[FE 3.1 TypeScript — от базовых типов к продвинутым|3.1 TypeScript: от базовых типов к продвинутым]] · ← [[FE 3.1.17 Тестирование типов — expectTypeOf, vue-tsc в CI|Предыдущая]] · → [[FE 3.1.19 Runtime-валидация данных — Zod, Valibot и границы TypeScript|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->












> [!info] Зачем это на собесе
> Задачи на типы: реализуйте утилиту, типизируйте функцию, исправьте ошибку.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Задачи

**1. Реализуйте `MyPick`, `MyOmit`, `MyReadonly`.**

> [!question]- Решение
> ```ts
> type MyPick\<T, K extends keyof T\> = { [P in K]: T[P] };
> type MyOmit\<T, K extends keyof any\> = { [P in keyof T as P extends K ? never : P]: T[P] };
> type MyReadonly\<T\> = { readonly [P in keyof T]: T[P] };
> ```

**2. `DeepReadonly<T>`.**

> [!question]- Решение
> ```ts
> type DeepReadonly\<T\> = T extends (...a: any[]) => any ? T : T extends object ? { readonly [K in keyof T]: DeepReadonly\<T[K]\> } : T;
> ```

**3. Типизируйте `groupBy` так, чтобы результат знал ключи.**

> [!question]- Решение
> ```ts
> function groupBy\<T, K extends PropertyKey>(arr: readonly T[], key: (x: T) => K): Record\<K, T[]\> {
>   return arr.reduce((acc, x) => { (acc[key(x)] ||= []).push(x); return acc; }, {} as Record\<K, T[]\>);
> }
> ```

**4. Выведите union ключей, значения которых — функции.**

> [!question]- Решение
> ```ts
> type FnKeys\<T\> = { [K in keyof T]: T[K] extends (...a: any[]) => any ? K : never }[keyof T];
> ```

**5. Типизируйте `pluck` и объясните ошибку.**

```ts
function pluck<T>(arr: T[], key: string) { return arr.map(x => x[key]); }   // ошибка: индексация T строкой
```

> [!question]- Решение
> ```ts
> function pluck\<T, K extends keyof T>(arr: T[], key: K): T[K][] { return arr.map(x => x[key]); }
> ```

**6. Сделайте тип `PromiseType<T>` без `Awaited`.**

> [!question]- Решение
> ```ts
> type PromiseType\<T\> = T extends Promise\<infer U\> ? PromiseType\<U\> : T;
> ```

**7. Реализуйте `Tuple → Union` и `Union → Intersection`.**

> [!question]- Решение
> ```ts
> type TupleToUnion\<T extends readonly unknown[]\> = T[number];
> type UnionToIntersection\<U\> = (U extends any ? (k: U) => void : never) extends (k: infer I) => void ? I : never;
> ```

**8. Как типизировать результат `fetchJson<T>` безопасно?**

> [!question]- Решение
> `T` не проверяется в рантайме: возвращайте `unknown` и валидируйте схемой (Zod), либо `Promise<T>` только после валидации — см. runtime-валидацию.

## Как решать на собеседовании

1. Сформулировать входы/выходы типа на примерах.
2. Разбить на mapped/conditional/infer шаги.
3. Проверить на крайних случаях (`never`, `unknown`, union).
4. Объяснить компромиссы (читаемость, производительность компилятора).

## Связанные темы

- [[N:3ea331048679813da123f4a332bbf8c1]]
- [[N:cf701e59e7894adfb9428fd9c9678d93]]
