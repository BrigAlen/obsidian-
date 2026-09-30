---
type: topic
domain: backend
stage: 7
section: "7.1"
order: 1
status: todo
level: senior
notion_id: 3ea33104867981348f7afd2d924a3214
tags: [domain/backend, stage/7, level/senior, topic/dotnet, topic/performance, topic/profiling, priority/should]
reviewed:
next_review:
priority: should
time: 3
---

# Профилирование: dotnet-counters, dotnet-trace, dotnet-dump, PerfView

↑ [[BE 7.1 Производительность .NET и кэширование|7.1 Производительность .NET и кэширование]] · → [[BE 7.1.2 BenchmarkDotNet и микробенчмарки|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: senior</span></div>
<!-- meta:end -->

















> [!info] Зачем это на собесе
> «Сервис тормозит или течёт память — что делаете?» Ждут метод и инструменты, а не догадки.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

Порядок: **метрики → гипотеза → профиль → исправление → замер**.

| Инструмент | Что показывает |
|---|---|
| `dotnet-counters` | метрики рантайма в реальном времени: CPU, GC, аллокации, ThreadPool, исключения |
| `dotnet-trace` | трассировка (CPU sampling, события) → `.nettrace`, открывается в PerfView/Speedscope/VS |
| `dotnet-dump` | снимок памяти: `dumpheap -stat`, `gcroot`, `clrstack -all` |
| `dotnet-gcdump` | лёгкий снимок кучи (только графы объектов) |
| PerfView, Visual Studio Profiler, JetBrains dotTrace/dotMemory | анализ CPU, памяти, аллокаций |
| Application Insights, OpenTelemetry, Pyroscope/Parca | непрерывное профилирование в проде |

```bash
dotnet-counters monitor -n MyService --counters System.Runtime,Microsoft.AspNetCore.Hosting
dotnet-trace collect -p <pid> --profile cpu-sampling --duration 00:00:30
dotnet-dump collect -p <pid> && dotnet-dump analyze core_...
> dumpheap -stat        # кто занимает память
> gcroot <адрес>        # почему объект не освобождается
> clrstack -all         # что делают потоки (deadlock, блокировки)
```

Типичные диагнозы:

| Симптом | Причина |
|---|---|
| Высокий CPU | «горячий» метод, регулярные выражения, сериализация, спин |
| Рост памяти | утечка через события/статические кэши/`HttpClient`, большой LOH |
| Высокий gen2 GC | много долгоживущих аллокаций, LOH |
| Низкий CPU, высокая задержка | блокировка потоков, thread starvation, ожидание внешних систем |
| Рост числа потоков | sync-over-async |

## Нюансы и подводные камни

- Профилировать нужно на реалистичной нагрузке и в Release-сборке.
- Дамп содержит данные памяти, включая секреты и персональные данные: храните и передавайте осторожно.
- В контейнере нужны права и общий `/tmp` для диагностического сокета.
- Не оптимизируйте без измерения: узкое место часто не там, где кажется.

## Практика

1. Воспроизведите утечку статическим списком и найдите её через `dumpheap`/`gcroot`.
2. Снимите CPU-трассу и найдите самый дорогой метод.
3. Наблюдайте в `dotnet-counters` рост ThreadPool при sync-over-async.

## Вопросы с ответами

> [!question]- Как искать утечку памяти в .NET?
> Снять несколько дампов/gcdump, сравнить рост типов, через `gcroot` найти корень удержания.

> [!question]- Чем sampling-профилирование отличается от инструментирования?
> Sampling периодически берёт стек (малые накладные расходы), инструментирование добавляет код вызовов (точнее, но дороже).

## Связанные темы

- [[N:3ea33104867981e88c8ffcdc0440cf35]]
- [[N:3ea33104867981419025f0bdbcb02acf]]
