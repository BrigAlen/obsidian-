---
type: topic
domain: frontend
stage: 4
section: "4.1"
order: 4
status: todo
level: middle
notion_id: 3ea3310486798159b099d64b024d840d
tags: [domain/frontend, stage/4, level/middle, topic/vue, topic/script-setup, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# script setup и макросы компилятора

↑ [[FE 4.1 Vue 3 — основы, компоненты, Composition API|4.1 Vue 3: основы, компоненты, Composition API]] · ← [[FE 4.1.3 Options API и Composition API|Предыдущая]] · → [[FE 4.1.5 Реактивность — ref, reactive, shallowRef, toRef, toRefs|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->






> [!info] Зачем это на собесе
> `<script setup>` — стандарт; вопросы про макросы (`defineProps`, `defineEmits`, `defineModel`) и почему их не нужно импортировать.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

`<script setup>` — синтаксический сахар для Composition API в SFC: код выполняется при создании компонента, все верхнеуровневые привязки (переменные, функции, импорты) доступны в шаблоне без `return`.

```vue
<script setup lang="ts">
import { ref } from "vue";
import OrderRow from "./OrderRow.vue";                      // компонент доступен в шаблоне без регистрации

interface Props { orders: Order[]; page?: number }
const props = withDefaults(defineProps<Props>(), { page: 1 });
const emit = defineEmits<{ select: [id: number]; "update:page": [page: number] }>();
const model = defineModel<string>("query", { default: "" });
defineOptions({ name: "OrdersTable", inheritAttrs: false });
defineExpose({ reset });                                    // публичный API компонента

const selected = ref<number | null>(null);
function reset() { selected.value = null; }
await Promise.resolve();                                     // top-level await → нужен <Suspense>
</script>
```

| Макрос | Назначение |
|---|---|
| `defineProps` | объявление props (типы выводятся из TS-интерфейса) |
| `defineEmits` | события |
| `defineModel` | `v-model` (props + emit) |
| `defineExpose` | что доступно через template ref |
| `defineOptions` | имя, `inheritAttrs` и др. |
| `defineSlots` | типизация слотов |
| `withDefaults` | значения по умолчанию для типизированных props |

Макросы — **compile-time**: компилятор преобразует их в обычные опции, импортировать их не нужно; аргументы не могут ссылаться на локальные переменные `setup` (кроме констант/импортов). Реактивная деструктуризация props (Vue 3.5) сохраняет реактивность: `const { page = 1 } = defineProps<Props>()`.

Отличие от `setup()`: компактнее, лучше производительность (шаблон компилируется в замыкание внутри `setup`), лучшая поддержка TS.

## Нюансы и подводные камни

- По умолчанию компонент «закрыт»: снаружи (через ref родителя) доступно только то, что в `defineExpose`.
- Нельзя использовать `export default` вместе с `<script setup>` (для этого второй обычный `<script>`).
- Дефолты объектов/массивов в `withDefaults` задаются фабриками.
- Для рекурсивных компонентов — имя файла или `defineOptions({ name })`.
- Директивы: локальные с префиксом `v` (`vFocus`).

## Практика

1. Объявите типизированные props, emits и `defineModel`.
2. Экспортируйте метод компонента через `defineExpose` и вызовите из родителя.
3. Используйте локальную директиву `vFocus`.

## Вопросы с ответами

> [!question]- Что такое макросы компилятора?
> Специальные функции (`defineProps` и др.), обрабатываемые при компиляции SFC и не требующие импорта.

> [!question]- Почему компонент на `<script setup>` «закрыт»?
> Его внутренние привязки не видны родителю без `defineExpose`.

## Связанные темы

- [[N:3ea33104867981d08201e00f96e273a7]]
- [[N:3ea33104867981d98f3ff4b0b75829f7]]
