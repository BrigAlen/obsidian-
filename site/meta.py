#!/usr/bin/env python3
"""Метаданные тем: приоритет, время чтения; таблицы в оглавлениях; страница «Прогресс».

Использование: meta.py [корень vault]   (по умолчанию — текущая папка)
Идемпотентно: можно запускать сколько угодно раз, в том числе в CI.
"""
import glob, math, os, re, sys

ROOT = sys.argv[1] if len(sys.argv) > 1 else "."
os.chdir(ROOT)

DOMAINS = {"backend": "Backend", "frontend": "Frontend", "db": "Базы данных", "devops": "DevOps", "fullstack": "Fullstack-практика"}
DOMAIN_ORDER = ["backend", "db", "frontend", "devops", "fullstack"]
PRIO_LABEL = {"must": "Обязательно", "should": "Желательно", "nice": "По желанию"}
PRIO_RANK = {"must": 0, "should": 1, "nice": 2}
STATUS_LABEL = {"todo": "Не начато", "wip": "В работе", "done": "Готово"}

# приоритет по умолчанию: (домен, этап) -> значение; переопределения по разделам ниже
STAGE_PRIO = {
    "backend": {1: "should", 2: "must", 3: "must", 4: "must", 5: "must", 6: "nice", 7: "should", 8: "should", 9: "must"},
    "frontend": {1: "should", 2: "must", 3: "must", 4: "must", 5: "must", 6: "should", 7: "should", 8: "should", 9: "must"},
    "db": {1: "must", 2: "must", 3: "should", 4: "should", 5: "should", 6: "should", 7: "nice"},
    "devops": {1: "should", 2: "must", 3: "must", 4: "should", 5: "should", 6: "nice", 7: "should", 8: "nice", 9: "must"},
    "fullstack": {0: "should"},
}
SECTION_PRIO = {
    ("backend", "1.3"): "must", ("backend", "1.4"): "must", ("backend", "1.5"): "must",
    ("backend", "5.5"): "nice", ("backend", "5.6"): "should",
    ("backend", "7.6"): "nice",
    ("backend", "8.1"): "must", ("backend", "8.2"): "must", ("backend", "8.4"): "must",
}
# порядок прохождения (фазы из рекомендованного маршрута)
PHASE = {}
for d, stages, ph in [
    ("backend", (1, 2, 3), 1), ("db", (1, 2), 1),
    ("backend", (4, 5), 2), ("db", (3, 4, 5), 2),
    ("frontend", (1, 2, 3, 4, 5, 6), 3), ("devops", (1, 2, 3, 4), 4), ("fullstack", (0,), 5),
    ("backend", (7, 8), 6), ("db", (6, 7), 6), ("frontend", (7, 8), 6), ("devops", (5, 6, 7, 8), 6),
    ("backend", (9,), 7), ("frontend", (9,), 7), ("devops", (9,), 7), ("backend", (6,), 8),
]:
    for s in stages:
        PHASE[(d, s)] = ph


def split_fm(text):
    m = re.match(r"---\n(.*?)\n---\n?", text, re.S)
    if not m:
        return None, text
    return m.group(1), text[m.end():]


def fm_get(fm, key, default=""):
    m = re.search(rf"^{key}:[ \t]*(.*)$", fm, re.M)
    return m.group(1).strip().strip('"') if m else default


def fm_set(fm, key, value):
    line = f"{key}: {value}"
    if re.search(rf"^{key}:", fm, re.M):
        return re.sub(rf"^{key}:.*$", line, fm, count=1, flags=re.M)
    return fm + "\n" + line


def tags_get(fm):
    m = re.search(r"^tags:\s*\[(.*?)\]\s*$", fm, re.M)
    return [t.strip() for t in m.group(1).split(",") if t.strip()] if m else []


def tags_set(fm, tags):
    line = "tags: [" + ", ".join(tags) + "]"
    if re.search(r"^tags:", fm, re.M):
        return re.sub(r"^tags:.*$", line, fm, count=1, flags=re.M)
    return fm + "\n" + line


def fmt_min(m):
    if m < 60:
        return f"{m} мин"
    h, r = divmod(m, 60)
    return f"{h} ч {r} мин" if r else f"{h} ч"


def badge(kind, label):
    return f'<span class="badge {kind}">{label}</span>'


def bar(done, total):
    pct = round(100 * done / total) if total else 0
    return f'<div class="bar"><span style="width:{pct}%"></span></div>'


def h1(body, fallback):
    m = re.search(r"^#\s+(.+)$", body, re.M)
    return (m.group(1).strip() if m else fallback).replace("#", "♯").replace("/", "∕")


def estimate(body):
    text = re.sub(r"<!-- meta:start -->.*?<!-- meta:end -->", "", body, flags=re.S)
    text = re.sub(r"<!-- toc:start -->.*?<!-- toc:end -->", "", text, flags=re.S)
    code_lines = sum(max(0, len(b.strip().splitlines()) - 2) for b in re.findall(r"```.*?```", text, re.S))
    prose = re.sub(r"```.*?```", "", text, flags=re.S)
    words = len(re.findall(r"\w+", prose))
    return words, code_lines


notes = {}  # path -> dict
for p in glob.glob("0[1-7]-*/**/*.md", recursive=True):
    text = open(p, encoding="utf-8").read()
    fm, body = split_fm(text)
    if fm is None:
        continue
    notes[p] = {"path": p, "fm": fm, "body": body, "type": fm_get(fm, "type"), "domain": fm_get(fm, "domain")}

# ---- 1. темы: приоритет, время, плашка ----
for p, n in notes.items():
    if n["type"] != "topic":
        continue
    fm, body = n["fm"], n["body"]
    domain = n["domain"]
    stage = int(fm_get(fm, "stage", "0") or 0)
    section = fm_get(fm, "section")
    key = section or f"{stage}.{fm_get(fm, 'order')}"   # тема-раздел без вложенных страниц: этап.порядок
    prio = SECTION_PRIO.get((domain, key)) or STAGE_PRIO.get(domain, {}).get(stage, "should")
    words, code_lines = estimate(body)
    stub = words < 150
    minutes = 20 if stub else max(3, round(words / 170 + code_lines / 12))
    tags = [t for t in tags_get(fm) if not t.startswith("priority/") and t != "flag/todo"]
    tags.append(f"priority/{prio}")
    if stub:
        tags.append("flag/todo")
    fm = tags_set(fm, tags)
    fm = fm_set(fm, "priority", prio)
    fm = fm_set(fm, "time", str(minutes))
    status = fm_get(fm, "status", "todo") or "todo"
    level = fm_get(fm, "level")
    when = f"≈{minutes} мин по плану" if stub else f"~{minutes} мин чтения"
    chips = [badge(prio, PRIO_LABEL[prio]), f'<span class="chip">{when}</span>']
    if level:
        chips.append(f'<span class="chip">Уровень: {level}</span>')
    if stub:
        chips.append('<span class="chip">тема не наполнена</span>')
    block = "<!-- meta:start -->\n<div class=\"meta-strip\">" + "".join(chips) + "</div>\n<!-- meta:end -->"
    body = re.sub(r"<!-- meta:start -->.*?<!-- meta:end -->\n?", "", body, flags=re.S)
    lines = body.split("\n")
    idx = next((i for i, l in enumerate(lines) if l.startswith("# ")), None)
    if idx is not None:
        j = idx + 1
        while j < len(lines) and not lines[j].strip():
            j += 1
        if j < len(lines) and lines[j].startswith("↑"):
            insert_at = j + 1
        else:
            insert_at = idx + 1
        lines[insert_at:insert_at] = ["", block]
        body = "\n".join(lines)
    n.update(fm=fm, body=body, prio=prio, time=minutes, stub=stub, status=status,
             stage=stage, section=section, order=int(fm_get(fm, "order", "0") or 0),
             title=h1(body, os.path.basename(p)[:-3]), name=os.path.basename(p)[:-3])


def topics_of(domain, stage=None, section=None):
    out = []
    for n in notes.values():
        if n["type"] != "topic" or n["domain"] != domain:
            continue
        if stage is not None and n["stage"] != stage:
            continue
        if section is not None and n["section"] != section:
            continue
        out.append(n)
    return out


def agg_status(items):
    st = [i["status"] for i in items]
    if st and all(s == "done" for s in st):
        return "done"
    if any(s in ("done", "wip", "in-progress") for s in st):
        return "wip"
    return "todo"


def norm_status(s):
    return "wip" if s == "in-progress" else s


for n in notes.values():
    if n["type"] == "topic":
        n["status"] = norm_status(n["status"])

# ---- 2. оглавления с таблицами ----
def table_block(rows_md):
    return "<!-- toc:start -->\n" + rows_md + "\n<!-- toc:end -->"


def replace_toc(body, heading_re, block):
    if "<!-- toc:start -->" in body:
        return re.sub(r"<!-- toc:start -->.*?<!-- toc:end -->", lambda m: block, body, flags=re.S)
    return re.sub(rf"(^## (?:{heading_re})\n)(.*?)(?=^## |\Z)", lambda m: m.group(1) + block + "\n\n", body, count=1, flags=re.S | re.M)


for p, n in notes.items():
    t = n["type"]
    d = os.path.dirname(p)
    dom = n["domain"]
    if t == "section":
        sect = fm_get(n["fm"], "section")
        stage = int(fm_get(n["fm"], "stage", "0"))
        kids = sorted(topics_of(dom, stage, sect), key=lambda x: x["order"])
        rows = ["| # | Тема | Приоритет | Чтение | Статус |", "|---|---|---|---|---|"]
        for k in kids:
            rows.append(f"| {k['order']} | [[{k['name']}\\|{k['title']}]] | "
                        f"{badge(k['prio'], PRIO_LABEL[k['prio']])} | {fmt_min(k['time'])} | {badge(k['status'], STATUS_LABEL[k['status']])} |")
        total = sum(k["time"] for k in kids)
        done = sum(1 for k in kids if k["status"] == "done")
        summary = f"**Итого:** {len(kids)} тем · ~{fmt_min(total)} · готово {done} из {len(kids)}\n\n{bar(done, len(kids))}\n\n"
        n["body"] = replace_toc(n["body"], "Темы", table_block(summary + "\n".join(rows)))
        n["agg"] = {"time": total, "done": done, "total": len(kids), "status": agg_status(kids),
                    "prio": min((k["prio"] for k in kids), key=lambda x: PRIO_RANK[x]) if kids else "should"}
    elif t == "stage":
        stage = int(fm_get(n["fm"], "stage", "0"))
        items = []  # (order, name, title, prio, time, status, done, total)
        for q, m in notes.items():
            if os.path.dirname(q) != d or m is n:
                continue
            if m["type"] == "topic":
                items.append((m["order"], m["name"], m["title"], m["prio"], m["time"], m["status"], int(m["status"] == "done"), 1))
        for q, m in notes.items():
            if m["type"] == "section" and os.path.dirname(q) == d:
                items.append(("sec", m))
        sec_rows = []
        for it in items:
            if it[0] == "sec":
                m = it[1]
                sect = fm_get(m["fm"], "section")
                kids = topics_of(dom, stage, sect)
                if not kids:
                    continue
                order = int(fm_get(m["fm"], "order", "0") or 0)
                prio = min((k["prio"] for k in kids), key=lambda x: PRIO_RANK[x])
                sec_rows.append((order, os.path.basename(q)[:-3], h1(m["body"], "Раздел " + sect), prio,
                                 sum(k["time"] for k in kids), agg_status(kids),
                                 sum(1 for k in kids if k["status"] == "done"), len(kids)))
            else:
                sec_rows.append(it)
        sec_rows.sort(key=lambda r: r[0])
        rows = ["| # | Раздел или тема | Приоритет | Чтение | Прогресс |", "|---|---|---|---|---|"]
        for order, name, title, prio, tm, st, dn, tt in sec_rows:
            prog = f"{dn} из {tt}<br>{bar(dn, tt)}" if tt > 1 else badge(st, STATUS_LABEL[st])
            rows.append(f"| {order} | [[{name}\\|{title}]] | {badge(prio, PRIO_LABEL[prio])} | {fmt_min(tm)} | {prog} |")
        total = sum(r[4] for r in sec_rows)
        dn = sum(r[6] for r in sec_rows)
        tt = sum(r[7] for r in sec_rows)
        summary = f"**Итого:** {tt} тем · ~{fmt_min(total)} · готово {dn} из {tt}\n\n{bar(dn, tt)}\n\n"
        n["body"] = replace_toc(n["body"], "Темы|Разделы", table_block(summary + "\n".join(rows)))
        n["agg"] = {"time": total, "done": dn, "total": tt, "stage": stage,
                    "prio": min((r[3] for r in sec_rows), key=lambda x: PRIO_RANK[x]) if sec_rows else "should"}

stage_notes = {(m["domain"], int(fm_get(m["fm"], "stage", "0"))): m for m in notes.values() if m["type"] == "stage"}
for p, n in notes.items():
    if n["type"] == "domain" and n["domain"] in DOMAINS:
        dom = n["domain"]
        rows = ["| Этап | Приоритет | Чтение | Прогресс |", "|---|---|---|---|"]
        tot_time = tot_done = tot_all = 0
        for (dm, st), m in sorted(stage_notes.items(), key=lambda kv: kv[0][1]):
            if dm != dom or "agg" not in m:
                continue
            a = m["agg"]
            name = os.path.basename(m["path"])[:-3]
            rows.append(f"| [[{name}\\|{h1(m['body'], name)}]] | {badge(a['prio'], PRIO_LABEL[a['prio']])} | {fmt_min(a['time'])} | "
                        f"{a['done']} из {a['total']}<br>{bar(a['done'], a['total'])} |")
            tot_time += a["time"]; tot_done += a["done"]; tot_all += a["total"]
        if tot_all:
            summary = f"**Итого:** {tot_all} тем · ~{fmt_min(tot_time)} · готово {tot_done} из {tot_all}\n\n{bar(tot_done, tot_all)}\n\n"
            n["body"] = replace_toc(n["body"], "Этапы", table_block(summary + "\n".join(rows)))

# ---- 3. запись файлов ----
for p, n in notes.items():
    new = "---\n" + n["fm"] + "\n---\n\n" + n["body"].lstrip("\n")
    old = open(p, encoding="utf-8").read()
    if new != old:
        open(p, "w", encoding="utf-8").write(new)

# ---- 4. страница «Прогресс» ----
topics = [n for n in notes.values() if n["type"] == "topic"]
total = len(topics)
done = sum(1 for n in topics if n["status"] == "done")
wip = sum(1 for n in topics if n["status"] == "wip")
left_min = sum(n["time"] for n in topics if n["status"] != "done")
all_min = sum(n["time"] for n in topics)
filled = sum(1 for n in topics if not n["stub"])


def kpi(v, label):
    return f'<div class="kpi"><b>{v}</b><span>{label}</span></div>'


out = ["---", "title: Прогресс", "tags: [kind/dashboard]", "---", "", "# Прогресс", "",
       "Страница собирается автоматически из свойств тем (`status`, `priority`, `time`).", "",
       '<div class="kpis">' + kpi(total, "тем в роадмапе") + kpi(filled, "наполнено") + kpi(done, "изучено")
       + kpi(wip, "в работе") + kpi(fmt_min(left_min), "чтения осталось") + "</div>", "",
       f"Общий прогресс изучения: **{done} из {total}**", "", bar(done, total), "", "## По разделам", "",
       "| Раздел | Тем | Чтение | Прогресс |", "|---|---|---|---|"]
for dom in DOMAIN_ORDER:
    ts = [n for n in topics if n["domain"] == dom]
    if not ts:
        continue
    dn = sum(1 for n in ts if n["status"] == "done")
    out.append(f"| **{DOMAINS[dom]}** | {len(ts)} | {fmt_min(sum(n['time'] for n in ts))} | {dn} из {len(ts)}<br>{bar(dn, len(ts))} |")
out += ["", "## По приоритету", "", "| Приоритет | Тем | Чтение | Изучено |", "|---|---|---|---|"]
for pr in ("must", "should", "nice"):
    ts = [n for n in topics if n["prio"] == pr]
    dn = sum(1 for n in ts if n["status"] == "done")
    out.append(f"| {badge(pr, PRIO_LABEL[pr])} | {len(ts)} | {fmt_min(sum(n['time'] for n in ts))} | {dn} из {len(ts)}<br>{bar(dn, len(ts))} |")

todo = [n for n in topics if n["status"] == "todo"]
todo.sort(key=lambda n: (PHASE.get((n["domain"], n["stage"]), 9), PRIO_RANK[n["prio"]], DOMAIN_ORDER.index(n["domain"]), n["stage"], n["order"]))
out += ["", "## Что читать дальше", "", "Порядок по рекомендуемому маршруту, внутри этапа сначала обязательное.", "",
        "| Тема | Приоритет | Чтение |", "|---|---|---|"]
for n in todo[:12]:
    out.append(f"| [[{n['name']}\\|{n['title']}]] | {badge(n['prio'], PRIO_LABEL[n['prio']])} | {fmt_min(n['time'])} |")

for flag, title in (("flag/hot", "Часто спрашивают"), ("flag/weak", "Слабые места"), ("flag/review", "Пора повторить")):
    ts = [n for n in topics if flag in tags_get(n["fm"])]
    if ts:
        out += ["", f"## {title}", ""] + [f"- [[{n['name']}\\|{n['title']}]]" for n in ts[:20]]
open("Прогресс.md", "w", encoding="utf-8").write("\n".join(out) + "\n")
print(f"topics={total} filled={filled} done={done} left={fmt_min(left_min)}")
