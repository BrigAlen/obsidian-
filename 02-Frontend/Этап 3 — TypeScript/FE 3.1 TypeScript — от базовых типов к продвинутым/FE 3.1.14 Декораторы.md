---
type: topic
domain: frontend
stage: 3
section: "3.1"
order: 14
status: todo
level: middle
notion_id: 3ea331048679814d8d16e9408e1b696e
tags: [domain/frontend, stage/3, level/middle, topic/typescript, topic/decorators, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Декораторы

↑ [[FE 3.1 TypeScript — от базовых типов к продвинутым|3.1 TypeScript: от базовых типов к продвинутым]] · ← [[FE 3.1.13 Структурная типизация, вариантность, satisfies|Предыдущая]] · → [[FE 3.1.15 Декларации и .d.ts|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->













> [!info] Зачем это на собесе
> Декораторы встречаются в Angular/NestJS/TypeORM; во Vue редки, но знать стоит.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

Декоратор — функция, изменяющая класс или его член. Есть два поколения:

| | Экспериментальные (legacy) | Стандартные (TC39, TS 5.0+) |
|---|---|---|
| Включение | `experimentalDecorators` | по умолчанию |
| Параметры | `(target, key, descriptor)` | `(value, context)` |
| Декораторы параметров | да | нет |
| Метаданные `reflect-metadata` | да (NestJS/Angular/TypeORM) | нет (свой механизм) |

```ts
// Стандартный декоратор метода
function log<T extends (...a: any[]) => any>(fn: T, ctx: ClassMethodDecoratorContext) {
  return function (this: any, ...args: Parameters<T>): ReturnType<T> {
    console.log(`→ ${String(ctx.name)}`, args);
    return fn.apply(this, args);
  } as T;
}

class Service {
  @log
  save(order: Order) { /* ... */ }
}

// Декоратор класса-фабрика (legacy-стиль, NestJS)
@Controller("orders")
class OrdersController {
  @Get(":id") find(@Param("id") id: string) {}
}
```

Виды: класс, метод, аксессор, свойство, параметр (legacy).

Применения: DI-метаданные (NestJS, Angular), маршруты, ORM-колонки, валидация (`class-validator`), логирование, кэширование, MobX. Во Vue — `vue-class-component`/`vue-property-decorator` устарели; используйте Composition API.

## Нюансы и подводные камни

- Две несовместимые реализации: проверьте, что выбрано в `tsconfig`.
- Декораторы выполняются при определении класса, а не при создании экземпляра.
- Порядок выполнения: сверху вниз при вычислении фабрик, снизу вверх при применении.
- Неявная «магия» усложняет отладку и статический анализ; Vite/esbuild требуют настройки.

## Практика

1. Напишите декоратор `@memoize` и `@log` для метода.
2. Определите, какие декораторы использует ваш backend-фреймворк (NestJS).
3. Сравните код с декораторами и функциональным подходом.

## Вопросы с ответами

> [!question]- Что такое декоратор?
> Функция, которая оборачивает или расширяет класс/член класса при его определении.

> [!question]- Чем стандартные декораторы отличаются от экспериментальных?
> Другая сигнатура (контекст вместо дескриптора), нет декораторов параметров и `emitDecoratorMetadata`.

## Связанные темы

- [[N:3ea33104867981a1b567e0d670b97106]]
- [[N:3ea331048679817b8eecc9de531cdcaa]]
