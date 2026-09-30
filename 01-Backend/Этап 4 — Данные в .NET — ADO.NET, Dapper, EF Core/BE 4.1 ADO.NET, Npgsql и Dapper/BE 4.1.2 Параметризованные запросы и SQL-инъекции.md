---
type: topic
domain: backend
stage: 4
section: "4.1"
order: 2
status: todo
level: middle
notion_id: 3ea3310486798158868ffb2e607fee11
tags: [domain/backend, stage/4, level/middle, topic/dotnet, topic/data, topic/security, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Параметризованные запросы и SQL-инъекции

↑ [[BE 4.1 ADO.NET, Npgsql и Dapper|4.1 ADO.NET, Npgsql и Dapper]] · ← [[BE 4.1.1 ADO.NET и Npgsql — соединения, команды, пул соединений|Предыдущая]] · → [[BE 4.1.3 Dapper — микро-ORM, мультимаппинг, когда вместо EF|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->






























> [!info] Зачем это на собесе
> SQL-инъекция — обязательная тема безопасности. Нужно объяснить, почему параметры защищают, и где всё же можно ошибиться.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

Инъекция возникает, когда пользовательские данные подставляются в текст SQL как код.

```csharp
// Уязвимо: name = "x'; drop table users; --"
var sql = $"select * from users where name = '{name}'";

// Безопасно: значение передаётся отдельно от текста запроса
await using var cmd = new NpgsqlCommand("select * from users where name = @name", conn);
cmd.Parameters.AddWithValue("name", name);
```

С параметрами текст запроса и данные идут отдельно (protocol-level), поэтому БД никогда не трактует значение как SQL; план запроса при этом кэшируется.

| Ситуация | Как безопасно |
|---|---|
| Значения | параметры |
| Имена таблиц/колонок, `ORDER BY` | белый список допустимых значений |
| `LIKE` | параметр + экранирование `%`, `_` |
| Списки `IN` | `= ANY(@ids)` (PostgreSQL), Dapper раскрывает коллекции |
| EF Core | `FromSql($"...")` интерполяция = параметры, `FromSqlRaw` с конкатенацией — уязвим |

```csharp
// EF Core: безопасно, интерполяция превращается в параметры
db.Users.FromSql($"select * from users where name = {name}");
// Уязвимо
db.Users.FromSqlRaw("select * from users where name = '" + name + "'");
```

## Нюансы и подводные камни

- Динамический `ORDER BY` — частая дыра: сопоставляйте вход с enum/словарём.
- Хранимая процедура с динамическим SQL внутри тоже уязвима.
- Экранирование кавычек вручную ненадёжно.
- Минимальные права учётной записи БД снижают ущерб.
- Не показывайте текст SQL-ошибок пользователю.

## Практика

1. Найдите в проекте конкатенацию SQL и замените параметрами.
2. Реализуйте безопасную динамическую сортировку.
3. Проверьте эндпоинт инструментом sqlmap на тестовой БД.

## Вопросы с ответами

> [!question]- Почему параметры защищают от инъекций?
> Значение не становится частью текста запроса: СУБД разбирает SQL отдельно и подставляет данные как значения.

> [!question]- Как защитить динамический ORDER BY?
> Белый список колонок; имена нельзя параметризовать.

> [!question]- FromSql и FromSqlRaw — в чём разница?
> `FromSql` с интерполяцией параметризует значения, `FromSqlRaw` принимает строку как есть.

## Связанные темы

- [[N:3ea33104867981a48a67fbad9002cd95]]
- [[N:3ea33104867981008e07e7e6edb5cbc2]]
