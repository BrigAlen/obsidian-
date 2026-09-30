---
type: topic
domain: devops
stage: 1
order: 6
status: todo
level: junior
tags: [domain/devops, stage/1, level/junior, priority/should]
group: Скрипты и автоматизация
reviewed: 
next_review: 
priority: should
time: 5
---

# Диски и файловые системы: разделы, LVM, монтирование, fstab, df и du, inode

↑ [[DO Этап 1 · Фундамент — Linux, Bash, сети|Этап 1 · Фундамент: Linux, Bash, сети]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~5 мин чтения</span><span class="chip">Уровень: junior</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> «Диск заполнен» — один из самых частых инцидентов. Нужно знать инструменты диагностики, LVM и то, чем место отличается от inode.

## Блочные устройства и разделы

```bash
lsblk -f                      # дерево устройств, ФС, UUID, точки монтирования
blkid                         # UUID и типы
fdisk -l; parted -l           # таблицы разделов
```

Таблицы разделов: **MBR** (до 2 ТБ, 4 основных) и **GPT** (современная). Диски: `/dev/sda`, `/dev/nvme0n1`; разделы: `/dev/sda1`, `/dev/nvme0n1p1`.

```bash
sudo parted /dev/sdb -- mklabel gpt mkpart primary ext4 1MiB 100%
sudo mkfs.ext4 -L data /dev/sdb1         # или mkfs.xfs
sudo mkdir /data && sudo mount /dev/sdb1 /data
```

## Файловые системы

| ФС | Особенности |
|---|---|
| **ext4** | универсальная, надёжная; можно расширять и (офлайн) сжимать |
| **XFS** | производительность на больших файлах, по умолчанию в RHEL; расширять можно, **сжимать нельзя** |
| **Btrfs / ZFS** | снимки, сжатие, контроль целостности, RAID |
| **tmpfs** | в памяти (`/run`, `/dev/shm`) |
| **NFS / CIFS** | сетевые |

## Монтирование и fstab

```bash
mount; findmnt; umount /data
mount -o remount,rw /
```

`/etc/fstab`: постоянные монтирования (**используйте UUID**, не имена устройств):

```text
UUID=3f1c...  /data  ext4  defaults,noatime,nofail  0  2
# поля: устройство  точка  ФС  опции  dump  fsck-порядок
```

`nofail` — не падать при загрузке, если диска нет. Проверка: `sudo mount -a` (ошибка в fstab может не дать системе загрузиться).

## LVM (Logical Volume Manager)

Слой абстракции над дисками: **PV** (физический том) → **VG** (группа) → **LV** (логический том).

```bash
sudo pvcreate /dev/sdb /dev/sdc
sudo vgcreate vg_data /dev/sdb /dev/sdc
sudo lvcreate -L 100G -n lv_app vg_data
sudo mkfs.ext4 /dev/vg_data/lv_app
pvs; vgs; lvs

# расширение «на лету»
sudo lvextend -L +50G -r /dev/vg_data/lv_app       # -r расширяет и ФС
# или
sudo lvextend -l +100%FREE /dev/vg_data/lv_app && sudo resize2fs /dev/vg_data/lv_app   # ext4
sudo xfs_growfs /data                                                                  # XFS

sudo lvcreate -s -L 10G -n snap /dev/vg_data/lv_app   # снимок
```

Преимущества: гибкое изменение размеров, снимки, объединение дисков. Диск в облаке увеличили → `growpart /dev/sda 1`, `pvresize`, `lvextend`, `resize2fs`.

## df, du, inode

```bash
df -h                   # использование по ФС
df -i                   # использование inode
du -sh /var/* | sort -h # крупные каталоги
du -xh --max-depth=1 / | sort -h | tail
ncdu /var               # интерактивно
lsof +L1                # удалённые, но открытые файлы
```

**Inode** — запись о файле (метаданные); их число фиксируется при создании ФС. Миллионы мелких файлов исчерпывают inode при свободном месте: «No space left on device» при `df -h` с запасом — проверьте `df -i`.

## Типовые причины «диск заполнен»

1. **Логи** (`/var/log`, логи контейнеров `/var/lib/docker/containers/*/*-json.log`) — ротация, лимиты;
2. **Docker**: образы, тома, кэш сборки: `docker system df`, `docker system prune -a --volumes` (осторожно);
3. **Удалённый, но открытый файл**: процесс держит дескриптор, место не освобождается (`lsof +L1`, перезапуск процесса или `> /proc/<pid>/fd/<n>` для обнуления);
4. **Исчерпаны inode**;
5. **Резерв root** (5% на ext4): `tune2fs -m 1`;
6. Временные файлы, дампы памяти (`core`), кэши пакетов, старые ядра;
7. **Бэкапы** на том же диске.

Порядок: `df -h` → `df -i` → `du` по каталогам → `lsof +L1` → причина и очистка; затем **настроить мониторинг и алерт** (80%/90%).

## Прочее

- RAID: `mdadm` (0, 1, 5, 6, 10); RAID — не бэкап;
- `smartctl -a /dev/sda` — здоровье диска;
- `fstrim -av` — TRIM для SSD;
- шифрование: LUKS (`cryptsetup`);
- swap-файл: `fallocate`, `mkswap`, `swapon`;
- квоты, `noatime`, отдельные разделы для `/var`, `/home`.

## Вопросы с ответами

> [!question]- df показывает 100%, но du не находит столько файлов. Почему?
> Удалённые файлы, которые держит открытыми процесс (`lsof +L1`); либо файлы под точкой монтирования, либо разница в учёте метаданных. Решение — перезапуск процесса или очистка дескриптора.

> [!question]- «No space left on device», а df -h показывает свободное место. Причина?
> Закончились inode (проверить `df -i`) или достигнут лимит квоты/резерв.

> [!question]- Зачем LVM?
> Гибкое управление томами: расширение и перенос без остановки, объединение дисков, снимки.
