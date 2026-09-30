# Vault API

Бэкенд сайта: вход по логину и паролю (регистрация по приглашениям), отметки о прохождении тем, заметки. ASP.NET Core (.NET 10), EF Core, PostgreSQL. В Docker-образе вместе с собранным сайтом.

## Переменные окружения

| Переменная | Назначение |
|---|---|
| `DATABASE_URL` | строка подключения PostgreSQL (`postgresql://user:pass@host/db?sslmode=require` или формат Npgsql) |
| `ADMIN_LOGIN`, `ADMIN_PASSWORD` | первый администратор, создаётся при пустой базе |
| `PORT` | порт (Render задаёт сам) |
| `AUTH_RATE_LIMIT` | попыток входа и регистрации в минуту с одного IP, по умолчанию 10 |

Секреты хранятся только в панели Render, в репозитории их нет.

## Локальный запуск

Пошаговая инструкция (всё в Docker или только API через `dotnet run`) — в корневом `README.md`, раздел «Локальный запуск».

## Тесты

Интеграционные тесты идут на локальном PostgreSQL (пользователь `vault`, пароль `vault`, право создавать базы):

```bash
dotnet test api/tests/VaultApi.Tests
```

## API

Все изменяющие запросы требуют заголовок `X-Requested-With: vault` (защита от CSRF).

| Метод | Путь | Кто |
|---|---|---|
| POST | `/api/auth/register` `{login,password,invite}` | по приглашению |
| POST | `/api/auth/login`, `/api/auth/logout`, `/api/auth/password` | |
| GET | `/api/me` (204 без входа) | |
| GET, PUT | `/api/progress/` `{slug,status}` | вошедший |
| GET, POST | `/api/notes/` (`?slug=&q=&skip=&take=`) | вошедший |
| PUT, DELETE | `/api/notes/{id}` | автор |
| POST | `/api/admin/invites` | админ |
| GET | `/api/admin/users` | админ |
| POST | `/api/admin/users/{id}/reset-password`, `/block?blocked=` | админ |
| GET | `/healthz` | все |

## Миграции

```bash
dotnet tool install --global dotnet-ef
dotnet ef migrations add Name --project api/src/VaultApi -o Data/Migrations
```

Применяются автоматически при запуске.
