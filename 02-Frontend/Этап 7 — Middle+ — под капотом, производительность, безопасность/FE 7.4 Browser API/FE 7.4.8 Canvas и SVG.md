---
type: topic
domain: frontend
stage: 7
section: "7.4"
order: 8
status: todo
level: senior
notion_id: 3ea33104867981e0a988fae381ee0ed9
tags: [domain/frontend, stage/7, level/senior, topic/browser-api, topic/canvas, topic/svg, topic/graphics, priority/should]
reviewed:
next_review:
priority: should
time: 3
---

# Canvas и SVG

↑ [[FE 7.4 Browser API|7.4 Browser API]] · ← [[FE 7.4.7 Web Workers|Предыдущая]] · → [[FE 7.4.9 Web Components и Shadow DOM|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: senior</span></div>
<!-- meta:end -->



> [!info] Зачем это на собесе
> Выбор технологии графики: что лучше для диаграммы на 10 тыс. точек, а что для иконок.

## SVG

Векторная разметка в DOM: каждый элемент — узел.

```html
<svg viewBox="0 0 100 40" width="200">
  <circle cx="20" cy="20" r="10" fill="currentColor" />
  <path d="M40 30 L60 10 L80 30" stroke="black" fill="none" />
</svg>
```

Плюсы: масштабируется без потери качества, стилизуется CSS, обрабатывает события на элементах, доступен (title, aria), анимация SMIL/CSS.
Минусы: много элементов (тысячи) → тормоза DOM.

## Canvas

Растровая область, рисуем командами; DOM-элементов нет.

```ts
const ctx = canvas.getContext('2d')!
ctx.fillStyle = '#4c8bf5'
ctx.fillRect(10, 10, 100, 50)
ctx.beginPath(); ctx.arc(60, 80, 20, 0, Math.PI * 2); ctx.fill()

// чёткость на retina
const dpr = devicePixelRatio
canvas.width = cssWidth * dpr; canvas.height = cssHeight * dpr
ctx.scale(dpr, dpr)
```

Плюсы: очень быстро для десятков тысяч объектов, игры, обработка изображений, WebGL/WebGPU (3D).
Минусы: нет объектной модели (сами делаем hit-testing), хуже с доступностью, при масштабировании нужна перерисовка.

## Выбор

| Задача | Что взять |
|---|---|
| Иконки, логотипы, простые диаграммы | SVG |
| Интерактивные графики до тысяч элементов | SVG (D3, ECharts SVG-режим) |
| Огромные данные, тепловые карты, игры | Canvas |
| 3D, шейдеры | WebGL / WebGPU (Three.js) |

Библиотеки: ECharts, Chart.js (canvas), D3 (SVG), Konva/Fabric (canvas-сцены), Three.js.

## Вопросы с ответами

> [!question]- Когда Canvas, а когда SVG?
> SVG — для небольшого числа интерактивных, стилизуемых элементов. Canvas — для большого числа объектов и частых перерисовок.

> [!question]- Как сделать Canvas чётким на retina?
> Умножить внутренний размер на `devicePixelRatio` и масштабировать контекст.
