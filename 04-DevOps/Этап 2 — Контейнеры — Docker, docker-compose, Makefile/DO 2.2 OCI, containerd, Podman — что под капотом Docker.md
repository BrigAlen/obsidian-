---
type: topic
domain: devops
stage: 2
order: 2
status: todo
level: junior
tags: [domain/devops, stage/2, level/junior, priority/must]
reviewed: 
next_review: 
priority: must
time: 4
---

# OCI, containerd, Podman: что под капотом Docker

↑ [[DO Этап 2 · Контейнеры — Docker, docker-compose, Makefile|Этап 2 · Контейнеры: Docker, docker-compose, Makefile]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~4 мин чтения</span><span class="chip">Уровень: junior</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> Docker — лишь один из инструментов. Понимание стека (OCI, containerd, runc) нужно для Kubernetes и отладки.

## Стандарты OCI

**Open Container Initiative** (Linux Foundation) задаёт открытые стандарты:

- **Image Spec**: формат образа (манифест, конфигурация, слои, контент-адресация по sha256);
- **Runtime Spec**: как запускать контейнер по «бандлу» (`config.json` + rootfs);
- **Distribution Spec**: API реестров образов (`/v2/...`, pull/push).

Благодаря стандартам образ, собранный Docker, запускается в Podman, containerd, CRI-O и Kubernetes.

## Стек компонентов

```text
docker CLI ──▶ dockerd (Docker Engine, API, сети, тома, build)
                  │
                  ▼
              containerd (управление жизненным циклом, образы, снимки)
                  │
                  ▼
              containerd-shim ──▶ runc ──▶ процесс контейнера (namespaces, cgroups)
```

| Компонент | Роль |
|---|---|
| **runc** | низкоуровневый runtime (референсная реализация OCI): создаёт namespaces/cgroups и запускает процесс |
| **containerd** | высокоуровневый runtime: загрузка образов, хранилище, снимки, вызовы runc; используется Docker и Kubernetes |
| **dockerd** | демон Docker: REST API, build (BuildKit), сети, volumes, compose |
| **containerd-shim** | «прокладка»: контейнер не зависит от перезапуска containerd; хранит stdio/код выхода |
| **CRI-O** | лёгкий runtime специально для Kubernetes |
| **crun, youki, gVisor (runsc), kata** | альтернативные низкоуровневые runtimes |
| **nerdctl** | Docker-совместимый CLI для containerd |
| **ctr, crictl** | низкоуровневые CLI (отладка containerd / CRI) |

## Kubernetes и Docker

**CRI** (Container Runtime Interface) — API между kubelet и runtime. С версии 1.24 Kubernetes **убрал dockershim**: кластеры используют containerd или CRI-O напрямую. Образы Docker по-прежнему работают (стандарт OCI). Для отладки на ноде: `crictl ps`, `crictl logs`, `crictl images`.

## Podman

Совместимая с Docker CLI альтернатива **без демона** и с упором на **rootless**.

```bash
podman run -d --name web -p 8080:80 nginx
podman ps; podman logs web; podman build -t app .
podman generate kube web > web.yaml      # генерация манифеста Kubernetes
podman play kube web.yaml                # запуск pod из YAML
podman pod create --name mypod -p 8080:80   # поды как в Kubernetes
podman compose up                        # или podman-compose
```

Особенности:

- **без демона** (fork/exec, каждый контейнер — дочерний процесс пользователя): нет единой точки отказа и root-демона;
- **rootless по умолчанию**: контейнеры без root-привилегий на хосте (user namespaces, `slirp4netns`/`pasta` для сети);
- интеграция с **systemd** (Quadlet: `.container` unit-файлы) — запуск контейнеров как сервисов;
- `alias docker=podman` для совместимости; Buildah (сборка), Skopeo (копирование образов между реестрами).

## Образ внутри

```bash
docker save nginx -o nginx.tar && tar -tf nginx.tar      # манифест, конфиг, слои (tar)
skopeo inspect docker://nginx:1.27
crane manifest nginx:1.27 | jq                            # go-containerregistry
```

Манифест → конфиг (env, cmd, entrypoint) + список слоёв; **digest** (`sha256:...`) идентифицирует контент неизменяемо, теги — подвижные указатели.

## Сборка

**BuildKit** (по умолчанию в Docker): параллельная сборка, кэш, секреты (`--mount=type=secret`), SSH, multi-platform (`buildx`). Альтернативы: Buildah, Kaniko (без демона, для CI в Kubernetes), ko (Go), Jib (Java), `dotnet publish /t:PublishContainer` (.NET без Dockerfile).

## Вопросы с ответами

> [!question]- Что такое runc и чем он отличается от containerd?
> runc — низкоуровневый OCI-runtime, который непосредственно создаёт контейнер (namespaces, cgroups). containerd — высокоуровневый демон: образы, хранилище, жизненный цикл, вызывает runc.

> [!question]- Чем Podman отличается от Docker?
> Без демона, rootless по умолчанию, интеграция с systemd и концепция pod; CLI совместим с Docker.

> [!question]- Почему Kubernetes отказался от Docker?
> Убрали dockershim — промежуточный слой: kubelet общается с runtime по CRI напрямую (containerd/CRI-O). Образы Docker продолжают работать благодаря стандарту OCI.
