---
type: topic
domain: db
stage: 4
section: "4.2"
order: 5
status: todo
level: middle
notion_id: 3ea331048679814799baccbb094459f7
tags: [domain/db, stage/4, level/middle, topic/s3, topic/multipart, topic/versioning, topic/lifecycle, topic/replication, priority/should]
reviewed:
next_review:
priority: should
time: 4
---

# Multipart upload, версионирование, lifecycle, репликация

↑ [[DB 4.2 Объектное хранилище — MinIO и S3|4.2 Объектное хранилище: MinIO и S3]] · ← [[DB 4.2.4 Presigned URL и прямая загрузка с фронта|Предыдущая]] · → [[DB 4.2.6 Файлы в БД или в объектном хранилище — связь метаданных и объектов|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~4 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> Управление большими файлами и жизненным циклом данных: отказоустойчивость, экономия и защита от удаления.

## Multipart upload

Большой объект загружается частями параллельно.

1. `CreateMultipartUpload` → `UploadId`.
2. `UploadPart` (номер 1–10000, размер 5 МБ–5 ГБ, кроме последней) для каждой части, можно параллельно и повторять.
3. `CompleteMultipartUpload` (список номеров и ETag частей) → объект собран.
4. `AbortMultipartUpload` — очистка при отказе.

Преимущества: возобновление и повтор только неудавшихся частей, параллелизм, загрузка без знания итогового размера, файлы больше 5 ГБ (лимит одной операции PUT).

**Рекомендации**: размер части 8–64 МБ; обязательно настроить lifecycle на удаление неоконченных загрузок (`AbortIncompleteMultipartUpload`, например через 7 дней), иначе скрытые части копят стоимость.

```csharp
var transfer = new TransferUtility(_s3);
await transfer.UploadAsync(new TransferUtilityUploadRequest
{
    BucketName = _bucket, Key = key, FilePath = path,
    PartSize = 16 * 1024 * 1024,
});
```

## Версионирование

`mc version enable local/bucket` / `PutBucketVersioning`. Каждая перезапись создаёт новую **версию** (`versionId`), `DELETE` ставит **delete marker**, предыдущие версии остаются.

- защита от случайного удаления и перезаписи, откат (`GetObject?versionId=...`);
- стоимость: хранение всех версий: нужны lifecycle-правила (`NoncurrentVersionExpiration`);
- включённое версионирование нельзя полностью отключить, только приостановить;
- в сочетании с **Object Lock** (WORM: режимы `GOVERNANCE`, `COMPLIANCE`, retention, legal hold) защищает от удаления и шифровальщиков.

## Lifecycle

Правила автоматического управления данными по префиксу/тегу/возрасту:

```json
{
  "Rules": [
    { "ID": "tmp-cleanup", "Status": "Enabled", "Filter": { "Prefix": "tmp/" }, "Expiration": { "Days": 1 } },
    { "ID": "logs", "Status": "Enabled", "Filter": { "Prefix": "logs/" },
      "Transitions": [{ "Days": 30, "StorageClass": "STANDARD_IA" }, { "Days": 180, "StorageClass": "GLACIER" }],
      "Expiration": { "Days": 365 } },
    { "ID": "versions", "Status": "Enabled", "Filter": {}, "NoncurrentVersionExpiration": { "NoncurrentDays": 30 } },
    { "ID": "abort-mpu", "Status": "Enabled", "Filter": {}, "AbortIncompleteMultipartUpload": { "DaysAfterInitiation": 7 } }
  ]
}
```

Применения: временные файлы, логи и бэкапы по срокам хранения (политика ретенции, требования закона), переход на более дешёвые классы, очистка версий. В MinIO: `mc ilm`, tiering на удалённые уровни (S3, Azure, GCS).

## Репликация

| Тип | Описание |
|---|---|
| **Bucket replication** (CRR/SRR) | копирование новых объектов в другой бакет/кластер/регион |
| **Site replication** (MinIO) | синхронизация нескольких кластеров: бакеты, политики, пользователи |
| Active-passive / active-active | резерв или двусторонняя репликация |

Свойства: требуется версионирование; асинхронная (возможна задержка); реплицируются новые объекты (существующие — через batch replication); можно реплицировать delete markers; фильтры по префиксу/тегам; метрики задержки.

Цели: отказоустойчивость (DR), близость к пользователям, соответствие требованиям (копия в другом регионе), миграция.

## Другие возможности

- **Event notifications**: событие `s3:ObjectCreated:*` → очередь/webhook (обработка загруженных файлов, превью);
- **Batch операции**, **инвентаризация**;
- **Тегирование** для lifecycle и учёта затрат;
- **Классы хранения** (Standard, IA, Glacier/Archive) — цена против скорости доступа.

## Вопросы с ответами

> [!question]- Зачем multipart upload?
> Для больших файлов: параллельная загрузка частей, повтор только упавших, возобновление и снятие лимита одной операции.

> [!question]- Что такое lifecycle-правило?
> Автоматическое действие над объектами по возрасту/префиксу/тегу: удаление, переход в более дешёвый класс, очистка неактуальных версий и незавершённых multipart-загрузок.

> [!question]- Как защитить данные от случайного или злонамеренного удаления?
> Включить версионирование и Object Lock (WORM), ограничить права удаления, настроить репликацию в другой кластер/регион и регулярно проверять восстановление.
