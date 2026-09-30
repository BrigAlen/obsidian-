---
type: topic
domain: frontend
stage: 5
section: "5.3"
order: 8
status: todo
level: middle
notion_id: 3ea3310486798181b78cc70995a735cc
tags: [domain/frontend, stage/5, level/middle, topic/quasar, topic/plugins, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# Quasar Plugins: Notify, Dialog, Loading, LocalStorage

↑ [[FE 5.3 Quasar|5.3 Quasar]] · ← [[FE 5.3.7 Валидация форм в Quasar|Предыдущая]] · → [[FE 5.3.9 Темизация — SASS-переменные, brand colors, dark mode|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->














> [!info] Зачем это на собесе
> Императивные API Quasar: уведомления, диалоги, лоадеры — как использовать и тестировать.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

Плагины включаются в `quasar.config` → `framework.plugins` и вызываются через `useQuasar()` или напрямую.

```ts
import { useQuasar, Notify, Dialog, Loading, LocalStorage, SessionStorage, Cookies, Dark, Screen, Meta, copyToClipboard, date } from "quasar";
const $q = useQuasar();

$q.notify({ type: "positive", message: "Сохранено", position: "top-right", timeout: 3000, actions: [{ label: "Отмена", handler: undo }] });

$q.dialog({ title: "Удалить?", message: "Действие необратимо", cancel: true, persistent: true, ok: { color: "negative", label: "Удалить" } })
  .onOk(() => remove()).onCancel(() => {}).onDismiss(() => {});
// prompt / options: $q.dialog({ prompt: { model: "", type: "text" } }); свой компонент: $q.dialog({ component: MyDialog, componentProps: { id } })

$q.loading.show({ message: "Загрузка..." }); $q.loading.hide();               // глобальный лоадер
$q.loadingBar.start(); $q.loadingBar.stop();                                     // полоса сверху (LoadingBar)

LocalStorage.set("prefs", { a: 1 }); LocalStorage.getItem("prefs");             // сериализация типов (Date, RegExp и др.)
Cookies.set("k", "v", { expires: 7, secure: true, sameSite: "Lax" });
$q.dark.set("auto"); $q.screen.gt.sm; $q.platform.is.mobile;
```

| Плагин | Назначение |
|---|---|
| `Notify` | всплывающие уведомления |
| `Dialog` | программные диалоги (alert/confirm/prompt/свой компонент) |
| `Loading`, `LoadingBar` | оверлей и прогресс-бар |
| `LocalStorage`, `SessionStorage`, `Cookies` | хранилища |
| `Dark`, `Screen`, `Platform` | тема, размеры экрана, платформа |
| `Meta` | управление `<title>` и meta |
| `AppFullscreen`, `AddressbarColor`, `BottomSheet`, `Bex` | прочее |

Обёртка над уведомлениями:

```ts
export function useNotify() {
  const $q = useQuasar();
  return { ok: (m: string) => $q.notify({ type: "positive", message: m }), fail: (e: unknown) => $q.notify({ type: "negative", message: toMessage(e) }) };
}
```

Интеграция: глобальный обработчик ошибок HTTP показывает `notify`; `Loading` — на долгие операции; `Dialog` — подтверждения.

## Нюансы и подводные камни

- Плагин нужно объявить в конфиге, иначе `$q.notify` не сработает.
- В тестах плагины нужно подключать (`installQuasarPlugin`) или мокать `useQuasar`.
- Не показывайте `Loading` поверх всего экрана на быстрых операциях (мерцание): используйте задержку.
- Много одновременных уведомлений — группируйте (`group`).
- LocalStorage плагин безопасен для сериализации, но не для секретов.

## Практика

1. Сделайте composable `useNotify` и подключите к обработчику ошибок API.
2. Реализуйте подтверждение удаления через `$q.dialog`.
3. Покройте компонент тестом с `installQuasarPlugin`.

## Вопросы с ответами

> [!question]- Как вызвать уведомление в Quasar?
> `$q.notify({...})` через `useQuasar()` при включённом плагине `Notify`.

> [!question]- Чем `Dialog` плагин отличается от `<q-dialog>`?
> Плагин создаёт диалог императивно из кода, компонент — декларативно в шаблоне.

## Связанные темы

- [[N:3ea33104867981a6ba83f0a29df4be37]]
- [[N:3ea33104867981ccb8a9f3af56b3a9be]]
