---
type: topic
domain: frontend
stage: 8
section: "8.4"
order: 3
status: todo
level: senior
notion_id: 3ea33104867981e09ad8d47003170fd6
tags: [domain/frontend, stage/8, level/senior, topic/system-design, topic/pagination, topic/api, priority/should]
reviewed:
next_review:
priority: should
time: 3
---

# Пагинация: offset, cursor, infinite scroll

↑ [[FE 8.4 Frontend System Design|8.4 Frontend System Design]] · ← [[FE 8.4.2 Модель данных и нормализация состояния|Предыдущая]] · → [[FE 8.4.4 Real-time — чат, уведомления|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: senior</span></div>
<!-- meta:end -->




> [!info] Зачем это на собесе
> Один из самых частых блоков в дизайне лент и таблиц.

## Способы

| Способ | Запрос | Плюсы | Минусы |
|---|---|---|---|
| **Offset/limit** | `?offset=40&limit=20` (или `page`) | произвольный переход на страницу, просто | дубли и пропуски при вставках, медленно на больших offset (БД), нужен total |
| **Cursor (keyset)** | `?after=<cursor>&limit=20` | стабильно при изменениях, быстро на больших данных | нельзя прыгнуть на страницу N |
| **Time-based / id-based** | `?since=ts` | инкрементальная загрузка | привязка к порядку |

## Cursor

Ответ содержит `nextCursor`; курсор — непрозрачная строка (закодированные значения сортировки + id).

```json
{ "items": [...], "nextCursor": "eyJpZCI6MTIzfQ", "hasMore": true }
```

## Клиентские паттерны

- **Страницы** (номера): таблицы админки, нужен переход по номеру;
- **«Показать ещё»**: явное действие, хороший контроль;
- **Infinite scroll**: `IntersectionObserver` на sentinel, подгрузка при приближении к концу;
- **Виртуализация** при больших массивах в DOM;
- **Двунаправленная** (чат): подгрузка вверх с сохранением позиции.

```ts
const { data, fetchNextPage, hasNextPage } = useInfiniteQuery({
  queryKey: ['feed'],
  queryFn: ({ pageParam }) => api.feed({ cursor: pageParam }),
  initialPageParam: undefined as string | undefined,
  getNextPageParam: (last) => last.nextCursor,
})
```

## Нюансы infinite scroll

- потеря позиции при возврате (восстановление скролла, кэш);
- доступ к футеру и поиск по странице;
- доступность: клавиатура, объявление загрузки;
- дедупликация элементов, если данные сдвинулись;
- индикаторы: loading, пусто, ошибка с повтором;
- SEO: страницы с URL для индексации.

## Как выбрать

| Сценарий | Выбор |
|---|---|
| Таблица с переходом по номеру, стабильные данные | offset |
| Лента, чат, активные вставки | cursor |
| Мобильный список | infinite scroll + cursor |
| Отчёт с фильтрами | серверные фильтры + offset/cursor |

## Вопросы с ответами

> [!question]- Почему cursor лучше offset на активных данных?
> Offset «плывёт» при вставках и удалениях (дубли и пропуски), cursor привязан к последнему элементу и стабилен; ещё быстрее на больших таблицах.

> [!question]- Как не потерять позицию при возврате на список?
> Хранить кэш страниц (Query), восстановить скролл (scrollRestoration, сохранение offset), либо хранить страницу и фильтры в URL.
