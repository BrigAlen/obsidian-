---
type: topic
domain: backend
stage: 4
section: "4.3"
order: 1
status: todo
level: middle
notion_id: 3ea33104867981df8306e2ce8ba91fbb
tags: [domain/backend, stage/4, level/middle, topic/dotnet, topic/efcore, topic/testing, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# InMemory и SQLite провайдеры: подводные камни

↑ [[BE 4.3 Тестирование слоя данных|4.3 Тестирование слоя данных]] · → [[BE 4.3.2 Testcontainers для PostgreSQL и ClickHouse|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->





















> [!info] Зачем это на собесе
> «Как вы тестируете код с EF?» — ловушка: InMemory выглядит удобно, но обманывает.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

| Провайдер | Скорость | Транзакции | Ограничения и SQL | Вывод |
|---|---|---|---|---|
| `UseInMemoryDatabase` | максимальная | нет | не проверяет FK, unique, типы; не SQL | подходит только для простых демо |
| SQLite in-memory | высокая | да | диалект ≠ PostgreSQL, нет многих типов/функций | компромисс |
| Реальная БД (Testcontainers) | ниже | да | полное соответствие | рекомендуется для интеграционных тестов |

```csharp
// InMemory пропустит то, что в реальной БД упадёт
db.Orders.Add(new Order { CustomerId = Guid.NewGuid() });   // FK на несуществующего клиента
await db.SaveChangesAsync();                                 // ok в InMemory, ошибка в PostgreSQL
```

Практическое правило: логику unit-тестируйте без БД (fake-репозитории), запросы и схему — на настоящей СУБД.

## Нюансы и подводные камни

- InMemory не поддерживает `ExecuteUpdate`, сырой SQL, транзакции, `xmin`, JSON-колонки.
- В SQLite отличаются `DateTimeOffset`, `decimal`, регистр строк, сортировка.
- Тесты «зелёные» на InMemory могут скрывать баги трансляции LINQ.
- Команда EF Core прямо не рекомендует InMemory для тестирования.

## Практика

1. Найдите тесты на InMemory и проверьте на реальной БД, какие ошибки они скрывали.
2. Напишите тест, нарушающий FK/unique, и посмотрите различие.
3. Переведите тестовую фикстуру на Testcontainers.

## Вопросы с ответами

> [!question]- Почему не стоит использовать EF InMemory?
> Он не реализует поведение реальной БД (ограничения, транзакции, SQL), поэтому тесты дают ложную уверенность.

> [!question]- Когда допустим SQLite?
> Если продакшен использует SQLite или запросы простые; иначе диалектные отличия скрывают ошибки.

## Связанные темы

- [[N:3ea33104867981048155ce6c5ea28bef]]
- [[N:3ea33104867981bb9daceb1fff42831f]]
