---
type: topic
domain: frontend
stage: 4
section: "4.1"
order: 14
status: todo
level: middle
notion_id: 3ea331048679813dbb9aec9570420803
tags: [domain/frontend, stage/4, level/middle, topic/vue, topic/provide-inject, topic/di, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# provide и inject

↑ [[FE 4.1 Vue 3 — основы, компоненты, Composition API|4.1 Vue 3: основы, компоненты, Composition API]] · ← [[FE 4.1.13 Слоты — default, named, scoped|Предыдущая]] · → [[FE 4.1.15 Атрибуты — $attrs и inheritAttrs|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->




> [!info] Зачем это на собесе
> Аналог DI во Vue: передача данных через несколько уровней без prop drilling.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

```ts
// Предок (или app.provide на уровне приложения)
const theme = ref<"light" | "dark">("light");
const toggle = () => (theme.value = theme.value === "light" ? "dark" : "light");
provide(ThemeKey, { theme: readonly(theme), toggle });      // отдаём readonly + функция изменения

// Потомок (любой глубины)
const ctx = inject(ThemeKey);                               // может быть undefined
const safe = inject(ThemeKey, defaultValue);                // значение по умолчанию
const strict = inject(ThemeKey) ?? (() => { throw new Error("ThemeProvider missing"); })();
```

Типизированный ключ:

```ts
import type { InjectionKey, Ref } from "vue";
interface ThemeContext { theme: Readonly<Ref<"light" | "dark">>; toggle(): void }
export const ThemeKey: InjectionKey<ThemeContext> = Symbol("theme");
```

Применения: темы, i18n, контекст формы (`FormItem` находит `Form`), UI-библиотеки (Quasar/Element используют внутри), плагины (`app.provide`), внедрение сервисов (API-клиент) и тестовых подстановок.

Реактивность: передавайте `ref`/`computed`; изменения выполняйте через функции, переданные вместе (**единый источник изменений** — у поставщика).

Сравнение способов передачи данных:

| Способ | Когда |
|---|---|
| Props/emits | родитель–потомок, явный контракт |
| `provide/inject` | сквозная передача, контекст компонентного дерева |
| Pinia | глобальное состояние приложения |
| Event bus | не рекомендуется |

## Нюансы и подводные камни

- Неявные зависимости усложняют чтение: документируйте ключи и используйте типизацию.
- Потомок не должен мутировать инжектируемые данные напрямую.
- `inject` работает только в `setup` (или через `app.runWithContext`).
- Ключ-строка может конфликтовать: используйте `Symbol`.
- Компонент, использующий `inject`, тяжелее тестировать: передавайте контекст через `global.provide`.

## Практика

1. Создайте `ThemeProvider` с `provide` и `useTheme()` composable.
2. Реализуйте контекст формы для вложенных полей.
3. Подмените контекст в тесте.

## Вопросы с ответами

> [!question]- Когда `provide/inject`, а когда Pinia?
> `provide/inject` — контекст поддерева компонентов; Pinia — глобальное состояние приложения с DevTools и логикой.

> [!question]- Как сохранить реактивность при `provide`?
> Передавать `ref/computed`, а не примитивные значения.

## Связанные темы

- [[N:3ea331048679819bb62fc73c089ec18f]]
- [[N:3ea33104867981d4b22bd2fb85d16222]]
