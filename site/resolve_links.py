#!/usr/bin/env python3
"""Превращает плейсхолдеры [[N:<notion_id>]] в wiki-ссылки по frontmatter `notion_id`.

Использование: resolve_links.py <dir>
Ссылки, для которых заметки ещё нет, заменяются обычным текстом.
"""
import os, re, sys

root = sys.argv[1]
ids = {}   # notion_id -> (имя файла без .md, заголовок)
files = []
for d, _, fs in os.walk(root):
    for f in fs:
        if f.endswith(".md"):
            files.append(os.path.join(d, f))

for p in files:
    text = open(p, encoding="utf-8").read()
    m = re.search(r"^notion_id:\s*([0-9a-f]{32})", text, re.M)
    if not m:
        continue
    h = re.search(r"^#\s+(.+)$", text, re.M)
    name = os.path.basename(p)[:-3]
    ids[m.group(1)] = (name, h.group(1).strip() if h else name)

pat = re.compile(r"\[\[N:([0-9a-f]{32})\]\]")
resolved = missing = 0
for p in files:
    text = open(p, encoding="utf-8").read()
    if "[[N:" not in text:
        continue

    def sub(m):
        global resolved, missing
        t = ids.get(m.group(1))
        if t:
            resolved += 1
            return f"[[{t[0]}|{t[1]}]]"
        missing += 1
        return "_(тема ещё не перенесена)_"

    new = pat.sub(sub, text)
    open(p, "w", encoding="utf-8").write(new)

print(f"links resolved: {resolved}, pending: {missing}")
