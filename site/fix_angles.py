#!/usr/bin/env python3
"""Экранирует '<' перед буквой вне блоков кода и inline-кода (иначе markdown принимает generics за HTML-теги)."""
import glob, re, sys

ALLOWED = ("div", "span", "br", "a ", "a>", "svg", "details", "summary", "kbd", "sub", "sup", "/", "!--", "m ")

def fix(text):
    out, in_code = [], False
    for line in text.split("\n"):
        if line.lstrip().startswith("```"):
            in_code = not in_code
            out.append(line)
            continue
        if in_code or line.startswith("<") and line.rstrip().endswith(">") and re.match(r"<(div|/div|span|!--)", line):
            out.append(line)
            continue
        parts = re.split(r"(`[^`]*`)", line)
        for i, p in enumerate(parts):
            if i % 2 == 0:
                p = re.sub(r"(?<!\\)<(?=[A-Za-z])(?!(?:%s))" % "|".join(re.escape(a) for a in ALLOWED),
                           r"\\<", p)
                p = re.sub(r"(?<!\\)(?<=[\w\]\)])>(?=[\s,.)\]]|$)", r"\\>", p) if "\\<" in p else p
                parts[i] = p
        out.append("".join(parts))
    return "\n".join(out)

n = 0
for path in glob.glob("0[1-5]-*/**/*.md", recursive=True):
    t = open(path, encoding="utf-8").read()
    if "notion_id:" not in t or "type: topic" not in t:
        continue
    fm_end = t.index("\n---", 4) + 4
    new = t[:fm_end] + fix(t[fm_end:])
    if new != t:
        open(path, "w", encoding="utf-8").write(new); n += 1
print("fixed files:", n)
