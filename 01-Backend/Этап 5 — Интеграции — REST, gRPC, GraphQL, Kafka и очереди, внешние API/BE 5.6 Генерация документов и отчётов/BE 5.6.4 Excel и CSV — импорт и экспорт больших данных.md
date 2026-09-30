---
type: topic
domain: backend
stage: 5
section: "5.6"
order: 4
status: todo
level: middle
notion_id: 3ea33104867981f3b6f9f4a53a5b5df9
tags: [domain/backend, stage/5, level/middle, topic/documents, topic/excel, topic/csv, priority/should]
reviewed:
next_review:
priority: should
time: 3
---

# Excel и CSV: импорт и экспорт больших данных

↑ [[BE 5.6 Генерация документов и отчётов|5.6 Генерация документов и отчётов]] · ← [[BE 5.6.3 Хранение и отдача файлов через MinIO|Предыдущая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->









> [!info] Зачем это на собесе
> Частая практическая задача: выгрузка на 1 млн строк и импорт пользовательских файлов без OOM.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

| Библиотека | Особенности |
|---|---|
| ClosedXML | удобный API, тяжело по памяти на больших файлах |
| EPPlus | богатый функционал, коммерческая лицензия |
| MiniExcel | потоковое чтение/запись, малая память |
| OpenXML SDK (`SAX`-режим) | низкоуровневый потоковый доступ |
| CsvHelper | стандарт для CSV |

Принцип: **потоковая обработка** — читаем и пишем строки по одной/пачками, не держим весь файл в памяти.

```csharp
// Экспорт: поток из БД → поток в файл
await using var output = File.Create(path);
await MiniExcel.SaveAsAsync(output, GetRowsAsync(ct), cancellationToken: ct);   // IAsyncEnumerable/IEnumerable

async IAsyncEnumerable<object> GetRowsAsync([EnumeratorCancellation] CancellationToken ct)
{
    await foreach (var o in db.Orders.AsNoTracking().AsAsyncEnumerable().WithCancellation(ct))
        yield return new { o.Number, o.Customer, o.Total };
}
```

```csharp
// Импорт CSV с валидацией и пакетной вставкой
using var reader = new StreamReader(stream);
using var csv = new CsvReader(reader, CultureInfo.InvariantCulture);
var batch = new List<Row>(1000);
await foreach (var row in csv.GetRecordsAsync<Row>(ct))
{
    if (!Validate(row, out var error)) { errors.Add((csv.Parser.Row, error)); continue; }
    batch.Add(row);
    if (batch.Count == 1000) { await SaveBatchAsync(batch, ct); batch.Clear(); }
}
```

Практики импорта: загрузка файла → валидация → отчёт об ошибках по строкам (номер, поле, причина) → применение в одной транзакции или частично с отчётом.

## Нюансы и подводные камни

- Excel ограничен 1 048 576 строками на лист; для больших выгрузок — CSV или несколько листов.
- Кодировка и разделители CSV (`;` в русской локали, UTF-8 с BOM для Excel).
- Формулы и внедрение: значения, начинающиеся с `=`, `+`, `@`, `-`, экранируйте (CSV/formula injection).
- Форматы дат/чисел зависят от культуры: используйте инвариантную культуру.
- Большие импорты выполняйте асинхронно с прогрессом и возможностью отмены.

## Практика

1. Экспортируйте 1 млн строк в CSV и в XLSX потоково и сравните память.
2. Реализуйте импорт с отчётом об ошибках по строкам.
3. Защитите экспорт от CSV-инъекций.

## Вопросы с ответами

> [!question]- Как выгрузить миллион строк без OOM?
> Потоково читать из БД и писать в файл/ответ, не материализуя всё в память.

> [!question]- Что такое CSV injection?
> Ячейки, начинающиеся с `=`/`+`/`@`, воспринимаются Excel как формулы; их нужно экранировать.

> [!question]- Как вести импорт пользовательских файлов?
> Валидировать построчно, накапливать ошибки с номерами строк, применять пачками, выполнять асинхронно.

## Связанные темы

- [[N:3ea33104867981dd851ddc18dbf209d9]]
- [[N:3ea33104867981fa9871f6da12aaf8b4]]
