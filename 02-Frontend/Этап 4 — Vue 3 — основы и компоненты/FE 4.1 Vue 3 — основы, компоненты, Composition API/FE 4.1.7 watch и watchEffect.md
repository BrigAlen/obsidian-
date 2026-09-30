---
type: topic
domain: frontend
stage: 4
section: "4.1"
order: 7
status: todo
level: middle
notion_id: 3ea33104867981b588dcc193852b1e9a
tags: [domain/frontend, stage/4, level/middle, topic/vue, topic/watch, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# watch и watchEffect

↑ [[FE 4.1 Vue 3 — основы, компоненты, Composition API|4.1 Vue 3: основы, компоненты, Composition API]] · ← [[FE 4.1.6 computed|Предыдущая]] · → [[FE 4.1.8 Кастомные директивы|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->




















> [!info] Зачем это на собесе
> Когда `watch`, когда `watchEffect`, что такое `flush` и очистка эффектов.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

```ts
// watch: явные источники, ленивый по умолчанию, даёт старое и новое значение
watch(userId, async (id, oldId, onCleanup) => {
  const ctrl = new AbortController();
  onCleanup(() => ctrl.abort());                       // отмена предыдущего запроса
  user.value = await api.user(id, { signal: ctrl.signal });
}, { immediate: true });

watch([a, b], ([na, nb], [oa, ob]) => {});             // несколько источников
watch(() => state.filter.query, search, { deep: false });   // геттер
watch(state, cb, { deep: true });                       // глубокое наблюдение (дорого)

// watchEffect: зависимости отслеживаются автоматически, запускается сразу
watchEffect(() => { document.title = `${count.value} — ${title.value}`; });
watchEffect((onCleanup) => { const t = setInterval(tick, 1000); onCleanup(() => clearInterval(t)); });
```

| | `watch` | `watchEffect` |
|---|---|---|
| Источники | явные | автоматические (всё прочитанное синхронно) |
| Старое значение | да | нет |
| Первый запуск | нет (`immediate: true`) | да |
| Когда | нужен контроль, реакция на конкретное изменение | много зависимостей, эффект «синхронизации» |

Опции: `immediate`, `deep`, `once`, `flush: "pre" | "post" | "sync"` (`post` — после обновления DOM; `watchPostEffect`, `watchSyncEffect`), `onWatcherCleanup` (3.5).

Остановка: watcher внутри `setup` останавливается автоматически при размонтировании; созданный асинхронно — вручную (`const stop = watch(...)`, `stop()`).

Практики: избегайте `watch` там, где достаточно `computed`; для загрузки данных при смене параметров лучше **Vue Query** (кэш, отмена, состояния).

## Нюансы и подводные камни

- `watch(state.field, ...)` — источник примитив, не реактивный: используйте геттер `() => state.field`.
- В `watchEffect` асинхронные зависимости после `await` не отслеживаются.
- `deep: true` на больших объектах — дорого.
- Изменение отслеживаемого состояния внутри самого watcher вызывает циклы.
- Гонки запросов: применяйте отмену (`onCleanup`).

## Практика

1. Реализуйте поиск при изменении запроса с отменой предыдущего запроса.
2. Синхронизируйте `document.title` через `watchEffect`.
3. Замените `watch` на `computed` там, где это возможно.

## Вопросы с ответами

> [!question]- Чем `watch` отличается от `watchEffect`?
> `watch` следит за явными источниками и даёт старое значение, `watchEffect` автоматически отслеживает всё прочитанное и запускается сразу.

> [!question]- Зачем `onCleanup`?
> Отменять предыдущие побочные эффекты (запросы, таймеры) перед новым запуском и при остановке.

## Связанные темы

- [[N:3ea3310486798127b268e92751718ab6]]
- [[N:3ea33104867981c18a4ad4ea83878013]]
