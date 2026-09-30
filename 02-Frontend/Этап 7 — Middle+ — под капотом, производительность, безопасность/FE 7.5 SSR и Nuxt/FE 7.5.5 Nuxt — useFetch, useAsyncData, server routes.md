---
type: topic
domain: frontend
stage: 7
section: "7.5"
order: 5
status: todo
level: senior
notion_id: 3ea3310486798126aec0ed9244862d23
tags: [domain/frontend, stage/7, level/senior, topic/nuxt, topic/useFetch, topic/nitro, priority/should]
reviewed:
next_review:
priority: should
time: 4
---

# Nuxt: useFetch, useAsyncData, server routes

↑ [[FE 7.5 SSR и Nuxt|7.5 SSR и Nuxt]] · ← [[FE 7.5.4 Nuxt — структура, file-based routing, auto-imports|Предыдущая]] · → [[FE 7.5.6 SSR в Quasar|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~4 мин чтения</span><span class="chip">Уровень: senior</span></div>
<!-- meta:end -->


> [!info] Зачем это на собесе
> Загрузка данных в SSR: главное — не делать запрос дважды и передать состояние клиенту.

## useFetch и useAsyncData

```vue
<script setup lang="ts">
const { data: user, status, error, refresh } = await useFetch(`/api/users/${route.params.id}`, {
  key: `user-${route.params.id}`,
  server: true,
  lazy: false,
  watch: [() => route.params.id],
  transform: (u) => ({ ...u, name: u.name.trim() }),
})

const { data: stats } = await useAsyncData('stats', () => $fetch('/api/stats'))
</script>
```

- `useFetch(url)` — сокращение для `useAsyncData(key, () => $fetch(url))`;
- на сервере запрос выполняется, результат **сериализуется в payload** страницы, клиент берёт его без повторного запроса;
- `lazy: true` — не блокировать навигацию, показать состояние загрузки;
- `$fetch` — чистая утилита без дедупликации и payload (для событий, POST-действий на клиенте).

Типичная ошибка: вызов `$fetch` в `setup` напрямую → запрос выполнится дважды (сервер и клиент).

## Кэш и повторное использование

Ключ (`key`) дедуплицирует запросы; `getCachedData` управляет кэшем; `refreshNuxtData('key')`, `clearNuxtData`.

## Общее состояние

```ts
const token = useState<string | null>('token', () => null)   // безопасно для SSR, переносится клиенту
```

## Server routes (Nitro)

```ts
// server/api/users/[id].get.ts
export default defineEventHandler(async (event) => {
  const id = getRouterParam(event, 'id')
  const user = await db.users.find(id)
  if (!user) throw createError({ statusCode: 404, statusMessage: 'Not found' })
  return user
})
```

```ts
// server/api/orders.post.ts
export default defineEventHandler(async (event) => {
  const body = await readValidatedBody(event, orderSchema.parse)
  return await createOrder(body)
})
```

Применение: BFF (проксирование и агрегация бэкендов), скрытие секретов (ключи хранятся в `runtimeConfig` на сервере), обход CORS.

## runtimeConfig

```ts
export default defineNuxtConfig({
  runtimeConfig: {
    apiSecret: '',                 // только сервер
    public: { apiBase: '' },       // доступно и клиенту
  },
})
```

Значения переопределяются переменными `NUXT_API_SECRET`, `NUXT_PUBLIC_API_BASE` во время выполнения.

## Вопросы с ответами

> [!question]- Почему $fetch в setup выполнится дважды?
> На сервере и на клиенте при гидрации: нет передачи результата. `useFetch` и `useAsyncData` сохраняют результат в payload.

> [!question]- Чем useFetch отличается от useAsyncData?
> `useFetch` — обёртка для HTTP-запроса с автоматическим ключом, `useAsyncData` принимает произвольную асинхронную функцию.
