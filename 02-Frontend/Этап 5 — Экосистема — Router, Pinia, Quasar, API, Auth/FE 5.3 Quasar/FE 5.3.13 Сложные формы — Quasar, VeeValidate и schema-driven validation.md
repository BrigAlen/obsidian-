---
type: topic
domain: frontend
stage: 5
section: "5.3"
order: 13
status: todo
level: middle
notion_id: c0b760520d08405aa560ec038f0c7d5a
tags: [domain/frontend, stage/5, level/middle, topic/quasar, topic/forms, topic/vee-validate, topic/zod, priority/must]
reviewed:
next_review:
priority: must
time: 4
---

# Сложные формы: Quasar, VeeValidate и schema-driven validation

↑ [[FE 5.3 Quasar|5.3 Quasar]] · ← [[FE 5.3.12 Кастомизация и обёртки над компонентами Quasar|Предыдущая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~4 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->













> [!info] Зачем это на собесе
> Для больших форм (вложенные структуры, зависимые поля, массивы) нужна схема, а не десятки inline-правил.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

**Схема-first**: правила описываются в одной схеме (Zod/Valibot/Yup), а форма получает валидацию, типы и значения по умолчанию.

```ts
import { useForm, useFieldArray } from "vee-validate";
import { toTypedSchema } from "@vee-validate/zod";
import { z } from "zod";

const schema = toTypedSchema(z.object({
  customer: z.object({ name: z.string().min(2, "Минимум 2 символа"), email: z.string().email("Неверный email") }),
  delivery: z.enum(["pickup", "courier"]),
  address: z.string().optional(),
  items: z.array(z.object({ sku: z.string().min(1), qty: z.number().int().min(1) })).min(1, "Добавьте позицию"),
}).superRefine((v, ctx) => {                                        // кросс-полевые проверки
  if (v.delivery === "courier" && !v.address) ctx.addIssue({ code: "custom", path: ["address"], message: "Укажите адрес" });
}));

const { handleSubmit, errors, defineField, setErrors, meta, isSubmitting, resetForm } = useForm({ validationSchema: schema, initialValues: { items: [{ sku: "", qty: 1 }] } });
const [name, nameAttrs] = defineField("customer.name", { validateOnModelUpdate: false });
const { fields: items, push, remove } = useFieldArray<{ sku: string; qty: number }>("items");

const onSubmit = handleSubmit(async (values) => {                    // values типизированы по схеме
  try { await api.createOrder(values); } catch (e) { setErrors(mapServerErrors(e)); }
});
```

```vue
<q-form @submit.prevent="onSubmit">
  <q-input v-model="name" v-bind="nameAttrs" label="Имя" :error="!!errors['customer.name']" :error-message="errors['customer.name']" />
  <div v-for="(f, i) in items" :key="f.key">
    <q-input v-model.number="f.value.qty" type="number" :error-message="errors[`items[${i}].qty`]" :error="!!errors[`items[${i}].qty`]" />
    <q-btn icon="delete" @click="remove(i)" />
  </div>
  <q-btn label="Добавить" @click="push({ sku: '', qty: 1 })" />
  <q-btn type="submit" color="primary" :loading="isSubmitting" :disable="!meta.dirty" />
</q-form>
```

Возможности: состояния (`dirty`, `touched`, `valid`, `pending`), вложенные объекты и массивы, зависимые поля, серверные ошибки (`setErrors`), сброс/восстановление, `defineField` с компонентными атрибутами.

Практики:

- Одна схема на форму, повторно используемая на клиенте и (по возможности) синхронизированная с бэкендом (OpenAPI → Zod).
- Значения по умолчанию — часть модели; нормализация данных до отправки (`z.coerce`, `.transform`).
- Защита от потери данных: предупреждение при уходе (`onBeforeRouteLeave` и `meta.dirty`).
- Автосохранение черновика (debounce) в стор/`localStorage`.
- Доступность: связывание ошибок с полями (`aria-describedby`), фокус на первом ошибочном поле после submit.
- Мастер-формы (stepper): валидация по шагам через `validate({ mode })`/отдельные схемы.

Альтернативы: FormKit, Vuelidate (валидация без схем), TanStack Form, `@formkit/...`.

## Нюансы и подводные камни

- Расхождение схемы клиента и правил сервера — согласуйте контракт.
- Слишком частая валидация при каждом вводе раздражает: `validateOnModelUpdate: false`, валидация при `blur`.
- Массивы: используйте стабильные `key` (`f.key`), не индекс.
- Большие схемы замедляют ввод: разбивайте на части.
- Тестируйте форму через Testing Library (заполнение → submit → ошибки).

## Практика

1. Соберите форму заказа с вложенным объектом, массивом позиций и зависимым полем адреса.
2. Подключите отображение ошибок сервера по полям.
3. Добавьте защиту от потери несохранённых данных и автосохранение черновика.

## Вопросы с ответами

> [!question]- Зачем схема для валидации формы?
> Единое описание правил, типы значений, поддержка вложенности и кросс-полевых проверок, повторное использование.

> [!question]- Как показать ошибки, пришедшие с сервера?
> Преобразовать ответ в `{ путь: сообщение }` и передать в `setErrors`.

## Связанные темы

- [[N:3ea33104867981059bb4e4c24f055d22]]
- [[N:3ea3310486798111bac4ca5217597700]]
