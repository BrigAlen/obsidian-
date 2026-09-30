---
type: topic
domain: backend
stage: 7
section: "7.1"
order: 3
status: todo
level: senior
notion_id: 3ea33104867981fb8c07fdd4f935833b
tags: [domain/backend, stage/7, level/senior, topic/dotnet, topic/performance, topic/memory, priority/should]
reviewed:
next_review:
priority: should
time: 3
---

# Аллокации и зеро-аллокационный код

↑ [[BE 7.1 Производительность .NET и кэширование|7.1 Производительность .NET и кэширование]] · ← [[BE 7.1.2 BenchmarkDotNet и микробенчмарки|Предыдущая]] · → [[BE 7.1.4 Кэширование — IMemoryCache, IDistributedCache, HybridCache, output caching|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: senior</span></div>
<!-- meta:end -->













> [!info] Зачем это на собесе
> Про низкоуровневую производительность: `Span<T>`, пулы, `struct` и когда это оправдано.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

Каждая аллокация в куче нагружает GC. В горячих путях (парсеры, сериализация, middleware) снижают число аллокаций.

| Приём | Эффект |
|---|---|
| `Span<T>`/`ReadOnlySpan<T>`/`Memory<T>` | срезы без копирования массивов и подстрок |
| `stackalloc` | небольшие буферы на стеке |
| `ArrayPool<T>.Shared` | переиспользование больших массивов |
| `ObjectPool<T>`, `StringBuilder` из пула | переиспользование объектов |
| `struct`/`readonly struct`/`ref struct` | значения без кучи (осторожно с копированием) |
| `ValueTask` | без аллокации при синхронном завершении (см. [[N:3ea331048679815b938fd2f3f2a7c66d]]) |
| `string.Create`, интерполяция в `DefaultInterpolatedStringHandler` | меньше промежуточных строк |
| Избежание замыканий/боксинга/LINQ в горячих путях | нет скрытых аллокаций |
| `static` лямбды | нет захвата контекста |
| `FrozenDictionary`/`SearchValues` | быстрые неизменяемые структуры |

```csharp
// Разбор строки без Substring
static int SumCsv(ReadOnlySpan<char> line)
{
    int sum = 0;
    foreach (var range in line.Split(','))       // .NET 9: MemoryExtensions.Split
        sum += int.Parse(line[range]);
    return sum;
}

var buffer = ArrayPool<byte>.Shared.Rent(64 * 1024);
try { /* работа */ } finally { ArrayPool<byte>.Shared.Return(buffer); }
```

## Нюансы и подводные камни

- Оптимизация оправдана только по профилю: читаемость дороже.
- Массив из пула может быть больше запрошенного и не очищен.
- `Span<T>` нельзя хранить в поле класса и использовать в `async`.
- Возврат буфера в пул дважды или использование после возврата приводит к порче данных.
- Большие объекты (≥85 КБ) попадают в LOH и собираются только при gen2.

## Практика

1. Уберите аллокации в парсере строк через `Span` и сравните в BenchmarkDotNet.
2. Замените выделение буферов на `ArrayPool`.
3. Найдите скрытые аллокации через `dotnet-trace`/allocation profiler.

## Вопросы с ответами

> [!question]- Зачем Span\<T>?
> Позволяет работать со срезами памяти (массив, стек, нативная память) без копирования и аллокаций.

> [!question]- Когда ArrayPool оправдан?
> Для временных больших буферов в горячем пути, чтобы не нагружать LOH и GC.

## Связанные темы

- [[N:3ea33104867981419025f0bdbcb02acf]]
- [[N:3ea33104867981aead48c78238ef618a]]
