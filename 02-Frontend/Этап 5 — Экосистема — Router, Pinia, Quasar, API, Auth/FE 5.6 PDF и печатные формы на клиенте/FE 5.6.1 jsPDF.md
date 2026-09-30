---
type: topic
domain: frontend
stage: 5
section: "5.6"
order: 1
status: todo
level: middle
notion_id: 3ea33104867981c9ba57d2f24f3163ab
tags: [domain/frontend, stage/5, level/middle, topic/pdf, topic/jspdf, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# jsPDF

↑ [[FE 5.6 PDF и печатные формы на клиенте|5.6 PDF и печатные формы на клиенте]] · → [[FE 5.6.2 pdf.js|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->










> [!info] Зачем это на собесе
> Когда документ нужно собрать в браузере: чеки, простые отчёты; и почему кириллица требует шрифта.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

**jsPDF** — библиотека генерации PDF на клиенте (императивный API: текст, линии, изображения, таблицы через `jspdf-autotable`).

```ts
import { jsPDF } from "jspdf";
import autoTable from "jspdf-autotable";
import robotoBase64 from "./fonts/Roboto-Regular.base64?raw";

const doc = new jsPDF({ unit: "mm", format: "a4", orientation: "portrait" });
doc.addFileToVFS("Roboto.ttf", robotoBase64);
doc.addFont("Roboto.ttf", "Roboto", "normal");
doc.setFont("Roboto");                                        // без встроенного шрифта кириллица превратится в «мусор»

doc.setFontSize(16).text(`Счёт № ${inv.number}`, 14, 20);
autoTable(doc, {
  startY: 30,
  head: [["Товар", "Кол-во", "Сумма"]],
  body: inv.items.map(i => [i.title, i.qty, fmt(i.total)]),
  styles: { font: "Roboto", fontSize: 10 },
  didDrawPage: (d) => doc.text(`Стр. ${doc.getNumberOfPages()}`, 190, 285, { align: "right" }),
});
doc.addImage(logoDataUrl, "PNG", 150, 10, 40, 15);
doc.save(`invoice-${inv.number}.pdf`);                       // скачать
const blobUrl = doc.output("bloburl");                        // предпросмотр в iframe/окне
```

Возможности: разметка страниц, шрифты (Unicode через TTF), изображения (PNG/JPEG/SVG плагином `svg2pdf`), `html()` (рендер HTML через html2canvas — растровый), метаданные, защита паролем, водяные знаки.

Подходит: простые документы, чеки, экспорт таблиц, когда важны офлайн и отсутствие нагрузки на сервер. Не подходит: сложная вёрстка, тысячи страниц, юридически значимые формы, единый вид для всех пользователей — лучше серверная генерация (QuestPDF, FastReport — см. [[N:3ea3310486798186b924e9e6527d4deb]]).

## Нюансы и подводные камни

- Кириллица и специальные символы требуют встроенного TTF-шрифта (размер бандла).
- Позиции задаются вручную в миллиметрах: сложная вёрстка трудоёмка.
- Большие документы блокируют главный поток: используйте Web Worker.
- `doc.html()` даёт растровый (не текстовый) результат — не копируется и тяжёлый.
- Безопасность: данные документа формируются на клиенте и могут быть подделаны — не для официальных документов.

## Практика

1. Сгенерируйте счёт с таблицей и русским шрифтом.
2. Добавьте нумерацию страниц и колонтитулы.
3. Вынесите генерацию в Web Worker.

## Вопросы с ответами

> [!question]- Почему в jsPDF не отображается кириллица?
> Стандартные шрифты не содержат кириллицу: нужно подключить TTF-шрифт с поддержкой Unicode.

> [!question]- Когда генерацию лучше делать на сервере?
> Для сложных шаблонов, больших объёмов, единообразия и юридически значимых документов.

## Связанные темы

- [[N:3ea33104867981959103d2c15e81596d]]
- [[N:3ea3310486798101b2eeca4cfd1d1aa6]]
