---
type: topic
domain: frontend
stage: 5
section: "5.3"
order: 9
status: todo
level: middle
notion_id: 3ea33104867981ccb8a9f3af56b3a9be
tags: [domain/frontend, stage/5, level/middle, topic/quasar, topic/theming, topic/dark-mode, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Темизация: SASS-переменные, brand colors, dark mode

↑ [[FE 5.3 Quasar|5.3 Quasar]] · ← [[FE 5.3.8 Quasar Plugins — Notify, Dialog, Loading, LocalStorage|Предыдущая]] · → [[FE 5.3.10 Режимы сборки — SPA, SSR, PWA, Electron, Capacitor|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->










> [!info] Зачем это на собесе
> Как привести Quasar к дизайн-системе компании и поддержать тёмную тему.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

Три уровня настройки:

1. **Brand colors** (рантайм, CSS-переменные):

```ts
// quasar.config
framework: { config: { brand: { primary: "#1976d2", secondary: "#26a69a", accent: "#9c27b0", dark: "#1d1d1d", positive: "#21ba45", negative: "#c10015", info: "#31ccec", warning: "#f2c037" } } }
// в рантайме
import { setCssVar, getCssVar } from "quasar"; setCssVar("primary", "#ff5722");
```

2. **SASS-переменные** (`src/css/quasar.variables.scss`, компиляция):

```scss
$primary: #1976d2;
$typography-font-family: "Inter", sans-serif;
$button-border-radius: 8px;
$spaces: (sm: (x: 8px, y: 8px), md: (x: 16px, y: 16px));
$breakpoint-md: 1024px;
```

3. **Глобальные стили** (`app.scss`) и CSS-переменные собственных токенов:

```scss
:root { --app-radius: 8px; --app-border: #e0e0e0; }
body.body--dark { --app-border: #424242; }
.text-muted { color: var(--q-secondary); }
```

**Dark mode**:

```ts
framework: { config: { dark: "auto" } }         // true | false | "auto" (системные предпочтения)
$q.dark.set(true); $q.dark.toggle(); $q.dark.isActive;
```

Класс `body--dark` включается на `<body>`; компоненты Quasar адаптируются. Для собственных стилей: селектор `.body--dark .my`, CSS-переменные `--q-*` (`var(--q-primary)`), утилиты `bg-dark`, `text-white`. Сохраняйте выбор пользователя (Pinia + `LocalStorage`) и учитывайте `prefers-color-scheme`.

Иконки и шрифты: `extras` (`material-icons`, `mdi-v7`, `fontawesome-v6`), `iconSet`.

Дизайн-токены: держите цвета/радиусы/отступы в SASS-переменных и CSS-переменных; избегайте магических значений в компонентах.

## Нюансы и подводные камни

- SASS-переменные Quasar работают только при использовании SASS-сборки (Quasar CLI подключает).
- Цвета контраста (WCAG) в тёмной теме проверяйте отдельно.
- Смена `brand` в рантайме не перекрашивает жёстко заданные цвета в CSS.
- Мигание светлой темы при загрузке: устанавливайте класс до рендера (inline-скрипт или ранняя инициализация).
- Картинки и графики требуют версий для тёмной темы.

## Практика

1. Настройте фирменные цвета и шрифт через SASS-переменные.
2. Реализуйте переключатель темы с сохранением выбора.
3. Проверьте контраст в тёмной теме и исправьте.

## Вопросы с ответами

> [!question]- Как поменять основные цвета Quasar?
> Через `brand` в конфиге/`setCssVar` (рантайм) или SASS-переменные (`$primary`) на этапе сборки.

> [!question]- Как включить тёмную тему?
> `dark: "auto"` в `framework.config` или `$q.dark.set(true)`; класс `body--dark`.

## Связанные темы

- [[N:3ea3310486798181b78cc70995a735cc]]
- [[N:3ea331048679811593a2ee4be38da7e1]]
