---
type: topic
domain: frontend
stage: 8
section: "8.4"
order: 5
status: todo
level: senior
notion_id: 3ea331048679815e9c48f55a1d6f8f76
tags: [domain/frontend, stage/8, level/senior, topic/system-design, topic/offline, topic/sync, topic/indexeddb, priority/should]
reviewed:
next_review:
priority: should
time: 3
---

# Офлайн-режим и синхронизация

↑ [[FE 8.4 Frontend System Design|8.4 Frontend System Design]] · ← [[FE 8.4.4 Real-time — чат, уведомления|Предыдущая]] · → [[FE 8.4.6 Кейс — автокомплит - typeahead|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: senior</span></div>
<!-- meta:end -->



> [!info] Зачем это на собесе
> Offline-first — сложный кейс; проверяют умение обеспечить консистентность.

## Уровни поддержки

1. **Оболочка offline**: Service Worker кэширует статику, приложение открывается.
2. **Чтение offline**: данные в IndexedDB/кэше.
3. **Запись offline**: очередь мутаций, отправка после восстановления сети.
4. **Полная синхронизация**: несколько устройств, разрешение конфликтов.

## Хранилища

| Хранилище | Особенности |
|---|---|
| localStorage | синхронный, ~5 МБ, строки |
| **IndexedDB** | асинхронное, большие объёмы, индексы (Dexie, idb) |
| Cache API | ответы HTTP (Service Worker) |
| OPFS | файловая система, большие файлы |

## Очередь мутаций

```ts
type Mutation = { id: string; type: string; payload: unknown; createdAt: number; attempts: number }

async function enqueue(m: Mutation) { await db.outbox.put(m); tryFlush() }

async function tryFlush() {
  if (!navigator.onLine) return
  for (const m of await db.outbox.orderBy('createdAt').toArray()) {
    try { await api.apply(m); await db.outbox.delete(m.id) }
    catch (e) { if (isFatal(e)) await markFailed(m); break }
  }
}
window.addEventListener('online', tryFlush)
```

Требования: **идемпотентность** (ключ идемпотентности), сохранение порядка, ограничение повторов, показ статуса пользователю.

## Конфликты

| Стратегия | Описание |
|---|---|
| Last write wins | побеждает последняя запись; просто, возможна потеря |
| По версии (ETag, `version`) | сервер отвергает устаревшую, клиент сливает |
| Слияние по полям | конфликтуют только одинаковые поля |
| **CRDT** / OT | автоматическое слияние (коллаборативное редактирование) |
| Ручное разрешение | показать пользователю |

## Синхронизация

- pull по `updatedSince` / cursor, push очереди;
- фоновая синхронизация (Background Sync API, периодически);
- дельты вместо полной загрузки;
- миграции схемы IndexedDB;
- `navigator.onLine` не гарантирует наличие сети: проверять реальным запросом.

## UX

Индикатор состояния (offline, синхронизация, ошибка), понятные сообщения, безопасное поведение при истечении токена.

## Вопросы с ответами

> [!question]- Как обеспечить, чтобы повторная отправка не создала дубль?
> Идемпотентные операции: клиент генерирует ключ мутации, сервер запоминает и повторно возвращает результат.

> [!question]- Как разрешать конфликты?
> По версии с отказом устаревших записей и слиянием, для текстов — CRDT, в критичных случаях — вручную.
