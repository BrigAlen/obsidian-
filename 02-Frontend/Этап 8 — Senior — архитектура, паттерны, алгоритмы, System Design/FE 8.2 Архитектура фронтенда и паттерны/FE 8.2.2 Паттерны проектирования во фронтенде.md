---
type: topic
domain: frontend
stage: 8
section: "8.2"
order: 2
status: todo
level: senior
notion_id: 3ea3310486798113a7b3e7f09f79e8e2
tags: [domain/frontend, stage/8, level/senior, topic/patterns, topic/design, priority/should]
reviewed:
next_review:
priority: should
time: 3
---

# Паттерны проектирования во фронтенде

↑ [[FE 8.2 Архитектура фронтенда и паттерны|8.2 Архитектура фронтенда и паттерны]] · ← [[FE 8.2.1 SOLID, DRY, KISS, YAGNI на фронтенде|Предыдущая]] · → [[FE 8.2.3 Структура проекта — по типам и по фичам|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: senior</span></div>
<!-- meta:end -->





> [!info] Зачем это на собесе
> Ожидают не перечисление GoF, а примеры из реального кода: где вы использовали и почему.

## Порождающие

| Паттерн | Пример |
|---|---|
| **Factory** | `createApiClient(config)`, фабрика компонентов по типу поля |
| **Singleton** | экземпляр HTTP-клиента, стор; осторожно с SSR (общий на процесс) |
| **Builder** | конструктор запросов, конфигуратор графиков |

## Структурные

| Паттерн | Пример |
|---|---|
| **Adapter** | преобразование DTO бэкенда в модели UI |
| **Decorator** | HOC, обёртки над функциями (retry, логирование) |
| **Facade** | сервис поверх нескольких API |
| **Proxy** | `Proxy` во Vue-реактивности, кэширующий клиент |
| **Composite** | дерево компонентов, меню, файловое дерево |

## Поведенческие

| Паттерн | Пример |
|---|---|
| **Observer** | реактивность, `EventTarget`, RxJS |
| **Strategy** | стратегия валидации, сортировки, форматирования |
| **Command** | undo/redo, очередь операций |
| **State** | конечные автоматы для UI (XState) |
| **Mediator** | шина событий, стор |
| **Iterator** | итераторы и генераторы |
| **Chain of Responsibility** | interceptors, middleware роутера |

## Frontend-специфичные

- **Container/Presentational** (умные и глупые компоненты);
- **Repository**: скрывает получение и сохранение domain-данных;
- **Provider / Dependency Injection**: `provide/inject`;
- **Store (Flux)**: единый источник состояния, однонаправленный поток;
- **Renderless component**: логика без разметки (slot props, composable);
- **Backend For Frontend**;
- **Optimistic UI**: показываем результат до подтверждения сервера.

## Пример: Strategy

```ts
type PriceRule = (base: number) => number
const rules: Record<string, PriceRule> = {
  regular: p => p,
  vip: p => p * 0.9,
  promo: p => p - 100,
}
export const price = (base: number, kind: keyof typeof rules) => rules[kind](base)
```

## Пример: Adapter

```ts
export const toUser = (dto: UserDto): User => ({
  id: dto.user_id,
  fullName: `${dto.last_name} ${dto.first_name}`,
  createdAt: new Date(dto.created_at),
})
```

## Как отвечать

Проблема → минимальный код → альтернатива без паттерна → цена паттерна → реальный сценарий.

## Вопросы с ответами

> [!question]- Где во Vue встречается паттерн Observer?
> Реактивность: эффекты подписываются на данные и уведомляются об изменении.

> [!question]- Зачем Adapter при работе с API?
> Изолирует UI от формы бэкенда: смена контракта правится в одном месте, а компоненты работают с удобной моделью.
