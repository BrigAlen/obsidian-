// Клиентская часть аккаунтов: вход, отметки о прохождении, заметки, личный кабинет.
// Работает поверх статического сайта Quartz; всё общение с сервером — /api/*.
(() => {
  const STATUS = [
    ["todo", "Не начато"],
    ["inProgress", "В работе"],
    ["done", "Изучено"],
  ];
  const state = { me: null, progress: new Map(), loaded: false };

  const el = (tag, props = {}, ...kids) => {
    const n = document.createElement(tag);
    for (const [k, v] of Object.entries(props)) {
      if (k === "class") n.className = v;
      else if (k.startsWith("on")) n.addEventListener(k.slice(2), v);
      else n.setAttribute(k, v);
    }
    for (const c of kids) n.append(c);
    return n;
  };

  async function api(method, url, body) {
    const r = await fetch(url, {
      method,
      headers: { "Content-Type": "application/json", "X-Requested-With": "vault" },
      body: body === undefined ? undefined : JSON.stringify(body),
      credentials: "same-origin",
    });
    let data = null;
    if (r.status !== 204) {
      try { data = await r.json(); } catch { /* пустой ответ */ }
    }
    if (!r.ok) {
      const err = new Error((data && data.error) || "Ошибка " + r.status);
      err.status = r.status;
      throw err;
    }
    return data;
  }

  const slugOf = () => (document.body.dataset.slug || "").replace(/^\/+|\/+$/g, "");
  const isTopicPage = (s) => /^0\d-[^/]+\/[^/]+\/.+/.test(s) && !/-overview$/.test(s);

  // ---- состояние ----
  async function loadMe() {
    try { state.me = await api("GET", "/api/me"); } catch { state.me = null; }
    state.progress = new Map();
    if (state.me) {
      try {
        const p = await api("GET", "/api/progress/");
        for (const i of p.items) state.progress.set(i.slug, i.status);
      } catch { /* оставим пустым */ }
    }
    state.loaded = true;
  }

  // ---- кнопка аккаунта ----
  function renderAccount() {
    document.getElementById("acct")?.remove();
    const box = el("div", { id: "acct", class: "acct" });
    if (!state.me) {
      box.append(el("button", { class: "acct-btn", onclick: openAuth }, "Войти"));
    } else {
      const menu = el("div", { class: "acct-menu", hidden: "" },
        el("a", { href: "/cabinet" }, "Личный кабинет"),
        state.me.role === "Admin" ? el("a", { href: "/cabinet#admin" }, "Администрирование") : "",
        el("button", { onclick: openPassword }, "Сменить пароль"),
        el("button", { onclick: logout }, "Выйти"));
      box.append(el("button", { class: "acct-btn", onclick: () => menu.toggleAttribute("hidden") }, state.me.login), menu);
    }
    document.body.append(box);
  }

  async function logout() {
    await api("POST", "/api/auth/logout");
    await refresh();
  }

  // ---- модальные окна ----
  function modal(title, content) {
    document.querySelector(".vmodal")?.remove();
    const m = el("div", { class: "vmodal", onclick: (e) => { if (e.target === m) m.remove(); } },
      el("div", { class: "vmodal-body" }, el("h3", {}, title), content));
    document.body.append(m);
    return m;
  }

  function field(label, type, name, extra = {}) {
    return el("label", { class: "vf" }, label, el("input", { type, name, required: "", ...extra }));
  }

  function openAuth() {
    let mode = "login";
    const err = el("p", { class: "verr" });
    const form = el("form", { class: "vform" });
    const draw = () => {
      form.replaceChildren(
        field("Логин", "text", "login", { autocomplete: "username" }),
        field("Пароль", "password", "password", mode === "login"
          ? { autocomplete: "current-password" }
          : { autocomplete: "new-password", minlength: "8" }), // длину проверяем только при создании пароля
        ...(mode === "register" ? [field("Код приглашения", "text", "invite", { autocomplete: "off" })] : []),
        err,
        el("button", { type: "submit", class: "vbtn primary" }, mode === "login" ? "Войти" : "Зарегистрироваться"),
        el("button", { type: "button", class: "vbtn link", onclick: () => { mode = mode === "login" ? "register" : "login"; err.textContent = ""; draw(); } },
          mode === "login" ? "Есть код приглашения? Зарегистрироваться" : "Уже есть аккаунт? Войти"));
    };
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      const d = Object.fromEntries(new FormData(form));
      try {
        await api("POST", mode === "login" ? "/api/auth/login" : "/api/auth/register", d);
        document.querySelector(".vmodal")?.remove();
        await refresh();
      } catch (x) { err.textContent = x.status === 429 ? "Слишком много попыток, подождите минуту" : x.message; }
    });
    draw();
    modal(mode === "login" ? "Вход" : "Регистрация", form);
  }

  function openPassword() {
    const err = el("p", { class: "verr" });
    const form = el("form", { class: "vform" },
      field("Текущий пароль", "password", "current", { autocomplete: "current-password" }),
      field("Новый пароль", "password", "new", { autocomplete: "new-password", minlength: "8" }),
      err, el("button", { type: "submit", class: "vbtn primary" }, "Сменить"));
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      try {
        await api("POST", "/api/auth/password", Object.fromEntries(new FormData(form)));
        document.querySelector(".vmodal")?.remove();
      } catch (x) { err.textContent = x.message; }
    });
    modal("Смена пароля", form);
  }

  // ---- панель темы: отметка и заметки ----
  async function renderTopicPanel() {
    document.getElementById("topic-panel")?.remove();
    const slug = slugOf();
    const article = document.querySelector("article");
    if (!article || !isTopicPage(slug)) return;
    const panel = el("section", { id: "topic-panel", class: "tpanel" });
    article.append(panel);

    if (!state.me) {
      panel.append(el("p", { class: "muted" }, "Войдите, чтобы отмечать пройденное и вести заметки к этой теме. ",
        el("button", { class: "vbtn link", onclick: openAuth }, "Войти")));
      return;
    }

    const cur = state.progress.get(slug) || "todo";
    const seg = el("div", { class: "seg" });
    for (const [val, label] of STATUS) {
      seg.append(el("button", {
        class: "seg-btn" + (val === cur ? " on" : ""),
        onclick: async () => {
          await api("PUT", "/api/progress/", { slug, status: val });
          if (val === "todo") state.progress.delete(slug); else state.progress.set(slug, val);
          decorateExplorer();
          renderTopicPanel();
        },
      }, label));
    }
    panel.append(el("h2", {}, "Мой прогресс"), seg);

    const title = (document.querySelector("article h1, .article-title")?.textContent || slug).trim();
    const list = el("div", { class: "notes" });
    const ta = el("textarea", { rows: "3", maxlength: "20000", placeholder: "Новая заметка по теме" });
    const add = el("button", { class: "vbtn primary", onclick: async () => {
      if (!ta.value.trim()) return;
      await api("POST", "/api/notes/", { slug, title, body: ta.value });
      ta.value = "";
      loadNotes();
    } }, "Добавить заметку");
    panel.append(el("h2", {}, "Мои заметки"), list, ta, add);

    async function loadNotes() {
      const r = await api("GET", "/api/notes/?slug=" + encodeURIComponent(slug));
      list.replaceChildren(...(r.items.length ? r.items.map(noteCard(loadNotes, false)) : [el("p", { class: "muted" }, "Заметок пока нет")]));
    }
    loadNotes();
  }

  function noteCard(reload, showTopic) {
    return (n) => {
      const body = el("div", { class: "note-body" }, n.body);
      const card = el("div", { class: "note" });
      const when = new Date(n.updatedAt).toLocaleString("ru-RU", { dateStyle: "medium", timeStyle: "short" });
      const head = el("div", { class: "note-head" },
        showTopic ? el("a", { href: "/" + n.slug }, n.title) : el("span", { class: "muted" }, when),
        el("span", { class: "note-actions" },
          el("button", { class: "vbtn link", onclick: () => edit() }, "Править"),
          el("button", { class: "vbtn link", onclick: async () => { if (confirm("Удалить заметку?")) { await api("DELETE", "/api/notes/" + n.id); reload(); } } }, "Удалить")));
      if (showTopic) head.append(el("span", { class: "muted" }, when));
      card.append(head, body);
      function edit() {
        const ta = el("textarea", { rows: "4", maxlength: "20000" });
        ta.value = n.body;
        const save = el("button", { class: "vbtn primary", onclick: async () => { await api("PUT", "/api/notes/" + n.id, { body: ta.value }); reload(); } }, "Сохранить");
        body.replaceWith(ta);
        card.append(save);
      }
      return card;
    };
  }

  // ---- галочки у изученных тем в боковом дереве ----
  function decorateExplorer() {
    document.querySelectorAll(".explorer a[data-for]").forEach((a) => {
      const slug = (a.getAttribute("data-for") || "").replace(/^\/+|\/+$/g, "");
      const st = state.progress.get(slug);
      a.classList.toggle("p-done", st === "done");
      a.classList.toggle("p-wip", st === "inProgress");
    });
  }

  // ---- личный кабинет: /cabinet ----
  async function renderCabinet() {
    const root = document.getElementById("cabinet-root");
    if (!root) return;
    root.replaceChildren();
    if (!state.me) {
      root.append(el("p", {}, "Войдите, чтобы увидеть прогресс и заметки. ", el("button", { class: "vbtn link", onclick: openAuth }, "Войти")));
      return;
    }
    // прогресс
    const total = Number(root.dataset.total || 0);
    const done = [...state.progress.values()].filter((s) => s === "done").length;
    const wip = [...state.progress.values()].filter((s) => s === "inProgress").length;
    const pct = total ? Math.round((done / total) * 100) : 0;
    root.append(el("h2", {}, "Мой прогресс"),
      el("p", {}, `Изучено: ${done}` + (total ? ` из ${total} (${pct}%)` : "") + `, в работе: ${wip}`));
    if (total) root.append(el("div", { class: "bar" }, el("span", { style: `width:${pct}%` })));

    // заметки
    const q = el("input", { type: "search", placeholder: "Поиск по заметкам", class: "vsearch" });
    const list = el("div", { class: "notes" });
    root.append(el("h2", {}, "Все мои заметки"), q, list);
    let timer;
    const load = async () => {
      const r = await api("GET", "/api/notes/?take=100&q=" + encodeURIComponent(q.value));
      list.replaceChildren(...(r.items.length ? r.items.map(noteCard(load, true)) : [el("p", { class: "muted" }, "Заметок пока нет")]));
    };
    q.addEventListener("input", () => { clearTimeout(timer); timer = setTimeout(load, 300); });
    load();

    if (state.me.role === "Admin") renderAdmin(root);
  }

  async function renderAdmin(root) {
    const out = el("p", { class: "muted" });
    const users = el("div", { class: "notes" });
    root.append(el("h2", { id: "admin" }, "Администрирование"),
      el("button", { class: "vbtn primary", onclick: async () => {
        const r = await api("POST", "/api/admin/invites");
        out.textContent = "Код приглашения (показывается один раз, действует 7 дней): " + r.code;
      } }, "Создать приглашение"), out, users);
    const us = await api("GET", "/api/admin/users");
    users.replaceChildren(...us.map((u) => el("div", { class: "note" },
      el("div", { class: "note-head" }, el("span", {}, u.login + (u.role === "Admin" ? " (админ)" : "") + (u.isBlocked ? " — заблокирован" : "")),
        el("span", { class: "note-actions" },
          el("button", { class: "vbtn link", onclick: async () => {
            const p = prompt("Новый пароль для " + u.login + " (минимум 8 символов)");
            if (p) { await api("POST", `/api/admin/users/${u.id}/reset-password`, { password: p }); alert("Пароль сброшен"); }
          } }, "Сбросить пароль"),
          el("button", { class: "vbtn link", onclick: async () => { await api("POST", `/api/admin/users/${u.id}/block?blocked=${!u.isBlocked}`); renderCabinet(); } },
            u.isBlocked ? "Разблокировать" : "Блокировать"))))));
  }

  async function refresh() {
    await loadMe();
    renderAccount();
    renderTopicPanel();
    renderCabinet();
    decorateExplorer();
  }

  // Quartz работает как SPA: событие nav приходит при каждом переходе
  document.addEventListener("nav", () => { if (state.loaded) { renderAccount(); renderTopicPanel(); renderCabinet(); decorateExplorer(); } else refresh(); });
  new MutationObserver(() => decorateExplorer()).observe(document.body, { childList: true, subtree: true });
  if (document.readyState !== "loading") refresh(); else document.addEventListener("DOMContentLoaded", refresh);
})();
