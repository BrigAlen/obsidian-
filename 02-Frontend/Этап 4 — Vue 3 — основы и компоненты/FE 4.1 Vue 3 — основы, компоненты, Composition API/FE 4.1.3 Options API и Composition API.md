---
type: topic
domain: frontend
stage: 4
section: "4.1"
order: 3
status: todo
level: middle
notion_id: 3ea33104867981d08201e00f96e273a7
tags: [domain/frontend, stage/4, level/middle, topic/vue, topic/composition-api, topic/options-api, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Options API и Composition API

↑ [[FE 4.1 Vue 3 — основы, компоненты, Composition API|4.1 Vue 3: основы, компоненты, Composition API]] · ← [[FE 4.1.2 Директивы — v-if и v-show, v-for и key, v-bind, v-on, v-model|Предыдущая]] · → [[FE 4.1.4 script setup и макросы компилятора|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->









> [!info] Зачем это на собесе
> Ждут аргументированного сравнения: почему Composition API стал рекомендуемым.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

**Options API**: код организован по опциям `data`, `methods`, `computed`, `watch`, хуки.

```js
export default {
  props: { userId: Number },
  data: () => ({ user: null, loading: false }),
  computed: { fullName() { return `${this.user?.first} ${this.user?.last}`; } },
  watch: { userId: { immediate: true, handler: "load" } },
  methods: { async load() { this.loading = true; this.user = await api.user(this.userId); this.loading = false; } },
  mounted() { /* ... */ },
};
```

**Composition API** (`setup`/`<script setup>`): логика группируется по смыслу и выносится в функции (composables).

```vue
<script setup lang="ts">
const props = defineProps<{ userId: number }>();
const { user, loading } = useUser(() => props.userId);      // вся логика в одном composable
const fullName = computed(() => `${user.value?.first} ${user.value?.last}`);
</script>
```

| Критерий | Options API | Composition API |
|---|---|---|
| Организация | по типам опций | по логическим задачам |
| Переиспользование | миксины (конфликты имён, неявные источники) | composables (явные, типизируемые) |
| TypeScript | ограниченно | отлично |
| Порог входа | ниже | выше (реактивность `ref`) |
| `this` | есть | нет |
| Размер бандла | чуть больше | лучше tree-shaking и минификация |
| Крупные компоненты | «размазывается» по опциям | компактнее |

Можно смешивать в рамках одного компонента (`setup()` + опции). Для новых проектов — **`<script setup>`**.

Причины появления Composition API: ограничения миксинов, слабая типизация, разрозненность логики в больших компонентах.

## Нюансы и подводные камни

- Composition API не «лучше во всём»: для простых компонентов Options API читаем.
- Не превращайте `setup` в свалку: выносите логику в composables.
- Реактивность `ref` требует `.value` в скрипте (в шаблоне разворачивается).
- В миграции Vue 2 → 3 Options API продолжает работать.

## Практика

1. Перепишите компонент с Options API на `<script setup>`.
2. Вынесите повторяющуюся логику двух компонентов в composable.
3. Сравните TS-поддержку в обоих подходах.

## Вопросы с ответами

> [!question]- Зачем Composition API?
> Организация кода по смыслу, лучшее переиспользование (composables вместо миксинов) и типизация.

> [!question]- Чем composable лучше mixin?
> Явные зависимости и возвращаемые значения, нет конфликтов имён, легко типизировать.

## Связанные темы

- [[N:3ea3310486798105b2c2db4cab84b0c5]]
- [[N:3ea3310486798159b099d64b024d840d]]
