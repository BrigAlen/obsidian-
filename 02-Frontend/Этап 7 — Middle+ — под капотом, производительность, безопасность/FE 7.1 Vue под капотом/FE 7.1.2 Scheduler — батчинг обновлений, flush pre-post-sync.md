---
type: topic
domain: frontend
stage: 7
section: "7.1"
order: 2
status: todo
level: senior
notion_id: 3ea3310486798160b2c6d2cb69043831
tags: [domain/frontend, stage/7, level/senior, topic/vue, topic/scheduler, topic/nexttick, priority/should]
reviewed:
next_review:
priority: should
time: 3
---

# Scheduler: батчинг обновлений, flush pre/post/sync

↑ [[FE 7.1 Vue под капотом|7.1 Vue под капотом]] · ← [[FE 7.1.1 Как устроена реактивность внутри — Proxy, track, trigger, effect|Предыдущая]] · → [[FE 7.1.3 effectScope, markRaw, readonly, customRef|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: senior</span></div>
<!-- meta:end -->




> [!info] Зачем это на собесе
> Объясняет, почему DOM обновляется не сразу и зачем нужен `nextTick`.

## Батчинг

Несколько изменений состояния подряд не вызывают несколько рендеров. Vue ставит компонент в очередь и обновляет **один раз за тик** (микрозадача).

```ts
const count = ref(0)
count.value++
count.value++
count.value++      // рендер будет один
await nextTick()   // DOM уже обновлён
```

## Очереди

1. **pre** — колбэки `watch` с `flush: 'pre'` (по умолчанию), до рендера компонента;
2. **render** — обновление компонентов (родитель раньше ребёнка, отсортировано по id);
3. **post** — `flush: 'post'`, `onMounted/onUpdated`: DOM уже готов;
4. **sync** — `flush: 'sync'`, срабатывает мгновенно при изменении.

```ts
watch(source, cb)                        // pre
watch(source, cb, { flush: 'post' })     // после обновления DOM
watch(source, cb, { flush: 'sync' })     // синхронно (осторожно)
watchPostEffect(() => { /* DOM готов */ })
```

## nextTick

Возвращает промис, который разрешается после текущего flush. Нужен, когда после изменения состояния надо прочитать обновлённый DOM (размеры, фокус).

## Нюансы

- `sync` может вызывать каскады и падение производительности;
- обновление родителя, не затрагивающее props ребёнка, не перерисовывает ребёнка;
- рекурсивные обновления ограничены (лимит 100) с предупреждением.

## Вопросы с ответами

> [!question]- Почему после изменения ref DOM ещё старый?
> Обновление отложено в очередь (микрозадача). Дождитесь `await nextTick()`.

> [!question]- Чем pre отличается от post?
> pre выполняется до обновления DOM компонента, post — после, когда можно читать актуальные размеры.
