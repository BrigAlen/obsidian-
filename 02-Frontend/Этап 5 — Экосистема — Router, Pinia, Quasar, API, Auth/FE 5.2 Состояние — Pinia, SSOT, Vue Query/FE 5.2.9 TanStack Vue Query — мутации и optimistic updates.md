---
type: topic
domain: frontend
stage: 5
section: "5.2"
order: 9
status: todo
level: middle
notion_id: 3ea331048679818fb89cd4c82a907497
tags: [domain/frontend, stage/5, level/middle, topic/vue, topic/vue-query, topic/mutations, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# TanStack Vue Query: мутации и optimistic updates

↑ [[FE 5.2 Состояние — Pinia, SSOT, Vue Query|5.2 Состояние: Pinia, SSOT, Vue Query]] · ← [[FE 5.2.8 TanStack Vue Query — запросы, кэш, инвалидация|Предыдущая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->



















> [!info] Зачем это на собесе
> Как отправлять изменения и мгновенно обновлять UI с корректным откатом.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

**Мутация** — операция изменения на сервере (`POST/PUT/DELETE`); в отличие от запроса, не кэшируется и запускается вручную.

```ts
const qc = useQueryClient();
const { mutate, mutateAsync, isPending, error } = useMutation({
  mutationFn: (dto: UpdateOrder) => api.updateOrder(dto.id, dto),
  onSuccess: (updated) => {
    qc.setQueryData(["order", updated.id], updated);                 // точечно
    qc.invalidateQueries({ queryKey: ["orders"] });                  // список — перезапрос
    notify("Сохранено");
  },
  onError: (e) => notify(errorMessage(e), "negative"),
  onSettled: () => qc.invalidateQueries({ queryKey: ["orders"] }),
});
mutate(dto, { onSuccess: () => router.back() });
```

**Оптимистичное обновление**: UI меняется сразу, откат при ошибке.

```ts
useMutation({
  mutationFn: (id: number) => api.toggleFavorite(id),
  onMutate: async (id) => {
    await qc.cancelQueries({ queryKey: ["orders"] });                // отменить исходящие запросы, чтобы не затёрли
    const previous = qc.getQueryData<Order[]>(["orders"]);           // снимок для отката
    qc.setQueryData<Order[]>(["orders"], (old) => old?.map(o => o.id === id ? { ...o, favorite: !o.favorite } : o));
    return { previous };
  },
  onError: (_e, _id, ctx) => qc.setQueryData(["orders"], ctx?.previous),    // откат
  onSettled: () => qc.invalidateQueries({ queryKey: ["orders"] }),          // синхронизация с сервером
});
```

В новых версиях можно оптимистично показывать `variables` мутации прямо в UI (`mutation.variables`) без правки кэша.

Практики:

- Идемпотентность и `Idempotency-Key` для повторов.
- Блокировка кнопки на время `isPending`, защита от двойного клика.
- Последовательные мутации: `scope` (очередь), `mutateAsync` + `await`.
- Ошибки валидации сервера (422) → поля формы.
- Офлайн: `networkMode`, `persistQueryClient`.

## Нюансы и подводные камни

- Без `cancelQueries` фоновый запрос может перезаписать оптимистичное значение.
- Откат должен восстанавливать именно снимок до изменений.
- Инвалидация в `onSettled` гарантирует итоговую согласованность.
- Оптимизм оправдан для частых и предсказуемых операций (лайк, чекбокс); для платежей — нет.
- Ключи кэша: обновляйте все затронутые (список, карточка).

## Практика

1. Реализуйте оптимистичное переключение статуса с откатом при ошибке.
2. После создания заказа инвалидируйте список и перейдите на карточку.
3. Защитите форму от повторной отправки.

## Вопросы с ответами

> [!question]- Что такое optimistic update?
> Мгновенное изменение UI до ответа сервера с откатом при ошибке.

> [!question]- Зачем `cancelQueries` в `onMutate`?
> Чтобы ответ фонового запроса не затёр оптимистичное значение.

## Связанные темы

- [[N:3ea33104867981caa116ffe38e5e4912]]
- [[N:3ea33104867981319af3fe3805ab8528]]
