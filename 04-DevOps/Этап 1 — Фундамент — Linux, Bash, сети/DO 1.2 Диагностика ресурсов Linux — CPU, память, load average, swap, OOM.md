---
type: topic
domain: devops
stage: 1
order: 2
status: todo
level: junior
tags: [domain/devops, stage/1, level/junior, priority/should]
group: Linux
reviewed: 
next_review: 
priority: should
time: 4
---

# Диагностика ресурсов Linux: CPU, память, load average, swap, OOM

↑ [[DO Этап 1 · Фундамент — Linux, Bash, сети|Этап 1 · Фундамент: Linux, Bash, сети]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~4 мин чтения</span><span class="chip">Уровень: junior</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> Классический вопрос: «сервер тормозит, что смотрите?». Нужен систематичный подход: CPU, память, диск, сеть.

## Load average

`uptime` показывает три числа: средняя длина очереди за 1, 5 и 15 минут: процессы в состоянии **running + runnable + uninterruptible (D)**.

- сравнивать с числом ядер (`nproc`): load 4 на 4 ядрах — полная загрузка, на 16 — 25%;
- высокий load при низком CPU — процессы ждут **I/O** (состояние D): диск, NFS;
- растёт 1-минутное относительно 15-минутного — нагрузка нарастает.

## CPU

```bash
top / htop                  # %us user, %sy kernel, %wa iowait, %st steal, %id idle
mpstat -P ALL 1             # по ядрам
pidstat 1                   # по процессам
ps aux --sort=-%cpu | head
perf top                    # профилирование (глубже)
```

Интерпретация: высокий `%us` — код приложения; `%sy` — системные вызовы/сеть/прерывания; `%wa` — ожидание диска; `%st` — «украдено» гипервизором (шумный сосед); одно ядро на 100% при многопоточной программе — однопоточное узкое место.

## Память

```bash
free -h                     # used, free, buff/cache, available
vmstat 1                    # si/so — swap in/out, r, b
cat /proc/meminfo
ps aux --sort=-%mem | head
smem -tk                    # реальное потребление (PSS)
```

- **`available`**, а не `free`, показывает реально доступную память (кэш можно вытеснить);
- Linux занимает свободную память под **page cache**: «мало free» — норма;
- **Swap**: постоянная активность `si/so` — нехватка памяти, резкая деградация. `swappiness` (по умолчанию 60; для БД 1–10).
- **OOM killer**: при исчерпании ядро убивает процесс с наибольшим `oom_score`; следы: `dmesg -T | grep -i 'killed process'`, `journalctl -k`. В контейнерах — OOM по лимиту cgroup (код выхода 137).
- Утечки: рост RSS во времени (`pmap`, профилировщики).

## Диск и I/O

```bash
iostat -xz 1                # %util, await, r/s w/s, aqu-sz
iotop -oP                   # кто нагружает диск
df -h; df -i                # место и inode
dmesg | grep -i error       # ошибки диска
```

`await` — задержка запросов; `%util` ~100% — диск насыщен.

## Сеть

```bash
ss -s; ss -tulpn            # сокеты и слушающие порты
sar -n DEV 1                # трафик интерфейсов
nload, iftop
```

## Систематичный подход (USE-метод Бренда Грегга)

Для каждого ресурса (CPU, память, диск, сеть) проверить **Utilization** (загрузка), **Saturation** (очереди) и **Errors** (ошибки).

Порядок на практике:

1. `uptime`, `dmesg | tail` — общая картина и ошибки ядра;
2. `vmstat 1` — CPU, память, swap, очередь;
3. `mpstat -P ALL 1`, `pidstat 1` — кто потребляет CPU;
4. `iostat -xz 1` — диск;
5. `free -h`, `sar -n DEV` — память и сеть;
6. `top`/`htop` — итог по процессам;
7. логи приложения и сервисов, недавние деплои/изменения.

## OOM и лимиты

- `ulimit -a`, `/etc/security/limits.conf`, `LimitNOFILE` в unit-файле systemd (ошибка «too many open files»);
- `sysctl vm.overcommit_memory`, `vm.max_map_count` (Elasticsearch);
- cgroups: `systemd-cgtop`, `systemctl show -p MemoryMax unit`.

## Вопросы с ответами

> [!question]- Load average 8 на 4 ядрах — это плохо?
> Вероятно, да: в среднем 8 задач на 4 ядра — очередь вдвое больше числа ядер. Надо смотреть, CPU это или ожидание I/O (`%wa`, состояние D).

> [!question]- Почему free показывает мало памяти, а сервер работает нормально?
> Ядро использует свободную память под кэш файлов. Смотреть нужно `available`: это память, которую можно освободить без swap.

> [!question]- Как выяснить, что процесс убил OOM killer?
> `dmesg -T | grep -i -E 'oom|killed process'` или `journalctl -k`; для контейнеров — `docker inspect` (`OOMKilled: true`, код 137).
