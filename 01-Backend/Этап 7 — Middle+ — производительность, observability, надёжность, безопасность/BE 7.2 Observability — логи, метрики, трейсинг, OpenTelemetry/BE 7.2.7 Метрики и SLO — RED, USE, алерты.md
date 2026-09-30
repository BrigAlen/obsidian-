---
type: topic
domain: backend
stage: 7
section: "7.2"
order: 7
status: todo
level: senior
notion_id: 3ea3310486798118bb10cd40be47fd97
tags: [domain/backend, stage/7, level/senior, topic/observability, topic/slo, topic/alerting, priority/should]
reviewed:
next_review:
priority: should
time: 3
---

# Метрики и SLO: RED, USE, алерты

↑ [[BE 7.2 Observability — логи, метрики, трейсинг, OpenTelemetry|7.2 Observability: логи, метрики, трейсинг, OpenTelemetry]] · ← [[BE 7.2.6 Хранение и визуализация — ClickHouse, Grafana, Prometheus, Jaeger-Tempo|Предыдущая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: senior</span></div>
<!-- meta:end -->



> [!info] Зачем это на собесе
> Что считается «здоровьем» сервиса и когда будить дежурного.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

| Метод | Для чего | Метрики |
|---|---|---|
| RED | сервисы (запросы) | Rate — запросов/с; Errors — доля ошибок; Duration — задержка (p50/p95/p99) |
| USE | ресурсы (CPU, диск, пул) | Utilization, Saturation, Errors |
| Golden signals (Google) | обобщение | latency, traffic, errors, saturation |

**SLI** — измеряемый показатель («доля успешных запросов быстрее 300 мс»). **SLO** — цель («99,9% за 30 дней»). **SLA** — договорное обязательство. **Error budget** — допустимая доля отказов (100% − SLO = 0,1% ≈ 43 минуты в месяц).

| SLO | Допустимая недоступность в месяц |
|---|---|
| 99% | ~7,3 ч |
| 99,9% | ~43 мин |
| 99,99% | ~4,3 мин |

Алерты:

- Алерт на **симптомы для пользователя** (ошибки, задержка), а не на причины (CPU 80%).
- **Burn rate**: сколько бюджета сжигается: быстрое сгорание (14× за 1 час) — критично, медленное (2× за 6 часов) — тикет.
- Каждый алерт — действие, срочность и runbook. Алерты без действий убирайте (alert fatigue).

```yaml
- alert: HighErrorBudgetBurn
  expr: (sum(rate(http_requests_total{status=~"5.."}[1h])) / sum(rate(http_requests_total[1h]))) > 14 * 0.001
  for: 5m
  labels: { severity: page }
  annotations: { runbook: "https://wiki/runbooks/orders-5xx" }
```

## Нюансы и подводные камни

- Средняя задержка скрывает хвосты: используйте перцентили и гистограммы.
- Перцентили нельзя усреднять между инстансами — агрегируйте гистограммы.
- SLO должно опираться на опыт пользователя, а не на удобство измерения.
- Слишком жёсткое SLO замедляет разработку; слишком мягкое обесценивает надёжность.

## Практика

1. Определите SLI/SLO для критичного эндпоинта.
2. Настройте алерты по burn rate.
3. Посчитайте error budget за месяц и решите, можно ли выкатывать риск.

## Вопросы с ответами

> [!question]- Чем SLI, SLO и SLA отличаются?
> SLI — измерение, SLO — внутренняя цель, SLA — договорное обязательство с последствиями.

> [!question]- Почему алертить на симптомы, а не на причины?
> Симптомы отражают влияние на пользователя; причин много, и часть не влияет на сервис.

## Связанные темы

- [[N:3ea33104867981869027f9a72bdd9a33]]
- [[N:3ea33104867981d99cced09dcdfa95e9]]
