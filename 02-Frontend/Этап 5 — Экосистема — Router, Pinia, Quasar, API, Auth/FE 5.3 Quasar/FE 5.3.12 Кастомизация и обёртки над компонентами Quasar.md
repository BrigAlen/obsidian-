---
type: topic
domain: frontend
stage: 5
section: "5.3"
order: 12
status: todo
level: middle
notion_id: 3ea33104867981059bb4e4c24f055d22
tags: [domain/frontend, stage/5, level/middle, topic/quasar, topic/components, topic/wrappers, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Кастомизация и обёртки над компонентами Quasar

↑ [[FE 5.3 Quasar|5.3 Quasar]] · ← [[FE 5.3.11 i18n|Предыдущая]] · → [[FE 5.3.13 Сложные формы — Quasar, VeeValidate и schema-driven validation|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> Как строить собственную дизайн-систему поверх Quasar и не дублировать настройки.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

Задачи обёрток: единые дефолты (outlined, dense), единая валидация и ошибки, интеграция с i18n, стабильный API при смене библиотеки.

```vue
<!-- BaseInput.vue: обёртка над QInput с прокидыванием атрибутов, слотов и ref -->
<script setup lang="ts">
import { QInput } from "quasar";
defineOptions({ inheritAttrs: false });
const props = defineProps<{ label: string; required?: boolean; error?: string }>();
const model = defineModel<string | number | null>();
const input = useTemplateRef<InstanceType<typeof QInput>>("input");
defineExpose({ focus: () => input.value?.focus(), validate: () => input.value?.validate() });
const { t } = useI18n();
const rules = computed(() => props.required ? [(v: unknown) => !!v || t("errors.required")] : []);
</script>
<template>
  <q-input ref="input" v-model="model" outlined dense lazy-rules :label="label" :rules="rules" :error="!!error" :error-message="error" v-bind="$attrs">
    <template v-for="(_, name) in $slots" #[name]="scope"><slot :name="name" v-bind="scope ?? {}" /></template>
  </q-input>
</template>
```

Приёмы:

| Приём | Как |
|---|---|
| Значения по умолчанию | пропсы обёртки + `v-bind="$attrs"` (последними, чтобы можно было переопределить) |
| Прокидывание слотов | итерация `$slots` |
| Прокидывание методов | `defineExpose` + `useTemplateRef` |
| Типы | `QInputProps` (`import type { QInputProps } from "quasar"`), `ExtractPropTypes` |
| Глобальные дефолты | `framework.config`: `defaults`/`extras` (через `app.config`/`Quasar.config`), плагин, CSS |
| Стили внутренних элементов | классы `.q-field__control`, `:deep(...)`, SASS-переменные |
| Расширение поведения | composables (`useFormField`), директивы |
| Библиотека компонентов | отдельный пакет `@company/ui` с Storybook и токенами |

Регистрация: авто-импорт компонентов проекта (`unplugin-vue-components`), префикс `App*`/`Base*`.

Документирование: Storybook, примеры состояний, доступность, визуальные тесты.

## Нюансы и подводные камни

- Обёртка не должна скрывать все возможности оригинала: прокидывайте `$attrs`, слоты, методы.
- Обновления Quasar меняют внутренние классы — минимизируйте зависимость от них.
- Не создавайте обёртку «на всякий случай»: она оправдана повторяющимися настройками.
- Потеря типизации при прокидывании — используйте типы Quasar.

## Практика

1. Сделайте `BaseInput`, `BaseSelect`, `BaseTable` с единым стилем и валидацией.
2. Пробросьте слоты и методы валидации.
3. Опишите компоненты в Storybook.

## Вопросы с ответами

> [!question]- Зачем обёртки над Quasar?
> Единые настройки и поведение, изоляция от библиотеки и общая дизайн-система.

> [!question]- Что важно при создании обёртки?
> Прокидывание `$attrs`, слотов и публичных методов, сохранение типов.

## Связанные темы

- [[N:3ea331048679814bbe6ef6cd309478ce]]
- [[N:c0b760520d08405aa560ec038f0c7d5a]]
