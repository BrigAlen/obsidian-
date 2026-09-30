# develop — vault для подготовки к собеседованиям (Obsidian)

Fullstack-роадмап: Backend (C#/.NET), Frontend (Vue 3 + TS), базы данных, DevOps, сквозной проект и промпты для AI-ассистента.
Перенесён по структуре из Notion. Тексты тем заполняются по шаблону `_templates/Тема.md`.

## Как открыть
1. Склонируйте репозиторий: `git clone https://github.com/BrigAlen/obsidian-`
2. Obsidian → *Open folder as vault* → выберите папку.
3. Начните с `00 Карта.md`.

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
```
Имена заметок: `BE|FE|DB|DO <этап>.<номер> <название>` — уникальны по всему vault.

## Прогресс
В frontmatter каждой темы: `status: todo | in-progress | done`, `reviewed`, `next_review`. Dataview на `00 Карта.md` считает прогресс сам.
