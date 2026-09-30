---
type: topic
domain: frontend
stage: 1
section: "1.3"
order: 10
status: todo
level: junior
notion_id: 3ea33104867981389815e50d96d369e7
tags: [domain/frontend, stage/1, level/junior, topic/css, topic/methodology, topic/architecture, priority/should]
reviewed:
next_review:
priority: should
time: 3
---

# Методологии: БЭМ, scoped styles, CSS Modules

↑ [[FE 1.3 CSS и SASS|1.3 CSS и SASS]] · ← [[FE 1.3.9 Анимации и transitions|Предыдущая]] · → [[FE 1.3.11 SASS-SCSS — переменные, миксины, функции, @use и @forward|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: junior</span></div>
<!-- meta:end -->









> [!info] Зачем это на собесе
> Как организовать CSS в большом проекте и не конфликтовать по именам.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

Проблема CSS — глобальная область видимости. Способы изоляции:

| Подход | Суть |
|---|---|
| БЭМ (Block__Element--Modifier) | договорённость по именам: `.card`, `.card__title`, `.card--featured` |
| Vue `<style scoped>` | компилятор добавляет `data-v-xxx` к элементам и селекторам |
| CSS Modules | локальные хэшированные имена классов (`styles.card`) |
| Shadow DOM | полная изоляция (Web Components) |
| CSS-in-JS | стили в JS (styled-components, Emotion) |
| Utility-first (Tailwind, UnoCSS) | маленькие атомарные классы |
| `@layer`, `@scope` | контроль каскада и области |

```html
<div class="card card--featured">
  <h3 class="card__title">Заголовок</h3>
</div>
```

```vue
<template><button class="btn">OK</button></template>
<style scoped>
.btn { padding: 8px 16px; }                 /* только этот компонент */
:deep(.q-field__native) { color: red; }     /* пробить в дочерние (осторожно) */
:slotted(.item) { margin: 0; }
</style>
<style module>.title { font-weight: 600; }</style>   <!-- CSS Modules: $style.title -->
```

Выбор: во Vue — `scoped` + токены/переменные; для библиотечных компонентов — БЭМ/`@layer`; для утилитарной вёрстки — Tailwind/UnoCSS.

## Нюансы и подводные камни

- `scoped` увеличивает специфичность и усложняет переопределение стилей UI-библиотек (нужен `:deep`).
- Слишком глубокая БЭМ-вложенность (`.a__b__c`) — признак плохой декомпозиции.
- Глобальные стили (reset, токены, типографика) — отдельным слоем.
- Утилитарные классы ускоряют разработку, но перегружают шаблон — извлекайте компоненты.
- CSS-in-JS в рантайме дороже по производительности.

## Практика

1. Перепишите компонент на БЭМ и на `scoped`, сравните.
2. Настройте `:deep` для кастомизации Quasar-компонента.
3. Ввести `@layer` для сторонних стилей.

## Вопросы с ответами

> [!question]- Как работает scoped во Vue?
> К элементам компонента добавляется атрибут `data-v-*`, а к селекторам — соответствующий атрибутный селектор.

> [!question]- Зачем БЭМ?
> Предсказуемые имена без вложенных селекторов и конфликтов.

## Связанные темы

- [[N:3ea331048679815781bfd3ecdd4a7e2e]]
- [[N:3ea33104867981afa824fa9aa72c4259]]
