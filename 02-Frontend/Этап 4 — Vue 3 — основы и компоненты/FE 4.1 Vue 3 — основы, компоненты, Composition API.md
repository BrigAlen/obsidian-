---
type: section
domain: frontend
stage: 4
section: "4.1"
order: 1
status: todo
level: middle
notion_id: 3ea33104867981cc842eeff72f0684c5
tags: [domain/frontend, stage/4, kind/section]
---

# 4.1 Vue 3: основы, компоненты, Composition API

↑ [[FE Этап 4 · Vue 3 — основы и компоненты|Этап 4]]

Шаблоны и директивы, реактивность, Composition API, компоненты и их коммуникация, composables, тестирование и типовые задачи.

## Темы
<!-- toc:start -->
**Итого:** 29 тем · ~1 ч 32 мин · готово 0 из 29

<div class="bar"><span style="width:0%"></span></div>

| # | Тема | Приоритет | Чтение | Статус |
|---|---|---|---|---|
| 1 | [[FE 4.1.1 SFC и шаблонный синтаксис\|SFC и шаблонный синтаксис]] | <span class="badge must">Обязательно</span> | 3 мин | <span class="badge todo">Не начато</span> |
| 2 | [[FE 4.1.2 Директивы — v-if и v-show, v-for и key, v-bind, v-on, v-model\|Директивы: v-if и v-show, v-for и key, v-bind, v-on, v-model]] | <span class="badge must">Обязательно</span> | 3 мин | <span class="badge todo">Не начато</span> |
| 3 | [[FE 4.1.3 Options API и Composition API\|Options API и Composition API]] | <span class="badge must">Обязательно</span> | 3 мин | <span class="badge todo">Не начато</span> |
| 4 | [[FE 4.1.4 script setup и макросы компилятора\|script setup и макросы компилятора]] | <span class="badge must">Обязательно</span> | 3 мин | <span class="badge todo">Не начато</span> |
| 5 | [[FE 4.1.5 Реактивность — ref, reactive, shallowRef, toRef, toRefs\|Реактивность: ref, reactive, shallowRef, toRef, toRefs]] | <span class="badge must">Обязательно</span> | 3 мин | <span class="badge todo">Не начато</span> |
| 6 | [[FE 4.1.6 computed\|computed]] | <span class="badge must">Обязательно</span> | 3 мин | <span class="badge todo">Не начато</span> |
| 7 | [[FE 4.1.7 watch и watchEffect\|watch и watchEffect]] | <span class="badge must">Обязательно</span> | 3 мин | <span class="badge todo">Не начато</span> |
| 8 | [[FE 4.1.8 Кастомные директивы\|Кастомные директивы]] | <span class="badge must">Обязательно</span> | 3 мин | <span class="badge todo">Не начато</span> |
| 9 | [[FE 4.1.9 Потеря реактивности и частые ошибки\|Потеря реактивности и частые ошибки]] | <span class="badge must">Обязательно</span> | 3 мин | <span class="badge todo">Не начато</span> |
| 10 | [[FE 4.1.10 Жизненный цикл компонента\|Жизненный цикл компонента]] | <span class="badge must">Обязательно</span> | 3 мин | <span class="badge todo">Не начато</span> |
| 11 | [[FE 4.1.11 Props и emits, однонаправленный поток данных\|Props и emits, однонаправленный поток данных]] | <span class="badge must">Обязательно</span> | 3 мин | <span class="badge todo">Не начато</span> |
| 12 | [[FE 4.1.12 v-model на компонентах и defineModel\|v-model на компонентах и defineModel]] | <span class="badge must">Обязательно</span> | 3 мин | <span class="badge todo">Не начато</span> |
| 13 | [[FE 4.1.13 Слоты — default, named, scoped\|Слоты: default, named, scoped]] | <span class="badge must">Обязательно</span> | 3 мин | <span class="badge todo">Не начато</span> |
| 14 | [[FE 4.1.14 provide и inject\|provide и inject]] | <span class="badge must">Обязательно</span> | 3 мин | <span class="badge todo">Не начато</span> |
| 15 | [[FE 4.1.15 Атрибуты — $attrs и inheritAttrs\|Атрибуты: $attrs и inheritAttrs]] | <span class="badge must">Обязательно</span> | 3 мин | <span class="badge todo">Не начато</span> |
| 16 | [[FE 4.1.16 Template refs и nextTick\|Template refs и nextTick]] | <span class="badge must">Обязательно</span> | 3 мин | <span class="badge todo">Не начато</span> |
| 17 | [[FE 4.1.17 defineExpose, useSlots, useAttrs, useTemplateRef\|defineExpose, useSlots, useAttrs, useTemplateRef]] | <span class="badge must">Обязательно</span> | 3 мин | <span class="badge todo">Не начато</span> |
| 18 | [[FE 4.1.18 Динамические компоненты — component —is\|Динамические компоненты: component :is]] | <span class="badge must">Обязательно</span> | 3 мин | <span class="badge todo">Не начато</span> |
| 19 | [[FE 4.1.19 Встроенные компоненты — Transition, KeepAlive, Teleport, Suspense\|Встроенные компоненты: Transition, KeepAlive, Teleport, Suspense]] | <span class="badge must">Обязательно</span> | 3 мин | <span class="badge todo">Не начато</span> |
| 20 | [[FE 4.1.20 Асинхронные компоненты и lazy loading\|Асинхронные компоненты и lazy loading]] | <span class="badge must">Обязательно</span> | 3 мин | <span class="badge todo">Не начато</span> |
| 21 | [[FE 4.1.21 Composables\|Composables]] | <span class="badge must">Обязательно</span> | 4 мин | <span class="badge todo">Не начато</span> |
| 22 | [[FE 4.1.22 VueUse\|VueUse]] | <span class="badge must">Обязательно</span> | 3 мин | <span class="badge todo">Не начато</span> |
| 23 | [[FE 4.1.23 Плагины Vue\|Плагины Vue]] | <span class="badge must">Обязательно</span> | 3 мин | <span class="badge todo">Не начато</span> |
| 24 | [[FE 4.1.24 Обработка ошибок — errorCaptured, app.config.errorHandler\|Обработка ошибок: errorCaptured, app.config.errorHandler]] | <span class="badge must">Обязательно</span> | 3 мин | <span class="badge todo">Не начато</span> |
| 25 | [[FE 4.1.25 TypeScript во Vue — типизация props, emits, ref, generic-компоненты\|TypeScript во Vue: типизация props, emits, ref, generic-компоненты]] | <span class="badge must">Обязательно</span> | 4 мин | <span class="badge todo">Не начато</span> |
| 26 | [[FE 4.1.26 Отличия Vue 2 и Vue 3\|Отличия Vue 2 и Vue 3]] | <span class="badge must">Обязательно</span> | 3 мин | <span class="badge todo">Не начато</span> |
| 27 | [[FE 4.1.27 Vue Test Utils — тестирование компонентов\|Vue Test Utils: тестирование компонентов]] | <span class="badge must">Обязательно</span> | 5 мин | <span class="badge todo">Не начато</span> |
| 28 | [[FE 4.1.28 Testing Library для Vue — тесты с позиции пользователя\|Testing Library для Vue: тесты с позиции пользователя]] | <span class="badge must">Обязательно</span> | 3 мин | <span class="badge todo">Не начато</span> |
| 29 | [[FE 4.1.29 Задачи на Vue — написать компонент или composable\|Задачи на Vue: написать компонент или composable]] | <span class="badge must">Обязательно</span> | 4 мин | <span class="badge todo">Не начато</span> |
<!-- toc:end -->

## Чек-лист раздела
- [ ] Прочитал все темы
- [ ] Могу объяснить каждую тему за 2 минуты вслух
