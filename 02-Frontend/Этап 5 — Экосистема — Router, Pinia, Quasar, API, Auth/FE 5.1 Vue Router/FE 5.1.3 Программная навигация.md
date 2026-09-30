---
type: topic
domain: frontend
stage: 5
section: "5.1"
order: 3
status: todo
level: middle
notion_id: 3ea3310486798194982ef8547def2804
tags: [domain/frontend, stage/5, level/middle, topic/vue, topic/router, topic/navigation, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Программная навигация

↑ [[FE 5.1 Vue Router|5.1 Vue Router]] · ← [[FE 5.1.2 Динамические и вложенные маршруты|Предыдущая]] · → [[FE 5.1.4 Navigation guards|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->


















> [!info] Зачем это на собесе
> `push` против `replace`, обработка результата навигации и передача состояния.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

```ts
const router = useRouter();

router.push("/orders");
router.push({ name: "order", params: { id: 5 }, query: { tab: "items" }, hash: "#comments" });
router.replace({ name: "login" });          // без записи в историю (кнопка «назад» не вернёт)
router.go(-1); router.back(); router.forward();

const failure = await router.push({ name: "order", params: { id } });     // NavigationFailure или undefined
if (isNavigationFailure(failure, NavigationFailureType.duplicated)) { /* уже здесь */ }

// Обновление query без перезагрузки данных
router.replace({ query: { ...route.query, page: 2 } });
```

| Метод | Особенности |
|---|---|
| `push` | добавляет запись в историю |
| `replace` | заменяет текущую |
| `go(n)`, `back`, `forward` | перемещение по истории |
| `resolve(to)` | получить `href`/`route` без перехода |
| `router.currentRoute` | реактивный текущий маршрут |
| `router.addRoute/removeRoute` | динамические маршруты (например, по правам) |

Передача данных: `params` (в пути), `query` (для фильтров, сортировки, пагинации — сохраняется в URL и ссылке), `state` (History state, не в URL, только для внутренних случаев). Не передавайте сложные объекты через `params`.

Состояние страницы в URL: фильтры/страница/сортировка в `query` делают ссылки шаринговыми и кнопку «назад» осмысленной; VueUse `useRouteQuery`.

Редиректы после логина: `router.push(route.query.redirect as string || "/")` (валидируйте `redirect` — защита от open redirect).

## Нюансы и подводные камни

- Повторный переход на тот же маршрут возвращает `NavigationFailure` (не исключение).
- `push` с `path` игнорирует `params`: используйте `name`.
- Гонка нескольких `push` подряд: побеждает последний.
- Открытые редиректы: проверяйте, что путь относительный.
- Query-значения всегда строки; массивы для повторяющихся ключей.

## Практика

1. Синхронизируйте фильтры таблицы с query-параметрами.
2. Реализуйте редирект на исходную страницу после логина.
3. Динамически добавьте маршруты по ролям через `addRoute`.

## Вопросы с ответами

> [!question]- `push` или `replace`?
> `push` добавляет запись в историю, `replace` заменяет текущую (например, после логина или для обновления query).

> [!question]- Зачем хранить фильтры в query?
> Состояние сохраняется в ссылке и при обновлении, работает «назад/вперёд» и шаринг.

## Связанные темы

- [[N:3ea3310486798144b803e92c11aa8054]]
- [[N:3ea33104867981d095e9fddd500a9f0e]]
