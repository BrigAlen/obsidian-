---
type: topic
domain: frontend
stage: 5
section: "5.3"
order: 11
status: todo
level: middle
notion_id: 3ea331048679814bbe6ef6cd309478ce
tags: [domain/frontend, stage/5, level/middle, topic/quasar, topic/i18n, topic/localization, priority/must]
reviewed:
next_review:
priority: must
time: 4
---

# i18n

↑ [[FE 5.3 Quasar|5.3 Quasar]] · ← [[FE 5.3.10 Режимы сборки — SPA, SSR, PWA, Electron, Capacitor|Предыдущая]] · → [[FE 5.3.12 Кастомизация и обёртки над компонентами Quasar|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~4 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->















> [!info] Зачем это на собесе
> Локализация — типичное требование: vue-i18n, плюрали, форматы, ленивая загрузка.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

Два уровня: **языковой пакет Quasar** (тексты его компонентов) и **vue-i18n** (тексты приложения).

```ts
// boot/i18n.ts
import { createI18n } from "vue-i18n";
import messages from "src/i18n";
export const i18n = createI18n({ locale: "ru", fallbackLocale: "en", legacy: false, messages,
  datetimeFormats: { ru: { short: { dateStyle: "medium" } } }, numberFormats: { ru: { currency: { style: "currency", currency: "RUB" } } } });
export default boot(({ app }) => app.use(i18n));

// src/i18n/ru/index.ts
export default { orders: { title: "Заказы", count: "нет заказов | {n} заказ | {n} заказа | {n} заказов" }, errors: { required: "Обязательное поле" } };
```

```vue
<script setup>
const { t, n, d, locale } = useI18n();
</script>
<template>
  <h1>{{ t("orders.title") }}</h1>
  <p>{{ t("orders.count", { n: 5 }, 5) }}</p>                       <!-- плюрализация: выбор формы по числу -->
  <p>{{ n(1234.5, "currency") }} · {{ d(new Date(), "short") }}</p>
  <i18n-t keypath="terms" tag="p"><template #link><a href="/terms">условия</a></template></i18n-t>   <!-- компонент с разметкой -->
</template>
```

Переключение языка:

```ts
import quasarLang from "quasar/lang/ru"; const $q = useQuasar();
async function setLang(l: string) {
  const pack = await import(`../../node_modules/quasar/lang/${l}.js`);      // пакет Quasar (ленивая загрузка)
  $q.lang.set(pack.default); i18n.global.locale.value = l; document.documentElement.lang = l;
  localStorage.setItem("lang", l);
}
```

Практики:

- Ключи структурированы по функциональности (`orders.title`), а не по тексту.
- Плюральные формы русского языка (1/2–4/5+) — `|` с 4 вариантами.
- Формат даты, чисел, валюты — `Intl` через `d()`/`n()`.
- Ленивая загрузка языков (`import()`), fallback-язык.
- Тексты валидации — тоже в i18n (правила возвращают ключи).
- Сообщения с переменными — параметры, а не конкатенация строк.
- Проверка отсутствующих ключей в CI (`vue-i18n-extract`), типизация ключей.
- Серверные ошибки — коды → локализованные сообщения на клиенте.

RTL, направление текста, длина строк: учитывайте в макете (немецкий длиннее).

## Нюансы и подводные камни

- Конкатенация строк ломает грамматику разных языков.
- Импорт всех языков в основной бандл раздувает его.
- Забытый языковой пакет Quasar — нелокализованные дни недели и подписи компонентов.
- Числа/даты «руками» вместо `Intl` — ошибки форматов.
- Ключи в шаблонах не находятся статическим анализом при динамической подстановке.

## Практика

1. Подключите vue-i18n, реализуйте плюрализацию для русского.
2. Реализуйте ленивое переключение языка с сохранением выбора.
3. Добавьте проверку неиспользуемых/отсутствующих ключей в CI.

## Вопросы с ответами

> [!question]- Как реализовать множественные числа в vue-i18n?
> Формы через `|` и передача числа третьим аргументом `t(key, params, count)`.

> [!question]- Зачем языковой пакет Quasar?
> Локализует встроенные тексты компонентов Quasar (календарь, пагинация, подписи).

## Связанные темы

- [[N:3ea331048679811593a2ee4be38da7e1]]
- [[N:3ea33104867981059bb4e4c24f055d22]]
