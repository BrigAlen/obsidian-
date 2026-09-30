---
type: topic
domain: frontend
stage: 5
section: "5.6"
order: 2
status: todo
level: middle
notion_id: 3ea3310486798101b2eeca4cfd1d1aa6
tags: [domain/frontend, stage/5, level/middle, topic/pdf, topic/pdfjs, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# pdf.js

↑ [[FE 5.6 PDF и печатные формы на клиенте|5.6 PDF и печатные формы на клиенте]] · ← [[FE 5.6.1 jsPDF|Предыдущая]] · → [[FE 5.6.3 html2canvas|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->










> [!info] Зачем это на собесе
> Просмотр PDF в приложении: рендер страниц, поиск, worker.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

**pdf.js** (Mozilla) — библиотека парсинга и отрисовки PDF в `<canvas>`; основа встроенного просмотрщика Firefox.

```ts
import * as pdfjs from "pdfjs-dist";
import workerUrl from "pdfjs-dist/build/pdf.worker.min.mjs?url";
pdfjs.GlobalWorkerOptions.workerSrc = workerUrl;                 // парсинг в Web Worker

const pdf = await pdfjs.getDocument({ url, withCredentials: true, cMapUrl: "/cmaps/", cMapPacked: true }).promise;   // cMaps для CJK/кириллических шрифтов
const page = await pdf.getPage(1);
const viewport = page.getViewport({ scale: 1.5 * devicePixelRatio });
canvas.width = viewport.width; canvas.height = viewport.height;
await page.render({ canvasContext: canvas.getContext("2d")!, viewport }).promise;

const text = await page.getTextContent();                        // текстовый слой (поиск, выделение)
pdf.numPages; await pdf.getMetadata();
```

Варианты интеграции:

| Способ | Особенности |
|---|---|
| `<iframe>`/`<embed>`/`<object>` с Blob URL | встроенный просмотрщик браузера, минимум кода, разное поведение на мобильных |
| pdf.js (`pdfjs-dist`) | полный контроль: canvas + текстовый слой + аннотации |
| `pdf.js` viewer (готовый `web/viewer.html`) | готовый интерфейс (поиск, миниатюры, печать) |
| Обёртки (`vue-pdf-embed`, `@tato30/vue-pdf`, `vue3-pdf-app`) | компоненты для Vue |
| Коммерческие SDK (PSPDFKit, Apryse) | подпись, аннотации, формы |

Практики: рендерить только видимые страницы (виртуализация, `IntersectionObserver`), кэшировать рендер, учитывать `devicePixelRatio`, освобождать ресурсы (`page.cleanup()`, `pdf.destroy()`), передавать `Authorization` при закрытых файлах (получить `Blob`/`ArrayBuffer` и открыть из данных).

Безопасность: PDF может содержать скрипты — pdf.js отключает выполнение (`enableScripting: false`); проверяйте источник; CSP для worker.

## Нюансы и подводные камни

- Версия worker должна совпадать с версией библиотеки.
- Большие файлы: потоковая загрузка (`rangeChunkSize`), `disableAutoFetch`.
- Шрифты без встроенных cMaps отображаются некорректно.
- `pdfjs-dist` тяжёлый (ленивая загрузка чанка).
- Мобильные браузеры: `iframe` с PDF часто показывает только первую страницу.

## Практика

1. Отобразите PDF постранично на canvas с навигацией и масштабом.
2. Добавьте текстовый слой и поиск по документу.
3. Загрузите защищённый PDF с токеном как Blob.

## Вопросы с ответами

> [!question]- Что такое pdf.js?
> Библиотека для парсинга и отрисовки PDF в браузере (canvas и текстовый слой).

> [!question]- Зачем Web Worker в pdf.js?
> Парсинг PDF выполняется вне главного потока, чтобы не блокировать интерфейс.

## Связанные темы

- [[N:3ea33104867981c9ba57d2f24f3163ab]]
- [[N:3ea33104867981439c1ac7bb5e16fa83]]
