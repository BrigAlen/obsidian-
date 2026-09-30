---
type: topic
domain: backend
stage: 2
section: "2.1"
order: 11
status: todo
level: middle
notion_id: 3ea331048679818ea358eaece94428c4
tags: [domain/backend, stage/2, level/middle, topic/serialization, topic/json, priority/must]
reviewed:
next_review:
priority: must
time: 7
---

# Сериализация: System.Text.Json и Newtonsoft

↑ [[BE 2.1 C♯ — продвинутый язык|2.1 C♯: продвинутый язык]] · ← [[BE 2.1.10 Source generators и Roslyn (как в analytics_generator)|Предыдущая]] · → [[BE 2.1.12 Что нового в C♯ 10–13 и .NET 8–9|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~7 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->












> [!info] Зачем это на собесе
> JSON — формат обмена почти в каждом API. Спросят, чем `System.Text.Json` отличается от Newtonsoft, как настроить имена и регистр, как сериализовать enum и даты, как работать с большими JSON потоково, что такое source generation и чем опасна десериализация типов из данных.

> [!note] Переписано
> В Notion эта страница содержала шаблонный текст без отношения к теме. Здесь — содержательная версия.

## Объяснение

### System.Text.Json (STJ) — встроенный
```csharp
var options = new JsonSerializerOptions(JsonSerializerDefaults.Web)   // camelCase, регистронезависимость при чтении
{
    WriteIndented = false,
    DefaultIgnoreCondition = JsonIgnoreCondition.WhenWritingNull,
    Converters = { new JsonStringEnumConverter() },                   // enum как строки
};

string json = JsonSerializer.Serialize(patient, options);
var back = JsonSerializer.Deserialize<PatientDto>(json, options);
```
Атрибуты:
```csharp
public record PatientDto(
    [property: JsonPropertyName("last_name")] string LastName,
    [property: JsonIgnore] string Secret,
    DateOnly BirthDate);

public class Item
{
    [JsonRequired] public string Code { get; set; } = "";                // обязательное поле (или C# required)
    [JsonPropertyOrder(1)] public int Qty { get; set; }
    [JsonConverter(typeof(JsonStringEnumConverter))] public Status Status { get; set; }
}
```
В ASP.NET Core настройки по умолчанию — `JsonSerializerDefaults.Web`. Свои: `builder.Services.ConfigureHttpJsonOptions(o => ...)` (Minimal API) или `AddJsonOptions` (MVC).

### Newtonsoft.Json (Json.NET)
Исторически самая популярная библиотека, богаче по возможностям: `JObject`/`JToken`, `[JsonProperty]`, `TypeNameHandling`, `NullValueHandling`, гибкие конвертеры, поддержка `ISerializable`, `IDictionary` со сложными ключами, `ReferenceLoopHandling` из коробки.
```csharp
var s = JsonConvert.SerializeObject(obj, new JsonSerializerSettings
{
    ContractResolver = new CamelCasePropertyNamesContractResolver(),
    NullValueHandling = NullValueHandling.Ignore,
});
```

### Сравнение
| | System.Text.Json | Newtonsoft.Json |
|---|---|---|
| Скорость и память | выше, меньше аллокаций (UTF-8, Span) | ниже |
| Возможности | строже, меньше «магии», быстро развивается | богаче, более терпим к формату |
| Регистр имён | точное сравнение (в Web-режиме нечувствителен) | нечувствителен |
| Циклические ссылки | `ReferenceHandler.Preserve` / `IgnoreCycles` | `ReferenceLoopHandling` |
| Динамика | `JsonNode`, `JsonDocument` | `JObject`, `dynamic` |
| Source generation / AOT | да | нет |
| Полиморфизм | `[JsonDerivedType]` (.NET 7+) | `TypeNameHandling` (рискованно) |

Выбор: STJ по умолчанию; Newtonsoft — когда нужна совместимость, сложные конвертеры или устаревшие сценарии (некоторые библиотеки всё ещё требуют).

### Даты, числа, enum
- `DateTime`/`DateTimeOffset` пишутся в ISO 8601. `DateOnly`/`TimeOnly` поддерживаются (.NET 7+).
- `decimal` сохраняет точность (число в JSON); для больших чисел в JS-клиенте возможна потеря точности (`long` > 2^53) → передавайте строкой (`JsonNumberHandling.WriteAsString`).
- Enum по умолчанию числом. Для устойчивого API — строки (`JsonStringEnumConverter`) и явные значения, чтобы порядок не менялся.

### Полиморфизм
```csharp
[JsonPolymorphic(TypeDiscriminatorPropertyName = "$type")]
[JsonDerivedType(typeof(Card), "card")]
[JsonDerivedType(typeof(Sbp), "sbp")]
public abstract record Payment(decimal Amount);
public sealed record Card(decimal Amount, string Last4) : Payment(Amount);
```

### Потоковая работа и низкий уровень
- `JsonSerializer.DeserializeAsyncEnumerable<T>(stream)` — читает массив элементов по одному без загрузки всего в память.
- `Utf8JsonReader` / `Utf8JsonWriter` — чтение и запись токенов без аллокаций.
- `JsonDocument` — только чтение с деревом DOM (требует `Dispose`), `JsonNode` — изменяемое дерево.
```csharp
await foreach (var item in JsonSerializer.DeserializeAsyncEnumerable<Item>(stream, options, ct)) { }
```

### Source generation
```csharp
[JsonSerializable(typeof(PatientDto))]
[JsonSerializable(typeof(List<PatientDto>))]
public partial class AppJsonContext : JsonSerializerContext;

var json = JsonSerializer.Serialize(patient, AppJsonContext.Default.PatientDto);
```
Быстрее старт и меньше памяти, совместимо с trimming и Native AOT, нет рефлексии в рантайме.

## Нюансы и подводные камни
- **Циклические ссылки** (`Parent.Children[0].Parent`): STJ бросает исключение; включите `ReferenceHandler.IgnoreCycles` или разрывайте цикл в DTO.
- **Регистр**: без `Web`-режима `lastName` не десериализуется в `LastName` (сравнение чувствительно).
- **Неизвестные поля** по умолчанию игнорируются; строгий режим — `UnmappedMemberHandling.Disallow`.
- **Null в не-nullable свойстве**: NRT не защищает; нужны `required` и валидация.
- **Приватные сеттеры/конструкторы**: STJ использует публичные сеттеры и конструктор с параметрами (для record удобно). Нужен `[JsonConstructor]` при нескольких конструкторах.
- **Безопасность:** `TypeNameHandling` у Newtonsoft в сочетании с недоверенным вводом — известная уязвимость (выполнение произвольных типов). Не включайте для внешних данных, используйте белые списки или `[JsonDerivedType]`.
- Большие JSON (сотни МБ) не читайте через `ReadAsStringAsync`: потоково и без буферизации всего.
- Смена сериализатора в API меняет формат (даты, enum, null) и ломает клиентов: фиксируйте контракт тестами.

## Практика
- Настроить `JsonSerializerOptions` для API: camelCase, enum строками, игнор null, `DateOnly`.
- Написать конвертер для типа-обёртки `Money`.
- Прочитать файл на 500 МБ через `DeserializeAsyncEnumerable` и замерить память.

## Вопросы с ответами
> [!question]- Чем System.Text.Json отличается от Newtonsoft.Json?
> STJ встроен, быстрее и экономичнее по памяти (работа с UTF-8 и Span), поддерживает source generation и AOT, но строже и изначально имел меньше возможностей. Newtonsoft богаче по функциям и терпимее к формату, но медленнее и без AOT.

> [!question]- Как настроить camelCase и enum как строки в ASP.NET Core?
> По умолчанию STJ в ASP.NET Core использует Web-настройки (camelCase). Enum строками: `Converters.Add(new JsonStringEnumConverter())` в `ConfigureHttpJsonOptions` или `AddJsonOptions`.

> [!question]- Как обработать огромный JSON без загрузки в память?
> Потоково: `DeserializeAsyncEnumerable<T>` для массивов или `Utf8JsonReader` для токенов; читать напрямую из `Stream`.

> [!question]- Что такое JSON source generation и зачем оно?
> Генерация сериализаторов во время компиляции через `JsonSerializerContext`: нет рефлексии в рантайме, быстрее старт, меньше памяти, совместимость с trimming и Native AOT.

> [!question]- Чем опасен TypeNameHandling в Newtonsoft?
> Тип для создания берётся из самих данных. Злоумышленник может указать опасный тип и получить выполнение кода при десериализации. Для недоверенных данных выключать или использовать белый список типов.

## Связанные темы
- Предыдущая: [[N:3ea331048679816ca016dc47df98b9ec]] · Следующая: [[N:3ea331048679811a82c2d9502acd1026]]
- Source generators: [[N:3ea331048679816ca016dc47df98b9ec]]
- Span и Utf8JsonReader: [[N:3ea33104867981548d57ffd75d21ec61]]
- Проектирование REST API: [[N:3ea331048679815bbaf8cf164556ce50]]
- JSON и fetch на фронтенде: [[N:3ea331048679814490f2caf93cdee339]]
