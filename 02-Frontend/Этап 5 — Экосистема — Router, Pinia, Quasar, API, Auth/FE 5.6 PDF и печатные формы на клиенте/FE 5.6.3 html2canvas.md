---
type: topic
domain: frontend
stage: 5
section: "5.6"
order: 3
status: todo
level: middle
notion_id: 3ea33104867981439c1ac7bb5e16fa83
tags: [domain/frontend, stage/5, level/middle, topic/pdf, topic/html2canvas, topic/screenshots, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# html2canvas

↑ [[FE 5.6 PDF и печатные формы на клиенте|5.6 PDF и печатные формы на клиенте]] · ← [[FE 5.6.2 pdf.js|Предыдущая]] · → [[FE 5.6.4 Печать из браузера и CSS @media print|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->



> [!info] Зачем это на собесе
> Скриншот DOM в изображение/PDF: возможности и ограничения подхода.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

**html2canvas** «перерисовывает» DOM в `<canvas>`, читая вычисленные стили (не делает настоящий снимок экрана).

```ts
import html2canvas from "html2canvas";
import { jsPDF } from "jspdf";

const el = document.getElementById("report")!;
const canvas = await html2canvas(el, { scale: 2, useCORS: true, backgroundColor: "#fff", logging: false, windowWidth: el.scrollWidth });
const img = canvas.toDataURL("image/png");                                       // PNG-изображение

const pdf = new jsPDF("p", "mm", "a4");
const w = 210, h = (canvas.height * w) / canvas.width;
pdf.addImage(img, "PNG", 0, 0, w, h);                                             // страница-картинка (без выделяемого текста)
pdf.save("report.pdf");
```

Многостраничность: разрезать canvas на страницы по высоте A4 и добавлять `addPage()`; либо использовать `pdf.html(el, {...})`.

Ограничения:

| Проблема | Комментарий |
|---|---|
| Результат — растр | текст не выделяется, размер файла большой |
| CSS-поддержка частичная | `backdrop-filter`, некоторые `transform`, `filter`, шрифты, `position: sticky` отображаются некорректно |
| CORS | изображения с чужих доменов «пачкают» canvas (нужны `useCORS` и заголовки) |
| Производительность | большие DOM/`scale: 2` тяжёлые, ограничения размера canvas |
| Шрифты | веб-шрифты должны быть загружены до захвата |
| Разбиение страниц | разрывы посреди строк/таблиц |
| Точность | отличается от отображения в браузере |

Альтернативы: **`dom-to-image-more`/`html-to-image`** (SVG `foreignObject`), **`@media print` + печать/«Сохранить как PDF»** (векторно, текст сохраняется), **серверный рендер в Chromium (Playwright/Puppeteer)** — идеальная точность, **`pdfmake`/jsPDF-таблицы** для структурированных документов.

Выбор: для быстрых «снимков» блоков (график, подпись, превью) — html2canvas; для документов — печать или серверная генерация.

## Нюансы и подводные камни

- Перед захватом дождитесь загрузки шрифтов и изображений (`document.fonts.ready`).
- Скрытые элементы и прокручиваемые контейнеры: временно раскрывайте (`overflow: visible`).
- Чувствительные данные в скриншоте — вопросы безопасности.
- Ограничения размера canvas в браузерах (особенно мобильных).

## Практика

1. Сделайте скриншот блока с графиком и сохраните как PNG.
2. Разбейте длинный отчёт на несколько страниц PDF.
3. Сравните качество с печатью через `@media print`.

## Вопросы с ответами

> [!question]- Как работает html2canvas?
> Обходит DOM, читает вычисленные стили и перерисовывает элементы в `<canvas>`; это имитация, а не снимок экрана.

> [!question]- Главный недостаток при создании PDF?
> Результат растровый: нет выделяемого текста, большой размер и артефакты разбиения страниц.

## Связанные темы

- [[N:3ea3310486798101b2eeca4cfd1d1aa6]]
- [[N:3ea3310486798179a72cfe83566355ca]]
