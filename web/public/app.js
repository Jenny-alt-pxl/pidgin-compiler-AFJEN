/* AFJEN Compiler - browser front end (vanilla JavaScript, no build step).
   Talks to the Express server, which talks to the Python compiler engine. */

const PAGES = [
  ["translate", "✦", "Translate", "Type or paste any Pidgin or franc-anglais text"],
  ["dictionary", "☰", "Dictionary", "Every word AFJEN knows, in alphabetical order - and the words you taught it"],
  ["statements", "❝", "Statements", "The collected statements and your own, each with a verified English and French translation"],
  ["insights", "▤", "Insights", "What you have been analysing"],
  ["about", "ⓘ", "About", "The founders, the story and how AFJEN works"],
];
const EXAMPLES = [
  "How you dey? I dey, thank you",
  "You dey dey ok so?",
  "Mama, make you reduce am na small",
  "Petrol dey scarce, pump don empty again",
  "Wuna mos pay for bus",
];
const TOKEN_COLORS = {
  NOUN: "#e9f0f8", PROPER_NOUN: "#d9e6f4", PRONOUN: "#efe7f5", ARTICLE: "#f3f0ec", VERB: "#e4f1e7",
  PIDGIN_VERB: "#cfe8d6", NEGATION: "#f9e0e0", SUBJUNCTIVE: "#fbe7d3", PIDGIN_MARKER: "#fbefd2",
  INTERJECTION: "#f8e1ea", CODE_MIXED: "#f3d9ee", ADJECTIVE: "#ddf1f3", ADVERB: "#ddf0ec",
  PREPOSITION: "#eef2cf", NUMBER: "#fbebc4", CONNECTOR: "#efece8", PUNCTUATION: "#efece8", QUESTION_WORD: "#e7d2ec",
};

const $ = (sel) => document.querySelector(sel);
const el = (tag, props = {}, ...kids) => {
  const node = Object.assign(document.createElement(tag), props);
  kids.flat().forEach((k) => node.append(k instanceof Node ? k : document.createTextNode(k)));
  return node;
};
const api = async (method, url, body) => {
  const res = await fetch(url, { method, headers: { "Content-Type": "application/json" },
                                 body: body ? JSON.stringify(body) : undefined });
  const data = await res.json();
  if (!res.ok) throw new Error(data.message || "Request failed");
  return data;
};
const toast = (text) => {
  const t = $("#toast"); t.textContent = text; t.hidden = false;
  clearTimeout(toast.timer); toast.timer = setTimeout(() => (t.hidden = true), 2600);
};

const state = { lang: "en", result: null, page: "translate", letter: "All", dict: null, stmts: null, liveTimer: null };
const history = JSON.parse(localStorage.getItem("afjen-history") || "[]");

/* ------------------------------------------------------------------ navigation -- */
function buildNav() {
  const nav = $("#nav");
  PAGES.forEach(([key, ico, label]) => {
    const b = el("button", { onclick: () => show(key) }, el("span", { className: "ico", textContent: ico }), label);
    b.dataset.page = key; nav.append(b);
  });
}
function show(key) {
  state.page = key;
  document.querySelectorAll(".page").forEach((p) => (p.hidden = p.id !== `page-${key}`));
  document.querySelectorAll("nav button").forEach((b) => b.classList.toggle("active", b.dataset.page === key));
  const page = PAGES.find((p) => p[0] === key);
  $("#page-title").textContent = page[2]; $("#page-sub").textContent = page[3];
  if (key === "dictionary") loadDictionary();
  if (key === "statements") loadStatements();
  if (key === "insights") loadInsights();
}
async function refreshSide() {
  const i = await api("GET", "/api/insights");
  $("#side-stats").innerHTML = `${i.dictionary} dictionary words<br>${i.statements} statements<br>${i.collected} words collected`;
}

/* -------------------------------------------------------------------- translate -- */
async function analyze() {
  const text = $("#input").value.trim();
  updateCount();
  if (!text) { $("#output").textContent = ""; $("#note").textContent = "Type or paste some text above."; return; }
  try { state.result = await api("POST", "/api/analyze", { text }); }
  catch (err) { $("#note").textContent = "Could not reach the engine: " + err.message; return; }
  if (history[0] !== text) { history.unshift(text); history.length = Math.min(history.length, 30);
    localStorage.setItem("afjen-history", JSON.stringify(history)); }
  render(); refreshSide();
}
function updateCount() {
  const n = ($("#input").value.match(/[A-Za-zÀ-ÿ'’-]+/g) || []).length;
  $("#word-count").textContent = `${n} word${n === 1 ? "" : "s"}`;
}
function render() {
  const r = state.result; if (!r || r.empty) return;
  const t = r.translations[state.lang];
  $("#output").textContent = t.text;
  const badge = $("#badge");
  const labels = { verified: "✔ Verified translation", partial: "◐ Partly verified", automatic: "⚙ Automatic translation" };
  badge.textContent = labels[t.method]; badge.className = `badge ${t.method}`;
  $("#note").textContent = { verified: "Hand-checked translation from the statement collection.",
    partial: "Some sentences are verified, the rest was produced by the rule engine.",
    automatic: "Produced by AFJEN's rules and expression table. Use “Save as a statement…” to store a corrected, verified version." }[t.method]
    + (t.unknown.length ? "   New words - click one to teach it:" : "");
  const chips = $("#unknown-chips"); chips.replaceChildren();
  t.unknown.slice(0, 10).forEach((w) => chips.append(el("button", { className: "chip new", textContent: "+ " + w, onclick: () => openWordModal(w) })));

  // grammar fit
  const pill = $("#pill");
  if (r.allFull) { pill.textContent = "✔  Fits the AFJEN grammar perfectly"; pill.className = "pill ok"; $("#detail").textContent = "Every sentence has a complete LL(1) parse tree."; }
  else if (r.coverage >= 50) { pill.textContent = `◐  ${r.matched} of ${r.total} clauses fit the grammar`; pill.className = "pill mid"; $("#detail").textContent = "The rest is informal speech - still translated and analysed word by word."; }
  else { pill.textContent = "◔  Informal speech - analysed word by word"; pill.className = "pill inf"; $("#detail").textContent = "This wording is looser than the strict grammar, so AFJEN read it as fragments."; }
  $("#donut").innerHTML = donut(r.allFull ? 100 : r.coverage, r.allFull ? "#4e8f6a" : r.coverage >= 50 ? "#c9a24b" : "#8a5bb0");
  const tiles = $("#tiles"); tiles.replaceChildren();
  [[r.wordCount, "words"], [r.sentences.length, "sentences"], [r.topic, "topic"], [r.intent, "intent"]]
    .forEach(([v, l]) => tiles.append(el("div", { className: "tile" }, el("b", { textContent: v }), el("span", { textContent: l }))));

  // tokens
  const body = $("#tokens tbody"); body.replaceChildren();
  r.tokens.forEach((tok) => { const tr = el("tr", {}, el("td", { textContent: tok.value }), el("td", { textContent: tok.type }), el("td", { textContent: tok.pos }));
    tr.style.background = TOKEN_COLORS[tok.type] || ""; body.append(tr); });

  // structure
  const box = $("#structure"); box.replaceChildren();
  r.sentences.forEach((s, i) => {
    box.append(el("div", { className: "sent", textContent: `Sentence ${i + 1}: ${s.text.slice(0, 90)}${s.text.length > 90 ? "…" : ""}` }));
    box.append(el("div", { className: s.kind === "full" ? "ok" : "frag",
      textContent: s.kind === "full" ? "  ✔ complete parse" : s.kind === "partial" ? `  ◐ ${s.matched} of ${s.total} clauses parsed` : "  ◔ informal - read as fragments" }));
    s.trees.forEach((tree) => drawTree(box, tree, 1));
    s.fragments.forEach((f) => box.append(el("div", { className: "frag", textContent: `    fragment: “${f}”` })));
    box.append(el("br"));
  });
}
function drawTree(box, node, depth) {
  const pad = "   ".repeat(depth);
  if (node.value !== undefined) {
    box.append(el("div", {}, el("span", { className: "node", textContent: `${pad}└─ ` }), el("span", { className: "leaf", textContent: node.value }),
      el("span", { className: "node", textContent: `  ${node.type}` })));
  } else {
    box.append(el("div", { className: "node", textContent: `${pad}▾ ${node.type}` }));
    (node.children || []).forEach((c) => drawTree(box, c, depth + 1));
  }
}
function donut(pct, colour) {
  const r = 46, c = 2 * Math.PI * r, off = c * (1 - Math.min(pct, 99.9) / 100);
  return `<svg width="124" height="124" viewBox="0 0 124 124"><circle cx="62" cy="62" r="${r}" fill="none" stroke="#efe6dc" stroke-width="11"/>
    <circle cx="62" cy="62" r="${r}" fill="none" stroke="${colour}" stroke-width="11" stroke-dasharray="${c}" stroke-dashoffset="${off}"
    transform="rotate(-90 62 62)" stroke-linecap="butt"/><text x="62" y="60" text-anchor="middle" font-family="Georgia" font-weight="bold" font-size="19">${pct}%</text>
    <text x="62" y="80" text-anchor="middle" font-size="10" fill="#85788a">grammar fit</text></svg>`;
}
function currentTranslation(lang) { return state.result?.translations?.[lang]?.text || ""; }
function saveFile() {
  const text = $("#input").value.trim(); if (!text || !state.result) return toast("Type or paste some text first.");
  const r = state.result.translations;
  const body = `AFJEN Compiler - ${new Date().toLocaleString()}\n\nOriginal (Pidgin / franc-anglais)\n${text}\n\n` +
    `English (${r.en.method})\n${r.en.text}\n\nFrançais (${r.fr.method})\n${r.fr.text}\n`;
  const a = el("a", { href: URL.createObjectURL(new Blob([body], { type: "text/plain;charset=utf-8" })), download: "afjen_translation.txt" });
  a.click(); URL.revokeObjectURL(a.href); toast("Saved afjen_translation.txt");
}
async function copy(text, msg) { await navigator.clipboard.writeText(text); toast(msg); }

/* ------------------------------------------------------------------- dictionary -- */
async function loadDictionary() { state.dict = await api("GET", "/api/dictionary"); renderDictionary(); }
function renderDictionary() {
  const d = state.dict; if (!d) return;
  const q = $("#dict-search").value.trim().toLowerCase();
  const letters = $("#letters"); letters.replaceChildren();
  ["All", ...d.letters].forEach((l) => letters.append(el("button", { textContent: l, className: state.letter === l ? "active" : "",
    onclick: () => { state.letter = l; renderDictionary(); } })));
  const strip = (s) => s.normalize("NFD").replace(/[̀-ͯ]/g, "").toUpperCase();
  const rows = d.rows.filter((r) => (state.letter === "All" || strip(r.word)[0] === state.letter) &&
    (!q || [r.word, r.type, r.english, r.french].some((c) => c.toLowerCase().includes(q))));
  $("#dict-count").textContent = `${rows.length} of ${d.total} words  ·  ${d.mine} added by you ★  ·  A → Z`;
  const body = $("#dict-table tbody"); body.replaceChildren();
  rows.forEach((r) => {
    const mine = r.type.startsWith("★");
    const tr = el("tr", { className: mine ? "mine" : "" }, el("td", { textContent: r.word }), el("td", { textContent: r.type }),
      el("td", { textContent: r.english }), el("td", { textContent: r.french }),
      el("td", {}, mine ? el("button", { className: "btn soft small", textContent: "Remove", onclick: async () => {
        await api("DELETE", "/api/dictionary", { word: r.word }); toast(`Removed “${r.word}”.`); loadDictionary(); refreshSide(); } }) : ""));
    body.append(tr);
  });
}

/* ------------------------------------------------------------------- statements -- */
async function loadStatements() { state.stmts = await api("GET", "/api/statements"); renderStatements(); }
function renderStatements() {
  const s = state.stmts; if (!s) return;
  const sel = $("#stmt-topic"), keep = sel.value;
  sel.replaceChildren(el("option", { textContent: "All topics" }), ...s.topics.map((t) => el("option", { textContent: t })));
  sel.value = keep && [...sel.options].some((o) => o.value === keep) ? keep : "All topics";
  const rows = s.rows.filter((r) => sel.value === "All topics" || r.topic === sel.value);
  $("#stmt-count").textContent = `${rows.length} of ${s.total} statements`;
  $("#stmt-note").textContent = `${s.collected} collected in Yaoundé  ·  ${s.examples} further examples  ·  ${s.mine} added by you ★.  Click a row to analyse it. Replace the examples with statements you heard yourselves.`;
  const body = $("#stmt-table tbody"); body.replaceChildren();
  const label = { collected: "Collected", example: "Example", yours: "Yours ★" };
  rows.forEach((r) => {
    const tr = el("tr", { className: r.source === "yours" ? "mine" : "", style: "cursor:pointer",
      onclick: () => { $("#input").value = r.text; show("translate"); analyze(); } },
      el("td", { textContent: r.n }), el("td", { textContent: r.topic }), el("td", { textContent: label[r.source] }),
      el("td", { textContent: r.text }), el("td", { textContent: r.en }), el("td", { textContent: r.fr }),
      el("td", {}, r.source === "yours" ? el("button", { className: "btn soft small", textContent: "Remove", onclick: async (e) => {
        e.stopPropagation(); await api("DELETE", "/api/statements", { text: r.text }); toast("Statement removed."); loadStatements(); refreshSide(); } }) : ""));
    body.append(tr);
  });
}

/* --------------------------------------------------------------------- insights -- */
async function loadInsights() {
  const i = await api("GET", "/api/insights");
  const tiles = $("#insight-tiles"); tiles.replaceChildren();
  [[i.dictionary, "dictionary words"], [i.statements, "statements"], [i.collected, "words collected"], [i.unknown.length, "waiting to be taught"]]
    .forEach(([v, l]) => tiles.append(el("div", { className: "tile" }, el("b", { textContent: v }), el("span", { textContent: l }))));
  const chart = $("#chart"); chart.replaceChildren();
  const peak = Math.max(1, ...i.top.map((t) => t.count));
  i.top.forEach((t) => chart.append(el("div", { className: "bar-row" }, el("span", { textContent: t.word }),
    Object.assign(el("div", { className: "bar" }), { style: `width:${(t.count / peak) * 60}%` }), el("em", { textContent: t.count }))));
  const list = $("#history"); list.replaceChildren();
  history.forEach((h) => list.append(el("li", { textContent: h.replace(/\n/g, " ").slice(0, 110), onclick: () => { $("#input").value = h; show("translate"); analyze(); } })));
}

/* ----------------------------------------------------------------------- modals -- */
function openModal(title, sub, bodyNodes, buttons) {
  $("#modal-title").textContent = title; $("#modal-sub").textContent = sub;
  $("#modal-body").replaceChildren(...bodyNodes); $("#modal-foot").replaceChildren(...buttons);
  $("#modal-msg").textContent = ""; $("#modal-msg").className = "modal-msg"; $("#modal").hidden = false;
}
const closeModal = () => ($("#modal").hidden = true);
const say = (ok, text) => { const m = $("#modal-msg"); m.textContent = (ok ? "✔ " : "✘ ") + text; m.className = "modal-msg " + (ok ? "ok" : "bad"); };
const field = (label, node) => el("div", {}, el("label", { textContent: label }), node);

async function openWordModal(word = "") {
  if (!state.dict) state.dict = await api("GET", "/api/dictionary");
  const w = el("input", { type: "text", value: word }), en = el("input", { type: "text" }), fr = el("input", { type: "text" });
  const type = el("select", {}, ...state.dict.types.map((t) => el("option", { textContent: t })));
  const gender = el("select", {}, el("option", { textContent: "m" }), el("option", { textContent: "f" }));
  const submit = async () => {
    const res = await api("POST", "/api/dictionary", { word: w.value, type: type.value, english: en.value, french: fr.value, gender: gender.value });
    say(res.ok, res.message);
    if (res.ok) { w.value = en.value = fr.value = ""; w.focus(); refreshSide(); if (state.page === "dictionary") loadDictionary(); if (state.result) analyze(); }
  };
  [w, en, fr].forEach((i) => i.addEventListener("keydown", (e) => e.key === "Enter" && submit()));
  openModal("Teach AFJEN a new word", "Give the word or expression and its meanings. It works immediately.",
    [field("Word or expression (Pidgin / slang)", w),
     el("div", { className: "grid" }, field("Type", type), field("Gender in French (nouns)", gender)),
     field("English meaning", en), field("Français (infinitive for verbs)", fr)],
    [el("button", { className: "btn primary", textContent: "Add word", onclick: submit }), el("button", { className: "btn soft", textContent: "Done", onclick: closeModal })]);
  (word ? en : w).focus();
}
async function openStatementModal(pre = {}) {
  if (!state.stmts) state.stmts = await api("GET", "/api/statements");
  const text = el("textarea", { rows: 2, value: pre.text || "" }), en = el("textarea", { rows: 2, value: pre.en || "" }), fr = el("textarea", { rows: 2, value: pre.fr || "" });
  const topic = el("input", { type: "text", value: state.stmts.topics[0], setAttribute: "list" });
  topic.setAttribute("list", "topics"); const dl = el("datalist", { id: "topics" }, ...state.stmts.topics.map((t) => el("option", { value: t })));
  const submit = async () => {
    const res = await api("POST", "/api/statements", { text: text.value, english: en.value, french: fr.value, topic: topic.value });
    say(res.ok, res.message);
    if (res.ok) { refreshSide(); if (state.page === "statements") loadStatements(); if (state.result) analyze(); setTimeout(closeModal, 700); }
  };
  openModal("Add a statement to the collection", "Write it exactly as you heard it, then give the correct English and French. It becomes a verified translation.",
    [field("Statement (Pidgin / franc-anglais)", text), field("English", en), field("Français", fr), field("Topic", topic), dl],
    [el("button", { className: "btn primary", textContent: "Add statement", onclick: submit }), el("button", { className: "btn soft", textContent: "Cancel", onclick: closeModal })]);
  (pre.text ? en : text).focus();
}

/* ------------------------------------------------------------------------ start -- */
function init() {
  buildNav();
  const chips = $("#examples");
  EXAMPLES.forEach((ex) => chips.append(el("button", { className: "chip", textContent: ex, onclick: () => { $("#input").value = ex; analyze(); } })));
  $("#input").value = "Brother, drop me na at Carrefour Yaoundé, the traffic done tire me small";
  $("#input").addEventListener("input", () => { updateCount(); if ($("#live").checked) { clearTimeout(state.liveTimer); state.liveTimer = setTimeout(analyze, 650); } });
  $("#btn-analyze").onclick = analyze;
  $("#btn-clear").onclick = () => { $("#input").value = ""; updateCount(); $("#input").focus(); };
  $("#btn-paste").onclick = async () => { try { $("#input").value = await navigator.clipboard.readText(); analyze(); } catch { toast("Allow clipboard access to paste."); } };
  $("#lang-switch").addEventListener("click", (e) => { const l = e.target.dataset.lang; if (!l) return; state.lang = l;
    document.querySelectorAll("#lang-switch button").forEach((b) => b.classList.toggle("active", b.dataset.lang === l)); render(); });
  $("#btn-save").onclick = saveFile;
  $("#btn-copy").onclick = () => copy(currentTranslation(state.lang), "Copied to the clipboard.");
  $("#btn-copy-both").onclick = () => copy(`English: ${currentTranslation("en")}\nFrançais: ${currentTranslation("fr")}`, "English and French copied.");
  $("#btn-save-statement").onclick = () => $("#input").value.trim() && openStatementModal({ text: $("#input").value.trim(), en: currentTranslation("en"), fr: currentTranslation("fr") });
  $("#btn-add-word").onclick = () => openWordModal();
  $("#btn-add-statement").onclick = () => openStatementModal();
  $("#dict-search").addEventListener("input", renderDictionary);
  $("#stmt-topic").addEventListener("change", renderStatements);
  $("#modal").addEventListener("click", (e) => e.target.id === "modal" && closeModal());
  document.addEventListener("keydown", (e) => { if (e.key === "Escape") closeModal(); if (e.ctrlKey && e.key === "Enter") analyze(); });
  show("translate"); analyze();
}
init();
