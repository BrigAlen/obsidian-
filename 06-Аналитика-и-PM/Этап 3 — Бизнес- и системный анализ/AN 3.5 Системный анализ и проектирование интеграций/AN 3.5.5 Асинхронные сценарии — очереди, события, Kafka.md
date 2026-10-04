---
type: topic
domain: analytics
stage: 3
section: "3.5"
order: 5
status: todo
level: middle
tags: [domain/analytics, stage/3, track/ba, level/middle, priority/must, flag/todo]
skeleton: true
reviewed: 
next_review: 
priority_override: must
priority: must
time: 20
---

# Асинхронные сценарии: очереди, события, Kafka

↑ [[AN 3.5 Системный анализ и проектирование интеграций|3.5 Системный анализ и проектирование интеграций]] · ← [[AN 3.5.4 Диаграммы последовательности для интеграций|Предыдущая]] · → [[AN 3.5.6 Идемпотентность, повторы, статусы и ошибки в ТЗ|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">≈20 мин по плану</span><span class="chip">Уровень: middle</span><span class="chip">тема не наполнена</span></div>
<!-- meta:end -->

> [!info] Зачем это аналитику и PM
> Для системного аналитика API и интеграции основная работа. Здесь связь с блоком разработки максимальна.

> [!todo] Скелет темы
> Текст ещё не написан. Раскройте пункты плана простым языком: определение, пример из жизни, картинка или схема, типичные ошибки. В конце добавьте вопросы с ответами и уберите `skeleton: true` из свойств.

## План темы
- [ ] как описывать события
- [ ] схемы сообщений
- [ ] порядок и дубли

## Связано с блоком Developer
- [[BE 5.4.2 Kafka — топики, партиции, offset, consumer groups|5.4.2 Kafka — топики, партиции, offset, consumer groups]]
- [[BE 5.4.5 RabbitMQ — exchanges, queues, routing, ack|5.4.5 RabbitMQ — exchanges, queues, routing, ack]]
- [[BE 5.4.8 Transactional Outbox и Inbox, идемпотентные консьюмеры|5.4.8 Transactional Outbox и Inbox, идемпотентные консьюмеры]]

## Практика
Написать спецификацию двух методов API с примерами и ошибками.

## Вопросы с ответами

_Добавить 3–5 вопросов с ответами (формат `> [!question]- Вопрос`)._
