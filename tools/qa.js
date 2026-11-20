// 教材ページ下部の「この教材について質問する」機能。
// claude.use("sample") で Claude に質問し、ページ本文を根拠に答えてもらう。
(function () {
  const box = document.getElementById("qa");
  if (!box) return;
  const log = box.querySelector(".qa-log");
  const form = box.querySelector("form");
  const input = box.querySelector("textarea");
  const send = box.querySelector(".qa-send");
  const stop = box.querySelector(".qa-stop");
  const clear = box.querySelector(".qa-clear");
  const status = box.querySelector(".qa-status");
  const chips = box.querySelectorAll(".qa-chip");
  const title = document.title.split("｜")[0];
  const key = "qa:" + location.pathname;
  let history = [];
  let sample = null;
  let ctrl = null;

  const SYSTEM = [
    "あなたは、医療系動画の制作者（医療者ではない人）向けの教材の講師です。",
    "下の【教材本文】を主な根拠に、日本語で答えてください。",
    "スマホで読むので、見出しは使わず、短い段落と箇条書きで簡潔に。専門用語には短い説明を添える。",
    "教材にない内容は一般的な医学知識で補ってよいが、その部分は「教材外の一般的な情報」と明記する。",
    "点数・頻度・制度など変わりうる数値は教材の記載を優先し、教材にない数値は断定しない。",
    "個人の症状の診断や治療の助言はしない（必要なら医療機関への相談をすすめる）。",
    "台本や説明文の作成を頼まれたら、医学的に正確で誤解を招かない表現にする。",
  ].join("\n");

  function lessonText() {
    const a = document.querySelector("article");
    return (a ? a.innerText : document.body.innerText).slice(0, 40000);
  }

  function esc(s) {
    return s.replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
  }

  function md(s) {
    const lines = esc(s).split("\n");
    let out = "", inList = false;
    for (let l of lines) {
      l = l.replace(/\*\*(.+?)\*\*/g, "<b>$1</b>").replace(/^#{1,6}\s*/, "");
      const m = l.match(/^\s*(?:[-・*]|\d+[.)])\s+(.*)$/);
      if (m) {
        if (!inList) { out += "<ul>"; inList = true; }
        out += "<li>" + m[1] + "</li>";
      } else {
        if (inList) { out += "</ul>"; inList = false; }
        if (l.trim()) out += "<p>" + l + "</p>";
      }
    }
    if (inList) out += "</ul>";
    return out;
  }

  function bubble(role, text) {
    const d = document.createElement("div");
    d.className = "qa-msg " + (role === "user" ? "qa-user" : "qa-bot");
    d.innerHTML = role === "user" ? "<p>" + esc(text) + "</p>" : md(text);
    log.appendChild(d);
    return d;
  }

  function save() {
    try { localStorage.setItem(key, JSON.stringify(history.slice(-20))); } catch (e) {}
  }

  function restore() {
    try {
      const h = JSON.parse(localStorage.getItem(key) || "[]");
      if (Array.isArray(h)) {
        history = h;
        for (const m of history) bubble(m.role, m.content);
      }
    } catch (e) { history = []; }
    clear.hidden = history.length === 0;
  }

  function busy(on) {
    send.disabled = on;
    input.disabled = on;
    stop.hidden = !on;
    chips.forEach((c) => (c.disabled = on));
  }

  async function ask(q) {
    q = q.trim();
    if (!q || !sample) return;
    bubble("user", q);
    input.value = "";
    const msgs = history.map((m) => ({ role: m.role, content: m.content }));
    msgs.push({ role: "user", content: q });
    // 最初のメッセージに指示と教材本文を付ける（Claude は前の会話を覚えていないため毎回送る）
    msgs[0] = {
      role: "user",
      content: SYSTEM + "\n\n【教材：" + title + "】\n" + lessonText() + "\n\n【質問】\n" + msgs[0].content,
    };
    const out = bubble("assistant", "考えています…");
    out.scrollIntoView({ behavior: "smooth", block: "nearest" });
    busy(true);
    status.textContent = "";
    ctrl = new AbortController();
    try {
      const r = await sample(msgs, {
        cache: false,
        signal: ctrl.signal,
        onText: ({ text }) => { out.innerHTML = md(text); },
      });
      out.innerHTML = md(r.text) + (r.truncated ? "<p class='qa-note'>（回答が長いため途中で切れました）</p>" : "");
      history.push({ role: "user", content: q }, { role: "assistant", content: r.text });
      save();
      clear.hidden = false;
    } catch (e) {
      const partial = e && e.text ? e.text : "";
      if (e && e.code === "not_granted") {
        out.remove();
        status.textContent = "Claude への質問が許可されていません。";
      } else if (e && e.code === "rate_limited") {
        out.innerHTML = md(partial) + "<p class='qa-note'>質問が混み合っています。少し時間をおいてもう一度送ってください。</p>";
      } else if (e && e.name === "AbortError") {
        out.innerHTML = md(partial) + "<p class='qa-note'>（停止しました）</p>";
      } else {
        out.innerHTML = md(partial) + "<p class='qa-note'>回答を取得できませんでした。もう一度お試しください。</p>";
      }
    } finally {
      busy(false);
      ctrl = null;
    }
  }

  form.addEventListener("submit", (e) => { e.preventDefault(); ask(input.value); });
  input.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) { e.preventDefault(); ask(input.value); }
  });
  chips.forEach((c) => c.addEventListener("click", () => ask(c.dataset.q)));
  stop.addEventListener("click", () => ctrl && ctrl.abort());
  clear.addEventListener("click", () => {
    history = [];
    log.innerHTML = "";
    save();
    clear.hidden = true;
  });

  restore();
  busy(true);
  stop.hidden = true;
  status.textContent = "準備中…";
  const use = window.claude && window.claude.use;
  if (!use) {
    status.textContent = "この表示では質問機能を使えません。claude.ai でこのページを開くと使えます。";
    return;
  }
  window.claude.use("sample").then((s) => {
    sample = s;
    if (!s) {
      status.textContent = "この表示では質問機能を使えません。";
      return;
    }
    status.textContent = "";
    busy(false);
  }, () => { status.textContent = "この表示では質問機能を使えません。"; });
})();

// 質問欄が見えている間は右下の「質問する」ボタンを隠す
(function () {
  const fab = document.querySelector(".qa-fab");
  const box = document.getElementById("qa");
  if (!fab || !box || !("IntersectionObserver" in window)) return;
  new IntersectionObserver((es) => { fab.hidden = es[0].isIntersecting; }).observe(box);
})();
