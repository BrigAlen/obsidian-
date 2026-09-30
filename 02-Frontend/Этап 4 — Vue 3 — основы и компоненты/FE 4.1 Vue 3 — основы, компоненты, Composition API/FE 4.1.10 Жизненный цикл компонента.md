---
type: topic
domain: frontend
stage: 4
section: "4.1"
order: 10
status: todo
level: middle
notion_id: 3ea3310486798154aaa2c3a16e62edaf
tags: [domain/frontend, stage/4, level/middle, topic/vue, topic/lifecycle, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Жизненный цикл компонента

↑ [[FE 4.1 Vue 3 — основы, компоненты, Composition API|4.1 Vue 3: основы, компоненты, Composition API]] · ← [[FE 4.1.9 Потеря реактивности и частые ошибки|Предыдущая]] · → [[FE 4.1.11 Props и emits, однонаправленный поток данных|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> Порядок хуков и что можно делать в каждом; связь с родителем и потомками.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

| Хук (Composition) | Options | Когда | Типичное использование |
|---|---|---|---|
| `setup()` | `beforeCreate/created` | создание компонента | объявление состояния, watchers |
| `onBeforeMount` | `beforeMount` | перед первым рендером | редко |
| `onMounted` | `mounted` | после вставки в DOM | доступ к DOM, подписки, запросы, инициализация библиотек |
| `onBeforeUpdate` | `beforeUpdate` | перед обновлением DOM | чтение DOM до изменений |
| `onUpdated` | `updated` | после обновления DOM | доступ к обновлённому DOM (осторожно с циклами) |
| `onBeforeUnmount` | `beforeUnmount` | перед удалением | подготовка |
| `onUnmounted` | `unmounted` | после удаления | очистка таймеров, слушателей, подписок |
| `onErrorCaptured` | `errorCaptured` | ошибка в потомке | перехват ошибок |
| `onActivated/onDeactivated` | `activated/deactivated` | в `KeepAlive` | обновление данных при показе |
| `onRenderTracked/Triggered` | | отладка | |
| `onServerPrefetch` | | SSR | загрузка данных на сервере |

Порядок для родителя и потомка:

```text
Создание:   parent setup → parent beforeMount → child setup → child beforeMount → child mounted → parent mounted
Обновление: parent beforeUpdate → child beforeUpdate → child updated → parent updated
Удаление:   parent beforeUnmount → child beforeUnmount → child unmounted → parent unmounted
```

```vue
<script setup>
const el = useTemplateRef("chart");
let chart;
onMounted(() => { chart = new Chart(el.value, options); });
onUnmounted(() => chart?.destroy());
</script>
```

Хуки можно вызывать только синхронно внутри `setup` (в composable, вызванном из `setup`). Composable, использующий хуки, должен вызываться в контексте компонента.

Запросы: в `setup`/`onMounted` (клиент); для SSR — `onServerPrefetch`/`useAsyncData` (Nuxt).

## Нюансы и подводные камни

- `mounted` потомков вызываются до родительского.
- DOM доступен только после `onMounted`; после изменения данных — после `nextTick`.
- Забытая очистка в `onUnmounted` — утечки.
- Изменение состояния в `onUpdated` вызывает бесконечные циклы.
- Хуки после `await` в `setup` теряют контекст (используйте `withAsyncContext`/`<script setup>` с top-level await корректно).

## Практика

1. Залогируйте порядок хуков родителя и двух потомков.
2. Инициализируйте и уничтожьте сторонний график в `onMounted/onUnmounted`.
3. Обновляйте данные при возврате в `KeepAlive`.

## Вопросы с ответами

> [!question]- Где безопасно обращаться к DOM?
> В `onMounted` и позже (после `nextTick` при изменении данных).

> [!question]- В каком порядке вызываются `mounted` родителя и потомка?
> Сначала потомка, затем родителя.

## Связанные темы

- [[N:3ea331048679815986d3d9f36b0a885b]]
- [[N:3ea33104867981298ee7da62c03689a1]]
