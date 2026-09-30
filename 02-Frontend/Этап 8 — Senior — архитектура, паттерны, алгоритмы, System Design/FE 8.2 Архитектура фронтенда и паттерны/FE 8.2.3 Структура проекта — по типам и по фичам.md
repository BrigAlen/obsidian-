---
type: topic
domain: frontend
stage: 8
section: "8.2"
order: 3
status: todo
level: senior
notion_id: 3ea33104867981e79fbdc15efbd42ca7
tags: [domain/frontend, stage/8, level/senior, topic/structure, topic/architecture, priority/should]
reviewed:
next_review:
priority: should
time: 3
---

# Структура проекта: по типам и по фичам

↑ [[FE 8.2 Архитектура фронтенда и паттерны|8.2 Архитектура фронтенда и паттерны]] · ← [[FE 8.2.2 Паттерны проектирования во фронтенде|Предыдущая]] · → [[FE 8.2.4 Feature-Sliced Design|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: senior</span></div>
<!-- meta:end -->


> [!info] Зачем это на собесе
> Организация кода влияет на скорость разработки; спрашивают, как вы масштабируете структуру.

## По типам (layer-based)

```text
src/
  components/
  composables/
  stores/
  services/
  views/
  utils/
```

Плюсы: просто, привычно для небольших проектов. Минусы: одна фича размазана по 5 папкам, растут «свалки» (`components` на 300 файлов), трудно вынести фичу.

## По фичам (feature-based)

```text
src/
  features/
    orders/
      components/
      composables/
      api.ts
      store.ts
      types.ts
      index.ts       # публичный API фичи
    users/
  shared/
    ui/
    lib/
    api/
  app/
```

Плюсы: всё по теме рядом, легко удалить или вынести, командные границы. Минусы: нужна дисциплина по общему коду.

## Правила

- фича не импортирует **внутренности** другой фичи, только её `index.ts`;
- общее в `shared`, а доменное — в фичах;
- запрет циклических импортов (`import/no-cycle`);
- границы проверять линтером (`eslint-plugin-boundaries`, `dependency-cruiser`);
- алиасы (`@/features/orders`).

## Гибрид

Общие UI-компоненты — по типам в `shared/ui`, домен — по фичам.

## Когда что

| Размер | Выбор |
|---|---|
| Маленький проект | по типам |
| Средний, несколько разработчиков | по фичам |
| Большой, несколько команд | FSD или monorepo с пакетами |

## Вопросы с ответами

> [!question]- Почему по фичам лучше при росте?
> Изменение затрагивает одну папку, ясные границы, проще владение командой и ленивая загрузка по фиче.

> [!question]- Как не превратить shared в свалку?
> Ввести правило: в shared только то, что нужно минимум двум фичам, и без знаний о домене.
