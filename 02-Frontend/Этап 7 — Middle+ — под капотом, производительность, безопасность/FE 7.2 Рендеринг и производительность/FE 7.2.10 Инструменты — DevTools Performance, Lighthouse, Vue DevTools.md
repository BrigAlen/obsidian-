---
type: topic
domain: frontend
stage: 7
section: "7.2"
order: 10
status: todo
level: senior
notion_id: 3ea3310486798133934be54dffff6093
tags: [domain/frontend, stage/7, level/senior, topic/devtools, topic/lighthouse, topic/profiling, priority/should]
reviewed:
next_review:
priority: should
time: 3
---

# Инструменты: DevTools Performance, Lighthouse, Vue DevTools

↑ [[FE 7.2 Рендеринг и производительность|7.2 Рендеринг и производительность]] · ← [[FE 7.2.9 Кэширование — HTTP-кэш, Service Worker|Предыдущая]] · → [[FE 7.2.11 Тестирование производительности — Lighthouse CI, performance budget|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: senior</span></div>
<!-- meta:end -->







> [!info] Зачем это на собесе
> Оптимизация без измерений — гадание. Спрашивают процесс профилирования.

## Chrome DevTools

- **Performance**: запись, flame chart, Long Tasks, Main thread, Layout/Paint, FPS, throttling CPU (4x, 6x) и сети;
- **Network**: waterfall, размеры, кэш, приоритеты, throttling;
- **Coverage**: сколько загруженного JS/CSS реально использовалось;
- **Memory**: heap snapshot, утечки (Detached DOM, растущие listeners);
- **Rendering**: подсветка перерисовок и layout shifts;
- **Lighthouse**: аудит производительности, доступности, SEO.

## Процесс профилирования

1. Зафиксировать сценарий и метрику (INP на клике «Применить»).
2. Включить throttling CPU 4x — приближение к среднему телефону.
3. Записать Performance, найти Long Tasks.
4. Раскрыть flame chart: чья функция занимает время (Bottom-Up, Call Tree).
5. Исправить, повторить замер, сравнить.

## Vue DevTools

- Components: props и состояние;
- Timeline: события компонентов, Performance (время рендера);
- Pinia: состояние сторов и time travel;
- Router: история переходов.

## Другие

WebPageTest (реальные устройства, waterfall), `PerformanceObserver`, User Timing (`performance.mark/measure`), Sentry Performance, Bundle analyzers.

```ts
performance.mark('filter-start')
applyFilter()
performance.measure('filter', 'filter-start')
```

## Вопросы с ответами

> [!question]- С чего начнёте разбор медленной страницы?
> Воспроизвести с throttling, снять Performance-профиль, найти долгие задачи и водопад запросов, определить по метрикам (LCP, INP, CLS), что именно страдает.

> [!question]- Как искать утечку памяти?
> Memory: два heap snapshot до и после действия, сравнить, найти растущие объекты и Detached DOM; проверить слушатели, таймеры, подписки без отписки.
