---
type: topic
domain: frontend
stage: 5
section: "5.2"
order: 8
status: todo
level: middle
notion_id: 3ea33104867981caa116ffe38e5e4912
tags: [domain/frontend, stage/5, level/middle, topic/vue, topic/vue-query, topic/cache, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# TanStack Vue Query: запросы, кэш, инвалидация

↑ [[FE 5.2 Состояние — Pinia, SSOT, Vue Query|5.2 Состояние: Pinia, SSOT, Vue Query]] · ← [[FE 5.2.7 Server state и client state|Предыдущая]] · → [[FE 5.2.9 TanStack Vue Query — мутации и optimistic updates|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->









> [!info] Зачем это на собесе
> Стандарт работы с серверным состоянием; спрашивают ключи, `staleTime`, инвалидацию.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

```ts
// main.ts
app.use(VueQueryPlugin, { queryClientConfig: { defaultOptions: { queries: { staleTime: 30_000, retry: 2, refetchOnWindowFocus: false } } } });

// Запрос
const filters = ref({ status: "paid", page: 1 });
const { data, isPending, isFetching, isError, error, refetch } = useQuery({
  queryKey: ["orders", filters],                        // ключ включает реактивные параметры — смена → новый запрос
  queryFn: ({ signal }) => api.getOrders(filters.value, { signal }),   // signal для отмены
  staleTime: 60_000,
  placeholderData: keepPreviousData,                    // без «мигания» при смене страницы
  enabled: computed(() => !!userId.value),              // зависимые запросы
  select: (d) => d.items,                               // преобразование
});
```

Ключевые понятия:

| Понятие | Смысл |
|---|---|
| `queryKey` | идентификатор кэша; массив, включает все параметры |
| `staleTime` | сколько данные считаются свежими (без фонового обновления) |
| `gcTime` (`cacheTime`) | сколько неиспользуемые данные хранятся в кэше |
| `isPending` / `isFetching` | нет данных вообще / идёт любой запрос (включая фоновый) |
| `status`: `pending/error/success` | состояние данных |
| Refetch | при монтировании, фокусе окна, восстановлении сети, интервал |
| Дедупликация | одинаковые запросы объединяются |
| Retry | повторы с экспоненциальной паузой |
| `queryClient` | доступ к кэшу: `getQueryData`, `setQueryData`, `invalidateQueries`, `prefetchQuery` |

**Инвалидация**: после изменения данных помечаем кэш устаревшим — активные запросы перезагружаются.

```ts
const qc = useQueryClient();
qc.invalidateQueries({ queryKey: ["orders"] });                 // все запросы, ключ которых начинается с "orders"
qc.setQueryData(["order", id], updated);                        // точечное обновление кэша
await qc.prefetchQuery({ queryKey: ["order", id], queryFn: () => api.getOrder(id) });   // предзагрузка на hover
```

Бесконечные списки — `useInfiniteQuery` (`getNextPageParam`), пагинация — `placeholderData`, SSR — `dehydrate/hydrate`, DevTools — `@tanstack/vue-query-devtools`.

Организация: фабрики ключей и хуки на сущность (`useOrders`, `useOrder`), общий слой API, обработка ошибок через `QueryCache.onError`.

## Нюансы и подводные камни

- Реактивные параметры нужно передавать как `ref/computed` в `queryKey`, иначе запрос не перезапустится.
- `staleTime: 0` (по умолчанию) вызывает частые перезапросы — настройте под данные.
- Деструктурированные значения — refs, в шаблоне разворачиваются, в скрипте — `.value`.
- Не храните копию `data` в локальном ref без нужды.
- Отменяйте запросы через `signal`.

## Практика

1. Замените ручную загрузку списка на `useQuery` с фильтрами в ключе.
2. Настройте `staleTime`, `placeholderData: keepPreviousData` для пагинации.
3. Предзагрузите карточку при наведении на строку таблицы.

## Вопросы с ответами

> [!question]- Что такое `queryKey`?
> Массив-идентификатор кэша запроса; включает параметры, при их изменении выполняется новый запрос.

> [!question]- Чем `staleTime` отличается от `gcTime`?
> `staleTime` — период «свежести» данных, `gcTime` — время хранения неиспользуемых данных в кэше.

> [!question]- Как обновить данные после изменения на сервере?
> `invalidateQueries` для затронутых ключей или точечно `setQueryData`.

## Связанные темы

- [[N:3ea331048679815eb262f10acd0ec50e]]
- [[N:3ea331048679818fb89cd4c82a907497]]
