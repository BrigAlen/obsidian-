---
type: topic
domain: backend
stage: 7
section: "7.1"
order: 2
status: todo
level: senior
notion_id: 3ea33104867981419025f0bdbcb02acf
tags: [domain/backend, stage/7, level/senior, topic/dotnet, topic/performance, topic/benchmark, priority/should]
reviewed:
next_review:
priority: should
time: 3
---

# BenchmarkDotNet и микробенчмарки

↑ [[BE 7.1 Производительность .NET и кэширование|7.1 Производительность .NET и кэширование]] · ← [[BE 7.1.1 Профилирование — dotnet-counters, dotnet-trace, dotnet-dump, PerfView|Предыдущая]] · → [[BE 7.1.3 Аллокации и зеро-аллокационный код|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: senior</span></div>
<!-- meta:end -->



































> [!info] Зачем это на собесе
> Как доказывать, что оптимизация работает; типичные ошибки бенчмарков.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

BenchmarkDotNet запускает код в изолированном процессе, прогревает JIT, делает много итераций и считает статистику.

```csharp
[MemoryDiagnoser]
[SimpleJob(RuntimeMoniker.Net90)]
public class ConcatBench
{
    private readonly string[] _parts = Enumerable.Range(0, 100).Select(i => i.ToString()).ToArray();

    [Benchmark(Baseline = true)]
    public string Plus() { var s = ""; foreach (var p in _parts) s += p; return s; }

    [Benchmark]
    public string Builder() { var sb = new StringBuilder(); foreach (var p in _parts) sb.Append(p); return sb.ToString(); }

    [Benchmark]
    public string Join() => string.Concat(_parts);
}

BenchmarkRunner.Run<ConcatBench>();   // dotnet run -c Release
```

Результат: среднее время, ошибка, StdDev, отношение к baseline, `Gen0/Gen1/Gen2` и `Allocated`.

## Нюансы и подводные камни

- Только Release без отладчика.
- JIT может удалить код без побочных эффектов (dead code elimination): возвращайте результат.
- Параметризуйте размеры (`[Params]`) — оптимизация может ломаться на других объёмах.
- Микробенчмарк не заменяет измерение в реальной системе: сеть, БД и GC ведут себя иначе.
- Стабильность: закройте фоновые процессы, не сравнивайте между машинами.
- Тиеринг JIT (`TieredPGO`) влияет на результаты: используйте warmup, как делает BDN.

## Практика

1. Сравните `string +`, `StringBuilder`, `string.Concat` с `MemoryDiagnoser`.
2. Сравните `foreach` по `List<T>` и по `IEnumerable<T>`.
3. Встройте бенчмарк в отдельный проект и храните результаты в репозитории.

## Вопросы с ответами

> [!question]- Почему нельзя измерять через Stopwatch в цикле?
> Не учитывается прогрев JIT, тиеринг, GC и шум; BDN обрабатывает всё это статистически.

> [!question]- Что означает Gen0 в отчёте?
> Количество сборок мусора поколения 0 на 1000 операций — оценка нагрузки на GC.

## Связанные темы

- [[N:3ea33104867981348f7afd2d924a3214]]
- [[N:3ea33104867981fb8c07fdd4f935833b]]
