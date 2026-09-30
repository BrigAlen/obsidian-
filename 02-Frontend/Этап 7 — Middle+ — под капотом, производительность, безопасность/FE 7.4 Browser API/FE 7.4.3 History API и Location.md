---
type: topic
domain: frontend
stage: 7
section: "7.4"
order: 3
status: todo
level: senior
notion_id: 3ea331048679814294ddf786f670b7b5
tags: [domain/frontend, stage/7, level/senior, topic/browser-api, topic/history, topic/routing, priority/should]
reviewed:
next_review:
priority: should
time: 3
---

# History API и Location

↑ [[FE 7.4 Browser API|7.4 Browser API]] · ← [[FE 7.4.2 requestAnimationFrame и requestIdleCallback|Предыдущая]] · → [[FE 7.4.4 File API, Blob, FileReader, загрузка файлов|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: senior</span></div>
<!-- meta:end -->





> [!info] Зачем это на собесе
> На этом построены SPA-роутеры. Спрашивают, как работает переход без перезагрузки.

## History API

```ts
history.pushState({ page: 2 }, '', '/catalog?page=2')   // добавляет запись, без перезагрузки
history.replaceState({}, '', '/catalog')                // заменяет текущую
history.back(); history.forward(); history.go(-2)

window.addEventListener('popstate', e => {
  // кнопки «назад/вперёд» и history.go; НЕ вызывается на pushState
  render(location.pathname, e.state)
})
```

`pushState` **не** вызывает `popstate` и не грузит страницу: роутер сам рисует нужный экран.

## Location

```ts
location.href      // полный URL
location.pathname  // /catalog
location.search    // ?page=2
location.hash      // #section
location.assign(url)   // переход с записью в историю
location.replace(url)  // без записи
location.reload()

const params = new URLSearchParams(location.search)
params.get('page')
```

## Режимы Vue Router

| Режим | URL | Требование |
|---|---|---|
| `createWebHistory` | `/catalog/1` | сервер должен отдавать `index.html` на любой путь (fallback) |
| `createWebHashHistory` | `/#/catalog/1` | не нужен серверный fallback |

## Нюансы

- `hashchange` для hash-режима;
- состояние в URL (фильтры, страница) — ссылка делится и переживает перезагрузку;
- `scrollRestoration = 'manual'` и `scrollBehavior` в роутере;
- Navigation API — современная замена части History API.

## Вопросы с ответами

> [!question]- Как SPA меняет URL без перезагрузки?
> `history.pushState` меняет адрес и историю, роутер слушает изменения и рендерит соответствующий компонент.

> [!question]- Почему при обновлении страницы SPA-роут даёт 404?
> Сервер ищет файл по этому пути. Нужен fallback на `index.html` (`try_files` в nginx) при history-режиме.
