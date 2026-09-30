---
type: topic
domain: frontend
stage: 5
section: "5.6"
order: 4
status: todo
level: middle
notion_id: 3ea3310486798179a72cfe83566355ca
tags: [domain/frontend, stage/5, level/middle, topic/pdf, topic/print, topic/css, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Печать из браузера и CSS @media print

↑ [[FE 5.6 PDF и печатные формы на клиенте|5.6 PDF и печатные формы на клиенте]] · ← [[FE 5.6.3 html2canvas|Предыдущая]] · → [[FE 5.6.5 Stimulsoft Reports|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> Самый надёжный способ печатных форм на клиенте — обычная вёрстка с print-стилями.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

Браузер печатает страницу и позволяет «Сохранить как PDF» — **векторно, с выделяемым текстом**. Управляем видом через `@media print` и `@page`.

```css
@page { size: A4 portrait; margin: 15mm 12mm; }
@page :first { margin-top: 25mm; }

@media print {
  body { background: #fff; color: #000; font: 11pt/1.4 "Times New Roman", serif; }
  .no-print, nav, aside, button { display: none !important; }
  a[href]::after { content: " (" attr(href) ")"; font-size: 9pt; }          /* URL после ссылок */
  table { border-collapse: collapse; width: 100%; }
  thead { display: table-header-group; }                                       /* повтор шапки на каждой странице */
  tr, img, figure { break-inside: avoid; }                                     /* не разрывать строку/блок */
  h2 { break-after: avoid; }
  .page-break { break-before: page; }
  * { -webkit-print-color-adjust: exact; print-color-adjust: exact; }          /* печатать фоны */
}
```

```ts
window.print();                                                                 // диалог печати
window.addEventListener("beforeprint", prepare); window.addEventListener("afterprint", cleanup);
// Печать отдельного фрагмента: скрытый iframe или окно с выбранной разметкой
const win = window.open("", "_blank")!; win.document.write(html); win.document.close(); win.onload = () => win.print();
```

Практики печатных форм:

| Задача | Решение |
|---|---|
| Единицы измерения | `mm`, `pt`, `cm` вместо `px`/`vh` |
| Разбиение на страницы | `break-before/after/inside`, `page-break-*` (легаси) |
| Повтор шапки таблицы | `thead { display: table-header-group }` |
| Колонтитулы, номера страниц | `@page` margin boxes (`@bottom-center { content: counter(page) }`) — поддержка ограничена; надёжнее — серверный рендер или библиотеки (Paged.js) |
| Формы с точной вёрсткой | фиксированная сетка на `mm`, `position: absolute` для бланков |
| Печать без диалога | недоступно из браузера (только киоск-режим/сервер) |
| Предпросмотр | отдельная страница «для печати» |

Полифилл для сложных требований: **Paged.js** (CSS Paged Media), серверный рендер **Playwright/Chromium** `page.pdf()` — единый результат.

## Нюансы и подводные камни

- Браузеры по-разному разбивают страницы и обрабатывают `@page` (Safari особенно).
- Пользователь может включить/выключить фоновую графику и колонтитулы в диалоге печати.
- Стили экрана применяются к печати, если не переопределены.
- Динамические изображения и шрифты должны быть загружены до `print()`.
- Печать SPA: рендерите маршрут «печатной версии», а не «скриншот».

## Практика

1. Подготовьте print-стили для страницы счёта (A4, повтор шапки таблицы, без навигации).
2. Проверьте результат в Chrome, Firefox и Safari.
3. Реализуйте кнопку «Печать» с `beforeprint/afterprint`.

## Вопросы с ответами

> [!question]- Почему печать через CSS лучше html2canvas для документов?
> Результат векторный, текст выделяется, размер меньше, разбиение страниц управляется CSS.

> [!question]- Как повторить шапку таблицы на каждой странице?
> `thead { display: table-header-group; }` в print-стилях.

## Связанные темы

- [[N:3ea33104867981439c1ac7bb5e16fa83]]
- [[N:3ea33104867981b4b4fcc2eac6967d70]]
