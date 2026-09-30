---
type: topic
domain: frontend
stage: 4
section: "4.1"
order: 25
status: todo
level: middle
notion_id: 3ea33104867981faaff2c0e3e99000ab
tags: [domain/frontend, stage/4, level/middle, topic/vue, topic/typescript, priority/must]
reviewed:
next_review:
priority: must
time: 4
---

# TypeScript во Vue: типизация props, emits, ref, generic-компоненты

↑ [[FE 4.1 Vue 3 — основы, компоненты, Composition API|4.1 Vue 3: основы, компоненты, Composition API]] · ← [[FE 4.1.24 Обработка ошибок — errorCaptured, app.config.errorHandler|Предыдущая]] · → [[FE 4.1.26 Отличия Vue 2 и Vue 3|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~4 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->

















> [!info] Зачем это на собесе
> Типобезопасность Vue-приложения: как типизировать компоненты и refs.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

```vue
<script setup lang="ts">
import type { PropType } from "vue";

// props: type-based
interface Props { items: Order[]; selected?: number | null; variant?: "primary" | "ghost" }
const props = withDefaults(defineProps<Props>(), { selected: null, variant: "primary" });

// emits: именованные кортежи
const emit = defineEmits<{ select: [id: number]; "update:selected": [id: number | null] }>();

// ref
const count = ref(0);                                   // Ref<number>
const user = ref<User | null>(null);                    // явный тип для «пусто/значение»
const el = useTemplateRef<HTMLInputElement>("input");
const list = ref<Order[]>([]);
const comp = shallowRef<InstanceType<typeof Modal> | null>(null);

// computed выводится, при необходимости явно
const total = computed<number>(() => props.items.reduce((s, i) => s + i.total, 0));

// provide/inject с InjectionKey, слоты
const slots = defineSlots<{ default(props: { item: Order }): any; empty(): any }>();
defineOptions({ name: "OrdersTable" });
</script>
```

**Generic-компоненты** (3.3+):

```vue
<script setup lang="ts" generic="T extends { id: number }, K extends keyof T">
defineProps<{ rows: T[]; columns: { key: K; title: string }[] }>();
defineEmits<{ rowClick: [row: T] }>();
</script>
<!-- <DataTable :rows="orders" :columns="[{ key: 'number', title: '№' }]" @row-click="(r) => r.id" />  — типы выводятся -->
```

Инструменты:

- **`vue-tsc`** — проверка типов `.vue` (в CI), Volar — поддержка в IDE.
- `tsconfig` с `"types": ["vite/client"]`, `verbatimModuleSyntax`, `strict`.
- Типы событий DOM: `(e: Event) => ...`, `MouseEvent`, приведение `e.target as HTMLInputElement`.
- `ComponentPublicInstance`, `InstanceType<typeof Comp>`, `ExtractPropTypes` для сложных случаев.
- `PropType<T>` для runtime-объявления `props` сложных типов.

Типизация Pinia и Router: типизированные сторы из коробки, `RouteMeta` через augmentation (см. [[N:3ea331048679817b8eecc9de531cdcaa]]).

## Нюансы и подводные камни

- Type-based `defineProps` нельзя импортировать сложные условные типы из внешних файлов (ограничения компилятора; в новых версиях улучшено).
- `ref(null)` без типа даёт `Ref<null>`.
- Реактивная деструктуризация props требует 3.5.
- Обработчики emit: событие, объявленное `update:x`, автоматически типизирует `v-model:x`.

## Практика

1. Типизируйте props, emits и слоты таблицы.
2. Напишите generic `SelectField<T>`.
3. Добавьте `vue-tsc --noEmit` в CI и исправьте ошибки.

## Вопросы с ответами

> [!question]- Как типизировать props в `<script setup>`?
> `defineProps<Props>()` с TS-интерфейсом и `withDefaults` для значений по умолчанию.

> [!question]- Что даёт `generic` в `<script setup>`?
> Параметризованные компоненты, где типы строк/колонок связаны между собой.

## Связанные темы

- [[N:3ea3310486798126a148ed51c5b0b006]]
- [[N:3ea33104867981ac9e4cf9d69605a89d]]
