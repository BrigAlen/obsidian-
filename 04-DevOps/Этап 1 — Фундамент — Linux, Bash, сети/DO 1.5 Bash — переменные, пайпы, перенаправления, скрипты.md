---
type: topic
domain: devops
stage: 1
order: 5
status: todo
level: junior
tags: [domain/devops, stage/1, level/junior, priority/should]
group: Скрипты и автоматизация
reviewed: 
next_review: 
priority: should
time: 7
---

# Bash: переменные, пайпы, перенаправления, скрипты

↑ [[DO Этап 1 · Фундамент — Linux, Bash, сети|Этап 1 · Фундамент: Linux, Bash, сети]]

<!-- meta:start -->
<div class="meta-strip"><span class="badge should">Желательно</span><span class="chip">~7 мин чтения</span><span class="chip">Уровень: junior</span></div>
<!-- meta:end -->

> [!info] Зачем это на собесе
> Скрипты автоматизации пишутся на Bash каждый день; ожидают корректную обработку ошибок, кавычки и понимание кодов возврата.

## Основы

```bash
#!/usr/bin/env bash
set -euo pipefail          # -e выйти при ошибке, -u ошибка на неопределённую переменную, pipefail — код пайпа по первой ошибке
IFS=$'\n\t'

name="World"               # без пробелов вокруг =
echo "Hello, ${name}"      # всегда кавычки вокруг переменных
readonly LOG=/var/log/app.log
```

Кавычки: `"..."` — подстановка переменных и команд; `'...'` — буквально. **Без кавычек** значения с пробелами разбиваются на слова и раскрываются шаблоны: источник ошибок (`rm -rf $dir/` при пустом `$dir`!).

## Переменные и подстановки

```bash
${var:-default}       # значение по умолчанию
${var:?нет значения}  # ошибка, если не задана
${var#prefix} ${var%suffix} ${var//old/new} ${#var} ${var:0:5}
$(command)            # подстановка вывода
$((a + b))            # арифметика
arr=(a b c); echo "${arr[@]}" "${#arr[@]}"
declare -A map; map[key]=value     # ассоциативные массивы (Bash 4+)
```

Специальные: `$0` имя скрипта, `$1..$9` аргументы, `$@` все аргументы (слова), `$#` количество, `$?` код возврата последней команды, `$$` PID, `$!` PID последнего фонового процесса.

## Условия и циклы

```bash
if [[ -f "$file" && -r "$file" ]]; then echo ok
elif [[ "$x" == "abc"* ]]; then echo prefix
else echo no; fi

[[ -z "$s" ]]  [[ -n "$s" ]]  [[ "$a" -eq 5 ]]  [[ -d dir ]]  [[ -x file ]]   # [[ ]] предпочтительнее [ ]

for f in *.log; do gzip "$f"; done
for i in {1..5}; do echo "$i"; done
while IFS= read -r line; do echo "$line"; done < file.txt
case "$1" in start) ... ;; stop|restart) ... ;; *) usage ;; esac
```

## Перенаправления и пайпы

```bash
cmd > out.txt          # stdout в файл (перезапись)
cmd >> out.txt         # добавление
cmd 2> err.txt         # stderr
cmd > all.txt 2>&1     # stderr туда же (порядок важен); сокращённо: cmd &> all.txt
cmd < input.txt
cmd1 | cmd2            # пайп: stdout первой в stdin второй
cmd | tee out.txt      # и на экран, и в файл
cmd > /dev/null 2>&1
cat <<'EOF' > file     # here-doc (кавычки вокруг EOF — без подстановок)
text
EOF
diff <(sort a) <(sort b)   # process substitution
```

Дескрипторы: 0 — stdin, 1 — stdout, 2 — stderr.

## Функции и обработка ошибок

```bash
log() { printf '%s %s\n' "$(date -Is)" "$*" >&2; }
die() { log "ERROR: $*"; exit 1; }

cleanup() { rm -rf "$tmp"; }
tmp=$(mktemp -d)
trap cleanup EXIT                      # выполнится при любом выходе
trap 'die "ошибка на строке $LINENO"' ERR

command -v docker >/dev/null || die "docker не установлен"
```

**Коды возврата**: 0 — успех, не 0 — ошибка; `exit 1`, `||`, `&&`. `set -e` не срабатывает в условиях `if`, левой части `&&`/`||`.

## Аргументы

```bash
usage() { echo "usage: $0 [-e env] [-v] target" >&2; exit 2; }
env=dev; verbose=0
while getopts "e:vh" opt; do
  case $opt in e) env=$OPTARG;; v) verbose=1;; *) usage;; esac
done
shift $((OPTIND - 1))
[[ $# -ge 1 ]] || usage
```

## Практика

- проверяйте скрипты **ShellCheck** (`shellcheck script.sh`) и форматируйте `shfmt`;
- **идемпотентность**: повторный запуск безопасен (`mkdir -p`, `ln -sfn`, проверка перед действием);
- блокировка от параллельного запуска: `flock -n /var/lock/job.lock cmd`;
- не парсите `ls`; используйте `find -print0 | xargs -0`, `while read`;
- временные файлы — `mktemp`, чистка через `trap`;
- секреты не передавайте аргументами (видны в `ps`) и не логируйте; `set +x` вокруг чувствительных команд;
- длинные скрипты со сложной логикой — перенести на Python;
- переносимость: `#!/usr/bin/env bash`, `sh` (dash) не поддерживает `[[ ]]` и массивы.

## Пример: бэкап с ротацией

```bash
#!/usr/bin/env bash
set -euo pipefail
DB=${1:?usage: $0 dbname}
DIR=/var/backups/pg; KEEP=7
mkdir -p "$DIR"
out="$DIR/${DB}_$(date +%F_%H%M).dump"
pg_dump -Fc "$DB" > "$out"
find "$DIR" -name "${DB}_*.dump" -mtime +"$KEEP" -delete
echo "saved $out ($(du -h "$out" | cut -f1))"
```

## Вопросы с ответами

> [!question]- Что делает set -euo pipefail?
> `-e` — завершиться при ошибке команды, `-u` — ошибка при использовании неопределённой переменной, `pipefail` — код пайпа равен коду первой упавшей команды, а не последней.

> [!question]- Чем $@ отличается от $*?
> В кавычках `"$@"` раскрывается в отдельные слова (сохраняя границы аргументов), `"$*"` — в одну строку.

> [!question]- Почему важно брать переменные в кавычки?
> Без них значение разбивается по пробелам и подвергается раскрытию шаблонов, что ломает команды и опасно (например, `rm -rf $dir/*` при пустой переменной).
