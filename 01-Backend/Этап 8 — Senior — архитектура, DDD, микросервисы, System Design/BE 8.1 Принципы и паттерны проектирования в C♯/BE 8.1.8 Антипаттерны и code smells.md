---
type: topic
domain: backend
stage: 8
section: "8.1"
order: 8
status: todo
level: senior
notion_id: 3ea331048679815a8e67e0370114ed0c
tags: [domain/backend, stage/8, level/senior, topic/design, topic/antipatterns, topic/refactoring, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Антипаттерны и code smells

↑ [[BE 8.1 Принципы и паттерны проектирования в C♯|8.1 Принципы и паттерны проектирования в C♯]] · ← [[BE 8.1.7 Result pattern и обработка ошибок без исключений|Предыдущая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: senior</span></div>
<!-- meta:end -->















> [!info] Зачем это на собесе
> «Что вам не нравится в этом коде?» — типичное ревью на собеседовании.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

| Запах / антипаттерн | Признак | Лечение |
|---|---|---|
| God Object | класс делает всё | разделение по ответственностям |
| Long Method / Long Parameter List | метод на сотни строк, 8 параметров | Extract Method, Parameter Object |
| Anemic Domain Model | сущности — только данные, логика в сервисах | переносить поведение в домен |
| Feature Envy | метод чаще использует чужие данные | переместить метод |
| Shotgun Surgery | одно изменение → правки в десяти местах | собрать ответственность |
| Primitive Obsession | `string email`, `decimal money` везде | value objects |
| Magic numbers/strings | «42», «"paid"» | константы, enum |
| Copy-Paste | дублирование логики | вынести знание |
| Speculative Generality | абстракции «на будущее» | YAGNI |
| Service Locator | `provider.GetService` в коде | внедрение через конструктор |
| Singleton-абьюз, статические синглтоны | глобальное состояние | DI |
| Golden Hammer | один инструмент для всего | выбор по задаче |
| Leaky Abstraction | детали реализации в интерфейсе | пересмотр границ |
| Lava Flow | мёртвый код, «трогать страшно» | тесты и удаление |
| Async: `async void`, `.Result` | см. [[N:3ea33104867981489552e5d712d06076]] | `await` по цепочке |
| Catch-all: `catch (Exception) {}` | проглоченные ошибки | обработка/логирование/проброс |
| Chatty API / N+1 | множество мелких запросов | батчинг, проекции |
| Distributed Monolith | сервисы связаны и деплоятся вместе | пересмотр границ |
| Big Ball of Mud | нет структуры | модульность, ADR, границы |

Рефакторинг: небольшими безопасными шагами, под защитой тестов (Extract Method, Introduce Parameter Object, Replace Conditional with Polymorphism, Move Method).

## Нюансы и подводные камни

- Запах — это подсказка, а не приговор: оценивайте контекст и стоимость исправления.
- Рефакторинг без тестов — риск; начните с тестов на текущее поведение (characterization tests).
- «Переписать с нуля» редко оправдано: улучшайте постепенно (strangler fig).
- Не оптимизируйте эстетику вместо ценности для продукта.

## Практика

1. Проведите ревью модуля и составьте список запахов по приоритету.
2. Выделите value object для email/денег.
3. Уберите анемичность: перенесите правило из сервиса в сущность.

## Вопросы с ответами

> [!question]- Что такое анемичная доменная модель?
> Сущности содержат только данные, а вся логика находится в сервисах; теряется инкапсуляция и инварианты.

> [!question]- Как безопасно рефакторить legacy?
> Сначала покрыть поведение тестами, затем малыми шагами улучшать структуру.

## Связанные темы

- [[N:3ea33104867981a8bdded452aaea7f32]]
- [[N:3ea33104867981389cc2e7e356bb96a2]]
