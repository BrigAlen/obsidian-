---
type: topic
domain: frontend
stage: 7
section: "7.5"
order: 7
status: todo
level: senior
notion_id: dbf78bbe8db24308b9692aeddabde98b
tags: [domain/frontend, stage/7, level/senior, topic/ssr, topic/streaming, topic/edge, topic/cache, priority/should]
reviewed:
next_review:
priority: should
time: 3
---

# SSR глубже: streaming, кэширование и edge rendering

↑ [[FE 7.5 SSR и Nuxt|7.5 SSR и Nuxt]] · ← [[FE 7.5.6 SSR в Quasar|Предыдущая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: senior</span></div>
<!-- meta:end -->


> [!info] Зачем это на собесе
> Уровень senior: как снизить TTFB, что кэшировать и где выполнять рендеринг.

## Streaming SSR

Сервер отправляет HTML **по частям**, не дожидаясь всех данных. Браузер начинает парсить и рисовать оболочку раньше, тяжёлые блоки приходят позже.

```ts
import { renderToWebStream } from 'vue/server-renderer'
const stream = renderToWebStream(app)
return new Response(stream, { headers: { 'content-type': 'text/html' } })
```

Vue: `<Suspense>` + async setup — граница потоковой доставки. Улучшает TTFB и FCP; ограничения: заголовки и статус уже отправлены, ошибки внутри потока обрабатывать сложнее.

## Кэширование

| Уровень | Что | Как |
|---|---|---|
| CDN | целые страницы | `Cache-Control: s-maxage=60, stale-while-revalidate=300` |
| Сервер | результат рендера | кэш по URL (LRU), Nitro `cachedEventHandler` |
| Данные | ответы API | Redis, `swr`, `getCachedData` |
| Фрагменты | компоненты без персонализации | component caching |

Правила: персональный контент не кэшировать на общем уровне; ключ кэша учитывает язык, устройство, cookies; `Vary`; инвалидация по тегам или вебхукам.

```ts
export default defineCachedEventHandler(async () => getCatalog(), {
  maxAge: 60,
  staleMaxAge: 600,
  swr: true,
})
```

## Edge rendering

Рендер на серверах CDN рядом с пользователем (Cloudflare Workers, Vercel Edge, Deno Deploy). Плюсы: низкая задержка, быстрый холодный старт. Ограничения: нет полного Node API, ограничения по CPU и размеру, данные могут быть далеко от edge (сеть до БД), нужны HTTP-доступные хранилища и репликация.

## Оптимизация SSR

- минимум работы на сервере: параллельные запросы данных, кэш;
- пул и лимиты: SSR нагружает CPU, нужны таймауты и деградация в CSR при перегрузке;
- ленивая гидрация и острова снижают клиентскую стоимость;
- метрики: TTFB, время рендера, размер HTML, доля ошибок гидрации.

## Отказоустойчивость

- fallback на SPA при падении SSR;
- таймаут на данные, отдавать оболочку и догружать на клиенте;
- изоляция сторонних источников (circuit breaker).

## Вопросы с ответами

> [!question]- Зачем streaming SSR?
> Снижает время до первого байта и первого контента: пользователь видит оболочку, пока тяжёлые части ещё готовятся.

> [!question]- Что нельзя кэшировать на CDN при SSR?
> Персональные страницы и ответы с `Set-Cookie`; либо кэш с ключом по пользователю, либо клиентская догрузка персональных блоков.

> [!question]- Когда edge-рендеринг не подходит?
> Когда логика тяжёлая или зависит от Node API, а данные лежат в одном регионе: задержка до БД перекроет выигрыш.
