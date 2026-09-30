---
type: topic
domain: devops
stage: 1
order: 10
status: todo
level: junior
tags: [domain/devops, stage/1, level/junior, priority/should]
group: Скрипты и автоматизация
reviewed: 
next_review: 
priority: should
time: 7
---

# Python для автоматизации DevOps-задач

↑ [[DO Этап 1 · Фундамент — Linux, Bash, сети|Этап 1 · Фундамент: Linux, Bash, сети]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~7 мин чтения</span><span class="chip">Уровень: junior</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> Когда Bash становится тесным, DevOps пишет на Python: работа с API, JSON, файлами, облаками. Спрашивают практику скриптов, а не синтаксис.

## Когда Python вместо Bash

| Bash | Python |
|---|---|
| склейка команд, простые пайпы | структуры данных, JSON/YAML, HTTP, исключения |
| до ~50 строк | длинные скрипты, тесты, библиотеки |
| есть только shell | нужна переносимость и читаемость |

## Окружение

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install requests pyyaml boto3 click
pip freeze > requirements.txt          # или pip-tools / poetry / uv для фиксации зависимостей
```

Всегда используйте **виртуальное окружение**; современные менеджеры: `uv`, `poetry`, `pipx` (для CLI-утилит).

## Каркас скрипта

```python
#!/usr/bin/env python3
"""Проверка доступности сервисов."""
import argparse, json, logging, subprocess, sys
from pathlib import Path
import requests

log = logging.getLogger("check")

def check(url: str, timeout: float = 5.0) -> bool:
    try:
        r = requests.get(url, timeout=timeout)
        r.raise_for_status()
        return True
    except requests.RequestException as e:
        log.error("%s недоступен: %s", url, e)
        return False

def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("urls", nargs="+")
    p.add_argument("-v", "--verbose", action="store_true")
    args = p.parse_args()
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO,
                        format="%(asctime)s %(levelname)s %(message)s")
    results = {u: check(u) for u in args.urls}
    print(json.dumps(results, indent=2))
    return 0 if all(results.values()) else 1

if __name__ == "__main__":
    sys.exit(main())
```

## Частые задачи DevOps

**Файлы и пути**

```python
from pathlib import Path
for p in Path("/var/log/app").glob("*.log"):
    if p.stat().st_size > 100 * 1024**2:
        print(p, p.stat().st_size)
Path("out").mkdir(parents=True, exist_ok=True)
text = Path("config.yaml").read_text(encoding="utf-8")
```

**JSON и YAML**

```python
import json, yaml
data = json.loads(text); json.dump(data, open("o.json", "w"), indent=2, ensure_ascii=False)
cfg = yaml.safe_load(open("values.yaml"))        # всегда safe_load
```

**Запуск команд**

```python
import subprocess
res = subprocess.run(["kubectl", "get", "pods", "-o", "json"], capture_output=True, text=True, check=True, timeout=30)
pods = json.loads(res.stdout)
# shell=True только при необходимости и НЕ с пользовательским вводом (инъекции)
```

**HTTP/API**

```python
s = requests.Session()
s.headers["Authorization"] = f"Bearer {token}"
r = s.get("https://api/x", params={"limit": 100}, timeout=10)   # timeout обязателен!
r.raise_for_status(); data = r.json()
```

Повторы с backoff: `tenacity`, `urllib3.util.Retry`. Параллелизм: `concurrent.futures.ThreadPoolExecutor` для I/O.

**Облака и инфраструктура**: `boto3` (AWS), SDK Yandex Cloud, `kubernetes` (клиент API), `docker` (SDK), `paramiko`/`fabric` (SSH), `psycopg` (БД), `prometheus_client` (метрики), `jinja2` (шаблоны).

```python
import boto3
s3 = boto3.client("s3", endpoint_url="http://minio:9000")
for obj in s3.list_objects_v2(Bucket="backups").get("Contents", []):
    print(obj["Key"], obj["Size"])
```

**CLI-утилиты**: `argparse`, `click`/`typer`; цвет и таблицы — `rich`.

## Практики качества

- **исключения и коды выхода**: ненулевой код при ошибке — иначе CI/cron не заметят;
- **логирование** через `logging`, а не `print`; уровни;
- **таймауты** на все сетевые вызовы;
- **идемпотентность** действий;
- **секреты** из переменных окружения/хранилища, не в коде (`os.environ["TOKEN"]`);
- **типизация** (type hints) и `mypy`/`ruff` для проверок; тесты `pytest`;
- зависимости зафиксированы; запуск в контейнере или `pipx`;
- не использовать `shell=True`, `eval`, `pickle` для недоверенных данных;
- `if __name__ == "__main__"` для импортируемости.

## Пример: очистка старых образов в реестре (псевдокод)

```python
from datetime import datetime, timedelta, timezone
cutoff = datetime.now(timezone.utc) - timedelta(days=30)
for tag in registry.list_tags(repo):
    if tag.created < cutoff and not tag.name.startswith(("v", "release-")):
        log.info("удаляю %s:%s", repo, tag.name)
        if not args.dry_run:
            registry.delete(repo, tag.name)
```

Всегда предусматривайте `--dry-run` для разрушающих операций.

## Вопросы с ответами

> [!question]- Почему нужен timeout у requests?
> По умолчанию `requests` ждёт бесконечно: зависший сервис подвесит скрипт, cron-задачу или пайплайн.

> [!question]- Чем плох subprocess с shell=True?
> Команда интерпретируется оболочкой: при подстановке внешних данных возможна инъекция команд; также сложнее корректно экранировать аргументы.

> [!question]- Когда писать на Python, а не на Bash?
> Когда нужны структуры данных, работа с JSON/HTTP/облачными API, обработка ошибок, тесты и поддержка; для склейки нескольких команд достаточно Bash.
