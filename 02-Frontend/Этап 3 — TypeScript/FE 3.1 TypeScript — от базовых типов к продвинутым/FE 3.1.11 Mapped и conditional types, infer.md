---
type: topic
domain: frontend
stage: 3
section: "3.1"
order: 11
status: todo
level: middle
notion_id: 3ea331048679816495f6eb1b9f2919b0
tags: [domain/frontend, stage/3, level/middle, topic/typescript, topic/mapped-types, topic/conditional-types, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Mapped и conditional types, infer

↑ [[FE 3.1 TypeScript — от базовых типов к продвинутым|3.1 TypeScript: от базовых типов к продвинутым]] · ← [[FE 3.1.10 keyof, typeof, indexed access|Предыдущая]] · → [[FE 3.1.12 Template literal types|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->





> [!info] Зачем это на собесе
> Продвинутая тема senior-уровня: как устроены `Partial`, `ReturnType` и как писать свои.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

**Mapped types** — преобразование каждого ключа типа:

```ts
type Partial<T> = { [K in keyof T]?: T[K] };
type Readonly<T> = { readonly [K in keyof T]: T[K] };
type Mutable<T> = { -readonly [K in keyof T]-?: T[K] };       // -readonly/-? снимают модификаторы
type Nullable<T> = { [K in keyof T]: T[K] | null };
type Getters<T> = { [K in keyof T as `get${Capitalize<string & K>}`]: () => T[K] };   // переименование ключей (as)
type OnlyStrings<T> = { [K in keyof T as T[K] extends string ? K : never]: T[K] };    // фильтрация
```

**Conditional types** — «if» на уровне типов: `T extends U ? X : Y`.

```ts
type IsString<T> = T extends string ? true : false;
type NonNullable<T> = T extends null | undefined ? never : T;
type Flatten<T> = T extends (infer U)[] ? U : T;              // infer: вывести часть типа
type ReturnType<F> = F extends (...a: any[]) => infer R ? R : never;
type Params<F> = F extends (...a: infer P) => any ? P : never;
type UnwrapPromise<T> = T extends Promise<infer U> ? UnwrapPromise<U> : T;   // рекурсия
```

**Дистрибутивность**: условный тип от голого параметра `T` распределяется по union: `IsString<string | number>` = `true | false`. Чтобы отключить: `[T] extends [U]`.

```ts
type DeepPartial<T> = T extends object ? { [K in keyof T]?: DeepPartial<T[K]> } : T;
type DeepReadonly<T> = T extends Function ? T : T extends object ? { readonly [K in keyof T]: DeepReadonly<T[K]> } : T;
type ExtractEvents<T> = T extends `on${infer E}` ? Uncapitalize<E> : never;
```

## Нюансы и подводные камни

- Глубокая рекурсия типов замедляет компилятор и имеет лимит.
- Условные типы внутри generics в теле функции не разрешаются до вызова — нужны приведения.
- Сообщения об ошибках сложных типов трудно читать: выносите промежуточные псевдонимы.
- `infer` работает только в условных типах, в позиции `extends`.
- Не усложняйте типы ради интеллектуальной красоты.

## Практика

1. Реализуйте `Pick`, `Omit`, `Record`, `ReturnType` вручную.
2. Напишите `DeepPartial` и `PathsOf<T>`.
3. Сделайте тип, извлекающий ключи с функциями.

## Вопросы с ответами

> [!question]- Что делает `infer`?
> Объявляет параметр типа, который выводится из сопоставляемой структуры внутри условного типа.

> [!question]- Что такое дистрибутивные условные типы?
> Условный тип над голым параметром применяется к каждому члену union по отдельности.

## Связанные темы

- [[N:3ea3310486798168bdb7c7a21246f521]]
- [[N:3ea33104867981b59058cb6474a9b446]]
