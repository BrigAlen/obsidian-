---
type: topic
domain: backend
stage: 1
section: "1.3"
order: 10
status: todo
level: junior
notion_id: 3ea33104867981339ec6f0b777d85f83
tags: [domain/backend, stage/1, level/junior, topic/equality, priority/must]
reviewed:
next_review:
priority: must
time: 6
---

# Equals, GetHashCode, сравнение объектов

↑ [[BE 1.3 C♯ — основы языка|1.3 C♯: основы языка]] · ← [[BE 1.3.9 Pattern matching и switch expressions|Предыдущая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~6 мин чтения</span><span class="chip">Уровень: junior</span></div>
<!-- meta:end -->















































> [!info] Зачем это на собесе
> контракт `Equals`/`GetHashCode` — любимый вопрос: «что будет, если переопределить Equals, но не GetHashCode». От этого зависит работа Dictionary, HashSet, LINQ `Distinct` и сравнений сущностей.

## Объяснение

### Виды равенства

- **Ссылочное** — один и тот же объект: `ReferenceEquals(a, b)`. По умолчанию для классов.
- **По значению** — одинаковые данные. По умолчанию для struct (через рефлексию, медленно), для record — сгенерировано компилятором.
- `==` для классов по умолчанию ссылочное, но может быть перегружено (`string`, `record`).

### Контракт Equals

Рефлексивность (`a.Equals(a)`), симметричность, транзитивность, согласованность (одинаковый результат при повторах), `a.Equals(null) == false`.

### Контракт GetHashCode

- Если `a.Equals(b)`, то `a.GetHashCode() == b.GetHashCode()` — **обязательно**.
- Обратное не требуется: одинаковый хэш ≠ равенство (коллизии допустимы).
- Хэш не должен меняться, пока объект лежит в хэш-коллекции.

### Почему это важно: как работает Dictionary

1. По `GetHashCode()` ключа вычисляется «корзина» (bucket).
2. Внутри корзины элементы сравниваются через `Equals`.
Если `Equals` переопределён, а `GetHashCode` нет — равные объекты попадут в разные корзины, и `dict.ContainsKey(equalKey)` вернёт **false**.

### Правильная реализация

```csharp
public sealed class Snils : IEquatable<Snils>
{
    public string Value { get; }
    public Snils(string value) => Value = Normalize(value);

    public bool Equals(Snils? other) => other is not null && Value == other.Value;
    public override bool Equals(object? obj) => obj is Snils s && Equals(s);
    public override int GetHashCode() => Value.GetHashCode();          // по тем же полям, что Equals
    public static bool operator ==(Snils? a, Snils? b) => Equals(a, b);
    public static bool operator !=(Snils? a, Snils? b) => !Equals(a, b);
}

// для нескольких полей
public override int GetHashCode() => HashCode.Combine(System, Code, Version);
```
Проще всего — `record`/`record struct`: всё генерирует компилятор.
```csharp
public sealed record CodingKey(string System, string Code, string? Version);  // ключ справочника терминологии
var cache = new Dictionary<CodingKey, Concept>();
```

### IEqualityComparer — равенство «снаружи»

Когда нельзя или не нужно менять тип:
```csharp
var byCode = new Dictionary<string, Concept>(StringComparer.OrdinalIgnoreCase);
var unique = patients.DistinctBy(p => p.Snils);        // .NET 6+
public sealed class PatientBySnilsComparer : IEqualityComparer<Patient>
{
    public bool Equals(Patient? x, Patient? y) => x?.Snils == y?.Snils;
    public int GetHashCode(Patient p) => p.Snils.GetHashCode();
}
```

### Сущности (Entity) vs Value Objects

- **Entity** — равенство по **идентификатору** (Id), данные могут меняться.
- **Value object** — равенство по **всем значениям**, иммутабелен (деньги, адрес, код справочника).

## Нюансы и подводные камни

- **Изменяемые поля в хэше:** положили объект в HashSet, изменили поле, участвующее в `GetHashCode`, — объект «потерялся» (Contains вернёт false).
- `GetHashCode` строки в .NET Core **рандомизирован между запусками процесса**: не сохраняйте его в БД и не используйте для шардирования. Для стабильного хэша — `XxHash64` или SHA.
- Переопределение `==` без `Equals` (и наоборот) приводит к непоследовательному поведению.
- EF Core сравнивает сущности по ключу через change tracker. Переопределённый `Equals` у сущностей может мешать, делайте это аккуратно.
- Struct без переопределения `Equals` сравнивается рефлексией и боксится — медленно в словарях.

## Тестирование

```csharp
[Fact]
public void Equal_objects_have_equal_hash_codes()
{
    var a = new CodingKey("icd10", "J06.9", null);
    var b = new CodingKey("icd10", "J06.9", null);
    a.Should().Be(b);
    a.GetHashCode().Should().Be(b.GetHashCode());
    new HashSet<CodingKey> { a }.Contains(b).Should().BeTrue();
}
```

## Вопросы с ответами

> [!question]- Что будет, если переопределить Equals, но не GetHashCode?
> Равные объекты будут иметь разные хэши, поэтому Dictionary, HashSet и Distinct перестанут их находить и считать одинаковыми. Компилятор выдаёт предупреждение.

> [!question]- Каков контракт GetHashCode?
> Равные по Equals объекты обязаны иметь равные хэши. Хэш стабилен, пока объект не изменён. Разные объекты могут иметь одинаковый хэш (коллизии).

> [!question]- Как работает Dictionary внутри?
> Хэш-таблица: GetHashCode ключа выбирает корзину, внутри корзины ключи сравниваются через Equals. Поиск в среднем O(1). При росте таблица перестраивается.

> [!question]- Чем равенство сущности отличается от равенства value object?
> Сущность равна другой, если совпадает идентификатор. Value object равен другому, если совпадают все значения. Value object обычно иммутабелен — удобно делать через record.

> [!question]- Можно ли сохранять string.GetHashCode() в БД?
> Нет. В .NET Core хэш строк рандомизирован для каждого процесса (защита от hash flooding) и меняется между запусками.

## Связанные темы

- Предыдущая: [[N:3ea331048679818988ebed24b809cb9a]] · Следующий раздел (ООП): [[N:3ea3310486798104b9bdfd08119606c4]]
- Коллекции: [[N:3ea331048679812fa686df688569debd]]
- Хэширование в задачах: [[N:3ea33104867981c79650f64aae90de85]]
- Records: [[N:3ea331048679810e866fff73c25c9cd8]]
- DDD: entity и value object: [[N:3ea33104867981fdacffc2220726e99c]]
- Сравнение в JS: [[N:3ea33104867981669b6bd6f060aa0c30]]
