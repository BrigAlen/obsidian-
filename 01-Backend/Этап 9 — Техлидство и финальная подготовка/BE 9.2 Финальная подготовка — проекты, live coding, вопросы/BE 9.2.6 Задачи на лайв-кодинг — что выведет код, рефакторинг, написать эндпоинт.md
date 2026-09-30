---
type: topic
domain: backend
stage: 9
section: "9.2"
order: 6
status: todo
level: senior
notion_id: 3ea331048679810698b8cc309c958cbe
tags: [domain/backend, stage/9, level/senior, topic/interview, topic/live-coding, priority/must]
reviewed:
next_review:
priority: must
time: 6
---

# Задачи на лайв-кодинг: что выведет код, рефакторинг, написать эндпоинт

↑ [[BE 9.2 Финальная подготовка — проекты, live coding, вопросы|9.2 Финальная подготовка: проекты, live coding, вопросы]] · ← [[BE 9.2.5 Частые вопросы C♯ и .NET — блиц|Предыдущая]] · → [[BE 9.2.7 Вопросы работодателю и переговоры о зарплате|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~6 мин чтения</span><span class="chip">Уровень: senior</span></div>
<!-- meta:end -->

















> [!info] Зачем это на собесе
> Три типовых формата: «что выведет код», «найдите проблемы и отрефакторите», «напишите эндпоинт».

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## 1. Что выведет код

```csharp
// Задача 1
var list = new List<int> { 1, 2, 3 };
IEnumerable<int> q = list.Where(x => x > 1);
list.Add(4);
Console.WriteLine(string.Join(",", q));
```

> [!question]- Ответ
> `2,3,4` — LINQ отложенный: запрос выполняется при переборе, уже после добавления `4`.

```csharp
// Задача 2
var actions = new List<Action>();
for (int i = 0; i < 3; i++) actions.Add(() => Console.Write(i));
foreach (var a in actions) a();
```

> [!question]- Ответ
> `333` — замыкание захватывает переменную `i`, а не значение; после цикла `i = 3`. В `foreach` переменная цикла своя на итерацию, поэтому там был бы `012`.

```csharp
// Задача 3
async Task<int> Work() { await Task.Delay(100); return 1; }
var t = Work();
Console.WriteLine("A");
Console.WriteLine(await t);
Console.WriteLine("B");
```

> [!question]- Ответ
> `A`, `1`, `B`: задача стартует сразу, но `await t` ждёт результат.

```csharp
// Задача 4
string s = "a"; object o = s; s += "b";
Console.WriteLine(o == (object)"a");
```

> [!question]- Ответ
> `True`: `o` по-прежнему ссылается на исходную строку `"a"` (строки неизменяемы), а литералы интернируются.

## 2. Найдите проблемы и отрефакторите

```csharp
public class OrderService
{
    public List<Order> GetOrders(string customer)
    {
        var db = new SqlConnection("Server=...;Password=123");
        db.Open();
        var cmd = new SqlCommand("select * from orders where customer='" + customer + "'", db);
        var reader = cmd.ExecuteReader();
        var res = new List<Order>();
        while (reader.Read()) res.Add(new Order { Id = (int)reader[0] });
        return res;
    }
}
```

> [!question]- Проблемы и исправление
> - SQL-инъекция → параметры.
> - Строка подключения с паролем в коде → конфигурация и секреты.
> - Соединение, команда и reader не освобождаются → `using`/`await using`.
> - Синхронный ввод-вывод → `async` с `CancellationToken`.
> - `select *` и индексы колонок → явный список, маппинг по имени (Dapper).
> - Создание соединения внутри метода и `new` без DI → внедрять `NpgsqlDataSource`/репозиторий.
> - Нет пагинации → ограничение выборки.

```csharp
public async Task<List<OrderDto>> GetOrdersAsync(string customer, CancellationToken ct)
{
    await using var conn = await dataSource.OpenConnectionAsync(ct);
    return (await conn.QueryAsync<OrderDto>(
        new CommandDefinition("select id, number, total from orders where customer = @customer order by id limit 100", new { customer }, cancellationToken: ct))).ToList();
}
```

## 3. Напишите эндпоинт

**Условие**: `POST /orders` принимает `{ customerId, items: [{ sku, qty }] }`, создаёт заказ, возвращает 201 и `Location`; валидирует вход, не создаёт заказ дважды при повторе запроса.

```csharp
app.MapPost("/orders", async (CreateOrderRequest req, HttpContext http, IValidator<CreateOrderRequest> validator,
    IOrderService orders, CancellationToken ct) =>
{
    var v = await validator.ValidateAsync(req, ct);
    if (!v.IsValid) return Results.ValidationProblem(v.ToDictionary());

    var key = http.Request.Headers["Idempotency-Key"].ToString();
    if (string.IsNullOrEmpty(key)) return Results.Problem("Idempotency-Key required", statusCode: 400);

    var result = await orders.CreateAsync(req, key, ct);           // внутри: unique(key) + транзакция
    return result switch
    {
        { IsDuplicate: true } => Results.Ok(result.Order),         // повтор: тот же результат
        _ => Results.Created($"/orders/{result.Order.Id}", result.Order),
    };
}).RequireAuthorization();
```

Что обсудить: авторизация и проверка владельца, транзакция, идемпотентность, события (outbox), тесты, коды ошибок, лимиты.

## Связанные темы

- [[N:3ea33104867981f7bd44c649b907e683]]
- [[N:3ea331048679814abad3e2c4a2ab2ddf]]
