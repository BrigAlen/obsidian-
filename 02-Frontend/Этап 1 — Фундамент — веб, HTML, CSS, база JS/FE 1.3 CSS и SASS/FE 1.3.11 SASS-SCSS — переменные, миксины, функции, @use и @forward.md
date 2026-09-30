---
type: topic
domain: frontend
stage: 1
section: "1.3"
order: 11
status: todo
level: junior
notion_id: 3ea33104867981afa824fa9aa72c4259
tags: [domain/frontend, stage/1, level/junior, topic/css, topic/sass, topic/scss, priority/should]
reviewed:
next_review:
priority: should
time: 4
---

# SASS/SCSS: переменные, миксины, функции, @use и @forward

↑ [[FE 1.3 CSS и SASS|1.3 CSS и SASS]] · ← [[FE 1.3.10 Методологии — БЭМ, scoped styles, CSS Modules|Предыдущая]] · → [[FE 1.3.12 Вёрстка на время|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~4 мин чтения</span><span class="chip">Уровень: junior</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> SCSS — стандарт препроцессора; ждут знания модульной системы `@use` вместо `@import`.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

```scss
// _tokens.scss
$breakpoints: (sm: 640px, md: 768px, lg: 1024px);
$radius: 8px;

// _mixins.scss
@use "sass:map";
@use "tokens" as t;

@mixin respond($bp) { @media (min-width: map.get(t.$breakpoints, $bp)) { @content; } }
@mixin truncate { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
@function rem($px, $base: 16) { @return math.div($px, $base) * 1rem; }

// component.scss
@use "mixins" as m;
.card {
  border-radius: t.$radius;
  &__title { @include m.truncate; font-size: m.rem(18); }
  &--featured { border: 2px solid var(--accent); }
  @include m.respond(md) { display: grid; }
  &:hover { box-shadow: 0 2px 8px rgb(0 0 0 / .15); }
}

@each $name, $color in (success: green, danger: red) { .text-#{$name} { color: $color; } }
%placeholder { color: gray; }         // @extend
.a { @extend %placeholder; }
```

| Возможность | Пример |
|---|---|
| Переменные | `$color: #333` |
| Вложенность | `&:hover`, `&__el` |
| Миксины | `@mixin`/`@include` |
| Функции | `@function`, встроенные `map.get`, `math.div`, `color.adjust` |
| Управляющие директивы | `@if`, `@each`, `@for`, `@while` |
| Модули | `@use`, `@forward` |
| Наследование | `@extend` с `%placeholder` |

**Модули**: `@use "file" as alias` подключает с пространством имён и один раз (без побочного дублирования CSS); `@forward` — реэкспорт модуля (файл-«барабан» `index.scss`). `@import` устарел (глобальные имена, повторная загрузка). Деление: `math.div` вместо `/`.

## Нюансы и подводные камни

- Глубокая вложенность увеличивает специфичность и размер CSS.
- `@extend` в сложном контексте генерирует неожиданные селекторы.
- Переменные SASS не реагируют на смену темы в рантайме — для тем используйте CSS-переменные.
- Не превращайте препроцессор в слой «магии»: логика — в миксинах с понятными именами.
- Quasar: переменные темы задаются в `quasar.variables.scss`.

## Практика

1. Создайте миксин `respond` и функцию `rem`.
2. Организуйте стили на `@use`/`@forward` с `index.scss`.
3. Сгенерируйте утилитарные классы цветов через `@each`.

## Вопросы с ответами

> [!question]- Чем @use отличается от @import?
> `@use` создаёт пространство имён и подключает модуль один раз, `@import` — глобальный и устарел.

> [!question]- Для чего `@forward`?
> Для реэкспорта содержимого модуля из другого файла.

## Связанные темы

- [[N:3ea33104867981389815e50d96d369e7]]
- [[N:3ea33104867981bc82efc791639f77c8]]
