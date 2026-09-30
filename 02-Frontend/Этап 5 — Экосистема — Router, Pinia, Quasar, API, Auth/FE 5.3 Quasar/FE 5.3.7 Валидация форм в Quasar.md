---
type: topic
domain: frontend
stage: 5
section: "5.3"
order: 7
status: todo
level: middle
notion_id: 3ea33104867981a6ba83f0a29df4be37
tags: [domain/frontend, stage/5, level/middle, topic/quasar, topic/forms, topic/validation, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Валидация форм в Quasar

↑ [[FE 5.3 Quasar|5.3 Quasar]] · ← [[FE 5.3.6 Ключевые компоненты — QTable, QForm, QInput, QSelect, QDialog|Предыдущая]] · → [[FE 5.3.8 Quasar Plugins — Notify, Dialog, Loading, LocalStorage|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->


















> [!info] Зачем это на собесе
> Встроенная валидация Quasar и её границы; когда подключать VeeValidate.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

Поля Quasar принимают массив правил `rules`: функция возвращает `true` (валидно) или строку ошибки.

```vue
<script setup lang="ts">
const required = (v: unknown) => (v !== null && v !== undefined && v !== "") || "Обязательное поле";
const email = (v: string) => /^\S+@\S+\.\S+$/.test(v) || "Неверный email";
const minLen = (n: number) => (v: string) => (v?.length ?? 0) >= n || `Минимум ${n} символов`;
const uniqueLogin = async (v: string) => (await api.checkLogin(v)) || "Логин занят";      // асинхронные правила поддерживаются
const form = useTemplateRef<QForm>("form");

async function save() {
  if (!(await form.value!.validate())) return;                                 // валидация всей формы
  await api.save(model.value);
  form.value!.resetValidation();
}
</script>

<template>
  <q-form ref="form" greedy @submit.prevent="save">                            <!-- greedy: показать все ошибки, а не первую -->
    <q-input v-model="model.email" label="Email" :rules="[required, email]" lazy-rules="ondemand" :error="!!serverErrors.email" :error-message="serverErrors.email" />
    <q-input v-model="model.login" label="Логин" :rules="[required, uniqueLogin]" debounce="500" />
  </q-form>
</template>
```

| Возможность | Описание |
|---|---|
| `rules` | массив функций (синхронных/асинхронных) |
| `lazy-rules` | проверка при потере фокуса; `ondemand` — только при `validate()` |
| `hide-bottom-space`, `no-error-icon` | внешний вид |
| `error`/`error-message` | внешняя ошибка (сервер) |
| `QForm.validate()`, `resetValidation()`, `submit()`, `reset()` | управление |
| `greedy` | валидировать всё, не останавливаться на первой ошибке |
| `@validation-error` / `@validation-success` | события формы |

Серверные ошибки (422) отображайте через `error-message` по полям (см. [[N:3ea3310486798146aa7cd46cc1613ab6]] о ProblemDetails).

Ограничения встроенной валидации: правила размазаны по шаблону, нет схемы, сложно сделать зависимые поля и вложенные структуры, нет автоматической типизации — для сложных форм подключают схему (Zod) и VeeValidate (см. [[N:c0b760520d08405aa560ec038f0c7d5a]]).

## Нюансы и подводные камни

- Асинхронные правила без `debounce` создают лавину запросов.
- `rules` — массив функций, пересоздаваемый при каждом рендере: выносите в константы.
- Сообщения нужно локализовать (i18n).
- Валидация UX: не показывайте ошибки до взаимодействия пользователя.
- Проверка на клиенте не заменяет серверную.

## Практика

1. Реализуйте набор переиспользуемых правил и сообщений через i18n.
2. Добавьте асинхронную проверку уникальности с debounce.
3. Отобразите ошибки сервера по полям.

## Вопросы с ответами

> [!question]- Как работают `rules` в Quasar?
> Массив функций, возвращающих `true` или текст ошибки; выполняются при вводе/потере фокуса/`validate()`.

> [!question]- Что делает `greedy` у QForm?
> Проверяет все поля и показывает все ошибки, а не только первую.

## Связанные темы

- [[N:3ea331048679814db069fdc55fcbd725]]
- [[N:3ea3310486798181b78cc70995a735cc]]
