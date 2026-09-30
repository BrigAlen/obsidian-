---
type: domain
domain: frontend
tags: [domain/frontend, kind/moc]
---

# Frontend

Vue 3 + Quasar + TypeScript, middle+/senior.

↑ [[00 Карта]]

> [!tip] Как проходить
> Этапы по порядку → внутри этапа разделы по порядку. После каждой темы: карточки → квиз → перенос в статус `done`.

## Этапы
- [[FE Этап 1 · Фундамент — веб, HTML, CSS, база JS|Этап 1 · Фундамент: веб, HTML, CSS, база JS]]
- [[FE Этап 2 · JavaScript глубоко|Этап 2 · JavaScript глубоко]]
- [[FE Этап 3 · TypeScript|Этап 3 · TypeScript]]
- [[FE Этап 4 · Vue 3 — основы и компоненты|Этап 4 · Vue 3: основы и компоненты]]
- [[FE Этап 5 · Экосистема — Router, Pinia, Quasar, API, Auth|Этап 5 · Экосистема: Router, Pinia, Quasar, API, Auth]]
- [[FE Этап 6 · Инженерные практики — Git, сборка, качество, тесты|Этап 6 · Инженерные практики: Git, сборка, качество, тесты]]
- [[FE Этап 7 · Middle+ — под капотом, производительность, безопасность|Этап 7 · Middle+: под капотом, производительность, безопасность]]
- [[FE Этап 8 · Senior — архитектура, паттерны, алгоритмы, System Design|Этап 8 · Senior: архитектура, паттерны, алгоритмы, System Design]]
- [[FE Этап 9 · Лидерство и финальная подготовка к собесу|Этап 9 · Лидерство и финальная подготовка к собесу]]

## Прогресс
```dataview
TABLE WITHOUT ID stage AS Этап, length(rows) AS Всего, length(filter(rows, (r) => r.status = "done")) AS Готово
FROM "02-Frontend"
WHERE type = "topic"
GROUP BY stage
SORT stage ASC
```
