---
type: topic
domain: backend
stage: 5
section: "5.6"
order: 3
status: todo
level: middle
notion_id: 3ea33104867981dd851ddc18dbf209d9
tags: [domain/backend, stage/5, level/middle, topic/documents, topic/storage, topic/minio, priority/should]
reviewed:
next_review:
priority: should
time: 3
---

# Хранение и отдача файлов через MinIO

↑ [[BE 5.6 Генерация документов и отчётов|5.6 Генерация документов и отчётов]] · ← [[BE 5.6.2 Фабрика отчётов и сбор данных из разных источников|Предыдущая]] · → [[BE 5.6.4 Excel и CSV — импорт и экспорт больших данных|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->
















































> [!info] Зачем это на собесе
> Объектные хранилища — стандарт для файлов. Ждут понимания pre-signed URL и почему не хранить файлы в БД.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

MinIO — S3-совместимое объектное хранилище (self-hosted). API совпадает с AWS S3, поэтому код переносится в облако.

| Понятие | Смысл |
|---|---|
| Bucket | контейнер объектов |
| Object | файл + метаданные, ключ (`reports/2025/06/a1.pdf`) |
| Pre-signed URL | временная подписанная ссылка на загрузку/скачивание |
| Lifecycle | правила удаления/перемещения по сроку |
| Versioning, Object Lock | версии и защита от удаления |
| Policies | права доступа на bucket/префикс |

```csharp
var client = new MinioClient().WithEndpoint("minio:9000").WithCredentials(key, secret).Build();

await client.PutObjectAsync(new PutObjectArgs().WithBucket("docs").WithObject(objectKey)
    .WithStreamData(stream).WithObjectSize(stream.Length).WithContentType("application/pdf"), ct);

// ссылка на скачивание на 10 минут
var url = await client.PresignedGetObjectAsync(new PresignedGetObjectArgs().WithBucket("docs").WithObject(objectKey).WithExpiry(600));
```

Схема:

- В БД хранится только метаданные (id, ключ, размер, тип, владелец), файл — в MinIO.
- Загрузка большими файлами — pre-signed PUT прямо из браузера (multipart для больших), минуя ваш сервис.
- Ключ объекта генерируйте сами (GUID), оригинальное имя храните в метаданных.
- Виртуальная папка = префикс ключа.

## Нюансы и подводные камни

- Публичный bucket по умолчанию не создавайте: доступ через pre-signed URL или прокси с проверкой прав.
- Pre-signed URL передаёт доступ любому, у кого ссылка: делайте срок коротким.
- Внутренний адрес MinIO ≠ публичный: ссылки для клиента должны использовать внешний хост.
- Файлы удаляйте вместе с записью (или lifecycle); осиротевшие объекты копят стоимость.
- Проверка типа и размера, антивирус для пользовательских загрузок.

## Практика

1. Поднимите MinIO в Docker и загрузите файл через SDK.
2. Реализуйте загрузку из браузера по pre-signed PUT.
3. Настройте lifecycle на удаление временных файлов через 7 дней.

## Вопросы с ответами

> [!question]- Почему не хранить файлы в БД?
> Раздувается БД и бэкапы, нагрузка на соединения; объектное хранилище дешевле и масштабируется.

> [!question]- Что такое pre-signed URL?
> Временная подписанная ссылка, дающая доступ к объекту без учётных данных.

> [!question]- Чем MinIO полезен?
> S3-совместимый API: код одинаково работает с MinIO и AWS S3.

## Связанные темы

- [[N:3ea33104867981f697efff1f2f6a4d2f]]
- [[N:3ea33104867981f3b6f9f4a53a5b5df9]]
