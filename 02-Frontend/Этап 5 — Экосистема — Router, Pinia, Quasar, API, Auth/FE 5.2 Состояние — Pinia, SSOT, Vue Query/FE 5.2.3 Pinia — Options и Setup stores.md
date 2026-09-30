---
type: topic
domain: frontend
stage: 5
section: "5.2"
order: 3
status: todo
level: middle
notion_id: 3ea33104867981dc9c17f29411b85b4e
tags: [domain/frontend, stage/5, level/middle, topic/vue, topic/pinia, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Pinia: Options и Setup stores

↑ [[FE 5.2 Состояние — Pinia, SSOT, Vue Query|5.2 Состояние: Pinia, SSOT, Vue Query]] · ← [[FE 5.2.2 Pinia — state, getters, actions|Предыдущая]] · → [[FE 5.2.4 Pinia — storeToRefs, плагины, persist|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> Два стиля определения стора и когда какой выбрать.

## Объяснение

**Options store** — объект с `state/getters/actions` (см. предыдущую тему). **Setup store** — функция, как `<script setup>`: `ref` = state, `computed` = getters, функции = actions.

```ts
export const useCartStore = defineStore("cart", () => {
  const items = ref<CartItem[]>([]);
  const total = computed(() => items.value.reduce((s, i) => s + i.price * i.qty, 0));
  const count = computed(() => items.value.length);

  function add(item: CartItem) {
    const ex = items.value.find(i => i.id === item.id);
    if (ex) ex.qty += item.qty; else items.value.push(item);
  }
  const remove = (id: number) => (items.value = items.value.filter(i => i.id !== id));
  const { data } = useQuery(...);                              // можно использовать composables, watch, inject

  watch(items, (v) => localStorage.setItem("cart", JSON.stringify(v)), { deep: true });
  return { items, total, count, add, remove };                  // вернуть всё, что должно быть публичным
});
```

| Критерий | Options | Setup |
|---|---|---|
| Порог входа | ниже, привычно для Vuex | как Composition API |
| Гибкость | ограничена | полная: composables, watchers, `provide/inject` |
| Приватность | нет | несвозвращаемое — приватное |
| Типизация | хорошая | отличная |
| `$reset()` | встроен | не поддерживается (реализуйте сами) |
| Правила | нужно вернуть **все** state-ref, иначе SSR/DevTools ломаются | |

Рекомендации: Setup store — для сложной логики и переиспользования composables; Options — для простых сторов и команд, привыкших к структуре. Смешивать стили в проекте допустимо, но лучше единообразие.

Сторы должны быть небольшими и предметно-ориентированными (`auth`, `cart`, `ui`, `settings`).

## Нюансы и подводные камни

- В setup-сторе нужно вернуть все `ref/reactive` состояния, иначе они не попадут в devtools/SSR-гидратацию.
- Нет `this`: полагайтесь на замыкания.
- `$reset()` отсутствует — реализуйте собственный `reset()`.
- Циклические зависимости между сторами (вызывать внутри actions, не на верхнем уровне).

## Практика

1. Перепишите Options-стор на Setup-стиль.
2. Добавьте в стор корзины автосохранение через `watch`.
3. Реализуйте `reset()`.

## Вопросы с ответами

> [!question]- Options или Setup store?
> Setup даёт полную мощность Composition API и приватные детали, Options проще для начинающих и имеет встроенный `$reset`.

> [!question]- Что нужно вернуть из setup-стора?
> Всё состояние, getters и actions, которые должны быть доступны снаружи; состояние — обязательно.

## Связанные темы

- [[N:3ea33104867981ccbb11cc4932778fa7]]
- [[N:3ea331048679816d9550cadc1c99705d]]
