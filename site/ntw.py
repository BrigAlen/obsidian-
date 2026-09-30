#!/usr/bin/env python3
"""Notion -> Obsidian: создаёт раздел (индекс + темы) из сырого текста страниц Notion.

Формат stdin:
@@section domain=backend stage=1 sec=1.3 code=BE level=junior notion=<id> title="C#: основы языка" desc="..."
@@topic n=1 id=<32hex> title="Название" topics="dotnet,csharp" [md=1] [ttitle="H1 если отличается"]
<текст страницы Notion (или готовый markdown при md=1)>
@@topic ...

Скрипт сам находит папку этапа по domain/stage, конвертирует разметку, ставит навигацию.
"""
import glob, os, re, shlex, sys

TAG_LANG = {"c#": "csharp", "plain text": "text", "shell": "bash", "sh": "bash", "javascript": "js", "typescript": "ts"}
ICON = {"⚠️": "warning", "⚠": "warning", "🎯": "info", "💡": "tip", "✅": "success", "❗": "danger", "🧭": "info", "📌": "note"}
EMOJI = re.compile("[\U0001F000-\U0001FAFF\u2600-\u27BF\u2B00-\u2BFF\uFE0F\u200D]")
DOMS = {"backend": "01-Backend", "frontend": "02-Frontend", "db": "03-Базы данных", "devops": "04-DevOps"}


def safe(s):
    s = s.replace(":", " —").replace("/", "-").replace("#", "♯").replace("?", "")
    s = re.sub(r'[<>*"\\|\[\]^]', "", s)
    return re.sub(r"\s+", " ", s).strip()


def convert(raw):
    t = raw.replace("\r", "")
    t = re.sub(r"\[([^\]]+)\]\(https?://\1\)", r"\1", t)          # [ASP.NET](http://ASP.NET)
    # callout
    def callout(m):
        icon = (re.search(r'icon="([^"]*)"', m.group(1)) or [None, ""])[1]
        body = re.sub(r"^\t", "", m.group(2), flags=re.M).strip()
        body = re.sub(r"^\*\*Зачем:\*\*\s*", "", body)
        kind = ICON.get(icon, "note")
        title = ""
        if icon == "🎯" or (m.start() == 0 and kind == "info"):
            title = " Зачем это на собесе"
        elif m.group(2).lstrip("\t\n ").startswith("**Зачем"):
            title = " Зачем это на собесе"
        lines = body.split("\n")
        if title:
            return f"> [!{kind}]{title}\n" + "\n".join("> " + l for l in lines) + "\n"
        return f"> [!{kind}]\n" + "\n".join("> " + l for l in lines) + "\n"
    t = re.sub(r"<callout([^>]*)>\n?(.*?)\n?</callout>", callout, t, flags=re.S)
    # details -> foldable question
    def details(m):
        q = m.group(1).strip()
        a = re.sub(r"^\t", "", m.group(2), flags=re.M).strip()
        return f"> [!question]- {q}\n" + "\n".join("> " + l if l.strip() else ">" for l in a.split("\n")) + "\n"
    t = re.sub(r"<details>\s*<summary>(.*?)</summary>\n?(.*?)\n?</details>", details, t, flags=re.S)
    # mentions
    t = re.sub(r'<mention-page url="[^"]*?([0-9a-f]{32})[^"]*"\s*(?:/>|>.*?</mention-page>)', r"[[N:\1]]", t, flags=re.S)
    t = re.sub(r"<m ([0-9a-f]{32})>", r"[[N:\1]]", t)               # короткая форма ссылки
    # code fence languages
    def fence(m):
        lang = TAG_LANG.get(m.group(1).strip().lower(), m.group(1).strip().lower())
        return "```" + lang
    t = re.sub(r"^```([^\n`]*)$", lambda m: fence(m) if m.group(1).strip() else m.group(0), t, flags=re.M)
    t = t.replace("## Вопросы на собесе", "## Вопросы с ответами")
    t = t.replace("## Примеры кода", "## Примеры")
    t = EMOJI.sub("", t)
    # пустые строки: вокруг заголовков и блоков
    t = re.sub(r"\n(#{2,4} )", r"\n\n\1", t)
    t = re.sub(r"(#{2,4} [^\n]*)\n(?!\n)", r"\1\n\n", t)
    t = re.sub(r"\n{3,}", "\n\n", t)
    return t.strip() + "\n"


def fix_nav(sec_dir, sec_name, sec_title):
    files = []
    for f in os.listdir(sec_dir):
        if not f.endswith(".md"):
            continue
        txt = open(os.path.join(sec_dir, f), encoding="utf-8").read()
        m = re.search(r"^order:\s*(\d+)", txt, re.M)
        files.append((int(m.group(1)) if m else 0, f[:-3], txt))
    files.sort()
    for i, (o, name, txt) in enumerate(files):
        nav = [f"↑ [[{sec_name}|{sec_title}]]"]
        if i > 0:
            nav.append(f"← [[{files[i-1][1]}|Предыдущая]]")
        if i < len(files) - 1:
            nav.append(f"→ [[{files[i+1][1]}|Следующая]]")
        new = re.sub(r"^↑ .*$", " · ".join(nav), txt, count=1, flags=re.M)
        if new != txt:
            open(os.path.join(sec_dir, name + ".md"), "w", encoding="utf-8").write(new)


def parse_args(line):
    parts = shlex.split(line)
    return dict(p.split("=", 1) for p in parts[1:] if "=" in p)


def main():
    data = sys.stdin.read()
    blocks = re.split(r"^@@", data, flags=re.M)[1:]
    sec = None
    topics = []
    for b in blocks:
        head, _, body = b.partition("\n")
        kind = head.split()[0]
        a = parse_args(head)
        if kind == "section":
            sec = a
        elif kind == "topic":
            a["body"] = body
            topics.append(a)
    d, stage, secno, code = sec["domain"], int(sec["stage"]), sec["sec"], sec.get("code", "BE")
    level = sec.get("level", "middle")
    droot = DOMS[d]
    stage_dir = next(p for p in glob.glob(f"{droot}/Этап {stage} —*") if os.path.isdir(p))
    sec_name = f"{code} {secno} {safe(sec['title'])}"
    sec_dir = os.path.join(stage_dir, sec_name)
    os.makedirs(sec_dir, exist_ok=True)
    stage_note = next((os.path.basename(p)[:-3] for p in glob.glob(f"{stage_dir}/{code} Этап {stage} *.md")), None)
    names = []
    for t in topics:
        names.append(f"{code} {secno}.{t['n']} {safe(t['title'])}")
    for i, t in enumerate(topics):
        n = int(t["n"])
        title = t.get("ttitle") or t["title"]
        tags = [f"domain/{d}", f"stage/{stage}", f"level/{level}"] + [f"topic/{x}" for x in t.get("topics", "").split(",") if x]
        body = t["body"] if t.get("md") else convert(t["body"])
        fm = ["---", "type: topic", f"domain: {d}", f"stage: {stage}", f'section: "{secno}"', f"order: {n}", "status: todo",
              f"level: {level}", f"notion_id: {t['id']}", "tags: [" + ", ".join(tags) + "]", "reviewed:", "next_review:", "---", ""]
        h1 = re.sub(r"[<>]", lambda m: "\\" + m.group(0), title)
        text = "\n".join(fm) + f"\n# {h1}\n\n↑ NAV\n\n" + body
        open(os.path.join(sec_dir, names[i] + ".md"), "w", encoding="utf-8").write(text)
    fix_nav(sec_dir, sec_name, f"{secno} {sec['title'].replace('#', '♯')}")
    # индекс раздела
    idx = ["---", "type: section", f"domain: {d}", f"stage: {stage}", f'section: "{secno}"', f"order: {sec.get('order', secno.split('.')[-1])}",
           "status: todo", f"level: {level}", f"notion_id: {sec['notion']}", f"tags: [domain/{d}, stage/{stage}, kind/section]", "---", "",
           f"# {secno} {sec['title'].replace('#', '♯')}", ""]
    if stage_note:
        idx.append(f"↑ [[{stage_note}|Этап {stage}]]\n")
    if sec.get("desc"):
        idx.append(sec["desc"] + "\n")
    idx += ["## Темы", "<!-- toc:start -->", "<!-- toc:end -->", "", "## Чек-лист раздела", "- [ ] Прочитал все темы", "- [ ] Могу объяснить каждую тему за 2 минуты вслух", ""]
    open(os.path.join(stage_dir, sec_name + ".md"), "w", encoding="utf-8").write("\n".join(idx))
    print(f"section {sec_name}: {len(topics)} topics")


main()
