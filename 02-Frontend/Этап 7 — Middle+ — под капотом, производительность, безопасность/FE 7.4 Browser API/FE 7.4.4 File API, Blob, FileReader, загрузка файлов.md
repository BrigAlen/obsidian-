---
type: topic
domain: frontend
stage: 7
section: "7.4"
order: 4
status: todo
level: senior
notion_id: 3ea331048679812caaa0e9ddeac3ce4f
tags: [domain/frontend, stage/7, level/senior, topic/browser-api, topic/file, topic/blob, topic/upload, priority/should]
reviewed:
next_review:
priority: should
time: 3
---

# File API, Blob, FileReader, загрузка файлов

↑ [[FE 7.4 Browser API|7.4 Browser API]] · ← [[FE 7.4.3 History API и Location|Предыдущая]] · → [[FE 7.4.5 Clipboard, Notifications, Geolocation|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: senior</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> Загрузка и скачивание файлов — типовая задача; спрашивают Blob, прогресс, большие файлы.

## Основные объекты

- **File** — файл из `<input type="file">` или drag-and-drop (наследует Blob, имя, размер, тип);
- **Blob** — неизменяемые бинарные данные;
- **FileReader** — асинхронное чтение (`readAsText`, `readAsDataURL`, `readAsArrayBuffer`);
- `URL.createObjectURL(blob)` — временная ссылка для превью или скачивания (не забыть `revokeObjectURL`).

## Загрузка

```ts
function onPick(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (!file) return
  if (file.size > 10 * 1024 * 1024) return showError('Файл больше 10 МБ')
  preview.value = URL.createObjectURL(file)
  upload(file)
}

async function upload(file: File) {
  const fd = new FormData()
  fd.append('file', file)
  await fetch('/api/files', { method: 'POST', body: fd })   // Content-Type выставится сам
}
```

Прогресс: `XMLHttpRequest.upload.onprogress` или axios `onUploadProgress` (`fetch` не отдаёт прогресс загрузки).

## Скачивание

```ts
async function download(url: string, name: string) {
  const blob = await fetch(url).then(r => r.blob())
  const a = document.createElement('a')
  a.href = URL.createObjectURL(blob)
  a.download = name
  a.click()
  URL.revokeObjectURL(a.href)
}
```

## Большие файлы

- чтение по частям: `file.slice(start, end)`;
- **chunked upload** с возобновлением (tus, S3 multipart): куски параллельно, повтор только упавших;
- presigned URL: загрузка напрямую в хранилище, минуя бэкенд;
- стримы: `file.stream()`, `ReadableStream`.

## Drag & Drop

```ts
el.addEventListener('dragover', e => e.preventDefault())
el.addEventListener('drop', e => { e.preventDefault(); handle([...(e.dataTransfer?.files ?? [])]) })
```

## Безопасность

Проверка типа и размера на клиенте — только удобство; окончательная валидация (MIME по содержимому, антивирус) на сервере.

## Вопросы с ответами

> [!question]- Почему при отправке FormData нельзя вручную ставить Content-Type: multipart?
> Браузер должен добавить boundary; при ручной установке заголовка граница теряется и сервер не разберёт тело.

> [!question]- Как загрузить файл на 5 ГБ?
> Разбить на части (chunked/multipart upload), загружать по presigned URL напрямую в хранилище, поддержать возобновление и параллельность.
