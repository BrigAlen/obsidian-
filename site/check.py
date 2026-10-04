#!/usr/bin/env python3
"""Проверка vault перед коммитом: python3 site/check.py [--skeleton]

Проверяет: битые wiki-ссылки, ровные таблицы (| внутри кода), YAML/JSON-блоки, незакрытые блоки кода,
frontmatter тем. Ключ --skeleton печатает, сколько тем ещё помечено skeleton: true.
Схемы Mermaid проверяются отдельно (нужен npm): см. README, раздел «Как устроена сборка сайта».
"""
import json, os, re, sys
import yaml

SKIP = ("/.git", "/api", "/site", "/_templates", "/.obsidian", "/.github", "/node_modules")
names, files = {}, []
for d, _, fs in os.walk("."):
    if any(x in d for x in SKIP):
        continue
    for f in fs:
        if f.endswith(".md"):
            names[f[:-3]] = os.path.join(d, f)
            files.append(os.path.join(d, f))
problems = []


def add(kind, path, detail):
    problems.append((kind, os.path.basename(path)[:60], detail))


skeleton = 0
for p in files:
    t = open(p, encoding="utf-8").read()
    fm = re.match(r"^---\n(.*?)\n---\n", t, re.S)
    is_topic = bool(fm and "type: topic" in fm.group(1))
    if is_topic:
        for key in ("order:", "level:", "priority:", "tags:"):
            if key not in fm.group(1):
                add("frontmatter", p, f"нет {key}")
        if re.search(r"^skeleton:\s*true", fm.group(1), re.M):
            skeleton += 1
    if t.count("```") % 2:
        add("fence", p, "нечётное число ``` (незакрытый блок кода)")
    body = re.sub(r"```.*?```", "", t, flags=re.S)
    plain = re.sub(r"`[^`\n]*`", "", body)
    # wiki-ссылки (плейсхолдеры N: разрешает CI)
    for m in re.finditer(r"\[\[([^\]|#]+)(?:#[^\]|]*)?(?:\|[^\]]*)?\]\]", plain):
        tgt = m.group(1).strip().replace("\\", "")
        if tgt not in names and not tgt.startswith("N:"):
            add("link", p, f"нет заметки «{tgt}»")
    # таблицы: одинаковое число столбцов, | в коде экранирован \|
    lines = body.split("\n")
    i = 0
    while i < len(lines):
        if lines[i].startswith("|") and i + 1 < len(lines) and re.match(r"^\|[\s:|-]+\|$", lines[i + 1].strip()):
            def cols(l):
                l = re.sub(r"\\\|", "", l)
                l = re.sub(r"\[\[[^\]]*\]\]", lambda m: m.group(0).replace("|", ""), l)
                return l.strip().strip("|").count("|") + 1
            n, j = cols(lines[i]), i + 1
            while j < len(lines) and lines[j].startswith("|"):
                if cols(lines[j]) != n:
                    add("table", p, lines[j][:70]); break
                j += 1
            i = j
        else:
            i += 1
    for m in re.finditer(r"```(json|yaml|yml)\n(.*?)```", t, re.S):
        lang, code = m.group(1), m.group(2)
        if re.search(r"\{\{|\{%|\.\.\.|<[A-Za-z_-]+>", code):
            continue  # шаблоны и сокращённые примеры не проверяем
        try:
            if lang == "json":
                c = re.sub(r"^\s*//.*$", "", code, flags=re.M)
                if re.match(r"^\s*(GET|PUT|POST|DELETE)\s", c):
                    c = c.split("\n", 1)[1]
                json.loads(c)
            else:
                list(yaml.safe_load_all(code))
        except Exception as e:
            add(lang, p, str(e).split("\n")[0][:70])

for k, f, d in problems[:60]:
    print(f"{k:12} {f} | {d}")
print(f"заметок: {len(files)}, проблем: {len(problems)}" + (f", skeleton: {skeleton}" if "--skeleton" in sys.argv else ""))
sys.exit(1 if problems else 0)
