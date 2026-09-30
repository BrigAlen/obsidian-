---
type: topic
domain: devops
stage: 1
order: 8
status: todo
level: junior
tags: [domain/devops, stage/1, level/junior, priority/should, flag/todo]
group: Скрипты и автоматизация
reviewed: 
next_review: 
priority: should
time: 20
---

# Утилиты: grep, sed, awk, find, curl, jq, htop, ss, lsof

↑ [[DO Этап 1 · Фундамент — Linux, Bash, сети|Этап 1 · Фундамент: Linux, Bash, сети]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">≈20 мин по плану</span><span class="chip">Уровень: junior</span><span class="chip">тема не наполнена</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> Скорость работы в терминале — признак практики: поиск в логах, разбор JSON и диагностика сокетов за секунды.

## grep — поиск текста

```bash
grep -rn "ERROR" /var/log/app/        # рекурсивно, с номерами строк
grep -E "timeout|refused" app.log     # расширенные регулярные выражения
grep -v "healthcheck" access.log      # исключить
grep -i -C 3 "exception" app.log      # 3 строки контекста
grep -c "500" access.log; grep -o "id=[0-9]*" log; grep -l "TODO" -r src/
zgrep "error" app.log.*.gz
rg "pattern"                          # ripgrep — быстрее
```

## sed — потоковый редактор

```bash
sed 's/old/new/g' file                 # заменить (вывод на экран)
sed -i.bak 's/DEBUG/INFO/' app.conf    # на месте с резервной копией
sed -n '10,20p' file                   # строки 10–20
sed '/^#/d;/^$/d' file                 # удалить комментарии и пустые строки
sed -E 's/([0-9]+)-([0-9]+)/\2-\1/' file
```

## awk — обработка столбцов

```bash
awk '{print $1, $9}' access.log                         # 1-й и 9-й столбцы
awk -F: '{print $1}' /etc/passwd                        # разделитель
awk '$9 >= 500 {c[$1]++} END {for (ip in c) print c[ip], ip}' access.log | sort -rn | head
awk '{s+=$NF} END {print s/NR}' file                    # среднее по последнему столбцу
awk 'NR==1 || /ERROR/' app.log
```

## find, xargs

```bash
find /var/log -name "*.log" -mtime +7 -size +100M
find . -type f -perm 0777
find /tmp -type f -mtime +3 -delete
find . -name "*.tmp" -print0 | xargs -0 rm -f
find . -name "*.cs" -exec grep -l "TODO" {} +
```

## curl и HTTP

```bash
curl -fsS https://api.example.com/health            # -f ошибка на 4xx/5xx, -s без прогресса, -S показывать ошибки
curl -i -X POST -H "Content-Type: application/json" -d '{"a":1}' https://api/x
curl -w "dns=%{time_namelookup} connect=%{time_connect} ttfb=%{time_starttransfer} total=%{time_total}\n" -o /dev/null -s https://site
curl -v --resolve site.com:443:10.0.0.5 https://site.com/    # обход DNS для теста
curl -k / --cacert ca.pem; curl -L (редиректы); curl -u user:pass; curl -H "Authorization: Bearer $TOKEN"
curl --retry 5 --retry-connrefused --max-time 10 URL
```

## jq — JSON

```bash
curl -s api/users | jq '.items[] | select(.active) | {id, email}'
jq -r '.items[].id' file.json                      # -r без кавычек
jq '.[] | .name' ; jq 'length'; jq -c . ; jq '.a.b // "default"'
jq -s 'map(.size) | add' *.json                    # объединить и посчитать
docker inspect c | jq '.[0].State'
kubectl get pods -o json | jq -r '.items[] | select(.status.phase!="Running") | .metadata.name'
```

## Мониторинг процессов и сокетов

```bash
htop                     # интерактивный обзор (F6 сортировка, F4 фильтр)
ss -tulpn                # слушающие порты и процессы (замена netstat)
ss -tan state established | wc -l
ss -o state time-wait; ss -s
lsof -i :8080            # кто слушает порт
lsof -p PID              # открытые файлы процесса
lsof +L1                 # удалённые, но открытые
lsof -u user
strace -p PID -f -e trace=network       # системные вызовы
```

## Работа с текстом и файлами

```bash
sort | uniq -c | sort -rn | head        # топ частот
cut -d, -f1,3 file.csv; tr -d '\r'; wc -l; head -n 20; tail -f; tail -n +2
column -t; paste; tee; xargs -P4 -n1 cmd
watch -n 2 'ss -s'; timeout 10 cmd; time cmd
less +F app.log                         # follow в less (Ctrl+C — режим поиска)
```

## Пример: топ IP по 5xx за последний час

```bash
awk -v since="$(date -d '1 hour ago' '+%d/%b/%Y:%H')" '$4 ~ since && $9 ~ /^5/ {print $1}' access.log \
  | sort | uniq -c | sort -rn | head
```

## Вопросы с ответами

> [!question]- Как найти процесс, занявший порт 8080?
> `ss -tulpn | grep :8080` или `lsof -i :8080`.

> [!question]- Как посчитать запросы по статусам в access.log?
> `awk '{print $9}' access.log | sort | uniq -c | sort -rn`.

> [!question]- Чем find -exec {} \; отличается от {} +?
> `\;` запускает команду для каждого файла, `+` передаёт много файлов одной командой (быстрее).
