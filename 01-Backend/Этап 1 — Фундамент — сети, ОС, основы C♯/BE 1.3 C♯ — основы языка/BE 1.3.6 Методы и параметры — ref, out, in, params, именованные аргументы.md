---
type: topic
domain: backend
stage: 1
section: "1.3"
order: 6
status: todo
level: junior
notion_id: 3ea33104867981fab5abd8e186ca973d
tags: [domain/backend, stage/1, level/junior, topic/methods, priority/must]
reviewed:
next_review:
priority: must
time: 5
---

# Методы и параметры: ref, out, in, params, именованные аргументы

↑ [[BE 1.3 C♯ — основы языка|1.3 C♯: основы языка]] · ← [[BE 1.3.5 Nullable — значимые типы и nullable reference types|Предыдущая]] · → [[BE 1.3.7 Исключения — try, catch, finally, when, свои исключения|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~5 мин чтения</span><span class="chip">Уровень: junior</span></div>
<!-- meta:end -->
































> [!info] Зачем это на собесе
> модификаторы параметров `ref`, `out`, `in` и передача ссылочных типов по значению — классическая ловушка на собесе: «изменится ли объект или ссылка вызывающего».

## Объяснение

### Передача по значению (по умолчанию)

В метод передаётся **копия переменной**:
- value type — копия данных;
- reference type — копия **ссылки** (метод может изменить объект, но присвоение параметру новой ссылки не влияет на вызывающего).
```csharp
void Rename(Patient p)   { p.Name = "Новое"; }         // вызывающий УВИДИТ изменение объекта
void Replace(Patient p)  { p = new Patient(); }         // вызывающий НЕ увидит: заменили копию ссылки
void Inc(int x)          { x++; }                       // вызывающий НЕ увидит
```

### ref — передача по ссылке

Метод работает с **самой переменной** вызывающего. Переменная должна быть инициализирована.
```csharp
void Replace(ref Patient p) { p = new Patient { Name = "Новый" }; }  // вызывающий увидит новый объект
void Inc(ref int x) { x++; }
int n = 1; Inc(ref n);  // n == 2
```

### out — выходной параметр

Метод **обязан** присвоить значение. Переменная может быть не инициализирована. Паттерн Try\*:
```csharp
if (int.TryParse(text, out var number)) Use(number);
if (_cache.TryGetValue(id, out var patient)) return patient;

bool TryFindPatient(Guid id, [NotNullWhen(true)] out Patient? patient) { ... }
```

### in — только для чтения по ссылке

Передача без копирования, но изменять нельзя. Полезно для **больших struct**:
```csharp
double Distance(in Vector3 a, in Vector3 b) => (a - b).Length();
```
Для `readonly struct` защитных копий не будет. Для обычной struct вызов метода внутри `in` может создать скрытую копию.

### ref readonly и ref-возвраты (продвинуто)

```csharp
ref int FindSlot(int[] arr, int value) { ... return ref arr[i]; }   // вернуть ссылку на элемент
ref var slot = ref FindSlot(data, 5); slot = 10;                     // изменили элемент массива
```

### params

Переменное число аргументов:
```csharp
void Log(string template, params object[] args) { ... }
Log("{0} {1}", a, b);
// C# 13: params с коллекциями и Span без аллокации массива
void Sum(params ReadOnlySpan<int> values) { ... }
```

### Именованные и необязательные аргументы

```csharp
Task<Report> BuildAsync(Guid patientId, string format = "pdf", bool includeHistory = false, CancellationToken ct = default);

await BuildAsync(id, includeHistory: true, ct: token);   // пропускаем format, читаемо
```
Значения по умолчанию **вшиваются** в вызывающий код (как `const`) — меняя их в публичной библиотеке, пересобирайте потребителей.

### Локальные функции и expression-bodied

```csharp
decimal Total(IEnumerable<Item> items)
{
    return items.Sum(Price);
    static decimal Price(Item i) => i.Price * i.Qty;   // static — не захватывает внешние переменные
}
```

## Нюансы и подводные камни

- `ref`, `out` и `in` нельзя использовать в `async`-методах и итераторах (`yield`).
- Злоупотребление `out` усложняет API: для нескольких результатов лучше кортеж или record.
- Много необязательных bool-параметров — признак, что нужен объект настроек (options-объект).
- Изменение объекта, переданного в метод, — побочный эффект, неочевидный для вызывающего. Документируйте или избегайте.

## Тестирование

```csharp
[Fact]
public void Reassigning_parameter_does_not_affect_caller()
{
    var p = new Patient { Name = "A" };
    Replace(p);                    // без ref
    p.Name.Should().Be("A");
}
```

## Вопросы с ответами

> [!question]- Если передать объект класса в метод и изменить его свойство, увидит ли вызывающий изменение? А если присвоить параметру новый объект?
> Изменение свойства увидит: обе ссылки указывают на один объект. Присвоение нового объекта не увидит, потому что меняется копия ссылки. Чтобы заменить объект у вызывающего, нужен ref.

> [!question]- Чем ref отличается от out?
> ref требует инициализированную переменную, метод может читать и менять её. out может быть не инициализирован до вызова, но метод обязан присвоить значение до выхода.

> [!question]- Зачем модификатор in?
> Передать большую структуру по ссылке без копирования и с гарантией, что метод её не изменит.

> [!question]- В чём опасность значений по умолчанию у параметров в публичных библиотеках?
> Значения вшиваются в вызывающий код при компиляции. Изменение в библиотеке не подхватится без пересборки потребителей.

## Связанные темы

- Предыдущая: [[N:3ea331048679815fb1d0cd967cf4bffe]] · Следующая: [[N:3ea3310486798167aae3ed222aeb634e]]
- Value и reference типы: [[N:3ea33104867981948314ef0273ece7b5]]
- Span и ref struct: [[N:3ea33104867981548d57ffd75d21ec61]]
- Делегаты и лямбды: [[N:3ea33104867981c39639da77c07532df]]
- Передача объектов в JS: [[N:3ea33104867981228603ca7fc9b662f2]]
