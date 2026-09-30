#!/usr/bin/env python3
"""Для каждой папки (домен, этап, раздел) создаёт index.md как копию её оглавления,
чтобы клик по папке в дереве открывал страницу с этапами/темами. Запускается в CI на копии vault."""
import os, re, sys

root = sys.argv[1]
SKIP = {"Inbox"}


def with_hide(txt):
    m = re.match(r"^---\n(.*?)\n---\n", txt, re.S)
    if not m:
        return txt
    fm = m.group(1)
    if re.search(r"^tags:\s*\[", fm, re.M):
        fm = re.sub(r"^(tags:\s*\[)", r"\1hide, ", fm, count=1, flags=re.M)
    else:
        fm += "\ntags: [hide]"
    return f"---\n{fm}\n---\n" + txt[m.end():]


made = 0
for d, dirs, files in os.walk(root):
    if "index.md" in files or os.path.basename(d) in SKIP or d == root:
        continue
    parent, name = os.path.split(d)
    src = None
    sibling = os.path.join(parent, name + ".md")
    if os.path.exists(sibling):                       # раздел: «BE 3.1 X.md» рядом с папкой «BE 3.1 X»
        src = sibling
    else:                                             # домен/этап: единственный оглавляющий файл внутри
        for f in files:
            t = open(os.path.join(d, f), encoding="utf-8").read(400)
            if re.search(r"^type:\s*(domain|stage)", t, re.M):
                src = os.path.join(d, f)
                break
    if src:
        txt = open(src, encoding="utf-8").read()
        open(os.path.join(d, "index.md"), "w", encoding="utf-8").write(with_hide(txt))
        made += 1
print("index pages:", made)
