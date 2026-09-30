---
type: topic
domain: frontend
stage: 1
section: "1.3"
order: 4
status: todo
level: junior
notion_id: 3ea33104867981f98d0ce4cd6ed713a0
tags: [domain/frontend, stage/1, level/junior, topic/css, topic/positioning, priority/should]
reviewed:
next_review:
priority: should
time: 3
---

# Позиционирование, z-index, stacking context

↑ [[FE 1.3 CSS и SASS|1.3 CSS и SASS]] · ← [[FE 1.3.3 Каскад, специфичность, наследование|Предыдущая]] · → [[FE 1.3.5 Flexbox|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: junior</span></div>
<!-- meta:end -->



















> [!info] Зачем это на собесе
> «Почему z-index не работает?» — классика про stacking context.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

| `position` | Поведение |
|---|---|
| `static` | по умолчанию, `top/left` не работают |
| `relative` | смещение от своей позиции, остаётся в потоке, задаёт контекст для потомков |
| `absolute` | вне потока, относительно ближайшего позиционированного предка |
| `fixed` | относительно viewport |
| `sticky` | липнет при прокрутке между `relative` и `fixed` (нужен `top`) |

```css
.modal-overlay { position: fixed; inset: 0; background: rgb(0 0 0 / .5); z-index: 100; }
.badge { position: absolute; top: -4px; right: -4px; }   /* родитель: position: relative */
.header { position: sticky; top: 0; }
```

**z-index** работает только у позиционированных элементов (и flex/grid-потомков) внутри своего **stacking context** — изолированной группы наложения.

Stacking context создаётся: корневым элементом, `position` с `z-index` не `auto`, `opacity < 1`, `transform`, `filter`, `will-change`, `isolation: isolate`, `position: fixed/sticky`, flex/grid-потомками с `z-index`.

Правило: элемент с `z-index: 9999` не выйдет из родительского контекста с меньшим `z-index` — сравниваются контексты родителей.

```css
.dropdown-wrapper { isolation: isolate; }   /* локальный контекст, чтобы z-index внутри не влиял на страницу */
```

## Нюансы и подводные камни

- Не сравнивайте `z-index` из разных контекстов.
- Модальные окна и подсказки выносят в `<body>` (Teleport во Vue), чтобы избежать обрезки `overflow` и контекстов.
- `transform` на родителе меняет поведение `position: fixed` потомка (становится относительным родителя).
- `sticky` не работает, если у предка `overflow` не `visible`.
- «Лестница» `z-index: 999999` — признак проблемы архитектуры слоёв: введите шкалу токенов.

## Практика

1. Воспроизведите ситуацию с недействующим `z-index` и исправьте через `isolation`.
2. Сделайте липкую шапку таблицы.
3. Введите переменные слоёв: `--z-dropdown`, `--z-modal`, `--z-toast`.

## Вопросы с ответами

> [!question]- Почему z-index не работает?
> Элемент не позиционирован, либо находится в другом stacking context, чей уровень ниже.

> [!question]- Чем fixed отличается от absolute?
> `fixed` привязан к viewport, `absolute` — к ближайшему позиционированному предку.

## Связанные темы

- [[N:3ea331048679815082f0e88439e55756]]
- [[N:3ea3310486798174b46ec9e364d8fb92]]
