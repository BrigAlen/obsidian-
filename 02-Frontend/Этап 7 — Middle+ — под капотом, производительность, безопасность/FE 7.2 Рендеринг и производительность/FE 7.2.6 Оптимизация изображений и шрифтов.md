---
type: topic
domain: frontend
stage: 7
section: "7.2"
order: 6
status: todo
level: senior
notion_id: 3ea33104867981bc8e82ef4525554470
tags: [domain/frontend, stage/7, level/senior, topic/images, topic/fonts, topic/performance, priority/should]
reviewed:
next_review:
priority: should
time: 3
---

# Оптимизация изображений и шрифтов

↑ [[FE 7.2 Рендеринг и производительность|7.2 Рендеринг и производительность]] · ← [[FE 7.2.5 Tree shaking и размер бандла|Предыдущая]] · → [[FE 7.2.7 Виртуализация длинных списков|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: senior</span></div>
<!-- meta:end -->







> [!info] Зачем это на собесе
> Изображения и шрифты — основной вес страницы и главный вклад в LCP и CLS.

## Изображения

- форматы: **AVIF** и **WebP** вместо JPEG и PNG; SVG для иконок;
- адаптивность: `srcset` и `sizes`, `<picture>` для смены формата;
- `width` и `height` для резервирования места (без CLS);
- `loading="lazy"` для изображений ниже сгиба, `fetchpriority="high"` для LCP-изображения;
- `decoding="async"`;
- CDN с трансформацией на лету (размер, формат, качество).

```html
<picture>
  <source type="image/avif" srcset="hero-800.avif 800w, hero-1600.avif 1600w">
  <img src="hero-800.jpg" width="800" height="450" alt="Панель управления"
       sizes="(max-width: 800px) 100vw, 800px" fetchpriority="high">
</picture>
```

## Шрифты

- **WOFF2** — основной формат;
- subset: оставить только нужные символы (кириллица, латиница);
- variable-шрифты вместо набора начертаний;
- `font-display: swap` (или `optional`) — не прятать текст;
- preload критичных шрифтов;
- размещать у себя, а не на стороннем домене (меньше DNS и TLS).

```css
@font-face {
  font-family: 'Inter';
  src: url('/fonts/inter-var.woff2') format('woff2');
  font-weight: 100 900;
  font-display: swap;
}
```

## CLS от шрифтов

Смена fallback на веб-шрифт двигает текст. Подберите fallback с похожими метриками (`size-adjust`, `ascent-override`).

## Вопросы с ответами

> [!question]- Как ускорить LCP-изображение?
> Preload или `fetchpriority="high"`, не ставить lazy, современный формат, правильный размер, CDN.

> [!question]- Зачем font-display: swap?
> Чтобы показывать текст запасным шрифтом сразу, а не ждать загрузки (иначе невидимый текст).
