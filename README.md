# Developer — vault для подготовки к собеседованиям (Obsidian)

Fullstack-роадмап: Backend (C#/.NET), Frontend (Vue 3 + TS), базы данных, DevOps, сквозной проект и промпты для AI-ассистента.
Перенесён по структуре из Notion. Тексты тем заполняются по шаблону `_templates/Тема.md`.

## Как открыть в Obsidian
1. Склонируйте репозиторий: `git clone https://github.com/BrigAlen/obsidian-`
2. Obsidian → *Open folder as vault* → выберите папку.
3. Начните с `00 Карта.md`.

## Сайт и приложение

Vault публикуется в двух видах:

| Вид | Адрес | Что есть |
|---|---|---|
| Статический сайт (GitHub Pages) | https://brigalen.github.io/obsidian-/ | только чтение, без аккаунтов |
| Приложение (Render + Neon) | адрес вида `https://vault-….onrender.com` | сайт плюс вход, отметки о прохождении, заметки, личный кабинет |

Приложение работает в одном Docker-образе: собранный сайт (Quartz) и API (ASP.NET Core, .NET 10). База данных внешняя, PostgreSQL в Neon. Список планов: заметка `Бэклог`.

### Запуск на Render

1. **Neon.** На neon.tech создайте проект с PostgreSQL. На странице проекта нажмите *Connect*, отключите *Pooled connection* и скопируйте строку подключения `postgresql://…`.
2. **Render.** Подключите GitHub-аккаунт и дайте доступ к репозиторию. *New → Blueprint* → выберите репозиторий, ветка `main`. Render прочитает `render.yaml`.
3. **Переменные** (вводятся в Render, в git их нет):
   - `DATABASE_URL` — строка из Neon;
   - `ADMIN_LOGIN` и `ADMIN_PASSWORD` — логин и пароль первого администратора (пароль от 8 символов).
4. Дождитесь первой сборки (10–15 минут) и статуса *Live*, откройте адрес сервиса и войдите.
5. Новые пользователи: *Личный кабинет → Администрирование → Создать приглашение*, код отправьте человеку. Регистрация только по приглашению.

Каждый push в `main` пересобирает и перезапускает сервис сам. Бесплатный тариф засыпает после простоя, первый запрос тогда идёт около минуты.

### Локальный запуск

Нужны Docker и свободные порты 5432 и 8080. Команды из корня репозитория.

**Всё в Docker (как на сервере):**

```bash
docker network create vaultnet
docker run -d --name vault-db --network vaultnet \
  -e POSTGRES_USER=vault -e POSTGRES_PASSWORD=vault -e POSTGRES_DB=vault postgres:16

docker build -t vault .          # собирает сайт и API, 5–10 минут
docker run --rm --name vault --network vaultnet -p 8080:8080 \
  -e DATABASE_URL="Host=vault-db;Database=vault;Username=vault;Password=vault" \
  -e ADMIN_LOGIN=admin -e ADMIN_PASSWORD=change-me-please \
  vault
```

Откройте http://localhost:8080 и войдите под `admin`. Остановить и убрать: `docker rm -f vault-db && docker network rm vaultnet`. Данные базы при этом удалятся.

**Только API, без пересборки сайта** (нужен .NET 10 SDK; удобно при правке кода):

```bash
docker run -d --name vault-db -e POSTGRES_USER=vault -e POSTGRES_PASSWORD=vault -e POSTGRES_DB=vault -p 5432:5432 postgres:16
export DATABASE_URL="Host=localhost;Database=vault;Username=vault;Password=vault"
export ADMIN_LOGIN=admin ADMIN_PASSWORD=change-me-please
dotnet run --project api/src/VaultApi
```

API стартует на порту из `PORT` (по умолчанию 5000). Без собранного сайта в `wwwroot` будут работать только методы `/api/*`. Сайт для этого режима собирает `site/build.sh <vault> <папка Quartz> <папка результата>` (нужны Node 22, git, python3, perl, rsync), результат кладётся в `api/src/VaultApi/wwwroot` или указывается через `ASPNETCORE_WEBROOT`.

**Тесты API** (нужен локальный PostgreSQL с ролью `vault`/`vault` и правом создавать базы):

```bash
dotnet test api/tests/VaultApi.Tests
```

Подробности по API, переменным окружения и миграциям: `api/README.md`.

### Частые проблемы

- *Сервис на Render в статусе Failed* — откройте *Logs*. Чаще всего неверная `DATABASE_URL` (обрезана строка, включён *Pooled connection*) или не заданы переменные.
- *«Неверный логин или пароль»* у администратора — `ADMIN_LOGIN` и `ADMIN_PASSWORD` применяются только при первом запуске, пока в базе нет пользователей. Для смены пароля используйте *Сменить пароль* в меню аккаунта.
- *Слишком много попыток* — лимит входа 10 в минуту с одного IP, подождите минуту.

## Плагины (Settings → Community plugins)
- **Dataview** — таблицы прогресса на картах (обязателен)
- **Templater** или встроенные Templates — папка шаблонов `_templates`
- **Spaced Repetition** — карточки `Вопрос::Ответ` (тег `#flashcards`)
- **Obsidian Git** — автосинхронизация с этим репозиторием

## Структура
```
00 Карта.md            главная страница (MOC, прогресс)
01-Backend/            9 этапов → темы
02-Frontend/           9 этапов → темы
03-Базы данных/        7 этапов → темы
04-DevOps/             9 этапов → темы
05-Fullstack-практика/ сквозной проект
07-Мои-заметки/        личные заметки, Inbox
_templates/            шаблоны заметок
api/                   бэкенд (ASP.NET Core) и его тесты
site/                  сборка сайта: Quartz, стили, клиентский код аккаунтов
Dockerfile, render.yaml   образ приложения и настройка Render
```
Имена заметок: `BE|FE|DB|DO <этап>.<номер> <название>` — уникальны по всему vault.

## Прогресс
В frontmatter каждой темы: `status: todo | in-progress | done`, `reviewed`, `next_review`. Dataview на `00 Карта.md` считает прогресс сам.
