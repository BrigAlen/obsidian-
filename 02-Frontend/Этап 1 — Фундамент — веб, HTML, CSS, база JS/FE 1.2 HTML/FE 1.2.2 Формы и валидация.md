---
type: topic
domain: frontend
stage: 1
section: "1.2"
order: 2
status: todo
level: junior
notion_id: 3ea33104867981d0ba11f7d15eee409c
tags: [domain/frontend, stage/1, level/junior, topic/html, topic/forms, topic/validation, priority/should]
reviewed:
next_review:
priority: should
time: 3
---

# Формы и валидация

↑ [[FE 1.2 HTML|1.2 HTML]] · ← [[FE 1.2.1 Семантическая вёрстка|Предыдущая]] · → [[FE 1.2.3 Загрузка скриптов — async, defer, module|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: junior</span></div>
<!-- meta:end -->



















> [!info] Зачем это на собесе
> Формы — основа взаимодействия. Ждут знания нативной валидации и разницы клиентской и серверной проверки.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

```html
<form action="/register" method="post" novalidate>
  <label for="email">Email</label>
  <input id="email" name="email" type="email" required autocomplete="email">

  <label for="age">Возраст</label>
  <input id="age" name="age" type="number" min="18" max="120">

  <label for="pwd">Пароль</label>
  <input id="pwd" name="pwd" type="password" minlength="8" pattern="(?=.*\d)(?=.*[a-z]).{8,}" required>

  <select name="role"><option value="dev">Разработчик</option></select>
  <button type="submit">Отправить</button>
</form>
```

| Возможность | Атрибуты |
|---|---|
| Типы | `text`, `email`, `url`, `tel`, `number`, `date`, `password`, `file`, `checkbox`, `radio`, `range` |
| Ограничения | `required`, `min`, `max`, `minlength`, `maxlength`, `pattern`, `step` |
| Подсказки | `placeholder` (не замена label), `autocomplete`, `inputmode` |
| Связь label | `for`/`id` или вложенный `label` |
| Группы | `fieldset`/`legend` |

**Constraint Validation API**:

```js
const form = document.querySelector("form");
form.addEventListener("submit", (e) => {
  if (!form.checkValidity()) { e.preventDefault(); form.reportValidity(); }
  const email = form.elements.email;
  if (email.validity.typeMismatch) email.setCustomValidity("Неверный email"); else email.setCustomValidity("");
});
```

Состояния CSS: `:valid`, `:invalid`, `:user-invalid`, `:required`, `:focus-visible`.

Клиентская валидация — для удобства пользователя. **Серверная обязательна**: клиент можно обойти.

## Нюансы и подводные камни

- `placeholder` пропадает при вводе и плохо читается: нужен `label`.
- `type="number"` неудобен для телефонов/индексов: используйте `inputmode="numeric"`.
- `pattern` проверяет полное совпадение и не заменяет серверные правила.
- Отправка по Enter и двойной submit: блокируйте кнопку на время запроса.
- Файлы: `enctype="multipart/form-data"`, проверка размера и типа на клиенте и сервере.

## Практика

1. Сверстайте форму регистрации с нативной валидацией и кастомными сообщениями.
2. Подсветите ошибки через `:user-invalid`.
3. Сделайте отправку через `fetch` с `FormData`.

## Вопросы с ответами

> [!question]- Достаточно ли клиентской валидации?
> Нет: её можно обойти; обязательна серверная проверка.

> [!question]- Зачем `label`?
> Связывает подпись с полем: доступность, клик по подписи фокусирует поле.

## Связанные темы

- [[N:3ea33104867981dcb25cf3f6b7eeba03]]
- [[N:3ea3310486798136a85bfe7fb3bfcefe]]
