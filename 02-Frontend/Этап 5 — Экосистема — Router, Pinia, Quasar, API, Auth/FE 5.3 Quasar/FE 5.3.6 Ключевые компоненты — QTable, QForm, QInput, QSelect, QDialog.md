---
type: topic
domain: frontend
stage: 5
section: "5.3"
order: 6
status: todo
level: middle
notion_id: 3ea331048679814db069fdc55fcbd725
tags: [domain/frontend, stage/5, level/middle, topic/quasar, topic/components, priority/must]
reviewed:
next_review:
priority: must
time: 4
---

# Ключевые компоненты: QTable, QForm, QInput, QSelect, QDialog

↑ [[FE 5.3 Quasar|5.3 Quasar]] · ← [[FE 5.3.5 Grid и flex-классы Quasar|Предыдущая]] · → [[FE 5.3.7 Валидация форм в Quasar|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~4 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->
















> [!info] Зачем это на собесе
> Самые используемые компоненты: таблицы с серверной пагинацией, формы, селекты, диалоги.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

**QTable** — таблица: сортировка, фильтр, пагинация, выбор строк, слоты.

```vue
<q-table
  v-model:pagination="pagination" v-model:selected="selected" selection="multiple"
  :rows="rows" :columns="columns" row-key="id" :loading="loading" :filter="filter"
  binary-state-sort :rows-per-page-options="[10, 20, 50]"
  @request="onRequest">                                                   <!-- серверная пагинация/сортировка -->
  <template #body-cell-status="props"><q-td :props="props"><q-badge :color="color(props.value)">{{ props.value }}</q-badge></q-td></template>
  <template #top-right><q-input dense debounce="300" v-model="filter" placeholder="Поиск"><template #append><q-icon name="search" /></template></q-input></template>
  <template #no-data>Нет данных</template>
</q-table>
```

```ts
const columns: QTableColumn[] = [{ name: "number", label: "№", field: "number", sortable: true, align: "left" }, { name: "total", label: "Сумма", field: (r) => r.total, format: (v) => fmt(v) }];
async function onRequest({ pagination: p, filter }: { pagination: QTableProps["pagination"]; filter?: string }) {
  loading.value = true;
  const res = await api.list({ page: p!.page, size: p!.rowsPerPage, sort: p!.sortBy, desc: p!.descending, q: filter });
  rows.value = res.items; pagination.value = { ...p!, rowsNumber: res.total };     // rowsNumber обязателен для серверной пагинации
  loading.value = false;
}
```

**Формы и поля**:

```vue
<q-form @submit.prevent="save" @reset="reset" greedy>
  <q-input v-model="f.name" label="Имя" outlined dense :rules="[required, minLen(2)]" lazy-rules clearable />
  <q-select v-model="f.status" :options="statuses" emit-value map-options option-value="id" option-label="title" use-input @filter="filterFn" multiple use-chips />
  <q-checkbox v-model="f.agree" label="Согласен" /><q-toggle v-model="f.active" /><q-date v-model="f.date" mask="YYYY-MM-DD" />
  <q-btn type="submit" color="primary" label="Сохранить" :loading="saving" />
</q-form>
```

**QDialog**:

```vue
<q-dialog v-model="open" persistent>
  <q-card style="min-width: 350px"><q-card-section class="text-h6">Подтверждение</q-card-section>
    <q-card-actions align="right"><q-btn flat label="Отмена" v-close-popup /><q-btn color="negative" label="Удалить" @click="del" /></q-card-actions>
  </q-card>
</q-dialog>
```

Также: `QBtn`, `QCard`, `QList/QItem`, `QMenu`, `QTooltip`, `QTabs`, `QStepper`, `QExpansionItem`, `QTree`, `QVirtualScroll`, `QInfiniteScroll`, `QPagination`, `QSkeleton`, `QUploader`, `QBadge`, `QChip`, `QAvatar`.

## Нюансы и подводные камни

- Для серверной пагинации нужен `@request` и `rowsNumber`; без них таблица обрабатывает данные на клиенте.
- `q-select` с объектами: `emit-value` и `map-options` для примитивного значения.
- `use-input` + `@filter` — асинхронный поиск, вызывать `update()`.
- `lazy-rules` откладывает проверку до потери фокуса.
- Большие таблицы: виртуальная прокрутка (`virtual-scroll`), пагинация.

## Практика

1. Сделайте таблицу с серверной пагинацией, сортировкой и поиском.
2. Соберите форму с валидацией и `q-select` с поиском.
3. Реализуйте диалог подтверждения удаления.

## Вопросы с ответами

> [!question]- Как сделать серверную пагинацию в QTable?
> Обработать событие `@request`, загрузить страницу и обновить `pagination` с `rowsNumber`.

> [!question]- Что делают `emit-value` и `map-options` у QSelect?
> `emit-value` кладёт в модель только значение опции, `map-options` показывает соответствующую метку.

## Связанные темы

- [[N:3ea33104867981a7b0fbc3bc6173feaf]]
- [[N:3ea33104867981a6ba83f0a29df4be37]]
