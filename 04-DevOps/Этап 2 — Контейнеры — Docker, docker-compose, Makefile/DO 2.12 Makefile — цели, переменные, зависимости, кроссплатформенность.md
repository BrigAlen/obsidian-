---
type: topic
domain: devops
stage: 2
order: 12
status: todo
level: junior
tags: [domain/devops, stage/2, level/junior, priority/must]
reviewed: 
next_review: 
priority: must
time: 9
---

# Makefile: цели, переменные, зависимости, кроссплатформенность

↑ [[DO Этап 2 · Контейнеры — Docker, docker-compose, Makefile|Этап 2 · Контейнеры: Docker, docker-compose, Makefile]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~9 мин чтения</span><span class="chip">Уровень: junior</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> Makefile — «единая точка входа» в проект: как удобно запускать сборку, тесты, деплой и окружение. Спрашивают переменные, зависимости, .PHONY.

## Зачем Makefile в проекте

Единый интерфейс команд для разработчиков и CI: `make up`, `make test`, `make deploy ENV=stage`. Вместо длинных команд в README и разрозненных скриптов. Старый инструмент (make), есть везде (кроме Windows «из коробки»), легко читается.

## Базовый синтаксис

```make
цель: зависимости
<TAB>команда
```

**Обязателен символ табуляции** перед командой (не пробелы).

```make
.PHONY: build test up down logs clean

build:
	docker compose build

up: build
	docker compose up -d

test:
	dotnet test --no-build

clean:
	rm -rf bin obj
```

- **`.PHONY`**: цели, не соответствующие файлам (иначе при наличии файла/каталога с таким именем make «решит», что цель актуальна и ничего не сделает);
- зависимости выполняются раньше цели; make строит граф и пропускает актуальные цели (для файловых целей сравнение времени изменения);
- `@command` — не печатать команду; `-command` — игнорировать ошибку; `+command` — выполнять даже в `--dry-run`;
- каждая строка рецепта выполняется в **отдельном shell** (`cd` не сохраняется): объединяйте `cd dir && cmd` или `.ONESHELL:`.

## Переменные

```make
SHELL := /bin/bash
.SHELLFLAGS := -eu -o pipefail -c          # ошибки в пайпах не теряются
.DEFAULT_GOAL := help

ENV      ?= dev                            # ?= значение по умолчанию, можно переопределить: make ENV=prod
IMAGE    := registry.example.com/clinic/api
VERSION  := $(shell git describe --tags --always --dirty)
COMPOSE  := docker compose -f compose.yaml -f compose.$(ENV).yaml

build:
	docker build -t $(IMAGE):$(VERSION) --build-arg GIT_SHA=$(shell git rev-parse --short HEAD) .
```

Операторы: `=` (рекурсивное, отложенное), `:=` (простое, вычисляется сразу), `?=` (если не задана), `+=` (добавление). Переменные окружения доступны как переменные make; переопределение в командной строке приоритетнее. `$(VAR)` — подстановка; в shell-части `$$VAR` (двойной `$`).

Автоматические переменные: `$@` — имя цели, `$<` — первая зависимость, `$^` — все зависимости.

```make
%.o: %.c                    # шаблонное правило
	$(CC) -c $< -o $@
```

## Справка (help) — самодокументируемый Makefile

```make
.PHONY: help
help:  ## Показать список команд
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN{FS=":.*?## "}{printf "\033[36m%-18s\033[0m %s\n", $$1, $$2}'

up: ## Запустить окружение
	$(COMPOSE) up -d --wait

down: ## Остановить окружение
	$(COMPOSE) down

migrate: ## Применить миграции БД
	$(COMPOSE) run --rm migrate

test: ## Запустить тесты
	dotnet test

lint: ## Проверки кода
	dotnet format --verify-no-changes && npm --prefix web run lint
```

`make` без аргументов показывает справку.

## Условия, include, окружения

```make
ifeq ($(ENV),prod)
  COMPOSE_FILES := -f compose.yaml -f compose.prod.yaml
else
  COMPOSE_FILES := -f compose.yaml
endif

-include .env                               # подключить переменные окружения (- не падать, если нет файла)
export                                      # экспортировать переменные в дочерние процессы

define check_env
	@test -n "$($1)" || (echo "Переменная $1 не задана" && exit 1)
endef

deploy: ## make deploy ENV=stage TAG=1.2.3
	$(call check_env,TAG)
	ansible-playbook -i inventories/$(ENV) deploy.yml -e tag=$(TAG)
```

## Параллелизм и зависимости

`make -j4` выполняет независимые цели параллельно. `order-only` зависимости (`| dir`) для каталогов. Не зависеть от порядка неявно.

## Кроссплатформенность

- на Windows make нет по умолчанию (Git Bash, WSL, `choco install make`, `scoop`); команды должны работать в sh: избегайте `rm`/`cp` без учёта ОС, используйте Docker/кросс-платформенные утилиты;
- различия GNU make и BSD/macOS make (macOS ставит старую 3.81: `brew install make`, `gmake`);
- `uname -s` для ветвления по ОС:

```make
UNAME := $(shell uname -s)
ifeq ($(UNAME),Darwin)
  OPEN := open
else
  OPEN := xdg-open
endif
```

- держите «тяжёлую» логику в скриптах (`scripts/*.sh` или Python), а Makefile — лёгкой оболочкой;
- альтернативы: **Taskfile (go-task)**, **just**, `npm scripts`, Nx/Turborepo, Cake/Nuke (для .NET), `mise`.

## Типичные цели проекта

```text
make setup      — установить зависимости, pre-commit, скопировать .env.example
make up / down  — локальное окружение (compose)
make build      — сборка образов
make test / lint / fmt
make migrate / seed
make logs S=api — логи сервиса
make shell S=api
make release VERSION=1.2.0 — тег, образы, changelog
make deploy ENV=stage
make clean
```

## Практики

- документируйте цели (`##`), цель `help` по умолчанию;
- **идемпотентность** и безопасные значения по умолчанию;
- `.PHONY` для всех нефайловых целей;
- CI вызывает те же цели (`make test`), что и разработчик — исключает расхождения;
- не прятать секреты в Makefile; пароли через окружение;
- защищать опасные цели (`make prod-destroy` запрашивает подтверждение);
- `make -n` (dry-run), `make -B` (пересобрать всё), `make --debug`.

## Вопросы с ответами

> [!question]- Зачем нужен .PHONY?
> Чтобы цели-команды (up, test, clean) выполнялись всегда, даже если в каталоге есть файл с тем же именем: иначе make сочтёт цель актуальной.

> [!question]- Почему cd в одной строке рецепта не влияет на следующую?
> Каждая строка выполняется в отдельном процессе shell; нужно объединять команды через `&&`/`;` или включить `.ONESHELL`.

> [!question]- Чем = отличается от :=?
> `=` вычисляется при каждом использовании (отложенно), `:=` — один раз в момент присваивания (с зафиксированным результатом, удобно для `$(shell ...)`).
