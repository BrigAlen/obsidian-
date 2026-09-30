---
type: topic
domain: frontend
stage: 1
section: "1.2"
order: 4
status: todo
level: junior
notion_id: 3ea33104867981408326d7b9cf34d28d
tags: [domain/frontend, stage/1, level/junior, topic/html, topic/images, topic/performance, priority/should]
reviewed:
next_review:
priority: should
time: 3
---

# Изображения и медиа: srcset, picture, lazy loading

↑ [[FE 1.2 HTML|1.2 HTML]] · ← [[FE 1.2.3 Загрузка скриптов — async, defer, module|Предыдущая]] · → [[FE 1.2.5 Доступность (a11y) и ARIA|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: junior</span></div>
<!-- meta:end -->













> [!info] Зачем это на собесе
> Изображения — основной вес страницы: важно уметь отдавать нужный размер и формат.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

```html
<!-- Адаптивные размеры: браузер выбирает подходящий файл -->
<img src="hero-800.jpg"
     srcset="hero-400.jpg 400w, hero-800.jpg 800w, hero-1600.jpg 1600w"
     sizes="(max-width: 600px) 100vw, 50vw"
     width="1600" height="900" alt="Описание" loading="lazy" decoding="async">

<!-- Разные форматы и «арт-дирекшн» -->
<picture>
  <source type="image/avif" srcset="hero.avif">
  <source type="image/webp" srcset="hero.webp">
  <source media="(max-width: 600px)" srcset="hero-mobile.jpg">
  <img src="hero.jpg" alt="Описание" width="1600" height="900">
</picture>
```

| Приём | Эффект |
|---|---|
| `srcset` + `sizes` | нужный размер под экран и плотность пикселей |
| `<picture>` | выбор формата (AVIF/WebP) и разные кадры |
| `loading="lazy"` | отложенная загрузка вне экрана (не для LCP-изображения) |
| `width`/`height` | резервирует место, нет сдвигов (CLS) |
| `decoding="async"`, `fetchpriority` | приоритеты для главного изображения |
| SVG | векторные иконки, стили через CSS |
| `<video>`, `<audio>` | `controls`, `preload`, `poster`, `playsinline`, несколько `source` |
| CDN и трансформации | ресайз, сжатие, форматы «на лету» |

Форматы: JPEG (фото), PNG (прозрачность), WebP/AVIF (лучше сжатие), SVG (иконки), GIF → видео `mp4/webm`.

## Нюансы и подводные камни

- `loading="lazy"` на главном изображении ухудшает LCP.
- Без размеров изображение сдвигает вёрстку при загрузке.
- `alt` обязателен: осмысленный для контента, пустой (`alt=""`) для декоративных.
- Огромные оригиналы на маленьких экранах — лишний трафик.
- Автовоспроизведение видео со звуком блокируется браузерами.

## Практика

1. Подготовьте три размера и форматы AVIF/WebP для изображения и подключите через `picture`.
2. Измерьте LCP до и после оптимизации.
3. Настройте lazy loading для галереи.

## Вопросы с ответами

> [!question]- Зачем `srcset` и `sizes`?
> Чтобы браузер выбрал файл под ширину области отображения и плотность экрана.

> [!question]- Когда не использовать `loading="lazy"`?
> Для изображений в первом экране, особенно LCP-элемента.

## Связанные темы

- [[N:3ea3310486798136a85bfe7fb3bfcefe]]
- [[N:3ea33104867981be928cde04d8f44c2f]]
