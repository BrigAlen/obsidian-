---
type: topic
domain: backend
stage: 6
section: "6.1"
order: 2
status: todo
level: junior
notion_id: 3ea33104867981099ac9ff396547152a
tags: [domain/backend, stage/6, level/junior, topic/nodejs, topic/npm, priority/nice]
reviewed:
next_review:
priority: nice
time: 3
---

# Модули, npm, package.json

↑ [[BE 6.1 Node.js изнутри|6.1 Node.js изнутри]] · ← [[BE 6.1.1 Event loop в Node.js и libuv|Предыдущая]] · → [[BE 6.1.3 Streams и Buffer|Следующая]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge nice">По желанию</span><span class="chip">~3 мин чтения</span><span class="chip">Уровень: junior</span></div>
<!-- meta:end -->




> [!info] Зачем это на собесе
> Базовые вопросы: CommonJS против ES modules, версии зависимостей, lock-файл.

> [!note] Переписано
> Страница в Notion была заготовкой, содержимое написано заново.

## Объяснение

| Система | Синтаксис | Особенности |
|---|---|---|
| CommonJS | `require`, `module.exports` | синхронная загрузка, значения кэшируются |
| ES modules | `import`/`export` | статический анализ, асинхронная загрузка, `"type": "module"` |

```json
{
  "name": "orders-api",
  "version": "1.0.0",
  "type": "module",
  "scripts": { "dev": "tsx watch src/main.ts", "build": "tsc", "test": "vitest" },
  "dependencies": { "fastify": "^4.28.0" },
  "devDependencies": { "typescript": "~5.5.0" },
  "engines": { "node": ">=20" }
}
```

Семантическое версионирование (`major.minor.patch`): `^4.28.0` разрешает minor и patch, `~5.5.0` — только patch. **package-lock.json** фиксирует точные версии и хэши; в CI используйте `npm ci` (строго по lock-файлу, быстрее и воспроизводимо).

| Менеджер | Особенности |
|---|---|
| npm | стандарт |
| pnpm | жёсткие ссылки, экономия диска, строгая структура зависимостей |
| yarn | workspaces, plug'n'play |

## Нюансы и подводные камни

- `dependencies` и `devDependencies`: в образ продакшена ставьте только первые (`npm ci --omit=dev`).
- Цепочки транзитивных зависимостей — риск supply chain: `npm audit`, фиксация версий, проверка пакетов.
- Скрипты `postinstall` выполняют код при установке.
- Смешение CJS и ESM даёт ошибки (`ERR_REQUIRE_ESM`, `__dirname` отсутствует в ESM).
- Не коммитьте `node_modules`; коммитьте lock-файл.

## Практика

1. Настройте проект на ESM с TypeScript.
2. Сравните время установки npm и pnpm.
3. Выполните `npm audit` и разберите найденные уязвимости.

## Вопросы с ответами

> [!question]- Чем npm ci отличается от npm install?
> `ci` ставит строго по lock-файлу, удаляет `node_modules` и падает при расхождении с `package.json`; предназначен для CI.

> [!question]- Что значит ^1.2.3?
> Любая версия `>=1.2.3` и `<2.0.0`.

> [!question]- CommonJS или ESM?
> Для новых проектов ESM; CJS остаётся в legacy-коде.

## Связанные темы

- [[N:3ea33104867981eca57edd25122e2f4d]]
- [[N:3ea3310486798147ba50e9e03c350889]]
