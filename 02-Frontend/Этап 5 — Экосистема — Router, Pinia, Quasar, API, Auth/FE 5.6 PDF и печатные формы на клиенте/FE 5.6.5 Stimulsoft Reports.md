---
type: topic
domain: frontend
stage: 5
section: "5.6"
order: 5
status: todo
level: middle
notion_id: 3ea33104867981b4b4fcc2eac6967d70
tags: [domain/frontend, stage/5, level/middle, topic/pdf, topic/reports, topic/stimulsoft, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Stimulsoft Reports

↑ [[FE 5.6 PDF и печатные формы на клиенте|5.6 PDF и печатные формы на клиенте]] · ← [[FE 5.6.4 Печать из браузера и CSS @media print|Предыдущая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->












> [!info] Зачем это на собесе
> Коммерческие дизайнеры отчётов встречаются в корпоративных системах: как встроить и чем ограничены.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

**Stimulsoft Reports** — коммерческий пакет для создания отчётов: JS-библиотеки (Viewer, Designer, Engine), версии для .NET, PHP, Java. Отчёт — шаблон (`.mrt`, JSON) с источниками данных, группировками, диаграммами, вычислениями.

```ts
import { Stimulsoft } from "stimulsoft-reports-js/Scripts/stimulsoft.reports";
import "stimulsoft-reports-js/Scripts/stimulsoft.viewer";

Stimulsoft.Base.StiLicense.key = import.meta.env.VITE_STIMULSOFT_KEY;

const report = new Stimulsoft.Report.StiReport();
report.loadFile("/templates/invoice.mrt");                        // или loadDocument(json) из API
const data = new Stimulsoft.System.Data.DataSet("Data"); data.readJson(invoiceJson);
report.regData("Data", "Data", data);                              // данные в шаблон

const viewer = new Stimulsoft.Viewer.StiViewer(new Stimulsoft.Viewer.StiViewerOptions(), "viewer", false);
viewer.report = report; viewer.renderHtml("viewerContainer");      // просмотр, печать, экспорт (PDF, Excel, Word)

// Экспорт без показа
report.renderAsync(() => report.exportDocumentAsync((pdf) => save(pdf, "invoice.pdf"), Stimulsoft.Report.StiExportFormat.Pdf));
```

Компоненты: **Designer** (веб-конструктор шаблонов для пользователей), **Viewer** (просмотр/печать/экспорт), **Engine** (рендер на клиенте или сервере).

Схемы использования:

| Схема | Плюсы | Минусы |
|---|---|---|
| Рендер на клиенте | нет нагрузки на сервер, интерактивность | тяжёлый бандл, данные на клиенте, зависимость от браузера |
| Рендер на сервере (.NET) | единый результат, безопасность данных, большие объёмы | инфраструктура |
| Шаблоны хранятся в БД/API | редактирование без релиза | версионирование, права |

Практика: шаблоны версионируются и хранятся на сервере, данные передаются в отчёт как JSON, права на просмотр проверяются на бэкенде; лицензионный ключ управляется через конфигурацию окружения; кириллические шрифты должны быть подключены.

Альтернативы: FastReport, DevExpress Reports, Telerik Reporting, Crystal Reports, JasperReports; open-source — pdfmake, QuestPDF/PDFsharp (сервер), Paged.js, `@react-pdf` (для React).

## Нюансы и подводные камни

- Лицензия коммерческая: ключ в клиентском коде виден — учитывайте условия использования.
- Размер библиотек — загружайте лениво (`import()`), только на страницах отчётов.
- Персональные данные в шаблонах/данных на клиенте — вопросы безопасности.
- Совместимость версий Designer/Viewer/Engine и формата `.mrt`.
- Кастомизация внешнего вида ограничена.

## Практика

1. Встройте Viewer и покажите отчёт по данным из API.
2. Реализуйте экспорт в PDF и Excel.
3. Оцените плюсы и минусы клиентского и серверного рендера для вашей задачи.

## Вопросы с ответами

> [!question]- Когда использовать готовый дизайнер отчётов?
> Когда пользователи должны сами настраивать шаблоны и требуется богатый функционал (группировки, диаграммы, экспорт) без разработки.

> [!question]- Клиентский или серверный рендер отчётов?
> Клиентский — для интерактивности и малых объёмов, серверный — для безопасности, больших данных и единообразия.

## Связанные темы

- [[N:3ea3310486798179a72cfe83566355ca]]
- [[N:3ea33104867981b5810dd862257958d2]]
