---
type: topic
domain: db
stage: 4
section: "4.2"
order: 4
status: todo
level: middle
notion_id: 3ea33104867981e1b808cde4830cdf4f
tags: [domain/db, stage/4, level/middle, topic/s3, topic/presigned-url, topic/upload, priority/should]
reviewed:
next_review:
priority: should
time: 6
---

# Presigned URL и прямая загрузка с фронта

↑ [[DB 4.2 Объектное хранилище — MinIO и S3|4.2 Объектное хранилище: MinIO и S3]] · ← [[DB 4.2.3 Работа с MinIO из .NET — загрузка, скачивание, стриминг|Предыдущая]] · → [[DB 4.2.5 Multipart upload, версионирование, lifecycle, репликация|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~6 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> Стандартный приём: клиент загружает файлы напрямую в хранилище, не нагружая бэкенд.

## Проблема

Если файл идёт «браузер → API → хранилище», сервер тратит трафик, память и потоки. Альтернатива: API выдаёт **временную подписанную ссылку**, а браузер грузит файл в S3/MinIO напрямую.

## Presigned URL

URL со встроенной подписью, временем жизни и параметрами операции. Любой, у кого есть ссылка, может выполнить именно эту операцию до истечения срока.

```csharp
public string GetUploadUrl(string key, string contentType, TimeSpan ttl) =>
    _s3.GetPreSignedURL(new GetPreSignedUrlRequest
    {
        BucketName = _bucket,
        Key = key,
        Verb = HttpVerb.PUT,
        Expires = DateTime.UtcNow.Add(ttl),
        ContentType = contentType,
    });

public string GetDownloadUrl(string key, string fileName) =>
    _s3.GetPreSignedURL(new GetPreSignedUrlRequest
    {
        BucketName = _bucket,
        Key = key,
        Verb = HttpVerb.GET,
        Expires = DateTime.UtcNow.AddMinutes(5),
        ResponseHeaderOverrides = { ContentDisposition = $"attachment; filename=\"{fileName}\"" },
    });
```

## Схема загрузки

```text
1. Клиент → API: POST /files/init { name, size, type }
2. API: проверяет права, лимиты, тип; создаёт запись files(status='pending'); генерирует key
3. API → клиент: { fileId, uploadUrl (PUT), expires }
4. Клиент → S3: PUT uploadUrl (тело файла, Content-Type как в подписи)
5. Клиент → API: POST /files/{id}/complete (или S3 → webhook/событие)
6. API: проверяет HeadObject (размер, ETag), ставит status='ready'
```

Альтернатива **POST Policy** (presigned POST): форма с полями подписи и условиями (`content-length-range`, тип), позволяет ограничить размер на стороне хранилища.

## Фронтенд (пример)

```ts
async function upload(file: File) {
  const { fileId, uploadUrl } = await api.post('/files/init', { name: file.name, size: file.size, type: file.type })
  await new Promise<void>((resolve, reject) => {
    const xhr = new XMLHttpRequest()               // XHR даёт прогресс загрузки
    xhr.open('PUT', uploadUrl)
    xhr.setRequestHeader('Content-Type', file.type)
    xhr.upload.onprogress = e => progress.value = Math.round((e.loaded / e.total) * 100)
    xhr.onload = () => (xhr.status < 300 ? resolve() : reject(new Error(String(xhr.status))))
    xhr.onerror = reject
    xhr.send(file)
  })
  await api.post(`/files/${fileId}/complete`)
}
```

Для больших файлов — multipart с presigned URL на каждую часть, параллельная загрузка, повтор частей.

## CORS

Браузер делает кросс-доменный запрос: на бакете нужна CORS-конфигурация.

```json
[{
  "AllowedOrigins": ["https://app.example.com"],
  "AllowedMethods": ["PUT", "GET", "HEAD"],
  "AllowedHeaders": ["*"],
  "ExposeHeaders": ["ETag"],
  "MaxAgeSeconds": 3000
}]
```

## Безопасность

- короткий срок жизни (минуты для загрузки и скачивания), ключ объекта генерирует **сервер**, а не клиент;
- подпись включает `Content-Type`: клиент обязан отправить тот же;
- лимит размера — через POST Policy или проверка после загрузки (`HeadObject`, удалять нарушителей);
- после загрузки выполняйте проверку содержимого (тип, антивирус) до перевода в `ready`;
- не делайте бакет публичным ради простоты;
- логируйте выдачу ссылок, привязывайте к пользователю и квотам;
- **ссылку на скачивание нельзя отозвать** до истечения срока: ставьте малый TTL; для приватных данных используйте проксирование через API;
- адрес хоста в подписи должен совпадать с публичным адресом хранилища (`MINIO_SERVER_URL`, внутренний и внешний hostname отличаются в Docker/Kubernetes!).

## Скачивание

- presigned GET для приватных файлов; кэширование на CDN с подписанными URL (CloudFront signed URLs);
- публичные ресурсы (аватары, статика) — через CDN, с неизменяемыми ключами и долгим кэшем.

## Вопросы с ответами

> [!question]- Зачем presigned URL?
> Чтобы клиент скачивал или загружал файл напрямую в хранилище без проксирования через бэкенд и без раскрытия постоянных ключей; ссылка ограничена операцией и временем.

> [!question]- Как ограничить размер загружаемого файла при прямой загрузке?
> Использовать presigned POST с условием `content-length-range`, либо проверять размер после загрузки и удалять/отклонять превышающие объекты.

> [!question]- Почему presigned URL может не работать в Docker?
> Подпись привязана к хосту. Если приложение подписывает внутренним адресом (`minio:9000`), а браузер обращается по внешнему, подпись недействительна. Нужно подписывать публичным адресом.
