---
type: topic
domain: backend
stage: 1
section: "1.4"
order: 4
status: todo
level: junior
notion_id: 3ea33104867981058510f56e083959bd
tags: [domain/backend, stage/1, level/junior, topic/oop, topic/interfaces, priority/must]
reviewed:
next_review:
priority: must
time: 5
---

# Интерфейсы и абстрактные классы, default interface methods

↑ [[BE 1.4 ООП в C♯|1.4 ООП в C♯]] · ← [[BE 1.4.3 Наследование, virtual, override, new|Предыдущая]] · → [[BE 1.4.5 Полиморфизм и инкапсуляция на практике|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~5 мин чтения</span><span class="chip">Уровень: junior</span></div>
<!-- meta:end -->









> [!info] Зачем это на собесе
> интерфейсы — основа DI, тестируемости и слабой связанности. Вопрос «интерфейс или абстрактный класс» гарантирован. В проекте: `ISagaContextAccessor`, `ISagaFinalizer`, сервисы терминологии с реализациями `grpc` и `pg`.

## Объяснение

### Интерфейс — контракт

Описывает, **что** умеет тип, без того **как**. Класс или struct может реализовать много интерфейсов.
```csharp
public interface ITerminologyService
{
    Task<Concept?> LookupAsync(string system, string code, CancellationToken ct);
    Task<IReadOnlyList<Concept>> ExpandAsync(string valueSetUrl, CancellationToken ct);
}

// две реализации одного контракта (как в проекте: services_terminology_implementation_grpc / _pg)
public sealed class PgTerminologyService(TerminologyDbContext db) : ITerminologyService { ... }
public sealed class GrpcTerminologyService(Terminology.TerminologyClient client) : ITerminologyService { ... }

// потребитель зависит от абстракции — реализацию выбирает DI
public sealed class DiagnosisValidator(ITerminologyService terminology) { ... }
```

### Default interface methods (C# 8)

Интерфейс может содержать реализацию по умолчанию — чтобы добавить метод, не ломая существующие реализации.
```csharp
public interface IReport
{
    string Title { get; }
    byte[] Render(ReportData data);
    string FileName => $"{Title}_{DateTime.UtcNow:yyyyMMdd}.pdf";   // реализация по умолчанию
}
```
Нюанс: default-метод доступен только через ссылку типа интерфейса, не через класс.
Ещё в интерфейсах можно: статические члены, `static abstract` (generic math, C# 11), приватные методы-хелперы.

### Явная реализация интерфейса

```csharp
public class AuditLog : IDisposable, IAsyncDisposable
{
    void IDisposable.Dispose() { ... }          // доступно только через IDisposable
    public ValueTask DisposeAsync() { ... }
}
```
Для разрешения конфликта одинаковых сигнатур из разных интерфейсов или чтобы скрыть член из публичного API класса.

### Интерфейс vs абстрактный класс

- **Множественность:** интерфейсов — много, базовый класс — один.
- **Состояние:** интерфейс — без полей экземпляра, абстрактный класс — может хранить состояние и иметь конструктор.
- **Назначение:** интерфейс — «умеет делать» (роль, контракт между модулями), абстрактный класс — «является» + общая реализация (шаблон алгоритма).
- **Эволюция:** добавить член в интерфейс без default-реализации ломает все реализации, в абстрактный класс — можно с виртуальной реализацией.
- **Struct:** может реализовать интерфейс, но не наследовать класс.
Практика: публичные контракты сервисов — интерфейсы. Абстрактный базовый класс — когда много общей реализации (Template Method), и часто вместе: `IReport` + `ReportBase : IReport`.

### Маркерные и ролевые интерфейсы

- Маркерный (пустой) интерфейс — лучше заменить атрибутом.
- **Interface Segregation:** много мелких ролевых интерфейсов лучше одного «толстого» (`IReadRepository` и `IWriteRepository`).

## Нюансы и подводные камни

- «Интерфейс на каждый класс» (`IPatientService` с единственной реализацией и без тестов) — церемония. Интерфейс оправдан, когда есть несколько реализаций, граница модуля или нужна подмена в тестах.
- Приведение struct к интерфейсу вызывает boxing. В generic-коде используйте ограничения `where T : IFoo` — без боксинга.
- Default interface methods — не замена базовых классов, у них нет состояния.
- Интерфейс, который протекает деталями реализации (`IUserRepository.GetDbContext()`), теряет смысл абстракции.

## Тестирование

Интерфейсы позволяют подменять зависимости:
```csharp
[Fact]
public async Task Validator_rejects_unknown_code()
{
    var terminology = Substitute.For<ITerminologyService>();
    terminology.LookupAsync("icd10", "XXX", Arg.Any<CancellationToken>()).Returns((Concept?)null);
    var sut = new DiagnosisValidator(terminology);
    (await sut.IsValidAsync("icd10", "XXX", default)).Should().BeFalse();
}
```

## Вопросы с ответами

> [!question]- Когда использовать интерфейс, а когда абстрактный класс?
> Интерфейс — для контракта или роли, когда нужны несколько независимых реализаций, множественная реализация и подмена в тестах. Абстрактный класс — когда у наследников много общей реализации и состояния (Template Method). Часто сочетают.

> [!question]- Что такое default interface methods и зачем они?
> Реализация метода прямо в интерфейсе (C# 8+). Позволяет развивать интерфейс, не ломая существующие реализации. Доступны через ссылку на интерфейс.

> [!question]- Что такое явная реализация интерфейса?
> Реализация члена с указанием имени интерфейса (void IFoo.Bar()). Член доступен только через ссылку на интерфейс. Нужна при конфликте сигнатур или чтобы скрыть член из API класса.

> [!question]- Зачем интерфейсы для DI?
> Потребитель зависит от абстракции, а не от конкретного класса. Реализацию можно заменить (другая БД, gRPC-клиент, мок в тестах) без изменения потребителя — принцип инверсии зависимостей.

## Связанные темы

- Предыдущая: [[N:3ea33104867981e28367f6c926e84d93]] · Следующая: [[N:3ea331048679813f8c82f603f6921990]]
- DI и IoC: [[N:3ea33104867981d7abcbd600756a8323]]
- SOLID (ISP, DIP): [[N:3ea331048679816f9f1cf6add2d19fc4]]
- Moq и NSubstitute: [[N:3ea33104867981b18627d30f782b4713]]
- Generics и static abstract: [[N:3ea33104867981d085d7ec58153f8c7b]]
- Interface и type в TS: [[N:3ea33104867981348550f303d11f5b03]]
