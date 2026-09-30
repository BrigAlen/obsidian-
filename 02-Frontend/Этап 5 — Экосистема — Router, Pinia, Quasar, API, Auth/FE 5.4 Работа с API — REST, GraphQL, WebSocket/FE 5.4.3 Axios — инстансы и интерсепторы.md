---
type: topic
domain: frontend
stage: 5
section: "5.4"
order: 3
status: todo
level: middle
notion_id: 3ea331048679812ba856e1ba38a2e798
tags: [domain/frontend, stage/5, level/middle, topic/api, topic/axios, topic/interceptors, priority/must]
reviewed:
next_review:
priority: must
time: 4
---

# Axios: инстансы и интерсепторы

↑ [[FE 5.4 Работа с API — REST, GraphQL, WebSocket|5.4 Работа с API: REST, GraphQL, WebSocket]] · ← [[FE 5.4.2 Fetch API и Axios|Предыдущая]] · → [[FE 5.4.4 Обработка ошибок, retry, отмена запросов (AbortController)|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~4 мин чтения</span><span class="chip">Уровень: middle</span></div>
<!-- meta:end -->















> [!info] Зачем это на собесе
> Типовая задача: подстановка токена, обновление при 401, общий обработчик ошибок.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

```ts
export const api = axios.create({ baseURL: import.meta.env.VITE_API_URL, timeout: 15_000, headers: { Accept: "application/json" }, withCredentials: false });

api.interceptors.request.use((cfg) => {
  const token = useAuthStore().accessToken;
  if (token) cfg.headers.Authorization = `Bearer ${token}`;
  cfg.headers["X-Request-Id"] = crypto.randomUUID();                 // корреляция с логами бэкенда
  return cfg;
});

// Обновление токена при 401 с очередью запросов и защитой от гонок
let refreshing: Promise<string> | null = null;
api.interceptors.response.use(
  (res) => res,
  async (error: AxiosError) => {
    const original = error.config as AxiosRequestConfig & { _retry?: boolean };
    if (error.response?.status === 401 && !original._retry && !original.url?.includes("/auth/")) {
      original._retry = true;
      refreshing ??= useAuthStore().refresh().finally(() => (refreshing = null));      // один refresh на все запросы
      try { const t = await refreshing; original.headers = { ...original.headers, Authorization: `Bearer ${t}` }; return api(original); }
      catch { useAuthStore().logout(); }
    }
    return Promise.reject(normalizeError(error));                      // единый формат ошибок
  },
);
```

Что типично делают интерсепторы:

| Задача | Интерсептор |
|---|---|
| Токен, язык (`Accept-Language`), tenant | request |
| Корреляционный id, трассировка (`traceparent`) | request |
| Обновление токена, редирект на логин | response (401) |
| Нормализация ошибок, показ уведомлений | response |
| Логирование, метрики | оба |
| Повторы | response (с ограничением) |
| Лоадер | счётчик активных запросов |

Несколько инстансов: публичный API, внутренний, внешние сервисы — с разными `baseURL`/авторизацией. Типизация: `api.get<Order[]>("/orders")`, обобщения обёртки.

Перевод на `fetch`-адаптер или `ky`/`ofetch` возможен; логика интерсепторов сохраняется (обёртка с хуками).

## Нюансы и подводные камни

- Бесконечный цикл при повторе запроса с 401: флаг `_retry`, исключение auth-эндпоинтов.
- Параллельные 401 вызывают несколько `refresh`: объединяйте в один промис.
- Интерсептор не должен показывать уведомление на каждую ошибку (ожидаемые 4xx обрабатываются локально).
- Утечки при добавлении интерсепторов в `setup` без `eject`.
- Секреты в логах интерсептора.

## Практика

1. Реализуйте обновление токена с очередью запросов.
2. Настройте единый формат ошибок и связь с Vue Query.
3. Добавьте `X-Request-Id`/`traceparent` в исходящие запросы.

## Вопросы с ответами

> [!question]- Как реализовать refresh токена в Axios?
> Response-интерсептор на 401: один общий запрос обновления, повтор оригинального запроса с новым токеном и флагом `_retry`.

> [!question]- Зачем несколько инстансов?
> Разные базовые URL, заголовки и политики для разных сервисов.

## Связанные темы

- [[N:3ea33104867981e4b92aed4daaecffce]]
- [[N:3ea331048679814ea06ec88873e2751d]]
