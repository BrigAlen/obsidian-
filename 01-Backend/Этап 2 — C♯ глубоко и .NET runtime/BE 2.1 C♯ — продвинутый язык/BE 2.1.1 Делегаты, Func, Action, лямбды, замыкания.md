---
type: topic
domain: backend
stage: 2
section: "2.1"
order: 1
status: todo
level: middle
notion_id: 3ea33104867981c39639da77c07532df
tags: [domain/backend, stage/2, level/middle, topic/delegates, topic/lambdas, priority/must]
reviewed:
next_review:
priority: must
time: 6
---

# Делегаты, Func, Action, лямбды, замыкания

↑ [[BE 2.1 C♯ — продвинутый язык|2.1 C♯: продвинутый язык]] · → [[BE 2.1.2 События и паттерн Observer в C♯|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~6 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->







> [!info] Зачем это на собесе
> делегаты и лямбды — основа LINQ, событий, Minimal API, middleware, DI-фабрик и callback-ов. Классические вопросы: что такое делегат, multicast, замыкание в цикле, стоимость лямбд.

## Объяснение

### Делегат

Типобезопасный указатель на метод: объект, хранящий ссылку на метод (и на экземпляр для экземплярных методов).
```csharp
public delegate decimal PriceCalculator(Item item);          // свой тип делегата

decimal Base(Item i) => i.Price * i.Qty;
PriceCalculator calc = Base;
calc(item);
```

### Встроенные Func, Action, Predicate

```csharp
Func<Item, decimal> price = i => i.Price * i.Qty;           // принимает Item, возвращает decimal
Action<string> log = msg => Console.WriteLine(msg);         // ничего не возвращает
Predicate<Patient> isAdult = p => p.Age >= 18;              // bool (исторический тип; чаще Func<T, bool>)
Func<Task<Report>> factory = () => BuildReportAsync();
```
Свои типы делегатов нужны редко: для понятного имени или `ref`/`out`-параметров.

### Лямбды

```csharp
Func<int, int> square = x => x * x;
Func<int, int, int> add = (a, b) => a + b;
Func<Patient, bool> filter = static p => p.IsActive;          // static — запрет захвата переменных, нет аллокации
var parse = (string s) => int.Parse(s);                        // естественный тип лямбды (C# 10) → Func<string,int>
var withDefault = (int x = 10) => x * 2;                       // параметры по умолчанию (C# 12)

// Minimal API — лямбда-обработчик
app.MapGet("/patients/{id:guid}", async (Guid id, IPatientService svc, CancellationToken ct) =>
    await svc.FindAsync(id, ct) is { } p ? Results.Ok(p) : Results.NotFound());
```

### Замыкания

Лямбда может **захватывать** внешние переменные. Компилятор создаёт класс (display class), переменная становится его полем, и захватывается **переменная, а не значение**.
```csharp
int threshold = 18;
Func<Patient, bool> isAdult = p => p.Age >= threshold;
threshold = 21;                 // лямбда увидит 21: захвачена переменная

// классическая задача
var actions = new List<Action>();
for (int i = 0; i < 3; i++) actions.Add(() => Console.Write(i));
actions.ForEach(a => a());      // 333 — одна переменная i на весь цикл for

foreach (var x in new[] { 0, 1, 2 }) actions.Add(() => Console.Write(x));
// 012 — с C# 5 в foreach своя переменная на каждую итерацию
```
Исправление для `for`: скопировать в локальную переменную внутри тела (`var copy = i;`).

### Multicast-делегаты

Делегат хранит **список вызовов**: `+=` добавляет метод, `-=` удаляет.
```csharp
Action notify = () => Console.WriteLine("SMS");
notify += () => Console.WriteLine("Email");
notify();                  // вызовет оба по порядку
```
- Для `Func<T>` возвращается результат **последнего** метода.
- Исключение в одном обработчике прерывает вызов остальных.
- На этом построены события (`event`).

### Делегаты в DI и конфигурации

```csharp
services.AddScoped<IReportExporter>(sp => sp.GetRequiredService<IOptions<ReportOptions>>().Value.Format == "xlsx"
    ? new ExcelExporter() : new PdfExporter());                  // фабрика — Func<IServiceProvider, T>
services.Configure<MinioOptions>(o => o.Endpoint = "minio:9000"); // Action<TOptions>
app.Use(async (ctx, next) => { /* middleware */ await next(ctx); });
```

## Нюансы и подводные камни

- **Аллокации:** лямбда с захватом создаёт объект замыкания и делегат при каждом выполнении выражения. В горячем коде используйте `static`-лямбды или передачу состояния параметром (`TryAdd(key, static (k, arg) => ..., arg)`).
- Захват `this` в лямбде продлевает жизнь объекта: утечки при подписке долгоживущего источника на короткоживущий объект.
- Захват scoped-сервиса (DbContext) в лямбде, которая выполнится позже в другом потоке или scope, — `ObjectDisposedException`.
- `Func<T, bool>` в EF Core вместо `Expression<Func<T, bool>>` ведёт к загрузке таблицы в память (лямбда не транслируется в SQL). Подробнее в теме про LINQ.

## Тестирование

```csharp
[Fact]
public void Closure_captures_variable_not_value()
{
    var threshold = 18;
    Func<int, bool> isAdult = age => age >= threshold;
    threshold = 21;
    isAdult(20).Should().BeFalse();
}
```

## Вопросы с ответами

> [!question]- Что такое делегат?
> Типобезопасная ссылка на метод (и объект, если метод экземплярный). Позволяет передавать поведение как значение: callback-и, события, LINQ.

> [!question]- Чем Func отличается от Action?
> Func возвращает значение (последний параметр типа — результат). Action ничего не возвращает.

> [!question]- Что выведет цикл for, добавляющий лямбды с захватом i, и почему?
> Все лямбды выведут последнее значение (3), потому что захватывается одна переменная i, а не её значения. В foreach с C# 5 у каждой итерации своя переменная.

> [!question]- Что такое multicast-делегат и что вернёт Func при нескольких подписчиках?
> Делегат со списком вызовов. Вызываются все методы по порядку, а возвращается результат последнего.

> [!question]- Как лямбды влияют на производительность?
> Лямбды с захватом аллоцируют объект замыкания и делегат. Без захвата делегат кэшируется компилятором. static-лямбды гарантируют отсутствие захвата.

## Связанные темы

- Следующая: [[N:3ea33104867981d5ae6bf41415020435]]
- LINQ и Expression: [[N:3ea33104867981dc98c9f760e86a24d5]]
- Middleware: [[N:3ea33104867981d5a91edcf41b2ae95a]]
- Замыкания в JS: [[N:3ea3310486798116b0c9e2e1ab363feb]]
- Утечки памяти в .NET: [[N:3ea331048679814cbeece465f98c6820]]
