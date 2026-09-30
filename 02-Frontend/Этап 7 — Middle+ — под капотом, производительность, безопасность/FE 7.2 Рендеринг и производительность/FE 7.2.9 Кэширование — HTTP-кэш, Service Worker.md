---
type: topic
domain: frontend
stage: 7
section: "7.2"
order: 9
status: todo
level: senior
notion_id: 3ea3310486798173b736dc31fad89790
tags: [domain/frontend, stage/7, level/senior, topic/cache, topic/http, topic/service-worker, priority/should]
reviewed:
next_review:
priority: should
time: 3
---

# Кэширование: HTTP-кэш, Service Worker

↑ [[FE 7.2 Рендеринг и производительность|7.2 Рендеринг и производительность]] · ← [[FE 7.2.8 Мемоизация и лишние ре-рендеры|Предыдущая]] · → [[FE 7.2.10 Инструменты — DevTools Performance, Lighthouse, Vue DevTools|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: senior</span></div>
<!-- meta:end -->




> [!info] Зачем это на собесе
> Кэширование даёт самое большое ускорение повторных визитов; спрашивают заголовки и стратегии.

## HTTP-кэш

| Заголовок | Смысл |
|---|---|
| `Cache-Control: max-age=31536000, immutable` | хранить год, не перепроверять (хэшированные файлы) |
| `Cache-Control: no-cache` | можно хранить, но перед использованием проверить |
| `Cache-Control: no-store` | не хранить вообще (чувствительные данные) |
| `ETag` / `If-None-Match` | условный запрос, ответ `304 Not Modified` |
| `Last-Modified` | то же по времени |
| `stale-while-revalidate=60` | отдать устаревшее, обновить в фоне |

Схема: HTML — `no-cache`, JS/CSS/картинки с хэшем — `immutable` на год, API — по ситуации.

## Service Worker

Скрипт между приложением и сетью. Перехватывает `fetch`, хранит ответы в Cache API.

Стратегии:

- **Cache First** — статика, шрифты;
- **Network First** — HTML, данные, где важна свежесть;
- **Stale While Revalidate** — быстро и обновляется;
- **Network Only** и **Cache Only**.

```ts
self.addEventListener('fetch', (e: FetchEvent) => {
  if (e.request.destination === 'image') {
    e.respondWith(
      caches.open('img-v1').then(async cache => {
        const hit = await cache.match(e.request)
        return hit ?? fetch(e.request).then(r => { cache.put(e.request, r.clone()); return r })
      }),
    )
  }
})
```

Инструмент: **Workbox** (`vite-plugin-pwa`).

## Нюансы

- обновление SW: `skipWaiting` и `clients.claim`, уведомление «доступна новая версия»;
- версия кэша, чистка старого;
- не кэшировать POST и авторизованные ответы без явной политики;
- кэш данных на клиенте: TanStack Query, SWR-подход.

## Вопросы с ответами

> [!question]- Как раздавать SPA, чтобы обновления доходили, а кэш работал?
> `index.html` с `no-cache`, статические файлы с хэшем в имени и `immutable`. Новый релиз меняет хэши, index ссылается на них.

> [!question]- Что такое stale-while-revalidate?
> Стратегия: сразу отдаём кэш, параллельно обновляем в фоне, пользователь видит быстрый ответ и получает свежие данные при следующем обращении.
