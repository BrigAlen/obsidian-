---
type: topic
domain: frontend
stage: 8
section: "8.4"
order: 6
status: todo
level: senior
notion_id: 3ea33104867981cd9248e0e28b64dab7
tags: [domain/frontend, stage/8, level/senior, topic/system-design, topic/typeahead, topic/autocomplete, priority/should]
reviewed:
next_review:
priority: should
time: 3
---

# Кейс: автокомплит / typeahead

↑ [[FE 8.4 Frontend System Design|8.4 Frontend System Design]] · ← [[FE 8.4.5 Офлайн-режим и синхронизация|Предыдущая]] · → [[FE 8.4.7 Кейс — лента новостей|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: senior</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> Компактный кейс на 45 минут: показывает работу с событиями, сетью, доступностью.

## Требования

Пользователь вводит запрос, видит подсказки, выбирает клавиатурой или мышью. Нефункциональные: задержка < 100 мс на подсказку, много пользователей, доступность, мобильные.

## Архитектура

```text
Input ─▶ debounce ─▶ cache? ─▶ API (отмена предыдущих) ─▶ список подсказок
                       ▲                                       │
                       └────────── LRU-кэш по префиксу ◀───────┘
```

## Клиент

- **debounce** 150–300 мс; минимальная длина запроса (2–3 символа);
- **отмена** устаревших запросов (`AbortController`) и защита от гонок: применять только ответ на последний запрос;
- **кэш** по префиксу (Map / LRU), повторное использование более короткого результата;
- **предзагрузка** популярных запросов;
- подсветка совпадения;
- состояния: пусто, загрузка, ошибка, нет результатов;
- история и недавние запросы.

```ts
let ctrl: AbortController | undefined
async function search(q: string) {
  ctrl?.abort(); ctrl = new AbortController()
  const cached = cache.get(q); if (cached) return show(cached)
  try {
    const items = await fetch(`/api/suggest?q=${encodeURIComponent(q)}`, { signal: ctrl.signal }).then(r => r.json())
    cache.set(q, items); show(items)
  } catch (e) { if ((e as Error).name !== 'AbortError') showError() }
}
```

## Доступность (ARIA combobox)

- `role="combobox"`, `aria-expanded`, `aria-controls`, `aria-activedescendant`;
- список `role="listbox"`, пункты `role="option"`;
- клавиши: стрелки, Enter, Esc, Home/End;
- объявление количества результатов (`aria-live="polite"`).

## Сервер

- **Trie** или инвертированный индекс для префиксного поиска; ранжирование по популярности;
- кэш на CDN для частых префиксов;
- ограничение частоты запросов;
- устойчивость к опечаткам (нечёткий поиск).

## Производительность и безопасность

- ответ малого размера (только id и label);
- экранирование при подсветке (не `v-html` с пользовательским вводом);
- ограничение количества (10–20 подсказок);
- IME (ввод на CJK): не запрашивать во время композиции (`compositionstart/end`).

## Вопросы с ответами

> [!question]- Как избежать гонок ответов в typeahead?
> Отменять предыдущий запрос через AbortController и учитывать только ответ на актуальный запрос.

> [!question]- Как сократить количество запросов?
> Debounce, минимальная длина, кэш по префиксу, отмена, повторное использование результатов более широкого запроса.
