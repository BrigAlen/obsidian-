#!/usr/bin/env python3
"""CI: делает адресa страниц короткими и читаемыми (латиница), сохраняя заголовки и ссылки.
Файлы и папки переименовываются, в frontmatter добавляется title со старым именем,
wikilink'и переписываются на новые имена."""
import os, re, sys

root = sys.argv[1]
TR = dict(zip("абвгдеёжзийклмнопрстуфхцчшщъыьэюя",
              ["a","b","v","g","d","e","e","zh","z","i","y","k","l","m","n","o","p","r","s","t","u","f","h","c","ch","sh","sch","","y","","e","yu","ya"]))
DOM = {"01-Backend": "01-backend", "02-Frontend": "02-frontend", "03-Базы данных": "03-databases",
       "04-DevOps": "04-devops", "05-Fullstack-практика": "05-fullstack", "06-Аналитика-и-PM": "06-analytics", "07-Мои-заметки": "07-notes"}
MAXLEN = 44


def slug(s):
    s = s.lower().replace("♯", "sharp").replace("c#", "csharp").replace(".net", "dotnet")
    s = "".join(TR.get(ch, ch) for ch in s)
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    if len(s) > MAXLEN:
        s = s[:MAXLEN].rsplit("-", 1)[0]
        while "-" in s and len(s.rsplit("-", 1)[1]) <= 2 and not s.rsplit("-", 1)[1].isdigit():
            s = s.rsplit("-", 1)[0]
    return s or "page"


def ascii_only(s):
    return re.fullmatch(r"[A-Za-z0-9._ -]+", s) is not None


def read(p):
    return open(p, encoding="utf-8").read()


def fm_get(txt, key):
    m = re.match(r"^---\n(.*?)\n---\n", txt, re.S)
    if not m:
        return None
    k = re.search(rf"^{key}:\s*(.+)$", m.group(1), re.M)
    return k.group(1).strip() if k else None


# 1. файлы
files = []
for d, _, fs in os.walk(root):
    for f in fs:
        if f.endswith(".md") and not (d == root and f == "index.md") and f != "index.md":
            files.append(os.path.join(d, f))

used, mapping = set(), {}
for p in sorted(files):
    stem = os.path.basename(p)[:-3]
    txt = read(p)
    typ, dom, stage = fm_get(txt, "type"), fm_get(txt, "domain"), fm_get(txt, "stage")
    if ascii_only(stem) and " " not in stem:
        new = stem
    elif typ == "domain" and dom:
        new = f"{dom}-overview"
    elif typ == "stage" and dom and stage:
        new = f"{dom}-stage-{stage}-overview"
    else:
        new = slug(stem)
    base, i = new, 2
    while new in used:
        new, i = f"{base}-{i}", i + 1
    used.add(new)
    mapping[stem] = new
    if not re.match(r"^---\n.*?\n---\n", txt, re.S):
        txt = "---\n---\n" + txt
    if fm_get(txt, "title") is None:
        title = re.sub(r"^(BE|FE|DB|DO|FS) ", "", stem).replace('"', "'")
        txt = txt.replace("---\n", f'---\ntitle: "{title}"\n', 1)
    open(p, "w", encoding="utf-8").write(txt)

# 2. wikilink'и (в таблицах пайп экранирован: \\|)
LINK = re.compile(r"\[\[([^\]|#\\]+)(#[^\]|\\]*)?(\\?\|[^\]]*)?\]\]")
known = set(mapping) | set(mapping.values()) | {"index"}


def repl(m):
    t = m.group(1).strip()
    pipe = "\\|" if (m.group(3) or "").startswith("\\") else "|"
    alias = (m.group(3) or "").lstrip("\\").lstrip("|")
    if t not in known:                      # страница не публикуется (например, Дашборд) — просто текст
        return alias or t
    if t in mapping:
        if not alias:
            alias = re.sub(r"^(BE|FE|DB|DO|FS) ", "", t).replace("#", "♯")
        return f"[[{mapping[t]}{m.group(2) or ''}{pipe}{alias}]]"
    return m.group(0)


for p in files + [os.path.join(root, "index.md")]:
    if not os.path.exists(p):
        continue
    txt = read(p)
    new = LINK.sub(repl, txt)
    if new != txt:
        open(p, "w", encoding="utf-8").write(new)

# 3. переименование файлов
for p in files:
    stem = os.path.basename(p)[:-3]
    if mapping[stem] != stem:
        os.rename(p, os.path.join(os.path.dirname(p), mapping[stem] + ".md"))

# 4. папки (снизу вверх)
for d, dirs, _ in sorted(os.walk(root), key=lambda x: -len(x[0])):
    name = os.path.basename(d)
    if d == root or (ascii_only(name) and " " not in name and name not in DOM):
        continue
    if name in DOM:
        new = DOM[name]
    else:
        m = re.match(r"^Этап (\d+)", name)
        new = f"stage-{m.group(1)}" if m else slug(name)
    if new != name:
        os.rename(d, os.path.join(os.path.dirname(d), new))
print("slugified", len(files), "pages")
