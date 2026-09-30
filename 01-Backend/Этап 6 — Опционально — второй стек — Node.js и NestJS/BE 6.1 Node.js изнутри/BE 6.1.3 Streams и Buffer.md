---
type: topic
domain: backend
stage: 6
section: "6.1"
order: 3
status: todo
level: junior
notion_id: 3ea3310486798147ba50e9e03c350889
tags: [domain/backend, stage/6, level/junior, topic/nodejs, topic/streams, priority/nice]
reviewed:
next_review:
priority: nice
time: 3
---

# Streams и Buffer

↑ [[BE 6.1 Node.js изнутри|6.1 Node.js изнутри]] · ← [[BE 6.1.2 Модули, npm, package.json|Предыдущая]] · → [[BE 6.1.4 Worker threads и cluster|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge nice">По желанию</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: junior</span></div>
<!-- meta:end -->




































> [!info] Зачем это на собесе
> Как обрабатывать большие файлы и HTTP-тела без загрузки в память.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

**Buffer** — фиксированный блок байт вне кучи V8. **Stream** — последовательная обработка данных по частям.

| Тип | Пример |
|---|---|
| Readable | `fs.createReadStream`, HTTP-запрос |
| Writable | `fs.createWriteStream`, HTTP-ответ |
| Duplex | сокет TCP |
| Transform | сжатие `zlib`, шифрование, парсинг |

```js
import { pipeline } from "node:stream/promises";
import { createReadStream, createWriteStream } from "node:fs";
import { createGzip } from "node:zlib";

await pipeline(
  createReadStream("big.log"),
  createGzip(),
  createWriteStream("big.log.gz"),
);   // корректно обрабатывает ошибки и закрывает потоки
```

**Backpressure** — механизм, когда быстрый источник замедляется медленным приёмником: `write()` возвращает `false`, нужно дождаться `drain`. `pipeline` делает это автоматически.

```js
for await (const chunk of createReadStream("data.csv", { encoding: "utf8" })) {
  // обработка порциями
}
```

## Нюансы и подводные камни

- `pipe()` без обработки ошибок оставляет потоки открытыми: используйте `pipeline`.
- Чтение всего файла `readFile` для гигабайт → OOM.
- Работа с кодировками: границы многобайтных символов могут делиться между чанками (`setEncoding`).
- Кэшируйте `Buffer.allocUnsafe` осторожно: содержит остатки памяти.
- Веб-стандарт Web Streams доступен в Node.js рядом с Node-потоками.

## Практика

1. Сожмите файл 2 ГБ потоком, контролируя память.
2. Постройте конвейер парсинга CSV → фильтрация → запись.
3. Отдайте большой файл в HTTP-ответе потоком.

## Вопросы с ответами

> [!question]- Что такое backpressure?
> Сигнал приёмнику/источнику замедлиться, чтобы данные не накапливались в памяти.

> [!question]- Зачем pipeline вместо pipe?
> Он передаёт ошибки, закрывает все потоки и учитывает backpressure.

## Связанные темы

- [[N:3ea33104867981099ac9ff396547152a]]
- [[N:3ea331048679815e88ece14f7c6b80ae]]
