---
type: topic
domain: frontend
stage: 3
section: "3.1"
order: 19
status: todo
level: middle
notion_id: cf701e59e7894adfb9428fd9c9678d93
tags: [domain/frontend, stage/3, level/middle, topic/typescript, topic/validation, topic/zod, priority/must]
reviewed:
next_review:
priority: must
time: 4
---

# Runtime-валидация данных: Zod, Valibot и границы TypeScript

↑ [[FE 3.1 TypeScript — от базовых типов к продвинутым|3.1 TypeScript: от базовых типов к продвинутым]] · ← [[FE 3.1.18 Задачи на TypeScript|Предыдущая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~4 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->














> [!info] Зачем это на собесе
> «TypeScript гарантирует типы?» — нет, только в компиляции. На границах (API, формы, localStorage) нужна проверка в рантайме.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

Типы TS стираются: данные из сети, `JSON.parse`, форм, URL, `localStorage`, `postMessage` приходят как `unknown`. `as User` не проверяет ничего.

**Схема-first**: описываем схему один раз и получаем и валидатор, и тип.

```ts
import { z } from "zod";

const OrderSchema = z.object({
  id: z.number().int().positive(),
  status: z.enum(["new", "paid", "cancelled"]),
  total: z.coerce.number().nonnegative(),
  createdAt: z.string().datetime(),
  items: z.array(z.object({ sku: z.string().min(1), qty: z.number().int().min(1) })).min(1),
  note: z.string().max(500).optional(),
});
type Order = z.infer<typeof OrderSchema>;                   // тип выводится из схемы

async function getOrder(id: number): Promise<Order> {
  const res = await fetch(`/api/orders/${id}`);
  return OrderSchema.parse(await res.json());               // бросает ZodError при несоответствии
}

const r = OrderSchema.safeParse(input);
if (!r.success) console.log(r.error.flatten().fieldErrors); else use(r.data);
```

| Библиотека | Особенности |
|---|---|
| Zod | самая распространённая, богатый API, `infer`, трансформации |
| Valibot | модульная (tree-shaking), очень маленький размер |
| ArkType, Yup, io-ts, TypeBox | альтернативы (TypeBox — JSON Schema) |

Где применять:

- Ответы API (особенно сторонних), особенно при подтверждении контрактов.
- Формы (VeeValidate + Zod, `@vee-validate/zod`), URL/query-параметры роутера.
- Конфигурация окружения (`import.meta.env`).
- Данные из `localStorage`, `postMessage`, WebSocket.

Дополнительные возможности: `.transform`, `.refine/superRefine` (кросс-полевые проверки), `discriminatedUnion`, значения по умолчанию, `strict()` (запрет лишних полей), генерация схем из OpenAPI (Orval, `openapi-zod-client`).

## Нюансы и подводные камни

- Проверка стоит CPU: не валидируйте огромные ответы на горячем пути без необходимости.
- Схема и OpenAPI/бэкенд могут расходиться: генерируйте схемы из контракта.
- Ошибки валидации нужно превращать в понятные сообщения формы.
- Избегайте дублирования: тип выводится из схемы (`z.infer`), а не пишется отдельно.
- Слишком строгая валидация внешнего API ломает приложение при добавлении поля на сервере (используйте `passthrough`/нестрогий режим для входящих данных).

## Практика

1. Замените `as Order` на `OrderSchema.parse` в API-слое.
2. Свяжите Zod со схемой формы (`toTypedSchema`) во Vue.
3. Провалидируйте `import.meta.env` при старте приложения.

## Вопросы с ответами

> [!question]- Почему `as Type` не защищает?
> Это утверждение для компилятора, оно не проверяет данные во время выполнения.

> [!question]- Зачем runtime-валидация, если есть TS?
> Типы существуют только на этапе компиляции, а данные снаружи не проверены; схема защищает границы приложения.

> [!question]- Что даёт `z.infer`?
> Тип, выведенный из схемы — один источник истины для валидатора и типа.

## Связанные темы

- [[N:3ea331048679819c9b56f7afc4868cd5]]
- [[N:3ea331048679811d86f8f287c4b108ec]]
