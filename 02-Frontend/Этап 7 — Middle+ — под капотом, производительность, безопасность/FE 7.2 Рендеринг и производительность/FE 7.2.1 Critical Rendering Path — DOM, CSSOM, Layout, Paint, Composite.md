---
type: topic
domain: frontend
stage: 7
section: "7.2"
order: 1
status: todo
level: senior
notion_id: 3ea3310486798199b116fac280ea01c6
tags: [domain/frontend, stage/7, level/senior, topic/browser, topic/rendering, topic/crp, priority/should]
reviewed:
next_review:
priority: should
time: 3
---

# Critical Rendering Path: DOM, CSSOM, Layout, Paint, Composite

↑ [[FE 7.2 Рендеринг и производительность|7.2 Рендеринг и производительность]] · → [[FE 7.2.2 Reflow и Repaint|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: senior</span></div>
<!-- meta:end -->











> [!info] Зачем это на собесе
> Вопрос «что происходит после ввода URL / как браузер рисует страницу» проверяет фундамент производительности.

## Шаги

1. **HTML → DOM**: парсер строит дерево узлов.
2. **CSS → CSSOM**: стили тоже превращаются в дерево.
3. **Render tree**: DOM + CSSOM, без `display: none` и `head`.
4. **Layout**: вычисление размеров и позиций.
5. **Paint**: отрисовка пикселей по слоям.
6. **Composite**: сборка слоёв на GPU в итоговое изображение.

## Блокировки

| Ресурс | Что блокирует |
|---|---|
| CSS | рендер (render-blocking) и выполнение скриптов после него |
| Синхронный `<script>` | парсинг HTML |
| `<script defer>` | не блокирует парсинг, выполняется после разбора, по порядку |
| `<script async>` | не блокирует парсинг, выполняется сразу как загрузится, без порядка |
| `type="module"` | как `defer` по умолчанию |

## Как ускорять

- критический CSS инлайнить, остальной грузить асинхронно;
- скрипты — `defer` или `module`;
- `<link rel="preload">` для критичных шрифтов и hero-изображения;
- `preconnect` к сторонним доменам, `dns-prefetch`;
- минимизировать глубину цепочек запросов (CSS → шрифт → изображение).

```html
<link rel="preconnect" href="https://cdn.example.com" crossorigin>
<link rel="preload" as="font" href="/fonts/inter.woff2" type="font/woff2" crossorigin>
<script type="module" src="/assets/app.js"></script>
```

## Вопросы с ответами

> [!question]- Почему CSS называют render-blocking?
> Браузер не рисует страницу, пока не построит CSSOM, иначе показал бы «мигание» без стилей.

> [!question]- Разница между defer и async?
> Оба не блокируют парсинг. `defer` выполняется по порядку после разбора документа, `async` — сразу после загрузки в произвольном порядке.
