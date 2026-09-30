---
type: topic
domain: backend
stage: 7
section: "7.4"
order: 2
status: todo
level: senior
notion_id: 3ea3310486798151bdfce23ff2d8a287
tags: [domain/backend, stage/7, level/senior, topic/security, topic/injection, priority/should]
reviewed:
next_review:
priority: should
time: 3
---

# Инъекции: SQL, командные, LDAP, десериализация

↑ [[BE 7.4 Безопасность бэкенда|7.4 Безопасность бэкенда]] · ← [[BE 7.4.1 OWASP Top 10 для API|Предыдущая]] · → [[BE 7.4.3 Секреты и конфигурация — user-secrets, Vault, переменные окружения|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: senior</span></div>
<!-- meta:end -->











> [!info] Зачем это на собесе
> Инъекции — общий класс: данные пользователя интерпретируются как код.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

| Вид | Как возникает | Защита |
|---|---|---|
| SQL | конкатенация в запросе (см. [[N:3ea3310486798158868ffb2e607fee11]]) | параметры, ORM, белые списки для имён |
| Командные (OS) | `Process.Start("sh -c " + input)` | не вызывать shell, передавать аргументы массивом, allowlist |
| LDAP | подстановка в фильтр | экранирование, параметризация |
| NoSQL | JSON-операторы (`{ "$ne": null }`) | валидация типов, санитайзинг операторов |
| XML (XXE) | внешние сущности в XML | отключить DTD/внешние сущности (`DtdProcessing.Prohibit`) |
| Небезопасная десериализация | `BinaryFormatter`, полиморфный JSON с типами из входных данных | не десериализовать недоверенные данные в произвольные типы |
| Template injection | пользовательский шаблон | песочница, не исполнять шаблоны от пользователей |
| XSS | вывод HTML без экранирования | контекстное экранирование, CSP |
| Path traversal | `../` в путях | нормализация и проверка корня, генерация имён |
| Header/log injection | переводы строк в значениях | санитайзинг, структурные логи |

```csharp
// Плохо
Process.Start("bash", $"-c \"convert {fileName} out.png\"");
// Лучше: без shell, аргументы раздельно, имя из белого списка/GUID
var psi = new ProcessStartInfo("convert") { ArgumentList = { storedPath, "out.png" }, RedirectStandardError = true };

// System.Text.Json: типы задаются кодом, а не входными данными
var dto = JsonSerializer.Deserialize<OrderDto>(json);
```

Принцип: **валидация на входе + кодирование на выходе + минимум прав**.

## Нюансы и подводные камни

- `BinaryFormatter` удалён из .NET 9: не возвращайте его.
- Newtonsoft `TypeNameHandling.All` на недоверенных данных приводит к RCE.
- Регулярные выражения без таймаута дают ReDoS: `Regex` с `matchTimeout`.
- Проверка расширения файла ≠ проверка содержимого.
- Права процесса: запуск не от root, минимальные права на файлы и БД.

## Практика

1. Найдите в проекте вызовы `Process.Start` и небезопасные десериализаторы.
2. Защитите обработчик загрузки от path traversal.
3. Добавьте таймауты ко всем `Regex`.

## Вопросы с ответами

> [!question]- Почему опасна десериализация недоверенных данных?
> Десериализатор может создать произвольные объекты и вызвать код в их конструкторах/сеттерах, что приводит к RCE.

> [!question]- Как защититься от command injection?
> Не использовать shell, передавать аргументы списком, ограничить допустимые значения.

## Связанные темы

- [[N:3ea331048679819fb453ede68cd221d1]]
- [[N:3ea331048679819c9bb7c741225859ca]]
