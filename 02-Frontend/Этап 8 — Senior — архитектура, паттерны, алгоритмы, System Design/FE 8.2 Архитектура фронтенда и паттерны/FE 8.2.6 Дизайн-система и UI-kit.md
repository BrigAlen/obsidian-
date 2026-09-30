---
type: topic
domain: frontend
stage: 8
section: "8.2"
order: 6
status: todo
level: senior
notion_id: 3ea3310486798103a4c5ec6de944f4a1
tags: [domain/frontend, stage/8, level/senior, topic/design-system, topic/ui-kit, topic/tokens, priority/should]
reviewed:
next_review:
priority: should
time: 3
---

# Дизайн-система и UI-kit

↑ [[FE 8.2 Архитектура фронтенда и паттерны|8.2 Архитектура фронтенда и паттерны]] · ← [[FE 8.2.5 Разделение логики — компоненты, composables, сервисы, сторы|Предыдущая]] · → [[FE 8.2.7 Микрофронтенды|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: senior</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> Senior отвечает за единообразие и скорость команды; спрашивают, как строить и поддерживать дизайн-систему.

## Компоненты

- **Дизайн-токены**: цвета, отступы, типографика, радиусы, тени как переменные (CSS custom properties или JSON, Style Dictionary);
- **Примитивы**: Button, Input, Select, Modal, Tooltip;
- **Составные**: DataTable, Form, DatePicker;
- **Шаблоны страниц** и правила использования.

```css
:root {
  --color-primary: #1976d2;
  --space-2: 8px;
  --radius-md: 6px;
}
[data-theme='dark'] { --color-primary: #90caf9; }
```

## Принципы API

- узкий понятный набор props, значения по умолчанию;
- композиция через slots вместо множества флагов;
- `v-model` для значения, события для действий;
- доступность из коробки (роли, фокус, клавиатура);
- типы TypeScript и JSDoc;
- темизация и локализация через токены и провайдеры.

## Сборка и доставка

- отдельный пакет в monorepo, публикация в npm (semver, changelog через changesets);
- tree-shaking: ESM, `sideEffects`;
- **Storybook** как каталог и документация;
- визуальные регрессии (Chromatic, Playwright);
- версионирование и **миграции** (codemods) при breaking changes.

## Готовая библиотека или своя

| Вариант | Когда |
|---|---|
| Quasar / Vuetify / PrimeVue / Element Plus | внутренние системы, быстро |
| Headless (Radix Vue, Reka UI, Headless UI) + свои стили | нужна кастомная визуальная идентичность |
| Полностью своя | продукт с уникальным брендом и ресурсами на поддержку |

## Управление

Владельцы, процесс предложений (RFC), контрибьюторы из продуктовых команд, метрики принятия (доля страниц на компонентах), регулярные релизы.

## Вопросы с ответами

> [!question]- Как убедиться, что команды используют дизайн-систему?
> Удобные и полные компоненты, документация с примерами, линтер запрещает нестандартные цвета, поддержка и быстрая обратная связь.

> [!question]- Зачем токены?
> Единый источник значений: смена темы или бренда затрагивает одну точку, платформы (web, mobile) синхронизируются.
