---
type: topic
domain: backend
stage: 1
section: "1.4"
order: 3
status: todo
level: junior
notion_id: 3ea33104867981e28367f6c926e84d93
tags: [domain/backend, stage/1, level/junior, topic/oop, topic/inheritance, priority/must]
reviewed:
next_review:
priority: must
time: 7
---

# Наследование, virtual, override, new

↑ [[BE 1.4 ООП в C♯|1.4 ООП в C♯]] · ← [[BE 1.4.2 Модификаторы доступа, static, sealed, partial|Предыдущая]] · → [[BE 1.4.4 Интерфейсы и абстрактные классы, default interface methods|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~7 мин чтения</span><span class="chip">Уровень: junior</span></div>
<!-- meta:end -->






























































> [!info] Зачем это на собесе
> классический блок собеса — `virtual`/`override` против `new`, что выведет код с приведением к базовому типу, абстрактные классы. Плюс в проекте есть иерархии (базовые storage-сервисы, отчёты).

## Объяснение

### Наследование

Класс может наследовать **один** базовый класс (множественного наследования классов нет) и реализовать много интерфейсов.
```csharp
public abstract class ReportBase
{
    protected ReportBase(string title) => Title = title;
    public string Title { get; }

    // Template Method: общий алгоритм, шаги переопределяются
    public byte[] Render(ReportData data)
    {
        Validate(data);
        var doc = BuildDocument(data);          // абстрактный шаг
        AddFooter(doc);                         // виртуальный шаг с реализацией по умолчанию
        return Export(doc);
    }

    protected abstract Document BuildDocument(ReportData data);   // обязаны реализовать
    protected virtual void AddFooter(Document doc) => doc.AddText($"Сформировано {DateTime.UtcNow:d}");
    protected virtual void Validate(ReportData data) => ArgumentNullException.ThrowIfNull(data);
    private byte[] Export(Document doc) => doc.ToPdf();
}

public sealed class DischargeSummaryReport() : ReportBase("Выписной эпикриз")
{
    protected override Document BuildDocument(ReportData data) => ...;
    protected override void AddFooter(Document doc)
    {
        base.AddFooter(doc);                                    // вызвать реализацию базового класса
        doc.AddText("Подпись врача: ________");
    }
}
```

### virtual / override / new — главная ловушка

```csharp
class Base    { public virtual string Who() => "Base";   public string Name() => "Base"; }
class Derived : Base
{
    public override string Who() => "Derived";           // переопределение (полиморфизм)
    public new string Name() => "Derived";               // сокрытие (НЕ полиморфизм)
}

Base b = new Derived();
b.Who();    // "Derived" — вызов по реальному типу объекта (виртуальная диспетчеризация)
b.Name();   // "Base"    — вызов по типу переменной (статическое связывание)
((Derived)b).Name();  // "Derived"
```
- `override` — метод выбирается по **типу объекта** в рантайме (через таблицу виртуальных методов, vtable).
- `new` — просто скрывает член базового класса. Выбор по **типу переменной** на этапе компиляции. Почти всегда признак проблемы в дизайне.
- Без `virtual` в базе переопределить нельзя. Методы в C# по умолчанию **невиртуальные** (в отличие от Java).

### abstract

- Абстрактный класс нельзя инстанцировать.
- Абстрактные члены не имеют реализации и **обязаны** быть переопределены в неабстрактном наследнике.
- Может содержать состояние (поля), конструкторы, реализованные методы.

### base

- `base.Method()` — вызвать реализацию родителя.
- `: base(args)` — вызвать конструктор родителя.

### Upcasting и downcasting

```csharp
ReportBase r = new DischargeSummaryReport();       // upcast — неявно и безопасно
if (r is DischargeSummaryReport ds) { ... }         // downcast — проверять через is
```

## Нюансы и подводные камни

- **Хрупкий базовый класс:** изменение базового класса ломает наследников неожиданным образом. Глубокие иерархии (больше 2–3 уровней) трудно поддерживать → композиция.
- Нарушение **LSP**: наследник, который бросает `NotSupportedException` на методы базового, — признак неправильной иерархии.
- `new` вместо `override` по ошибке (забыли `virtual`) — компилятор предупреждает CS0114. Не игнорируйте.
- Вызов `virtual` в конструкторе базового класса — опасно (см. тему про конструкторы).
- Для EF Core наследование сущностей маппится стратегиями TPH, TPT, TPC — у каждой свои компромиссы производительности.

## Тестирование

```csharp
[Fact]
public void Discharge_report_adds_signature_footer()
{
    var report = new DischargeSummaryReport();
    var pdf = report.Render(TestData.Discharge());
    PdfText(pdf).Should().Contain("Подпись врача");
}
```

## Вопросы с ответами

> [!question]- Чем override отличается от new?
> override переопределяет виртуальный метод: вызывается версия реального типа объекта, даже через ссылку базового типа. new скрывает метод: какой вызвать, решается по типу переменной на этапе компиляции.

> [!question]- Что выведет Base b = new Derived(); b.Method(), если в Derived метод помечен new?
> Версию из Base, потому что при сокрытии выбор идёт по типу переменной.

> [!question]- Чем абстрактный класс отличается от интерфейса?
> Абстрактный класс может содержать состояние, конструкторы и реализацию, а наследовать можно только один класс. Интерфейс описывает контракт (с default-методами без состояния), и реализовать можно много интерфейсов.

> [!question]- Почему в C# методы по умолчанию не виртуальные?
> Чтобы наследование было явным и осознанным (защита от хрупкого базового класса) и ради производительности: невиртуальный вызов дешевле и может быть заинлайнен.

> [!question]- Что такое паттерн Template Method?
> Базовый класс задаёт скелет алгоритма в невиртуальном методе, а наследники переопределяют отдельные шаги (абстрактные или виртуальные методы).

## Связанные темы

- Предыдущая: [[N:3ea331048679819c8d5af429a165212d]] · Следующая: [[N:3ea33104867981058510f56e083959bd]]
- Полиморфизм: [[N:3ea331048679813f8c82f603f6921990]]
- Композиция вместо наследования: [[N:3ea33104867981ccaa52e78aa5b0c0da]]
- SOLID (LSP): [[N:3ea331048679816f9f1cf6add2d19fc4]]
- Поведенческие паттерны: [[N:3ea33104867981f88d7cefc97436250e]]
- Прототипы в JS (сравнить): [[N:3ea33104867981c7890ad0da3eea40ca]]
