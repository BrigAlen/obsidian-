---
type: topic
domain: devops
stage: 2
order: 13
status: todo
level: junior
tags: [domain/devops, stage/2, level/junior, priority/must]
reviewed: 
next_review: 
priority: must
time: 5
---

# Безопасность контейнеров: capabilities, seccomp, read-only, rootless

↑ [[DO Этап 2 · Контейнеры — Docker, docker-compose, Makefile|Этап 2 · Контейнеры: Docker, docker-compose, Makefile]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge must">Обязательно</span><span class="chip">~5 мин чтения</span><span class="chip">Уровень: junior</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> Контейнер не является границей безопасности «по умолчанию». Спрашивают конкретные настройки хардeнинга.

## Модель угроз

Общее ядро хоста → уязвимость ядра или неверная конфигурация контейнера (privileged, docker.sock, hostPath) = компрометация хоста. Поэтому: минимум привилегий, минимум поверхности, изоляция.

## Capabilities

```bash
docker run --cap-drop ALL --cap-add NET_BIND_SERVICE myapp        # только нужное
docker run --privileged ...                                        # НЕТ: все capabilities, доступ к устройствам
```

Опасные: `SYS_ADMIN`, `NET_ADMIN`, `SYS_PTRACE`, `SYS_MODULE`, `DAC_READ_SEARCH`. По умолчанию у контейнера ~14 capabilities (CHOWN, NET_BIND_SERVICE, SETUID, KILL, …): большинству приложений хватает пустого набора + `NET_BIND_SERVICE`.

## seccomp, AppArmor, SELinux

- **seccomp**: фильтр системных вызовов; профиль Docker по умолчанию блокирует опасные (`mount`, `reboot`, `kexec_load`, `bpf`…); свой профиль: `--security-opt seccomp=profile.json`; **`seccomp=unconfined` — не использовать**;
- **AppArmor/SELinux**: профили MAC (`--security-opt apparmor=...`, `label=...`); в Kubernetes `seccompProfile: RuntimeDefault`.

## Запуск без root

```dockerfile
USER 10001:10001
```

- в Kubernetes: `runAsNonRoot: true`, `runAsUser`, `allowPrivilegeEscalation: false`;
- **rootless Docker/Podman**: демон и контейнеры работают без root на хосте (user namespaces): компрометация контейнера ≠ root на хосте;
- **userns-remap** в Docker: root в контейнере сопоставлен с непривилегированным UID хоста.

## Read-only и ограничение записи

```bash
docker run --read-only --tmpfs /tmp:rw,noexec,nosuid,size=64m -v data:/app/data myapp
```

```yaml
services:
  api:
    read_only: true
    tmpfs: ["/tmp"]
    cap_drop: [ALL]
    security_opt: ["no-new-privileges:true"]
    user: "10001:10001"
```

`no-new-privileges` запрещает получать дополнительные привилегии (setuid). Монтирование файлов конфигурации `:ro`.

## Ресурсы (защита от DoS)

`--memory`, `--cpus`, `--pids-limit` (защита от fork-бомб), `--ulimit nofile`, `--restart on-failure:3`, ограничение логов.

## Чего избегать

| Опасность | Почему |
|---|---|
| `--privileged` | фактически root на хосте |
| Монтирование `/var/run/docker.sock` | полный контроль над Docker = root на хосте |
| `--pid=host`, `--net=host`, `--ipc=host` | нарушают изоляцию |
| Монтирование `/`, `/etc`, `/proc`, `/sys` с записью | изменение хоста |
| `-v /:/host` | то же |
| Секреты в ENV/ARG/образе | видны в `docker inspect`, `history`, слоях |
| `latest` и неподписанные образы из недоверенных источников | цепочка поставок |
| Открытый Docker API (`tcp://0.0.0.0:2375`) | удалённый root |
| Контейнеры БД с публикацией портов на `0.0.0.0` | доступ из интернета |

Если нужен доступ к Docker API из сервиса (CI-раннер, Traefik): **docker-socket-proxy** с урезанными правами, rootless-раннер, Kaniko/BuildKit без демона.

## Образы и цепочка поставок

- минимальные базовые образы (distroless/chiseled), обновляемые;
- **сканирование**: Trivy/Grype/Scout в CI и в реестре; политика по серьёзности, игнор-лист с обоснованием и сроком;
- **SBOM** (Syft, CycloneDX/SPDX), **подпись и проверка** (cosign, Notary), **provenance** (SLSA);
- фиксация версий и digest, проверяемые источники (доверенные реестры, зеркала);
- секреты: BuildKit `--mount=type=secret`, хранилища секретов (Vault, Docker/K8s secrets), не `ENV`;
- **линтеры**: hadolint (Dockerfile), Dockle (CIS-проверки образа), `docker-bench-security` (CIS Docker Benchmark) для хоста и демона.

## Сеть

- внутренние сети для БД (`internal: true`), минимум публикуемых портов;
- TLS между сервисами там, где нужно (mTLS в service mesh);
- ограничение исходящего трафика (egress) для чувствительных контейнеров;
- фильтрация через `DOCKER-USER`, сетевые политики в Kubernetes.

## Kubernetes: Pod Security

Pod Security Standards: `privileged` / `baseline` / `restricted`; `securityContext` (non-root, read-only rootfs, drop ALL, seccomp RuntimeDefault); admission-политики (Kyverno, OPA Gatekeeper): запрет privileged, `hostPath`, тегов `latest`, требование подписей; NetworkPolicy; RBAC.

## Мониторинг и реагирование

Runtime-защита: **Falco** (подозрительные системные вызовы), Tetragon, аудит Docker-демона (`auditd`), логи доступа к реестру, алерты на запуск shell в продовых контейнерах, регулярные обновления ядра и Docker, управление уязвимостями.

## Чек-лист

- [ ] non-root, `no-new-privileges`, `cap_drop: ALL`;
- [ ] read-only rootfs + tmpfs;
- [ ] нет privileged, docker.sock, host-namespaces;
- [ ] лимиты ресурсов;
- [ ] образы минимальные, просканированы, зафиксированы по версии/digest;
- [ ] секреты вне образа и ENV;
- [ ] БД и внутренние сервисы не опубликованы наружу;
- [ ] Docker API не открыт, хост обновляется.

## Вопросы с ответами

> [!question]- Почему опасно монтировать docker.sock в контейнер?
> Доступ к сокету эквивалентен root на хосте: можно запустить привилегированный контейнер с монтированием корня хоста.

> [!question]- Как уменьшить риск, если контейнер будет скомпрометирован?
> Non-root, `cap_drop: ALL`, read-only файловая система, seccomp и AppArmor, `no-new-privileges`, лимиты ресурсов, изоляция сети и отсутствие секретов в образе.

> [!question]- Что такое rootless-режим?
> Демон и контейнеры запускаются от непривилегированного пользователя хоста через user namespaces: root в контейнере не даёт root на хосте.
