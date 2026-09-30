---
type: topic
domain: frontend
stage: 7
section: "7.2"
order: 11
status: todo
level: senior
notion_id: 3ea33104867981118305df81a5feea88
tags: [domain/frontend, stage/7, level/senior, topic/lighthouse-ci, topic/budget, topic/ci, priority/should]
reviewed:
next_review:
priority: should
time: 3
---

# Тестирование производительности: Lighthouse CI, performance budget

↑ [[FE 7.2 Рендеринг и производительность|7.2 Рендеринг и производительность]] · ← [[FE 7.2.10 Инструменты — DevTools Performance, Lighthouse, Vue DevTools|Предыдущая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: senior</span></div>
<!-- meta:end -->








> [!info] Зачем это на собесе
> Показывает, что производительность — процесс, а не разовая акция: регрессии ловятся в CI.

## Performance budget

Ограничения, которые нельзя превышать:

| Тип | Пример |
|---|---|
| Размер | JS на главной ≤ 200 КБ (gzip) |
| Метрики | LCP ≤ 2.5 с, TBT ≤ 200 мс, CLS ≤ 0.1 |
| Количество | запросов ≤ 50 |

## Lighthouse CI

```json
{
  "ci": {
    "collect": { "url": ["http://localhost:4173/"], "numberOfRuns": 3 },
    "assert": {
      "assertions": {
        "categories:performance": ["error", { "minScore": 0.9 }],
        "largest-contentful-paint": ["error", { "maxNumericValue": 2500 }],
        "total-byte-weight": ["warn", { "maxNumericValue": 500000 }]
      }
    },
    "upload": { "target": "temporary-public-storage" }
  }
}
```

```yaml
- run: npm run build && npm run preview &
- run: npx @lhci/cli autorun
```

Несколько прогонов и медиана снижают шум.

## Контроль размера бандла

`size-limit`, `bundlewatch`, порог на файл в PR:

```json
{ "size-limit": [{ "path": "dist/assets/index-*.js", "limit": "200 KB" }] }
```

## RUM в проде

`web-vitals`, Sentry, Grafana Faro: 75-й перцентиль по страницам, алерты при росте.

## Нюансы

- лабораторные замеры в CI шумные: сравнивайте тренды, а не одиночные значения;
- бюджет назначают по реальным данным и ужесточают постепенно;
- проверка нагрузки API: k6 (для фронтенда — сценарии с браузером).

## Вопросы с ответами

> [!question]- Как не допустить деградации производительности?
> Performance budget в CI (Lighthouse CI, size-limit), проверка размера бандла в PR, мониторинг Web Vitals в проде с алертами.

> [!question]- Почему результаты Lighthouse в CI нестабильны?
> Разная нагрузка раннеров, сеть, кэш. Делают несколько прогонов, берут медиану и выставляют допуски.
