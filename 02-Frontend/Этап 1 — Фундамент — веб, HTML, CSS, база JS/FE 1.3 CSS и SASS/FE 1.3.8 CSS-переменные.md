---
type: topic
domain: frontend
stage: 1
section: "1.3"
order: 8
status: todo
level: junior
notion_id: 3ea33104867981f9896cfe61d70bce85
tags: [domain/frontend, stage/1, level/junior, topic/css, topic/variables, priority/should]
reviewed:
next_review:
priority: should
time: 3
---

# CSS-переменные

↑ [[FE 1.3 CSS и SASS|1.3 CSS и SASS]] · ← [[FE 1.3.7 Адаптивность — media и container queries, единицы измерения|Предыдущая]] · → [[FE 1.3.9 Анимации и transitions|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: junior</span></div>
<!-- meta:end -->


















> [!info] Зачем это на собесе
> Custom properties — основа темизации и дизайн-токенов; спрашивают отличие от переменных SASS.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

```css
:root {
  --color-bg: #ffffff;
  --color-text: #1a1a1a;
  --space: 8px;
  --radius: 8px;
}
[data-theme="dark"] { --color-bg: #121212; --color-text: #eaeaea; }

.card {
  background: var(--color-bg);
  color: var(--color-text, black);        /* значение по умолчанию */
  padding: calc(var(--space) * 2);
  border-radius: var(--radius);
}
```

Свойства:

- Наследуются и подчиняются каскаду; можно переопределять на любом уровне (в компоненте, теме).
- Работают во время выполнения: меняются JS (`el.style.setProperty("--x", "10px")`), реагируют на media/theme.
- `@property` регистрирует тип и начальное значение → анимируемые переменные.

```css
@property --angle { syntax: "<angle>"; inherits: false; initial-value: 0deg; }
.spin { background: conic-gradient(from var(--angle), red, blue); transition: --angle .5s; }
```

| CSS-переменные | SASS-переменные |
|---|---|
| Живут в браузере, динамические, каскадные | Компилируются, значения фиксируются в сборке |
| Темизация, состояния, JS | Вычисления, циклы, миксины |
| Нельзя использовать в именах свойств/media (до контейнеров) | Можно в любом месте препроцессора |

Практика: **дизайн-токены** (`--color-*`, `--space-*`, `--font-*`) и семантические алиасы (`--color-danger`).

## Нюансы и подводные камни

- Циклические ссылки и неопределённые переменные делают значение недействительным (используйте fallback).
- Переменные нельзя использовать в `@media` условиях напрямую.
- Слишком много слоёв алиасов усложняют поиск.
- Изменение переменной на `:root` вызывает пересчёт стилей во всём документе.

## Практика

1. Сделайте светлую и тёмную темы через `data-theme` и токены.
2. Управляйте цветом акцента через JS-переменную.
3. Зарегистрируйте `@property` и анимируйте градиент.

## Вопросы с ответами

> [!question]- Чем CSS-переменные отличаются от SASS-переменных?
> CSS-переменные живут в рантайме и наследуются, SASS-переменные подставляются при компиляции.

> [!question]- Зачем `@property`?
> Задаёт тип и значение по умолчанию, позволяя анимировать пользовательские свойства.

## Связанные темы

- [[N:3ea331048679810dbe38e6c71614a1d7]]
- [[N:3ea331048679815781bfd3ecdd4a7e2e]]
