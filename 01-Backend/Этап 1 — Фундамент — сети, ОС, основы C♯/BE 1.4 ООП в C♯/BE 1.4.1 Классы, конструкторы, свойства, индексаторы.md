---
type: topic
domain: backend
stage: 1
section: "1.4"
order: 1
status: todo
level: junior
notion_id: 3ea331048679817b85dbefe554670a2e
tags: [domain/backend, stage/1, level/junior, topic/oop, topic/classes, priority/must]
reviewed:
next_review:
priority: must
time: 8
---

# Классы, конструкторы, свойства, индексаторы

↑ [[BE 1.4 ООП в C♯|1.4 ООП в C♯]] · → [[BE 1.4.2 Модификаторы доступа, static, sealed, partial|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~8 мин чтения</span><span class="chip">Уровень: junior</span></div>
<!-- meta:end -->

























> [!info] Зачем это на собесе
> база ООП в C#. Спросят порядок инициализации, чем поле отличается от свойства, что такое init и required, primary constructors, статический конструктор.

## Объяснение

### Поля и свойства

- **Поле** — переменная класса. Обычно `private`.
- **Свойство** — пара методов `get`/`set` с синтаксисом поля: контроль доступа, валидация, вычисление, совместимость API.
```csharp
public class Patient
{
    private readonly List<Encounter> _encounters = [];      // поле, коллекция-выражение C# 12

    public Guid Id { get; } = Guid.NewGuid();               // только чтение, инициализатор
    public required string LastName { get; init; }          // обязательно при создании, дальше не меняется
    public string? Phone { get; private set; }              // снаружи только чтение
    public DateOnly BirthDate { get; init; }

    public int Age => DateTime.Today.Year - BirthDate.Year; // вычисляемое свойство (упрощённо)

    private string _email = "";
    public string Email
    {
        get => _email;
        set => _email = value.Contains('@') ? value.Trim() : throw new ArgumentException("Bad email");
    }

    public IReadOnlyList<Encounter> Encounters => _encounters;   // наружу read-only представление
    public void ChangePhone(string phone) => Phone = phone;      // изменение через метод с логикой
}

var p = new Patient { LastName = "Иванова", BirthDate = new(1990, 5, 1) };   // object initializer
// p.LastName = "X";   // ошибка: init
```
- `init` — присваивание только при создании (конструктор или инициализатор объекта).
- `required` (C# 11) — компилятор требует задать свойство при создании.
- C# 13 и 14: ключевое слово `field` в свойствах — доступ к авто-сгенерированному полю без явного объявления.

### Конструкторы

```csharp
public class ReportService
{
    private readonly IDataCollector _collector;
    private readonly ILogger<ReportService> _log;

    public ReportService(IDataCollector collector, ILogger<ReportService> log)
    {
        _collector = collector ?? throw new ArgumentNullException(nameof(collector));
        _log = log;
    }
}

// Primary constructor (C# 12) — параметры доступны во всём классе
public class ReportService(IDataCollector collector, ILogger<ReportService> log)
{
    public Task<byte[]> BuildAsync(Guid id) { log.LogInformation("Build {Id}", id); return collector.CollectAsync(id); }
}
```
У primary constructor параметры — это **захваченные переменные**, а не readonly-поля: их можно переприсвоить внутри класса. Для гарантии иммутабельности присвойте в `private readonly` поле.
- Цепочки: `: this(...)` — вызвать другой конструктор этого класса, `: base(...)` — конструктор базового.
- **Статический конструктор** — выполняется один раз перед первым использованием типа, потокобезопасно. Исключение в нём делает тип непригодным навсегда (`TypeInitializationException`).

### Порядок инициализации (при наследовании)

1. Инициализаторы полей производного класса.
2. Инициализаторы полей базового класса.
3. Конструктор базового класса.
4. Конструктор производного класса.
(Статические: static-поля и статический конструктор — до первого обращения к типу.)
> [!warning]
> Не вызывайте виртуальные методы в конструкторе: переопределение в наследнике выполнится, когда поля наследника ещё не проинициализированы его конструктором.

### Индексаторы

```csharp
public class ConceptMap
{
    private readonly Dictionary<string, string> _map = new(StringComparer.OrdinalIgnoreCase);
    public string? this[string sourceCode]
    {
        get => _map.GetValueOrDefault(sourceCode);
        set => _map[sourceCode] = value ?? throw new ArgumentNullException(nameof(value));
    }
}
var target = conceptMap["J06.9"];
```

## Нюансы и подводные камни

- Публичные изменяемые коллекции (`public List<T> Items { get; set; }`) ломают инкапсуляцию: снаружи можно очистить список. Отдавайте `IReadOnlyList<T>` и меняйте через методы.
- «Анемичная модель» — классы только из get/set без поведения. В CRUD-сервисах нормально, в сложном домене — антипаттерн.
- Тяжёлая логика в геттере свойства неожиданна для вызывающего (ожидается дешёвая операция). Используйте метод.
- Сущностям EF Core нужен конструктор, который EF может вызвать (можно private без параметров) и сеттеры (можно private).

## Тестирование

```csharp
[Fact]
public void Email_setter_validates_format()
{
    var p = new Patient { LastName = "A" };
    var act = () => p.Email = "bad";
    act.Should().Throw<ArgumentException>();
}
```

## Вопросы с ответами

> [!question]- Чем поле отличается от свойства?
> Поле — переменная для хранения данных. Свойство — методы доступа get и set с синтаксисом поля: можно валидировать, вычислять, ограничивать доступ и менять реализацию без изменения публичного API.

> [!question]- Чем init отличается от private set и readonly?
> init разрешает присваивание только при создании объекта, включая инициализатор объекта снаружи. private set — изменение в любом месте внутри класса. readonly-поле — только в объявлении и конструкторе.

> [!question]- Каков порядок инициализации при наследовании?
> Инициализаторы полей наследника, затем инициализаторы полей базового класса, конструктор базового класса и конструктор наследника.

> [!question]- Почему нельзя вызывать виртуальные методы в конструкторе?
> Вызовется переопределение из наследника, хотя его конструктор ещё не выполнился, и поля наследника не инициализированы. Возможны NullReferenceException и некорректное состояние.

> [!question]- Что такое primary constructor и в чём его нюанс?
> Параметры конструктора в объявлении класса, доступные во всём теле. Это захваченные параметры, а не readonly-поля: их можно изменить, и они не видны как свойства.

## Связанные темы

- Следующая: [[N:3ea331048679819c8d5af429a165212d]]
- Records, init, required: [[N:3ea331048679810e866fff73c25c9cd8]]
- DI и конструкторы: [[N:3ea33104867981d7abcbd600756a8323]]
- DDD: сущности и агрегаты: [[N:3ea33104867981fdacffc2220726e99c]]
- Классы в JS: [[N:3ea3310486798130b7fece73b6a6d5cb]]
