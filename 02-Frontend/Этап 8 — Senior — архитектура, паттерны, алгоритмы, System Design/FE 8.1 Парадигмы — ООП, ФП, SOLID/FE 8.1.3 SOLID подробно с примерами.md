---
type: topic
domain: frontend
stage: 8
section: "8.1"
order: 3
status: todo
level: senior
notion_id: 3ea33104867981db83e0d1e47f9acb11
tags: [domain/frontend, stage/8, level/senior, topic/solid, topic/design, topic/typescript, priority/should]
reviewed:
next_review:
priority: should
time: 3
---

# SOLID подробно с примерами

↑ [[FE 8.1 Парадигмы — ООП, ФП, SOLID|8.1 Парадигмы: ООП, ФП, SOLID]] · ← [[FE 8.1.2 Композиция вместо наследования|Предыдущая]] · → [[FE 8.1.4 ФП — функции высшего порядка, compose и pipe|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: senior</span></div>
<!-- meta:end -->







> [!info] Зачем это на собесе
> SOLID спрашивают всегда. Хороший ответ включает примеры из фронтенда и оговорку, что это эвристики.

## S — Single Responsibility

У модуля одна причина для изменения.

```ts
// плохо: компонент грузит, кэширует, форматирует, рисует
// хорошо:
const useUserApi = () => { /* запросы */ }
const formatUser = (u: User) => `${u.last} ${u.first}`
// компонент только отображает
```

## O — Open/Closed

Открыт для расширения, закрыт для модификации: добавляем поведение без правки существующего кода.

```ts
const validators: Record<string, (v: unknown) => string | null> = { required, email }
export const registerValidator = (name: string, fn: Validator) => { validators[name] = fn }
```

Вместо `switch` по типу, который растёт, — реестр или стратегия.

## L — Liskov Substitution

Подтип можно подставить вместо базового без нарушения ожиданий.

Нарушение: `ReadOnlyList extends List` и `add()` бросает исключение. Во фронтенде: компонент-обёртка, меняющая смысл `v-model` или событий базового.

## I — Interface Segregation

Много специализированных интерфейсов лучше одного универсального.

```ts
// плохо: компоненту нужен только id
function open(user: FullUser) {}
// хорошо
function open(user: Pick<User, 'id'>) {}
```

Компоненту — минимум props; композиция `defineProps` небольших типов.

## D — Dependency Inversion

Модули верхнего уровня зависят от абстракций, а не от деталей.

```ts
export interface HttpClient { get<T>(url: string): Promise<T> }
export class UserService {
  constructor(private http: HttpClient) {}
  load(id: string) { return this.http.get<User>(`/users/${id}`) }
}
// в тесте подставляем фейковый HttpClient
```

Во Vue: `provide/inject`, параметры composables, Pinia и сервисы с внедрением.

## Оговорка senior

SOLID — эвристики для оценки границ и зависимостей, а не обязательная классовая архитектура. Излишнее следование даёт лишние абстракции (YAGNI). Функциональный стиль решает те же задачи иначе: функции высшего порядка вместо стратегий, замыкания вместо DI.

## Вопросы с ответами

> [!question]- Как применить SOLID к Vue-компоненту?
> Один компонент — одна ответственность (данные, логика и отображение разделены), расширение через slots и props, узкие props, зависимости через composables и inject.

> [!question]- Пример нарушения принципа подстановки Лисков?
> Наследник ужесточает предусловия или ломает контракт: например, обёртка над `input`, которая не эмитит `input`-событие, и потребитель базового компонента перестаёт работать.
