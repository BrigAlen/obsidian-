---
type: topic
domain: analytics
stage: 2
section: "2.3"
order: 3
status: todo
level: middle
tags: [domain/analytics, stage/2, track/shared, level/middle, priority/should, flag/todo]
skeleton: true
reviewed: 
next_review: 
priority_override: should
priority: should
time: 20
---

# Data lake, ClickHouse, Kafka: куда пишутся события

↑ [[AN 2.3 Хранилища данных и BI|2.3 Хранилища данных и BI]] · ← [[AN 2.3.2 DWH, ETL и ELT, витрины, звезда и снежинка|Предыдущая]] · → [[AN 2.3.4 BI-инструменты|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">≈20 мин по плану</span><span class="chip">Уровень: middle</span><span class="chip">тема не наполнена</span></div>
<!-- meta:end -->

> [!info] Зачем это аналитику и PM
> Отчётность строится не на боевой базе, а на хранилище и BI. Нужно понимать поток данных.

> [!todo] Скелет темы
> Текст ещё не написан. Раскройте пункты плана простым языком: определение, пример из жизни, картинка или схема, типичные ошибки. В конце добавьте вопросы с ответами и уберите `skeleton: true` из свойств.

## План темы
- [ ] события и потоки
- [ ] почему аналитика через очередь

## Связано с блоком Developer
- [[DB 3.1 ClickHouse|3.1 ClickHouse]]
- [[BE 8.4.9 Кейс — аналитика событий (Kafka + ClickHouse)|8.4.9 Кейс — аналитика событий (Kafka + ClickHouse)]]
- [[DB 6.1.5 Change Data Capture — Debezium, логическая репликация, PostgreSQL → Kafka → ClickHouse|6.1.5 Change Data Capture — Debezium, логическая репликация, PostgreSQL → Kafka → ClickHouse]]

## Практика
Описать путь данных от кнопки в приложении до графика в дашборде.

## Вопросы с ответами

_Добавить 3–5 вопросов с ответами (формат `> [!question]- Вопрос`)._
