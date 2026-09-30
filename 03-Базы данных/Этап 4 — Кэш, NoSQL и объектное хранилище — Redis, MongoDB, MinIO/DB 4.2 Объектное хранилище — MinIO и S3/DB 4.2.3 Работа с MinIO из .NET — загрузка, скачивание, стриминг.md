---
type: topic
domain: db
stage: 4
section: "4.2"
order: 3
status: todo
level: middle
notion_id: 3ea3310486798163b223fd6b51476db9
tags: [domain/db, stage/4, level/middle, topic/minio, topic/dotnet, topic/s3, topic/streaming, priority/should]
reviewed:
next_review:
priority: should
time: 6
---

# Работа с MinIO из .NET: загрузка, скачивание, стриминг

↑ [[DB 4.2 Объектное хранилище — MinIO и S3|4.2 Объектное хранилище: MinIO и S3]] · ← [[DB 4.2.2 MinIO — развёртывание, mc, политики доступа|Предыдущая]] · → [[DB 4.2.4 Presigned URL и прямая загрузка с фронта|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~6 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> Практика backend-разработчика: корректная загрузка и отдача файлов без перегрузки памяти.

## Клиенты

| Библиотека | Особенности |
|---|---|
| **AWSSDK.S3** | универсальный, стандартный S3-клиент (работает с MinIO, `ForcePathStyle = true`) |
| **Minio** (Minio .NET SDK) | фокус на MinIO, удобный fluent API |

Вариант с AWSSDK.S3:

```csharp
builder.Services.AddSingleton<IAmazonS3>(_ =>
{
    var cfg = new AmazonS3Config
    {
        ServiceURL = "http://minio:9000",
        ForcePathStyle = true,               // minio:9000/bucket/key вместо bucket.minio:9000
    };
    return new AmazonS3Client(accessKey, secretKey, cfg);
});
```

`IAmazonS3` потокобезопасен, регистрируем как singleton.

## Загрузка

```csharp
public async Task<string> UploadAsync(Stream content, string fileName, string contentType, CancellationToken ct)
{
    var key = $"uploads/{DateTime.UtcNow:yyyy/MM}/{Guid.NewGuid():N}{Path.GetExtension(fileName)}";

    await _s3.PutObjectAsync(new PutObjectRequest
    {
        BucketName = _bucket,
        Key = key,
        InputStream = content,
        ContentType = contentType,
        AutoCloseStream = false,
        Metadata = { ["original-name"] = Uri.EscapeDataString(fileName) },
    }, ct);

    return key;
}
```

Для больших файлов используйте `TransferUtility` (автоматический multipart):

```csharp
var tu = new TransferUtility(_s3);
await tu.UploadAsync(filePath, _bucket, key, ct);
```

## Скачивание и стриминг

**Не загружайте файл целиком в память** (`byte[]`): стримьте.

```csharp
[HttpGet("files/{id}")]
public async Task<IActionResult> Download(string id, CancellationToken ct)
{
    var file = await _files.FindAsync(id, ct) ?? throw new NotFoundException();
    var response = await _s3.GetObjectAsync(_bucket, file.Key, ct);

    Response.RegisterForDispose(response);              // освободит ответ после отправки
    return File(response.ResponseStream, response.Headers.ContentType, file.OriginalName, enableRangeProcessing: true);
}
```

- `enableRangeProcessing: true` — поддержка `Range` (докачка, перемотка видео), при этом нужен поток с поддержкой `Seek` или передача `Range` в S3 (`GetObjectRequest.ByteRange`);
- `Content-Disposition` для имени файла; `Content-Type` из метаданных.

## Загрузка в ASP.NET Core

```csharp
[HttpPost("upload")]
[RequestSizeLimit(100 * 1024 * 1024)]
public async Task<IActionResult> Upload(IFormFile file, CancellationToken ct)
{
    if (file.Length == 0) return BadRequest();
    if (!_allowed.Contains(file.ContentType)) return StatusCode(415);

    await using var stream = file.OpenReadStream();
    var key = await _storage.UploadAsync(stream, file.FileName, file.ContentType, ct);
    return Ok(new { key });
}
```

Для очень больших файлов читайте multipart-поток вручную (`MultipartReader`) без буферизации на диск, или используйте прямую загрузку клиента через presigned URL.

## Проверки безопасности

- проверять **реальный тип** по сигнатуре (magic bytes), а не только `Content-Type`/расширение;
- лимиты размера, антивирусное сканирование (ClamAV) для пользовательских файлов;
- не доверять имени файла (path traversal): генерировать свой ключ;
- отдавать скачиваемые файлы с `Content-Disposition: attachment` и безопасным `Content-Type` (защита от XSS через HTML/SVG).

## Операции

```csharp
await _s3.DeleteObjectAsync(_bucket, key, ct);
await _s3.CopyObjectAsync(_bucket, oldKey, _bucket, newKey, ct);

var list = await _s3.ListObjectsV2Async(new ListObjectsV2Request { BucketName = _bucket, Prefix = "uploads/2026/09/", MaxKeys = 100 }, ct);

var meta = await _s3.GetObjectMetadataAsync(_bucket, key, ct);   // HEAD
```

## Устойчивость

Повторы с backoff (встроены в SDK, настраиваются `MaxErrorRetry`), таймауты, отмена через `CancellationToken`, идемпотентность (ключ объекта детерминирован, перезапись безопасна), логирование ошибок `AmazonS3Exception` (`ErrorCode`, `StatusCode`).

## Тестирование

Testcontainers: `MinioBuilder` поднимает MinIO для интеграционных тестов.

## Вопросы с ответами

> [!question]- Почему нельзя читать файл целиком в byte[] при отдаче?
> Большие файлы займут много памяти и нагрузят GC, при нескольких параллельных скачиваниях приложение упадёт. Нужно стримить поток из хранилища клиенту.

> [!question]- Зачем ForcePathStyle для MinIO?
> Иначе клиент формирует адрес вида `bucket.host`, для которого нужен DNS на поддомены; path-style использует `host/bucket/key`, что работает с обычным адресом.

> [!question]- Как защититься от загрузки вредоносных файлов?
> Ограничить размер и типы, проверять содержимое по сигнатуре, сканировать антивирусом, генерировать собственные ключи и отдавать файлы с безопасными заголовками.
