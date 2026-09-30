---
type: topic
domain: backend
stage: 2
section: "2.2"
order: 6
status: todo
level: middle
notion_id: 3ea3310486798178b6c3ebe2c2759604
tags: [domain/backend, stage/2, level/middle, topic/pools, topic/memory, topic/performance, priority/must]
reviewed:
next_review:
priority: must
time: 6
---

# Пулы объектов: ArrayPool, ObjectPool, RecyclableMemoryStream

↑ [[BE 2.2 .NET runtime — CLR, память, GC|2.2 .NET runtime: CLR, память, GC]] · ← [[BE 2.2.5 Утечки памяти в .NET и как их искать|Предыдущая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~6 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->


> [!info] Зачем это на собесе
> Пулы — стандартный ответ на вопрос «как уменьшить аллокации и давление на GC». Ждут понимания, когда пул оправдан, как безопасно вернуть буфер, чем `ArrayPool` отличается от `ObjectPool` и зачем `RecyclableMemoryStream` вместо `MemoryStream`.

> [!note] Переписано
> В Notion эта страница содержала шаблонный текст без отношения к теме. Здесь — содержательная версия.

## Объяснение

### Зачем пулы
Частое создание больших или тяжёлых объектов нагружает GC (особенно LOH ≥ 85 000 байт). Пул **переиспользует** объекты: взял, использовал, вернул. Выигрыш — в меньшем числе аллокаций и сборок Gen 2.

### `ArrayPool<T>`
Пул массивов (`System.Buffers`). Общий пул: `ArrayPool<byte>.Shared`.
```csharp
var buffer = ArrayPool<byte>.Shared.Rent(64 * 1024);       // может вернуть массив БОЛЬШЕ запрошенного, содержимое не обнулено
try
{
    int read;
    while ((read = await stream.ReadAsync(buffer.AsMemory(0, buffer.Length), ct)) > 0)
        Process(buffer.AsSpan(0, read));                     // работаем только с реально прочитанной частью
}
finally
{
    ArrayPool<byte>.Shared.Return(buffer, clearArray: true);    // вернуть; clearArray, если внутри секреты
}
```
Правила:
- `Rent(n)` возвращает массив длиной **не меньше** n. Используйте размер, который вы сами знаете, а не `buffer.Length`.
- Возвращайте буфер **ровно один раз**, в `finally`. Повторный `Return` или использование после `Return` — use-after-free на уровне логики, данные будут испорчены другим потребителем.
- Не храните арендованный массив в долгоживущих объектах и не отдавайте наружу.
- Содержимое при аренде **не обнулено**: могут быть чужие данные.
- Для чувствительных данных — `clearArray: true`.

### `ObjectPool<T>`
`Microsoft.Extensions.ObjectPool` — пул произвольных объектов (StringBuilder, тяжёлые парсеры, буферы).
```csharp
services.AddSingleton<ObjectPoolProvider, DefaultObjectPoolProvider>();
services.AddSingleton(sp => sp.GetRequiredService<ObjectPoolProvider>().CreateStringBuilderPool());

public sealed class Formatter(ObjectPool<StringBuilder> pool)
{
    public string Build(IEnumerable<string> parts)
    {
        var sb = pool.Get();
        try { foreach (var p in parts) sb.Append(p).Append(';'); return sb.ToString(); }
        finally { pool.Return(sb); }         // политика Return сбрасывает состояние (Clear)
    }
}
```
Для своего типа реализуют `IPooledObjectPolicy<T>` (создание и сброс состояния). Объект перед возвратом нужно **сбросить**.

### `RecyclableMemoryStream`
Пакет `Microsoft.IO.RecyclableMemoryStream` — замена `MemoryStream`, использует пул блоков вместо одного большого массива.
```csharp
private static readonly RecyclableMemoryStreamManager Manager = new();

await using var ms = Manager.GetStream();
await report.ExportAsync(ms, ct);
ms.Position = 0;
await ms.CopyToAsync(response.Body, ct);
```
Плюсы против `MemoryStream`: не создаёт больших массивов в LOH при росте (нет удвоения буфера), меньше фрагментации, блоки переиспользуются. Полезно при генерации PDF/Excel/архивов в памяти.

### Другие приёмы уменьшения аллокаций
- `Span<T>`, `stackalloc` для небольших буферов (см. тему про Span).
- `StringBuilder` вместо конкатенаций, `string.Create`.
- `struct` для маленьких неизменяемых значений, `ValueTask` вместо `Task`.
- `System.IO.Pipelines` для сетевого ввода-вывода.
- Кэширование неизменяемых объектов, `static readonly` для повторно используемых значений.

## Нюансы и подводные камни
- Пул оправдан только для **крупных или очень частых** аллокаций. Для маленьких коротких объектов GC быстрее: пул добавляет накладные расходы и риск ошибок.
- Забыли вернуть объект — пул создаст новый, утечки нет (для `ArrayPool.Shared`), но выигрыш потерян.
- Вернули дважды или использовали после возврата — повреждение данных, трудноуловимые баги.
- Несброшенное состояние объекта из `ObjectPool` — утечка данных между запросами (безопасность!).
- Пул без ограничений держит память постоянно; у `ArrayPool.Shared` ограничение на размер и число массивов по корзинам.
- Проверяйте бенчмарком (`[MemoryDiagnoser]`): пул иногда не даёт выигрыша.

## Практика
- Переписать чтение файла с `new byte[81920]` на `ArrayPool` и сравнить `Allocated` в BenchmarkDotNet.
- Заменить `MemoryStream` в генерации отчёта на `RecyclableMemoryStream` и посмотреть размер LOH под нагрузкой.
- Добавить `ObjectPool<StringBuilder>` в сервис форматирования.

## Вопросы с ответами
> [!question]- Зачем нужны пулы объектов?
> Чтобы переиспользовать дорогие или большие объекты вместо постоянного создания. Это снижает число аллокаций и нагрузку на GC, особенно на LOH.

> [!question]- Какие правила безопасной работы с `ArrayPool`?
> Возвращать буфер ровно один раз в `finally`, не использовать после возврата, работать только с нужной длиной (массив может быть больше запрошенного), помнить, что содержимое не обнулено, и очищать секреты через `clearArray`.

> [!question]- Чем `RecyclableMemoryStream` лучше `MemoryStream`?
> `MemoryStream` растёт удвоением единого массива, что порождает большие временные массивы в LOH. `RecyclableMemoryStream` собирается из переиспользуемых блоков, поэтому нагрузка на GC и фрагментация меньше.

> [!question]- Когда пул не нужен?
> Для маленьких короткоживущих объектов: gen 0 сборки дешёвые, а пул усложняет код и может дать баги. Решение принимают по профилю и бенчмарку.

> [!question]- Чем `ArrayPool` отличается от `ObjectPool`?
> `ArrayPool<T>` арендует массивы нужного размера (с округлением вверх) и не сбрасывает содержимое. `ObjectPool<T>` управляет произвольными объектами через политику создания и сброса состояния.

## Связанные темы
- Предыдущая: [[N:3ea331048679814cbeece465f98c6820]] · Следующий раздел: [[N:3ea33104867981a9bca1efaa4f336770]]
- Span и Memory: [[N:3ea33104867981548d57ffd75d21ec61]]
- Сборщик мусора: [[N:3ea33104867981ff9626d62f5afa884d]]
- Аллокации и zero-alloc: [[N:3ea33104867981fb8c07fdd4f935833b]]
- Генерация документов и отчётов: [[N:3ea33104867981e6ababd167fde74e51]]
