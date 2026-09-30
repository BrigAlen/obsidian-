---
type: topic
domain: frontend
stage: 7
section: "7.1"
order: 6
status: todo
level: senior
notion_id: 3ea331048679816181dbdfd6a2ea7195
tags: [domain/frontend, stage/7, level/senior, topic/vue, topic/performance, priority/should]
reviewed:
next_review:
priority: should
time: 3
---

# Оптимизация производительности во Vue

↑ [[FE 7.1 Vue под капотом|7.1 Vue под капотом]] · ← [[FE 7.1.5 Алгоритм diff и роль key|Предыдущая]] · → [[FE 7.1.7 Что нового в Vue 3.3–3.5+ (Vapor Mode)|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: senior</span></div>
<!-- meta:end -->






> [!info] Зачем это на собесе
> Практический вопрос: «приложение тормозит, что вы будете делать». Нужен порядок действий, а не список приёмов.

## Сначала измерить

Vue DevTools (Performance, Timeline), Chrome Performance, `app.config.performance = true`. Ищем: лишние рендеры, тяжёлые вычисления, большие списки.

## Приёмы

| Проблема | Решение |
|---|---|
| Лишние ре-рендеры детей | стабильные props, `defineProps` по точным полям, `computed` вместо инлайн-выражений |
| Большой объект реактивен зря | `shallowRef`, `markRaw`, `shallowReactive` |
| Длинный список | виртуализация (vue-virtual-scroller, `@tanstack/vue-virtual`) |
| Статичное поддерево | `v-once` |
| Дорогой блок в списке | `v-memo="[item.id, item.selected]"` |
| Тяжёлые компоненты | `defineAsyncComponent`, lazy routes |
| Дорогие вычисления | `computed` (кэш), вынос в Web Worker |
| Переключение вкладок | `<KeepAlive>` |
| Всплеск watch | `watchEffect` осторожно, debounce |

## Примеры

```vue
<div v-for="row in rows" :key="row.id" v-memo="[row.id, row.selected]">
  <ExpensiveRow :row="row" />
</div>
```

```ts
const HeavyChart = defineAsyncComponent(() => import('./HeavyChart.vue'))
```

## Ловушки

- computed с побочными эффектами или тяжёлым кодом, зависящим от многого;
- `v-if` и `v-show`: `v-if` дороже при частом переключении, но экономит первый рендер;
- передача новой функции или объекта в props при каждом рендере вызывает лишнее обновление ребёнка;
- глубокие `watch` на больших структурах.

## Вопросы с ответами

> [!question]- Что делать, если список из 10 тысяч строк тормозит?
> Виртуализация: рендерим только видимые строки. Затем `shallowRef` для данных, `v-memo` и стабильные ключи.

> [!question]- Чем v-memo отличается от computed?
> `v-memo` пропускает патчинг поддерева, если значения в массиве не изменились; `computed` кэширует значение выражения.
