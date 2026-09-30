---
type: topic
domain: frontend
stage: 8
section: "8.4"
order: 2
status: todo
level: senior
notion_id: 3ea3310486798138bfdefde1639298ef
tags: [domain/frontend, stage/8, level/senior, topic/system-design, topic/state, topic/normalization, priority/should]
reviewed:
next_review:
priority: should
time: 3
---

# Модель данных и нормализация состояния

↑ [[FE 8.4 Frontend System Design|8.4 Frontend System Design]] · ← [[FE 8.4.1 Фреймворк ответа — требования, архитектура, данные, API, оптимизации|Предыдущая]] · → [[FE 8.4.3 Пагинация — offset, cursor, infinite scroll|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: senior</span></div>
<!-- meta:end -->




> [!info] Зачем это на собесе
> Хранение данных на клиенте определяет консистентность и производительность UI.

## Категории состояния

| Вид | Где | Инструмент |
|---|---|---|
| Серверные данные (кэш) | клиентский кэш | TanStack Query, Apollo |
| Глобальное UI-состояние | стор | Pinia |
| Локальное состояние | компонент | `ref` |
| Состояние URL | адресная строка | Vue Router |
| Форма | локально | vee-validate, FormKit |
| Постоянное | localStorage, IndexedDB | — |

## Проблема вложенных данных

Один и тот же пользователь встречается в постах, комментариях, лайках. Обновление в одном месте не отражается в других.

## Нормализация

Храним сущности в плоских таблицах по id, связи — ссылками.

```ts
// вложенный ответ
{ posts: [{ id: 1, author: { id: 7, name: 'Аня' }, comments: [{ id: 3, author: { id: 7, name: 'Аня' } }] }] }

// нормализованное состояние
{
  users: { 7: { id: 7, name: 'Аня' } },
  posts: { 1: { id: 1, authorId: 7, commentIds: [3] } },
  comments: { 3: { id: 3, authorId: 7 } },
  postIds: [1],
}
```

Плюсы: единое место правки, дешёвые обновления, нет дублей и рассинхронизации. Минусы: нужен код сборки (denormalize) и нормализации; библиотеки: `normalizr`, нормализованный кэш Apollo, Pinia ORM.

## Оптимистичные обновления

```ts
const mutation = useMutation({
  mutationFn: likePost,
  onMutate: async (id) => {
    await qc.cancelQueries({ queryKey: ['post', id] })
    const prev = qc.getQueryData(['post', id])
    qc.setQueryData(['post', id], (p: Post) => ({ ...p, liked: true, likes: p.likes + 1 }))
    return { prev }
  },
  onError: (_e, id, ctx) => qc.setQueryData(['post', id], ctx!.prev),
  onSettled: (_d, _e, id) => qc.invalidateQueries({ queryKey: ['post', id] }),
})
```

## Консистентность

- инвалидация связанных запросов после мутации;
- версии, ETag и обработка конфликтов;
- порядок событий при real-time (последнее победит или слияние по версии);
- временные id для новых объектов до ответа сервера.

## Вопросы с ответами

> [!question]- Когда нормализация нужна, а когда избыточна?
> Нужна при связанных сущностях, встречающихся в нескольких местах и часто обновляемых. Для простых списков достаточно кэша по ключу запроса.

> [!question]- Как реализовать оптимистичное обновление безопасно?
> Сохранить предыдущее состояние, применить изменение сразу, при ошибке откатить, после завершения синхронизировать с сервером.
