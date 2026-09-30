---
type: topic
domain: frontend
stage: 8
section: "8.4"
order: 9
status: todo
level: senior
notion_id: 3ea33104867981ab901cc818947d8d4a
tags: [domain/frontend, stage/8, level/senior, topic/system-design, topic/forms, topic/schema, priority/should]
reviewed:
next_review:
priority: should
time: 3
---

# Кейс: конструктор форм

↑ [[FE 8.4 Frontend System Design|8.4 Frontend System Design]] · ← [[FE 8.4.8 Кейс — сложная таблица - админка с фильтрами|Предыдущая]] · → [[FE 8.4.10 Мониторинг и логирование — Sentry, метрики|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: senior</span></div>
<!-- meta:end -->




> [!info] Зачем это на собесе
> Кейс проверяет проектирование схемы, расширяемость и валидацию.

## Требования

Администратор собирает форму (поля, порядок, правила), пользователи заполняют. Поддержка условной видимости, валидации, разных типов полей, версионирования и сохранения черновиков.

## Модель (JSON Schema-подобная)

```ts
type Field =
  | { id: string; type: 'text'; label: string; required?: boolean; pattern?: string }
  | { id: string; type: 'number'; label: string; min?: number; max?: number }
  | { id: string; type: 'select'; label: string; options: { value: string; label: string }[] }
  | { id: string; type: 'group'; label: string; fields: Field[] }

interface FormSchema {
  id: string
  version: number
  fields: Field[]
  rules: { when: { field: string; op: 'eq' | 'neq' | 'in'; value: unknown }; then: { show?: string[]; require?: string[] } }[]
}
```

Схема хранится на сервере, версионируется; ответы привязаны к версии схемы.

## Рендер

```vue
<component v-for="f in visibleFields" :key="f.id"
  :is="registry[f.type]" v-bind="f" v-model="values[f.id]" :error="errors[f.id]" />
```

- **реестр компонентов** по типу (расширяемость, Open/Closed);
- видимость полей вычисляется правилами (`computed`);
- значения — плоский объект `values` по id.

## Валидация

- схема генерирует валидатор (Zod/Yup/JSON Schema через Ajv);
- запуск на blur/submit, а не на каждый ввод; асинхронные проверки (уникальность) с debounce;
- **повторная проверка на сервере** обязательна;
- сообщения ошибок и i18n.

## Конструктор (editor)

- drag-and-drop порядка (Sortable, dnd-kit-аналоги), панель свойств поля;
- undo/redo (стек команд), предпросмотр;
- автосохранение черновика;
- ограничение циклических зависимостей правил.

## Сложные моменты

- условные поля и очистка значений скрытых полей;
- вложенные группы и повторяющиеся блоки (массивы);
- миграция ответов при смене версии схемы;
- доступность: связка label, ошибки `aria-describedby`, порядок фокуса;
- безопасность: не исполнять произвольный код из схемы (правила декларативные), санитизация HTML в подписях;
- производительность на больших формах (ленивый рендер шагов).

## Вопросы с ответами

> [!question]- Почему схема декларативная?
> Её можно хранить, версионировать, валидировать на сервере и клиенте, отрисовывать разными клиентами и не исполнять произвольный код.

> [!question]- Что делать при изменении схемы формы, когда есть старые ответы?
> Версионировать схему, хранить версию вместе с ответом, писать миграции или показывать ответ по старой версии.
