---
type: topic
domain: devops
stage: 2
order: 7
status: todo
level: junior
tags: [domain/devops, stage/2, level/junior, priority/must]
reviewed: 
next_review: 
priority: must
time: 6
---

# Сети и volumes в Docker

↑ [[DO Этап 2 · Контейнеры — Docker, docker-compose, Makefile|Этап 2 · Контейнеры: Docker, docker-compose, Makefile]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~6 мин чтения</span><span class="chip">Уровень: junior</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> Контейнерные сети и тома — обязательная часть вопросов: как контейнеры общаются и где хранятся данные.

## Сетевые драйверы

| Драйвер | Описание |
|---|---|
| **bridge** (по умолчанию) | виртуальный мост `docker0`/пользовательский: контейнеры в своей подсети, NAT наружу |
| **host** | контейнер использует сетевой стек хоста (без изоляции и NAT; быстро; порты хоста) |
| **none** | без сети |
| **overlay** | сеть между хостами (Swarm) |
| **macvlan / ipvlan** | контейнер получает адрес во внешней L2-сети |

```bash
docker network ls; docker network inspect bridge
docker network create --driver bridge --subnet 172.30.0.0/24 appnet
docker run -d --name api --network appnet myapi
docker network connect appnet existing_container
```

## Пользовательский bridge и DNS

В пользовательской сети (не `default bridge`) работает **встроенный DNS**: контейнеры обращаются друг к другу **по имени контейнера/сервиса** (`http://api:8080`, `postgres:5432`), а не по IP. В compose все сервисы автоматически попадают в общую сеть проекта с именами = названия сервисов; алиасы: `networks.<name>.aliases`.

Изоляция: контейнеры в разных сетях не видят друг друга; сервис может входить в несколько сетей (например, `frontend` и `backend`, а БД только в `backend`).

```yaml
services:
  nginx:   { networks: [public, internal] }
  api:     { networks: [internal] }
  db:      { networks: [internal] }
networks:
  public:
  internal: { internal: true }     # без доступа наружу
```

## Публикация портов

```bash
docker run -p 8080:80 nginx                    # хост:контейнер на всех интерфейсах (0.0.0.0)
docker run -p 127.0.0.1:5432:5432 postgres     # только localhost (БД наружу не выставлять!)
docker run -P nginx                            # случайные порты для EXPOSE
docker port web
```

- `EXPOSE` — документация, не публикация;
- публикация реализована через **iptables DNAT** и `docker-proxy`; Docker обходит ufw (см. firewall);
- связь контейнер→контейнер в одной сети **не требует** публикации портов.

Доступ контейнера к хосту: `host.docker.internal` (Docker Desktop; на Linux — `--add-host=host.docker.internal:host-gateway`).

## Volumes и хранение данных

Файловая система контейнера эфемерна. Способы сохранить данные:

| Тип | Пример | Когда |
|---|---|---|
| **Named volume** | `-v pgdata:/var/lib/postgresql/data` | данные, управляемые Docker (`/var/lib/docker/volumes`): БД, файлы приложений |
| **Bind mount** | `-v $(pwd)/conf:/etc/app:ro` | файлы хоста: разработка, конфиги |
| **tmpfs** | `--tmpfs /tmp` | временные данные в памяти (секреты, скорость) |

```bash
docker volume create pgdata; docker volume ls; docker volume inspect pgdata
docker run -d -v pgdata:/var/lib/postgresql/data postgres:17
docker run --rm -v pgdata:/data -v $(pwd):/backup alpine tar czf /backup/pgdata.tgz -C /data .   # бэкап тома
docker volume prune
```

```yaml
services:
  db:
    image: postgres:17
    volumes:
      - pgdata:/var/lib/postgresql/data
      - ./init:/docker-entrypoint-initdb.d:ro
volumes:
  pgdata:
```

Named volume **инициализируется содержимым образа** при первом монтировании (если пуст), bind mount — нет (перекрывает каталог). Права: UID процесса в контейнере должен иметь доступ (`chown`, `user:` в compose, `fsGroup` в Kubernetes).

Драйверы томов: `local`, NFS (`driver_opts`), облачные, плагины. Производительность bind mount на macOS/Windows ниже (файловая виртуализация).

## Данные и отказоустойчивость

- тома не равны бэкапам: копируйте (pg_dump/снапшоты);
- БД в контейнерах в проде: нужно осознанное хранение (PVC, локальные SSD, оператор) — часто управляемые БД;
- не храните состояние в слое контейнера.

## Диагностика

```bash
docker exec api getent hosts db          # DNS внутри сети
docker exec api nc -zv db 5432
docker network inspect appnet | jq '.[0].Containers'
docker inspect api | jq '.[0].NetworkSettings.Networks'
sudo nsenter -t $(docker inspect -f '{{.State.Pid}}' api) -n ss -tulpn
docker run --rm --network container:api nicolaka/netshoot    # сетевой toolbox в сети контейнера
```

Частые проблемы: `localhost` внутри контейнера — это сам контейнер (а не хост и не другой сервис); приложение слушает `127.0.0.1`, а нужно `0.0.0.0`; не в той сети; пересечение подсетей с VPN (`default-address-pools` в `daemon.json`); DNS (`--dns`), MTU за VPN.

## Вопросы с ответами

> [!question]- Как контейнеры находят друг друга по имени?
> В пользовательской bridge-сети (и в compose) работает встроенный DNS Docker, разрешающий имена контейнеров/сервисов. В default bridge имён нет.

> [!question]- Чем volume отличается от bind mount?
> Volume управляется Docker (хранится в его каталоге, портируем, инициализируется содержимым образа), bind mount связывает конкретный путь хоста с контейнером (удобно для разработки и конфигов).

> [!question]- Почему приложение в контейнере не доступно снаружи, хотя порт опубликован?
> Часто оно слушает `127.0.0.1` внутри контейнера вместо `0.0.0.0`, либо порт не опубликован/заблокирован firewall; проверять `ss -tulpn` внутри и `docker port`.
