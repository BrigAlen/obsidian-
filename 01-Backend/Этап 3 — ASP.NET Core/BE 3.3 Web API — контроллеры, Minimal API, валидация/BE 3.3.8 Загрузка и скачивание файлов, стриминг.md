---
type: topic
domain: backend
stage: 3
section: "3.3"
order: 8
status: todo
level: middle
notion_id: 3ea331048679813385bfc8013c2dc64f
tags: [domain/backend, stage/3, level/middle, topic/aspnet, topic/files, topic/streaming, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Загрузка и скачивание файлов, стриминг

↑ [[BE 3.3 Web API — контроллеры, Minimal API, валидация|3.3 Web API: контроллеры, Minimal API, валидация]] · ← [[BE 3.3.7 OpenAPI и Swagger, версионирование API|Предыдущая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->














> [!info] Зачем это на собесе
> Практический вопрос: как принять/отдать большой файл и не «съесть» память.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

### Загрузка

```csharp
app.MapPost("/upload", async (IFormFile file, IStorage storage, CancellationToken ct) =>
{
    if (file.Length > 20_000_000) return Results.BadRequest("too big");
    await using var s = file.OpenReadStream();
    var key = await storage.SaveAsync(s, file.ContentType, ct);
    return Results.Ok(new { key });
}).DisableAntiforgery();
```

Для больших файлов `IFormFile` буферизует (в память до 64 КБ, потом во временный файл). Для стриминга без буфера читают `HttpContext.Request.Body` или `MultipartReader`.

### Скачивание

```csharp
app.MapGet("/files/{key}", async (string key, IStorage storage, CancellationToken ct) =>
{
    var (stream, contentType, name) = await storage.OpenAsync(key, ct);
    return Results.File(stream, contentType, name, enableRangeProcessing: true);
});
```

`enableRangeProcessing` включает `Range`-запросы (докачка, видео). Для отдачи из объектного хранилища (MinIO/S3) лучше выдавать pre-signed URL, чтобы файл шёл мимо приложения.

### Стриминг данных

```csharp
app.MapGet("/export", async (IAsyncEnumerable<Row> rows) => Results.Ok(rows));   // JSON-массив потоком
app.MapGet("/events", (CancellationToken ct) => TypedResults.ServerSentEvents(Ticks(ct)));
```

## Нюансы и подводные камни

- Лимиты: `Kestrel MaxRequestBodySize`, `FormOptions.MultipartBodyLengthLimit`, лимиты proxy (nginx `client_max_body_size`).
- Проверяйте тип файла по содержимому (magic bytes), а не по расширению/Content-Type.
- Не используйте имя файла клиента как путь (path traversal).
- Антивирусная проверка и карантин для пользовательских загрузок.
- Не загружайте файл целиком в `byte[]`: OOM на больших файлах.

## Практика

1. Реализуйте загрузку 1 ГБ файла потоком с постоянным потреблением памяти.
2. Отдайте pre-signed URL из MinIO вместо проксирования.
3. Добавьте поддержку `Range` и проверьте докачку `curl -C -`.

## Вопросы с ответами

> [!question]- Как принять большой файл, не исчерпав память?
> Читать поток порциями (`MultipartReader`/`Request.Body`) и сразу писать в хранилище, увеличив лимиты сервера.

> [!question]- Зачем pre-signed URL?
> Клиент загружает/скачивает файл напрямую из хранилища, снимая нагрузку с приложения.

> [!question]- Как защититься от path traversal при сохранении?
> Генерировать собственное имя (GUID), не подставлять клиентские значения в пути.

## Связанные темы

- [[N:3ea331048679816ca2a9e01efe418d51]]
- [[N:3ea331048679811a91f1da415f818e6a]]
