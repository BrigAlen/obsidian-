---
type: topic
domain: frontend
stage: 1
section: "1.2"
order: 6
status: todo
level: junior
notion_id: 3ea331048679811cb0cbccea1d34e59c
tags: [domain/frontend, stage/1, level/junior, topic/html, topic/seo, topic/meta, priority/should]
reviewed:
next_review:
priority: should
time: 3
---

# SEO и meta-теги

↑ [[FE 1.2 HTML|1.2 HTML]] · ← [[FE 1.2.5 Доступность (a11y) и ARIA|Предыдущая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: junior</span></div>
<!-- meta:end -->





























> [!info] Зачем это на собесе
> Фронтендер отвечает за техническое SEO: разметку, meta, скорость и рендеринг SPA.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

```html
<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Заказы — Мой сервис</title>
  <meta name="description" content="Управление заказами: список, фильтры, статусы.">
  <link rel="canonical" href="https://example.com/orders">
  <meta name="robots" content="index,follow">

  <!-- Open Graph / Twitter: превью при шаринге -->
  <meta property="og:title" content="Заказы">
  <meta property="og:description" content="...">
  <meta property="og:image" content="https://example.com/og.png">
  <meta name="twitter:card" content="summary_large_image">
  <link rel="icon" href="/favicon.svg">
</head>
```

| Элемент | Значение |
|---|---|
| `title` | заголовок в выдаче (до ~60 символов) |
| `description` | сниппет (до ~155 символов) |
| `canonical` | предпочтительный URL, устраняет дубли |
| `lang` | язык страницы |
| `robots`/`X-Robots-Tag` | индексация |
| `hreflang` | языковые версии |
| Структурированные данные (JSON-LD, schema.org) | расширенные сниппеты |
| `sitemap.xml`, `robots.txt` | обход сайта |

Техническое SEO: семантика (заголовки), скорость и Core Web Vitals, мобильная адаптация, чистые URL, корректные редиректы и коды (404, 301), отсутствие битых ссылок.

SPA и SEO: поисковики выполняют JS, но с задержкой; для важного контента — **SSR/SSG/prerender** (Nuxt, Vite SSG). Мета-теги в SPA обновляются через `vueuse/head`/`useHead`.

## Нюансы и подводные камни

- Один и тот же `title` на всех страницах SPA.
- Контент, доступный только после действий пользователя, не индексируется.
- Дубли страниц без canonical.
- Закрытие от индексации (`noindex`) в проде из-за скопированной конфигурации.
- Динамически обновляемые OG-теги не читаются ботами соцсетей без SSR.

## Практика

1. Проверьте страницу Lighthouse SEO и исправьте замечания.
2. Добавьте JSON-LD для страницы товара.
3. Настройте `useHead` для смены `title`/`description` на маршрутах SPA.

## Вопросы с ответами

> [!question]- Как SPA сделать SEO-дружелюбным?
> SSR/SSG/prerender критичных страниц и корректные meta-теги на каждом маршруте.

> [!question]- Для чего canonical?
> Указывает основной URL при нескольких адресах одного контента.

## Связанные темы

- [[N:3ea33104867981be928cde04d8f44c2f]]
- [[N:3ea33104867981f28130c63f1c1c9290]]
