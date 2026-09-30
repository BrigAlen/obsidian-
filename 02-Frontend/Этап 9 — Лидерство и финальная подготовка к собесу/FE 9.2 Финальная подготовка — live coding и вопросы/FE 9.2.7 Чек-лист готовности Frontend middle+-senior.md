---
type: topic
domain: frontend
stage: 9
section: "9.2"
order: 7
status: todo
level: senior
notion_id: 9186109acae74c0baba25ecfe3d33943
tags: [domain/frontend, stage/9, level/senior, topic/interview, topic/checklist, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Чек-лист готовности Frontend middle+/senior

↑ [[FE 9.2 Финальная подготовка — live coding и вопросы|9.2 Финальная подготовка: live coding и вопросы]] · ← [[FE 9.2.6 Mock-интервью по Frontend System Design|Предыдущая]] · → [[FE 9.2.8 Take-home задание и code review на интервью|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: senior</span></div>
<!-- meta:end -->


> [!info] Зачем это на собесе
> Перед интервью полезно пройтись по списку и найти слабые места. Отмечайте только то, что можете объяснить вслух за 2 минуты.

## JavaScript и браузер

- [ ] event loop, микрозадачи и макрозадачи;
- [ ] замыкания, `this`, прототипы, классы;
- [ ] промисы, async/await, обработка ошибок, отмена (AbortController);
- [ ] модули ESM, tree shaking;
- [ ] критический путь рендеринга, reflow/repaint;
- [ ] Web Vitals и оптимизации;
- [ ] хранилища, кэш и Service Worker, CORS.

## TypeScript

- [ ] дженерики, условные и mapped типы, `infer`;
- [ ] `unknown` против `any`, сужение типов, type guards;
- [ ] utility types, `satisfies`, discriminated unions;
- [ ] строгий режим, типизация API.

## Vue 3

- [ ] реактивность: Proxy, `ref`/`reactive`, `computed`, `watch`;
- [ ] жизненный цикл, composables, provide/inject;
- [ ] Virtual DOM, diff и `key`, компилятор;
- [ ] Router (guards, lazy), Pinia, Vue Query;
- [ ] производительность: `shallowRef`, `v-memo`, виртуализация;
- [ ] SSR и Nuxt, гидрация.

## Quasar и UI

- [ ] компоненты, темизация, режимы сборки (SPA, SSR, PWA);
- [ ] формы и валидация, таблицы;
- [ ] доступность и i18n.

## Инженерные практики

- [ ] Git-процессы, conventional commits;
- [ ] сборка (Vite), env-конфигурация, CI/CD, Docker;
- [ ] ESLint, Prettier, husky;
- [ ] стратегия тестирования: unit, component, E2E, a11y;
- [ ] мониторинг: Sentry, Web Vitals.

## Безопасность

- [ ] XSS, CSRF, CSP, clickjacking;
- [ ] хранение токенов, OIDC, PKCE;
- [ ] зависимости и supply chain.

## Архитектура

- [ ] SOLID, паттерны, композиция;
- [ ] структура проекта, FSD;
- [ ] микрофронтенды, дизайн-система;
- [ ] управление состоянием и данными;
- [ ] ADR, компромиссы.

## Алгоритмы

- [ ] Big O;
- [ ] массивы, хэши, стек/очередь, деревья, графы;
- [ ] два указателя, окно, рекурсия, ДП;
- [ ] utility-задачи JS (debounce, deepClone, Promise).

## System Design

- [ ] фреймворк ответа;
- [ ] пагинация, real-time, offline;
- [ ] минимум 5 кейсов отрепетированы вслух.

## Лидерство и soft skills

- [ ] 5–7 историй STAR;
- [ ] декомпозиция и оценка;
- [ ] конфликты и обратная связь;
- [ ] менторинг, найм, техдолг.

## Организационно

- [ ] рассказ о себе на 2 минуты;
- [ ] 3 вопроса работодателю;
- [ ] проверил технику: камера, микрофон, IDE, доска;
- [ ] знаю компанию, продукт, стек;
- [ ] отдых накануне.

## Как использовать

Пометьте пробелы, вернитесь к соответствующим заметкам в этом хранилище. Повторяйте по системе интервальных повторений, а не за ночь до интервью.

## Вопросы с ответами

> [!question]- С чего начать, если времени мало?
> С самого вероятного: JavaScript/TypeScript/Vue основы, рассказ о себе и проектах, один-два кейса system design и истории STAR.
