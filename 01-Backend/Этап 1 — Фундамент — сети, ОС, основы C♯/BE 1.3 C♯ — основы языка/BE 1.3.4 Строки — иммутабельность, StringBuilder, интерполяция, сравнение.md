---
type: topic
domain: backend
stage: 1
section: "1.3"
order: 4
status: todo
level: junior
notion_id: 3ea33104867981278c7bd1c2c8906499
tags: [domain/backend, stage/1, level/junior, topic/strings, priority/must]
reviewed:
next_review:
priority: must
time: 5
---

# Строки: иммутабельность, StringBuilder, интерполяция, сравнение

↑ [[BE 1.3 C♯ — основы языка|1.3 C♯: основы языка]] · ← [[BE 1.3.3 Переменные, var, const и readonly, преобразования типов|Предыдущая]] · → [[BE 1.3.5 Nullable — значимые типы и nullable reference types|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~5 мин чтения</span><span class="chip">Уровень: junior</span></div>
<!-- meta:end -->





















































> [!info] Зачем это на собесе
> строки везде: логи, SQL, JSON, отчёты. Вопросы: почему string иммутабельна, когда StringBuilder, что такое интернирование, как правильно сравнивать строки.

## Объяснение

### Иммутабельность

`string` — ссылочный тип, но **неизменяемый**: любая «модификация» создаёт новую строку.
```csharp
var s = "hello";
var upper = s.ToUpper();   // новая строка, s не изменилась
s += " world";             // новая строка, старая станет мусором
```
Плюсы: потокобезопасность, безопасные ключи словарей, возможность интернирования. Минус: конкатенация в цикле создаёт много мусора.

### StringBuilder

```csharp
// плохо: O(n²) копирований, тысячи временных строк
string csv = "";
foreach (var r in rows) csv += $"{r.Id};{r.Name}\n";

// хорошо: изменяемый буфер
var sb = new StringBuilder(capacity: rows.Count * 32);
foreach (var r in rows) sb.Append(r.Id).Append(';').AppendLine(r.Name);
var result = sb.ToString();
```
Правило: для нескольких конкатенаций хватает `+` или интерполяции (компилятор оптимизирует), в циклах — `StringBuilder` или `string.Join`.

### Интерполяция

```csharp
var msg = $"Пациент {patient.Name}, возраст {age}, сумма {total:N2}";
var raw = $"""
    SELECT * FROM "Patients" WHERE "Id" = '{id}'   -- raw string literal, кавычки без экранирования
    """;
var path = @"C:\logs\app.log";                       // verbatim: \ без экранирования
```
С .NET 6 интерполяция использует `DefaultInterpolatedStringHandler` — без лишних аллокаций. Для логирования **не** используйте интерполяцию, используйте шаблоны (`_log.LogInformation("Patient {PatientId} loaded", id)`) — структурированные логи и нет затрат, если уровень выключен.
> [!warning]
> Никогда не подставляйте значения в SQL интерполяцией строк — SQL-инъекция. Только параметры. (Исключение — `FromSqlInterpolated` в EF Core, который сам превращает интерполяцию в параметры.)

### Сравнение строк

```csharp
string.Equals(a, b, StringComparison.Ordinal)            // побайтово, быстро — для кодов, ключей, путей
string.Equals(a, b, StringComparison.OrdinalIgnoreCase)  // без учёта регистра, для технических значений
string.Equals(a, b, StringComparison.CurrentCulture)     // лингвистически — для отображения и сортировки
a == b                                                    // Ordinal, с учётом регистра
"ё".Equals("е", StringComparison.CurrentCulture)         // зависит от культуры
var dict = new Dictionary<string, int>(StringComparer.OrdinalIgnoreCase);
```
`ToLower()` для сравнения — лишняя аллокация и ловушки культур (турецкая i). Используйте `StringComparison`.

### Интернирование

Литералы одинакового содержания в сборке указывают на один объект (пул строк). `string.Intern(s)` — поместить в пул вручную (редко нужно). Поэтому `(object)"abc" == (object)"abc"` обычно `true`, а для строк, собранных в рантайме, — `false`.

### Полезные API

```csharp
string.IsNullOrWhiteSpace(s)
s.Split(';', StringSplitOptions.RemoveEmptyEntries | StringSplitOptions.TrimEntries)
string.Join(", ", names)
s.Contains("abc", StringComparison.OrdinalIgnoreCase)
s.AsSpan().Slice(0, 5)            // подстрока без аллокации
string.Create(len, state, (span, st) => { /* заполнить */ })
```

## Нюансы и подводные камни

- `string.Empty` и `""` — одно и то же (интернированный литерал). Разница только стилистическая.
- Строки длиннее ~42 500 символов (85 000 байт) попадают в Large Object Heap.
- `Substring` создаёт новую строку. Для парсинга без аллокаций — `ReadOnlySpan<char>`.
- `Split` на больших текстах аллоцирует массив и строки. Для CSV — специализированные парсеры (CsvHelper) или Span.
- Сравнение пароля или токена через `==` уязвимо к timing-атакам → `CryptographicOperations.FixedTimeEquals`.

## Тестирование

```csharp
[Theory]
[InlineData("Иванов", "иванов", true)]
[InlineData("ABC", "abd", false)]
public void Compares_ignoring_case(string a, string b, bool expected) =>
    string.Equals(a, b, StringComparison.OrdinalIgnoreCase).Should().Be(expected);
```

## Вопросы с ответами

> [!question]- Почему string иммутабельна и что это даёт?
> Любое изменение создаёт новую строку. Это даёт потокобезопасность, безопасное использование в качестве ключей и в хэшах, интернирование и защиту от случайной модификации.

> [!question]- Когда использовать StringBuilder?
> При многократной конкатенации, особенно в циклах. Для нескольких склеек хватает + или интерполяции.

> [!question]- Как правильно сравнивать строки?
> Явно указывать StringComparison: Ordinal или OrdinalIgnoreCase для технических значений, CurrentCulture — для текста, который видит пользователь. Не использовать ToLower для сравнения.

> [!question]- Что такое интернирование строк?
> Хранение одного экземпляра для одинаковых строковых литералов в пуле. Литералы с одинаковым текстом ссылаются на один объект.

> [!question]- Почему в логах не стоит использовать интерполяцию?
> Шаблоны сохраняют параметры как отдельные поля (структурированный лог, поиск по PatientId) и не форматируют строку, если уровень лога выключен.

## Связанные темы

- Предыдущая: [[N:3ea331048679812d8d6ccc547b012764]] · Следующая: [[N:3ea331048679815fb1d0cd967cf4bffe]]
- Span и Memory: [[N:3ea33104867981548d57ffd75d21ec61]]
- Параметризованные запросы: [[N:3ea3310486798158868ffb2e607fee11]]
- Структурные логи: [[N:3ea33104867981edac43cf84838e178a]]
- Кодировки: [[N:3ea3310486798180a101f27fb02bd5ef]]
- Строки в JS: [[N:3ea33104867981188cebc5c86e255835]]
