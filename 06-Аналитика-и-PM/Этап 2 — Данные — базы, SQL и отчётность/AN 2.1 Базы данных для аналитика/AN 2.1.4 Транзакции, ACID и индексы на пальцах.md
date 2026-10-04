---
type: topic
domain: analytics
stage: 2
section: "2.1"
order: 4
status: todo
level: junior
tags: [domain/analytics, stage/2, track/shared, level/junior, priority/must, flag/todo]
skeleton: true
reviewed: 
next_review: 
priority_override: must
priority: must
time: 20
---

# Транзакции, ACID и индексы на пальцах

↑ [[AN 2.1 Базы данных для аналитика|2.1 Базы данных для аналитика]] · ← [[AN 2.1.3 Нормализация простыми словами, типы данных|Предыдущая]] · → [[AN 2.1.5 Как приложение ходит в БД — ORM, миграции|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">≈20 мин по плану</span><span class="chip">Уровень: junior</span><span class="chip">тема не наполнена</span></div>
<!-- meta:end -->

> [!info] Зачем это аналитику и PM
> Понимать, как устроены данные, чтобы ставить задачи на изменение модели и отчёты.

> [!todo] Скелет темы
> Текст ещё не написан. Раскройте пункты плана простым языком: определение, пример из жизни, картинка или схема, типичные ошибки. В конце добавьте вопросы с ответами и уберите `skeleton: true` из свойств.

## План темы
- [ ] что такое транзакция
- [ ] почему запрос тормозит
- [ ] зачем индексы

## Связано с блоком Developer
- [[DB 2.1.4 Транзакции и ACID|2.1.4 Транзакции и ACID]]
- [[DB 2.1.2 Индексы — B-tree, Hash, GIN, GiST, BRIN, составные, частичные, covering|2.1.2 Индексы — B-tree, Hash, GIN, GiST, BRIN, составные, частичные, covering]]

## Практика
Прочитать ER-диаграмму знакомой системы и описать связи.

## Вопросы с ответами

_Добавить 3–5 вопросов с ответами (формат `> [!question]- Вопрос`)._
