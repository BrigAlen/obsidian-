---
type: topic
domain: frontend
stage: 5
section: "5.5"
order: 8
status: todo
level: middle
notion_id: 3ea33104867981959103d2c15e81596d
tags: [domain/frontend, stage/5, level/middle, topic/auth, topic/acl, topic/rbac, priority/must]
reviewed:
next_review:
priority: must
time: 3
---

# ACL и RBAC на фронтенде

↑ [[FE 5.5 Аутентификация и доступ — Keycloak, SSO, ACL|5.5 Аутентификация и доступ: Keycloak, SSO, ACL]] · ← [[FE 5.5.7 Хранение токенов и их обновление|Предыдущая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->


















> [!info] Зачем это на собесе
> Как отображать интерфейс по правам, помня, что настоящая защита на сервере.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

| Модель | Суть |
|---|---|
| **RBAC** (role-based) | права привязаны к ролям (`admin`, `manager`), пользователь получает роли |
| **ACL** (access control list) | список прав на конкретный объект («пользователь X может редактировать документ Y») |
| **ABAC** (attribute-based) | политика по атрибутам (отдел, время, владение, статус объекта) |
| **Permissions (права)** | атомарные действия `orders:read`, `orders:write` — роли группируют права |

Клиентская сторона — **отображение**: маршруты, меню, кнопки, поля.

```ts
// stores/permissions.ts
export const usePermissions = defineStore("permissions", () => {
  const perms = ref(new Set<string>());
  const can = (p: string) => perms.value.has(p) || perms.value.has("*");
  const canAny = (...ps: string[]) => ps.some(can);
  return { perms, can, canAny };
});

// Директива
app.directive("can", { mounted(el, { value }) { if (!usePermissions().can(value)) el.remove(); } });
// <q-btn v-can="'orders:write'" label="Создать" />

// Компонент
// <Can permission="orders:delete" :resource="order"><q-btn label="Удалить" /></Can>

// Маршруты и меню
router.beforeEach((to) => { const need = to.meta.permissions; if (need && !usePermissions().canAny(...need)) return { name: "forbidden" }; });
const menu = computed(() => allMenu.filter(i => !i.permission || can(i.permission)));
```

Практики:

- Источник прав — **бэкенд** (endpoint `/me/permissions` или claims токена); фронтенд не выводит права из «названий ролей» по своей логике.
- Права на уровне объектов (владелец, статус) приходят с данными (`order.permissions: { canEdit, canDelete }`) — фронтенд не дублирует бизнес-правила.
- Отображение: скрывать или блокировать? Скрывайте недоступные разделы, блокируйте с подсказкой действия, которые «временно недоступны».
- Реактивность: при смене пользователя/прав пересчитывайте меню и очищайте кэш.
- 403 от API обрабатывается: показать сообщение и обновить права.
- Тестирование матрицы «роль × экран/действие».

Проверка на сервере обязательна для каждого запроса; клиентское скрытие — только UX.

## Нюансы и подводные камни

- Хардкод ролей в компонентах (`v-if="user.role === 'admin'"`) размазывает правила: используйте права.
- Утечка информации: клиентский бандл содержит все страницы (даже скрытые) — не помещайте секреты.
- Рассинхронизация прав фронта и бэка — источник багов «кнопка есть, а 403».
- Права из старого токена не обновляются до refresh.

## Практика

1. Реализуйте `usePermissions`, директиву `v-can` и фильтрацию меню.
2. Получайте права объекта с сервера и отображайте кнопки по ним.
3. Составьте матрицу ролей и проверьте её тестами.

## Вопросы с ответами

> [!question]- RBAC или ABAC?
> RBAC проще и подходит для большинства систем; ABAC гибче при зависимости прав от атрибутов и контекста.

> [!question]- Почему права должен определять бэкенд?
> Фронтенд можно обойти, а бизнес-правила должны быть в одном месте.

## Связанные темы

- [[N:3ea33104867981858e18c06e049a568c]]
- [[N:3ea33104867981c9ba57d2f24f3163ab]]
