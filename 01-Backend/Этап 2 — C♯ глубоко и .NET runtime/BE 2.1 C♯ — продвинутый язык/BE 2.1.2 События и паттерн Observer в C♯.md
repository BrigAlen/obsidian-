---
type: topic
domain: backend
stage: 2
section: "2.1"
order: 2
status: todo
level: middle
notion_id: 3ea33104867981d5ae6bf41415020435
tags: [domain/backend, stage/2, level/middle, topic/events, topic/patterns, priority/must]
reviewed:
next_review:
priority: must
time: 7
---

# События и паттерн Observer в C#

↑ [[BE 2.1 C♯ — продвинутый язык|2.1 C♯: продвинутый язык]] · ← [[BE 2.1.1 Делегаты, Func, Action, лямбды, замыкания|Предыдущая]] · → [[BE 2.1.3 LINQ глубоко — отложенное выполнение, IEnumerable и IQueryable, expression trees|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~7 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->














> [!info] Зачем это на собесе
> события — встроенная реализация Observer. Вопросы: чем `event` отличается от публичного делегата, почему события — источник утечек, какие альтернативы для слабой связанности в бэкенде.

## Объяснение

### event поверх делегата

```csharp
public sealed class ReportJob
{
    public event EventHandler<ReportProgressEventArgs>? ProgressChanged;   // событие
    public event EventHandler? Completed;

    public async Task RunAsync(CancellationToken ct)
    {
        for (var page = 1; page <= total; page++)
        {
            await RenderPageAsync(page, ct);
            OnProgressChanged(new ReportProgressEventArgs(page, total));
        }
        Completed?.Invoke(this, EventArgs.Empty);
    }

    private void OnProgressChanged(ReportProgressEventArgs e) => ProgressChanged?.Invoke(this, e);   // ?. — потокобезопасный вызов
}

public sealed class ReportProgressEventArgs(int page, int total) : EventArgs
{
    public int Page { get; } = page;
    public int Total { get; } = total;
}

// подписка и отписка
job.ProgressChanged += OnProgress;
job.ProgressChanged -= OnProgress;
```

### Чем event отличается от публичного поля-делегата

```csharp
public Action? OnDone;               // поле: снаружи можно
obj.OnDone = null;                   //   — затереть всех подписчиков
obj.OnDone?.Invoke();                //   — вызвать событие от имени объекта

public event Action? Done;           // событие: снаружи можно только += и -=
```
`event` — инкапсуляция: вызывать и сбрасывать может только владелец.

### Конвенция .NET

- Сигнатура `(object? sender, TEventArgs e)`, `EventHandler`/`EventHandler<T>`.
- Защищённый виртуальный метод `OnXxx` для вызова (наследники могут переопределить).
- Имена: `Changed`, `Completed`, `Changing` (до события).

### Утечки памяти через события

Источник события держит **сильную ссылку** на подписчика (через делегат). Если долгоживущий источник (singleton-сервис, статическое событие) и короткоживущий подписчик не отписался — подписчик не соберётся GC.
```csharp
public sealed class Widget : IDisposable
{
    private readonly ISettingsService _settings;          // singleton
    public Widget(ISettingsService s) { _settings = s; _settings.Changed += OnChanged; }
    public void Dispose() => _settings.Changed -= OnChanged;   // обязательно отписаться
    private void OnChanged(object? sender, EventArgs e) { }
}
```

### Альтернативы в бэкенде

В серверном коде классические события используют редко. Вместо них:
- **Доменные события + mediator** (MediatR `INotification`) — обработчики разрешаются из DI, без ручных подписок.
- **Channels** или `IObservable<T>` (Rx) — поток событий внутри процесса.
- **Брокер сообщений** (Kafka, RabbitMQ) — между сервисами.
- **`IProgress<T>`** — для отчёта о прогрессе асинхронных операций.
```csharp
public async Task GenerateAsync(IProgress<int>? progress, CancellationToken ct)
{
    for (var i = 1; i <= 100; i++) { await StepAsync(ct); progress?.Report(i); }
}
```

## Нюансы и подводные камни

- Обработчики вызываются **синхронно** в потоке, вызвавшем событие. Медленный обработчик тормозит источник.
- `async void` обработчики событий — единственное допустимое место для `async void`, но исключение в них роняет процесс. Оборачивайте в try/catch.
- Исключение в одном подписчике прерывает остальных.
- Событие не гарантирует доставку: если процесс упал, событие потеряно. Для надёжности нужны outbox и брокер.
- Отписка лямбдой не работает, если лямбду не сохранили: `-= (s, e) => ...` — это новый делегат.

## Тестирование

```csharp
[Fact]
public async Task Raises_progress_for_each_page()
{
    var job = new ReportJob(totalPages: 3);
    var pages = new List<int>();
    job.ProgressChanged += (_, e) => pages.Add(e.Page);
    await job.RunAsync(default);
    pages.Should().Equal(1, 2, 3);
}
```

## Вопросы с ответами

> [!question]- Чем event отличается от публичного делегата?
> event разрешает снаружи только подписку и отписку (+= и -=). Вызвать событие или заменить список подписчиков может только класс-владелец.

> [!question]- Почему события могут приводить к утечкам памяти?
> Источник хранит сильную ссылку на подписчика через делегат. Долгоживущий источник не даст GC собрать подписчика, если тот не отписался.

> [!question]- В каком потоке выполняются обработчики событий?
> Синхронно, в том же потоке, где вызвано событие, по очереди в порядке подписки.

> [!question]- Что использовать для слабосвязанных событий в веб-приложении?
> Доменные события с mediator (обработчики из DI), Channels для фоновой обработки внутри процесса, брокер сообщений для межсервисных событий. Для прогресса — IProgress.

## Связанные темы

- Предыдущая: [[N:3ea33104867981c39639da77c07532df]] · Следующая: [[N:3ea33104867981dc98c9f760e86a24d5]]
- Паттерн Observer: [[N:3ea33104867981f88d7cefc97436250e]]
- DDD: доменные события: [[N:3ea33104867981fdacffc2220726e99c]]
- Channels: [[N:3ea331048679817e96d8c67b432324e0]]
- EventEmitter в JS: [[N:3ea331048679812294bdeb38bfb575f8]]
