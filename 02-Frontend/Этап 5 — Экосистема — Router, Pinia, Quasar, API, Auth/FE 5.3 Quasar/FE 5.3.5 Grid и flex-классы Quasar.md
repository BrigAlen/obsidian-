---
type: topic
domain: frontend
stage: 5
section: "5.3"
order: 5
status: todo
level: middle
notion_id: 3ea33104867981a7b0fbc3bc6173feaf
tags: [domain/frontend, stage/5, level/middle, topic/quasar, topic/css, topic/grid, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Grid и flex-классы Quasar

↑ [[FE 5.3 Quasar|5.3 Quasar]] · ← [[FE 5.3.4 Layout — QLayout, QHeader, QDrawer, QPage|Предыдущая]] · → [[FE 5.3.6 Ключевые компоненты — QTable, QForm, QInput, QSelect, QDialog|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->















> [!info] Зачем это на собесе
> Быстрая вёрстка Quasar-классами: сетка на flex, адаптивные брейкпоинты, отступы.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

Quasar даёт utility-классы (аналог Tailwind в мини-формате).

```vue
<div class="row q-col-gutter-md">                                <!-- строка, промежуток 16px -->
  <div class="col-12 col-md-6 col-lg-4">...</div>                 <!-- 12 колонок: на sm — вся ширина, md — половина, lg — треть -->
  <div class="col">равная доля</div>
  <div class="col-auto">по содержимому</div>
</div>

<div class="row items-center justify-between no-wrap">            <!-- flex-выравнивание -->
<div class="column q-gutter-sm">                                  <!-- колонка с промежутками -->
```

| Класс | Назначение |
|---|---|
| `row`, `column`, `inline` | flex-контейнеры |
| `col-N`, `col`, `col-auto`, `col-md-N` | размеры (по брейкпоинтам `xs, sm, md, lg, xl`) |
| `justify-*`, `items-*`, `content-*`, `self-*` | выравнивание |
| `wrap`, `no-wrap`, `reverse` | поведение переноса и порядок |
| `q-col-gutter-{xs..xl}` | промежутки между колонками (компенсируют отступ контейнера) |
| `q-gutter-*` | промежутки между элементами |
| `q-pa-md`, `q-mt-sm`, `q-mx-auto`, `q-px-lg` | отступы `p/m` + сторона + размер (`none, xs, sm, md, lg, xl`) |
| `gt-sm`, `lt-md`, `xs`, `hidden`, `desktop-only` | видимость по экрану |
| `text-h5`, `text-bold`, `text-primary`, `bg-grey-2` | типографика и цвета из палитры |
| `full-width`, `full-height`, `fit`, `absolute-*` | размеры/позиция |
| `ellipsis`, `no-scroll`, `cursor-pointer`, `rounded-borders`, `shadow-2` | прочее |

Брейкпоинты: xs < 600, sm 600, md 1024, lg 1440, xl 1920. В JS: `$q.screen.gt.sm`, `$q.screen.lt.md`.

Когда использовать: быстрый макет и отступы; для сложной вёрстки — CSS Grid в scoped-стилях; не смешивайте несколько систем без необходимости.

## Нюансы и подводные камни

- `q-col-gutter-*` создаёт отрицательные margin; помещайте `row` в контейнер с достаточным отступом (иначе появляется горизонтальный скролл).
- `col-6` работает только внутри `row`.
- Классы Quasar и собственный CSS: следите за специфичностью.
- Есть `q-gutter` (на `gap` через margin) и `q-col-gutter` — не путать.

## Практика

1. Сверстайте адаптивную сетку карточек на `row/col`.
2. Скройте блоки на мобильных через `gt-sm`.
3. Замените `margin`-ы в своих стилях на `q-*` классы.

## Вопросы с ответами

> [!question]- Как в Quasar задать адаптивные колонки?
> `col-12 col-md-6 col-lg-4` внутри `row`.

> [!question]- Чем `q-gutter` отличается от `q-col-gutter`?
> `q-col-gutter` — промежутки между колонками сетки, `q-gutter` — между произвольными элементами.

## Связанные темы

- [[N:3ea33104867981e3a864d2ad5c1b7f36]]
- [[N:3ea331048679814db069fdc55fcbd725]]
