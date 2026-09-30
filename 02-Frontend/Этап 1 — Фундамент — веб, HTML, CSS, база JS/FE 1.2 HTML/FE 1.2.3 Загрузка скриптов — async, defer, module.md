---
type: topic
domain: frontend
stage: 1
section: "1.2"
order: 3
status: todo
level: junior
notion_id: 3ea3310486798136a85bfe7fb3bfcefe
tags: [domain/frontend, stage/1, level/junior, topic/html, topic/performance, topic/scripts, priority/should]
reviewed:
next_review:
priority: should
time: 3
---

# Загрузка скриптов: async, defer, module

↑ [[FE 1.2 HTML|1.2 HTML]] · ← [[FE 1.2.2 Формы и валидация|Предыдущая]] · → [[FE 1.2.4 Изображения и медиа — srcset, picture, lazy loading|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: junior</span></div>
<!-- meta:end -->















> [!info] Зачем это на собесе
> Критично для производительности: как скрипты блокируют рендер и чем отличаются `async` и `defer`.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

Обычный `<script>` блокирует парсинг HTML: браузер скачивает и выполняет его, затем продолжает.

| Атрибут | Загрузка | Выполнение | Порядок |
|---|---|---|---|
| (нет) | блокирует парсинг | сразу | по порядку |
| `async` | параллельно | сразу после загрузки (может прервать парсинг) | не гарантирован |
| `defer` | параллельно | после парсинга, до `DOMContentLoaded` | по порядку |
| `type="module"` | параллельно | как `defer`; строгий режим, свой scope, поддержка `import` | по порядку |
| `nomodule` | для старых браузеров | | |

```html
<script src="analytics.js" async></script>      <!-- независимые скрипты -->
<script src="app.js" defer></script>            <!-- зависят от DOM/порядка -->
<script type="module" src="/src/main.js"></script>
<script type="module">import { init } from "./app.js"; init();</script>
```

Также: `preload` для критичных ресурсов, `modulepreload`, динамический `import()` для код-сплиттинга, `fetchpriority="high"`, размещение скриптов в конце `<body>` (устаревший приём, заменён `defer`).

## Нюансы и подводные камни

- `async` для скриптов, зависящих друг от друга, приводит к гонкам порядка.
- `defer` и `async` не работают для inline-скриптов (без `src`).
- `type="module"` выполняется в строгом режиме, `this` на верхнем уровне — `undefined`.
- Модули подчиняются CORS, при `file://` могут не работать.
- Сторонние скрипты (метрики, чаты) — главный источник блокировок: загружайте `async` или по бездействию.

## Практика

1. Сравните загрузку страницы с обычным, `defer` и `async` скриптом в Performance.
2. Отложите загрузку виджета до `requestIdleCallback`.
3. Добавьте `preload` для критичного шрифта/скрипта и измерьте LCP.

## Вопросы с ответами

> [!question]- Чем async отличается от defer?
> `async` выполняется как только скачан, порядок не гарантирован; `defer` — после парсинга и в порядке подключения.

> [!question]- Когда использовать module?
> Для современных приложений с `import/export`; ведёт себя как `defer`.

## Связанные темы

- [[N:3ea33104867981d0ba11f7d15eee409c]]
- [[N:3ea33104867981408326d7b9cf34d28d]]
