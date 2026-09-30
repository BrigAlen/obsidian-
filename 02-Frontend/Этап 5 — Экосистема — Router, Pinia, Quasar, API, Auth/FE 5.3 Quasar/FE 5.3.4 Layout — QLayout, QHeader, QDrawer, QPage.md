---
type: topic
domain: frontend
stage: 5
section: "5.3"
order: 4
status: todo
level: middle
notion_id: 3ea33104867981e3a864d2ad5c1b7f36
tags: [domain/frontend, stage/5, level/middle, topic/quasar, topic/layout, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Layout: QLayout, QHeader, QDrawer, QPage

↑ [[FE 5.3 Quasar|5.3 Quasar]] · ← [[FE 5.3.3 Boot files|Предыдущая]] · → [[FE 5.3.5 Grid и flex-классы Quasar|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->





> [!info] Зачем это на собесе
> Каркас приложения: шапка, меню, страницы — как строится в Quasar.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

```vue
<!-- layouts/MainLayout.vue -->
<template>
  <q-layout view="lHh Lpr lFf">                                    <!-- 3×3 схема расположения частей -->
    <q-header elevated class="bg-primary text-white">
      <q-toolbar>
        <q-btn flat dense round icon="menu" aria-label="Меню" @click="drawer = !drawer" />
        <q-toolbar-title>Приложение</q-toolbar-title>
        <q-btn flat round icon="account_circle"><q-menu>...</q-menu></q-btn>
      </q-toolbar>
      <q-tabs align="left"><q-route-tab to="/orders" label="Заказы" /></q-tabs>
    </q-header>

    <q-drawer v-model="drawer" show-if-above bordered :width="260" :breakpoint="1024">
      <q-list><q-item clickable v-ripple :to="{ name: 'orders' }" active-class="text-primary"><q-item-section avatar><q-icon name="list" /></q-item-section><q-item-section>Заказы</q-item-section></q-item></q-list>
    </q-drawer>

    <q-page-container>
      <router-view />                                               <!-- страницы -->
    </q-page-container>

    <q-footer v-if="$q.screen.lt.md" />
  </q-layout>
</template>
```

| Компонент | Роль |
|---|---|
| `QLayout` | корневой контейнер; `view` задаёт поведение частей |
| `QHeader` / `QFooter` | шапка/подвал (`reveal`, `elevated`) |
| `QDrawer` | боковая панель (`side`, `overlay`, `mini`, `breakpoint`) |
| `QPageContainer` | контейнер страниц (учитывает размеры header/footer/drawer) |
| `QPage` | страница (`padding`, `style-fn`) |
| `QPageSticky`, `QPageScroller` | фиксированные элементы, «наверх» |
| `QToolbar`, `QTabs`, `QSplitter`, `QScrollArea` | вспомогательные |

**Строка `view`**: три части по три буквы (`lHh Lpr lFf`): `l/L` — drawer слева поверх/рядом с шапкой, `h/H` — шапка, `r/R` — правый drawer, `f/F` — подвал (заглавная — часть фиксируется/растягивается).

Дополнительно: `$q.screen` (реактивные breakpoints), `$q.dark`, `useQuasar()`; несколько layout-ов (`MainLayout`, `AuthLayout`) через вложенные маршруты.

## Нюансы и подводные камни

- `QPage` и страницы должны находиться внутри `QPageContainer`.
- Значение `view` сложно запомнить: пользуйтесь конструктором в документации.
- Высота страницы (`min-height`) вычисляется с учётом header/footer — `style-fn`.
- Adaptive drawer: `breakpoint` и `show-if-above`.
- Доступность: подписи `aria-label` у иконочных кнопок.

## Практика

1. Соберите layout с шапкой, боковым меню и страницами.
2. Реализуйте адаптивный drawer (mini на десктопе, overlay на мобильных).
3. Создайте отдельный layout для страницы входа.

## Вопросы с ответами

> [!question]- Зачем `QPageContainer`?
> Учитывает размеры header, footer и drawer и рендерит страницы в свободной области.

> [!question]- Что задаёт `view` у `QLayout`?
> Расположение и поведение шапки, подвала и боковых панелей относительно друг друга.

## Связанные темы

- [[N:3ea33104867981d89554c287a6494d1c]]
- [[N:3ea33104867981a7b0fbc3bc6173feaf]]
