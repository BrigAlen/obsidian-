---
type: topic
domain: frontend
stage: 7
section: "7.2"
order: 3
status: todo
level: senior
notion_id: 3ea33104867981d3a87ec92c52abaa2a
tags: [domain/frontend, stage/7, level/senior, topic/web-vitals, topic/lcp, topic/inp, topic/cls, priority/should]
reviewed:
next_review:
priority: should
time: 3
---

# Core Web Vitals: LCP, INP, CLS

↑ [[FE 7.2 Рендеринг и производительность|7.2 Рендеринг и производительность]] · ← [[FE 7.2.2 Reflow и Repaint|Предыдущая]] · → [[FE 7.2.4 Code splitting и lazy loading|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: senior</span></div>
<!-- meta:end -->


> [!info] Зачем это на собесе
> Стандартные метрики качества; спрашивают, что означают, пороги и как улучшать.

## Метрики

| Метрика | Что измеряет | Хорошо |
|---|---|---|
| **LCP** (Largest Contentful Paint) | время появления крупнейшего элемента | ≤ 2.5 с |
| **INP** (Interaction to Next Paint) | отзывчивость на взаимодействие (заменил FID) | ≤ 200 мс |
| **CLS** (Cumulative Layout Shift) | визуальные сдвиги | ≤ 0.1 |

Дополнительно: **TTFB**, **FCP**, **TBT** (лабораторная замена INP).

## Как улучшать

**LCP**: быстрый сервер и CDN, `preload` главного изображения, `fetchpriority="high"`, современные форматы, SSR или SSG, убрать render-blocking.

**INP**: разбивать длинные задачи (>50 мс), `scheduler.yield()`, отложить тяжёлую логику, Web Worker, меньше JS на главной, дебаунс обработчиков.

**CLS**: задавать размеры изображений, резерв места под баннеры и рекламу, `font-display: swap` вместе с подбором метрик fallback-шрифта, не вставлять контент выше существующего.

## Сбор данных

- **Lab** (Lighthouse, WebPageTest): воспроизводимо, для отладки;
- **Field / RUM** (CrUX, библиотека `web-vitals`, Sentry): реальные пользователи, 75-й перцентиль.

```ts
import { onLCP, onINP, onCLS } from 'web-vitals'
onLCP(m => sendToAnalytics(m))
onINP(m => sendToAnalytics(m))
onCLS(m => sendToAnalytics(m))
```

## Вопросы с ответами

> [!question]- Чем INP отличается от FID?
> FID измерял только задержку первого ввода. INP оценивает отзывчивость всех взаимодействий за сессию (по худшим).

> [!question]- Почему Lighthouse показывает 95, а пользователи жалуются?
> Lighthouse — лабораторный замер на мощной машине и стабильной сети. Реальные устройства и сети нужно смотреть по RUM.
