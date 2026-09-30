---
type: topic
domain: frontend
stage: 1
section: "1.3"
order: 3
status: todo
level: junior
notion_id: 3ea331048679815082f0e88439e55756
tags: [domain/frontend, stage/1, level/junior, topic/css, topic/cascade, priority/should]
reviewed:
next_review:
priority: should
time: 3
---

# Каскад, специфичность, наследование

↑ [[FE 1.3 CSS и SASS|1.3 CSS и SASS]] · ← [[FE 1.3.2 Селекторы, псевдоклассы и псевдоэлементы|Предыдущая]] · → [[FE 1.3.4 Позиционирование, z-index, stacking context|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: junior</span></div>
<!-- meta:end -->




> [!info] Зачем это на собесе
> «Почему мой стиль не применяется?» — вопрос про каскад. Нужно назвать порядок разрешения конфликтов.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

Порядок разрешения конфликтов:

1. **Происхождение и важность**: `!important` (author) > обычные author > user-agent.
2. **Слои** `@layer` (позже объявленный слой сильнее для обычных правил).
3. **Специфичность** селектора.
4. **Порядок в коде** — позднее побеждает.

Специфичность (a, b, c): a — количество `id`, b — классов/атрибутов/псевдоклассов, c — тегов/псевдоэлементов. Inline-стиль сильнее любого селектора.

| Селектор | Специфичность |
|---|---|
| `p` | 0,0,1 |
| `.card` | 0,1,0 |
| `.card p` | 0,1,1 |
| `#app .card` | 1,1,0 |
| `:where(.a)` | 0,0,0 |
| `:is(.a, #b)` | как самый специфичный аргумент |

**Наследование**: часть свойств наследуется потомками (`color`, `font-*`, `line-height`, `visibility`), другие — нет (`margin`, `padding`, `border`, `background`).

Управление: `inherit`, `initial`, `unset`, `revert`, `all: unset`.

```css
@layer reset, base, components, utilities;      /* явный порядок слоёв */
@layer components { .btn { padding: 8px 16px; } }
@layer utilities  { .p-0 { padding: 0; } }       /* сильнее компонентов независимо от специфичности */
```

## Нюансы и подводные камни

- `!important` ломает каскад, используйте только для утилит.
- Вложенность в SCSS увеличивает специфичность: не вкладывайте больше 2–3 уровней.
- Стили из `<style scoped>` во Vue добавляют атрибут — специфичность выше.
- Порядок подключения файлов CSS влияет на результат.
- Инспектор в DevTools показывает, какие правила перечёркнуты и почему.

## Практика

1. Посчитайте специфичность 5 селекторов и проверьте в DevTools.
2. Настройте `@layer` для reset/base/components/utilities.
3. Найдите и уберите `!important` из проекта.

## Вопросы с ответами

> [!question]- Что побеждает: `#id` или `.class .class .class`?
> Побеждает `#id`: специфичность считается по разрядам (1,0,0 против 0,3,0).

> [!question]- Какие свойства наследуются?
> Текстовые (`color`, `font`, `line-height`), но не блочные (`margin`, `padding`, `border`).

## Связанные темы

- [[N:3ea33104867981539d07fe1eba47e407]]
- [[N:3ea33104867981f98d0ce4cd6ed713a0]]
