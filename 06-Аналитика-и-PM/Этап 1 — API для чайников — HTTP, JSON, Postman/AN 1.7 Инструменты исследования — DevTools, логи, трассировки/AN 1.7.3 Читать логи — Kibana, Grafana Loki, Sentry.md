---
type: topic
domain: analytics
stage: 1
section: "1.7"
order: 3
status: todo
level: middle
tags: [domain/analytics, stage/1, track/shared, level/middle, priority/should, flag/todo]
skeleton: true
reviewed: 
next_review: 
priority_override: should
priority: should
time: 20
---

# Читать логи: Kibana, Grafana Loki, Sentry

↑ [[AN 1.7 Инструменты исследования — DevTools, логи, трассировки|1.7 Инструменты исследования: DevTools, логи, трассировки]] · ← [[AN 1.7.2 Копирование запроса как cURL, HAR|Предыдущая]] · → [[AN 1.7.4 Трассировка запроса — trace id и корреляция|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">≈20 мин по плану</span><span class="chip">Уровень: middle</span><span class="chip">тема не наполнена</span></div>
<!-- meta:end -->

> [!info] Зачем это аналитику и PM
> Чтобы разобраться, что происходит между системами, аналитику нужны инструменты наблюдения.

> [!todo] Скелет темы
> Текст ещё не написан. Раскройте пункты плана простым языком: определение, пример из жизни, картинка или схема, типичные ошибки. В конце добавьте вопросы с ответами и уберите `skeleton: true` из свойств.

## План темы
- [ ] поиск по trace id и времени
- [ ] уровни логов
- [ ] как формулировать запрос в поддержку

## Связано с блоком Developer
- [[DO 7.4 Логи — ELK, Loki, централизованный сбор|7.4 Логи — ELK, Loki, централизованный сбор]]
- [[BE 7.2 Observability — логи, метрики, трейсинг, OpenTelemetry|7.2 Observability — логи, метрики, трейсинг, OpenTelemetry]]

## Практика
Найти в DevTools запрос кнопки «Сохранить» и повторить его в Postman.

## Вопросы с ответами

_Добавить 3–5 вопросов с ответами (формат `> [!question]- Вопрос`)._
