---
type: topic
domain: backend
stage: 3
section: "3.1"
order: 1
status: todo
level: middle
notion_id: 3ea331048679810f8b4def6f1c5f7146
tags: [domain/backend, stage/3, level/middle, topic/aspnet, topic/hosting, priority/must]
reviewed:
next_review:
priority: must
time: 4
---

# Как устроен ASP.NET Core: Kestrel, хост, Program.cs, WebApplication

↑ [[BE 3.1 Хост, конфигурация и middleware pipeline|3.1 Хост, конфигурация и middleware pipeline]] · → [[BE 3.1.2 Middleware — конвейер, порядок, свои middleware|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~4 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->


















































> [!info] Зачем это на собесе
> «Что происходит от `dotnet run` до первого запроса?» — стартовый вопрос по ASP.NET Core. Он проверяет понимание хоста, DI и конвейера.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

Приложение ASP.NET Core — это консольное приложение, которое создаёт **хост** (`IHost`). Хост владеет DI-контейнером, конфигурацией, логированием и набором `IHostedService`, среди которых веб-сервер **Kestrel**.

```csharp
var builder = WebApplication.CreateBuilder(args);   // конфигурация, DI, логирование по умолчанию

builder.Services.AddControllers();                  // регистрация сервисов
builder.Services.AddScoped<IOrderService, OrderService>();

var app = builder.Build();                          // сборка контейнера и конвейера

app.UseExceptionHandler();                          // конвейер middleware
app.UseAuthentication();
app.UseAuthorization();
app.MapControllers();                               // endpoints

app.Run();                                          // запуск Kestrel и блокировка потока
```

| Компонент | Роль |
|---|---|
| Kestrel | кроссплатформенный HTTP-сервер внутри процесса, HTTP/1.1, HTTP/2, HTTP/3 |
| `WebApplicationBuilder` | собирает конфигурацию, сервисы, логирование |
| `WebApplication` | одновременно `IApplicationBuilder` (middleware) и `IEndpointRouteBuilder` (маршруты) |
| Reverse proxy (nginx, YARP, IIS) | TLS, балансировка, статические файлы, защита Kestrel от интернета |
| `IHostedService` | фоновые сервисы и сам сервер |

### Что делает CreateBuilder

1. Устанавливает `ContentRoot`, читает `appsettings.json`, `appsettings.{Environment}.json`, user secrets (в Development), переменные окружения, аргументы командной строки.
2. Подключает логирование (Console, Debug, EventSource).
3. Включает DI-контейнер с проверкой областей видимости в Development.
4. Настраивает Kestrel и `UseUrls`/`ASPNETCORE_URLS`.

### Жизненный цикл запроса

Сокет Kestrel → парсинг HTTP → `HttpContext` → цепочка middleware → routing выбирает endpoint → фильтры/обработчик → ответ проходит обратно через middleware.

### Minimal hosting и Startup

До .NET 6 использовались `Program.cs` + `Startup.cs` (`ConfigureServices`, `Configure`). Модель minimal hosting объединила это в один файл; функционально они эквивалентны.

## Нюансы и подводные камни

- Порядок вызовов `Use*` важен: это порядок конвейера (см. [[N:3ea33104867981d5a91edcf41b2ae95a]]).
- После `builder.Build()` регистрировать сервисы нельзя: контейнер неизменяем.
- Kestrel не стоит выставлять напрямую в интернет без proxy, если нужна защита от медленных клиентов и TLS-терминация в ingress.
- В Docker слушайте `http://+:8080` (порт по умолчанию с .NET 8 — 8080, не 80).
- `app.Run()` блокирует поток до сигнала остановки (SIGTERM/Ctrl+C); используйте `RunAsync` в тестах.

## Практика

1. Создайте пустое приложение и выведите список зарегистрированных сервисов и endpoints.
2. Запустите одно и то же приложение за nginx и напрямую, сравните заголовки (`X-Forwarded-*`).
3. Переведите старый проект со `Startup.cs` на minimal hosting.

## Вопросы с ответами

> [!question]- Что такое Kestrel и зачем reverse proxy?
> Kestrel — встроенный управляемый веб-сервер. Proxy добавляет TLS, балансировку, кэш, фильтрацию и изоляцию от прямого доступа.

> [!question]- В чём разница между IHost и WebApplication?
> `WebApplication` — надстройка над хостом: реализует `IHost`, `IApplicationBuilder` и `IEndpointRouteBuilder`, чтобы конфигурировать сервисы и конвейер в одном месте.

> [!question]- Что делают builder.Services и app.Use*?
> `builder.Services` — этап регистрации зависимостей (до `Build`), `app.Use*` — этап описания конвейера обработки запроса.

> [!question]- Как приложение узнаёт, на каких портах слушать?
> Из `ASPNETCORE_URLS`/`--urls`, `Kestrel:Endpoints` в конфигурации или `launchSettings.json` (только локально).

## Связанные темы

- [[N:3ea33104867981d5a91edcf41b2ae95a]]
- [[N:3ea33104867981bf8a02c3a4b52c7ec7]]
