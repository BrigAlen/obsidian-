---
type: topic
domain: frontend
stage: 8
section: "8.2"
order: 4
status: todo
level: senior
notion_id: 3ea33104867981e898d4eea46726c80e
tags: [domain/frontend, stage/8, level/senior, topic/fsd, topic/architecture, priority/should]
reviewed:
next_review:
priority: should
time: 3
---

# Feature-Sliced Design

↑ [[FE 8.2 Архитектура фронтенда и паттерны|8.2 Архитектура фронтенда и паттерны]] · ← [[FE 8.2.3 Структура проекта — по типам и по фичам|Предыдущая]] · → [[FE 8.2.5 Разделение логики — компоненты, composables, сервисы, сторы|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: senior</span></div>
<!-- meta:end -->






> [!info] Зачем это на собесе
> FSD — популярная методология для крупных фронтенд-проектов; знание показывает системность.

## Слои (сверху вниз)

| Слой | Что содержит |
|---|---|
| `app` | инициализация, провайдеры, роутер, глобальные стили |
| `pages` | страницы (композиция виджетов) |
| `widgets` | крупные самостоятельные блоки (шапка, таблица заказов) |
| `features` | пользовательские сценарии (добавить в корзину, фильтр) |
| `entities` | бизнес-сущности (user, order, product) |
| `shared` | переиспользуемое без домена (ui-kit, api, lib, config) |

**Правило зависимостей**: слой импортирует только из слоёв **ниже**. Слайсы одного слоя не знают друг о друге.

## Сегменты

Внутри слайса: `ui`, `model`, `api`, `lib`, `config`. Публичный API — `index.ts`.

```text
features/
  add-to-cart/
    ui/AddToCartButton.vue
    model/useAddToCart.ts
    api/addToCart.ts
    index.ts
entities/
  product/
    ui/ProductCard.vue
    model/types.ts
    index.ts
```

## Плюсы

- единый язык в команде, предсказуемые места файлов;
- изоляция изменений, слабая связность;
- масштабируемость и удобный онбординг.

## Минусы и критика

- порог входа, споры «где слой»;
- лишняя церемония на небольших проектах;
- сложные случаи (связь двух entities) требуют решений;
- нужен линтер границ (`@feature-sliced/eslint-config`, steiger).

## Когда брать

Большое приложение с несколькими командами и долгой жизнью. Небольшим проектам хватит feature-структуры.

## Вопросы с ответами

> [!question]- Основное правило FSD?
> Слой может зависеть только от нижележащих; между слайсами одного слоя зависимостей нет; наружу — только через публичный API.

> [!question]- Чем features отличается от entities?
> Entities — бизнес-сущности и их представление. Features — действия пользователя над сущностями.
