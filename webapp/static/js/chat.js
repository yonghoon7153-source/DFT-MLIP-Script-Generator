/* chat.js — 위키 근거 대화 화면.
 *
 * 하는 일: 질문을 /api/chat 에 POST → SSE 로 오는 조각을 화면에 붙인다 → 끝나면 /api/md 로
 * 서버 렌더러(raw HTML 차단 + wikilink)를 통과한 HTML 로 바꾼다.
 *
 * ⚠ 저장은 이 브라우저(localStorage `midni.chat.v1`)에만. 서버는 기록을 요청마다 **받아서**
 *   넘길 뿐 어디에도 쓰지 않는다.
 * ⚠ innerHTML 은 서버가 렌더한 HTML(/api/md — 우리 렌더러가 raw HTML 을 이미 걸렀다)에만 쓴다.
 *   모델 텍스트·근거 제목은 전부 textContent 다.
 */
(function () {
  "use strict";
  var root = document.getElementById("chat");
  if (!root) return;
  var ok = root.getAttribute("data-ok") === "y";
  var log = document.getElementById("chat-log");
  var empty = document.getElementById("chat-empty");
  var form = document.getElementById("chat-form");
  var ta = document.getElementById("chat-q");
  var sendBtn = document.getElementById("chat-send");
  var srcList = document.getElementById("src-list");
  var srcHint = document.getElementById("src-hint");
  var usageEl = document.getElementById("chat-usage");
  var KEY = "midni.chat.v1";
  var busy = false;

  function load() { try { return JSON.parse(localStorage.getItem(KEY) || "[]"); } catch (e) { return []; } }
  function save(h) { try { localStorage.setItem(KEY, JSON.stringify(h)); } catch (e) {} }

  function bubble(role, text) {
    var li = document.createElement("div");
    li.className = "msg msg-" + role;
    var who = document.createElement("div");
    who.className = "msg-who";
    who.textContent = role === "user" ? "나" : "위키 사서";
    var body = document.createElement("div");
    body.className = "msg-body prose prose-tight";
    if (text) body.textContent = text;
    li.appendChild(who); li.appendChild(body);
    log.appendChild(li);
    if (empty) empty.hidden = true;
    log.scrollTop = log.scrollHeight;
    return body;
  }

  function renderMd(el, text) {
    fetch("/api/md", { method: "POST", headers: { "Content-Type": "application/json" },
                       body: JSON.stringify({ text: text }) })
      .then(function (r) { return r.ok ? r.json() : null; })
      .then(function (d) { if (d && d.html) { el.innerHTML = d.html; } })
      .catch(function () { /* 텍스트 그대로 둔다 */ });
  }

  function paintSources(list) {
    srcList.textContent = "";
    if (!list || !list.length) { srcHint.hidden = false; return; }
    srcHint.hidden = true;
    list.forEach(function (s) {
      var li = document.createElement("li");
      li.className = "rail-i src-i";
      var a = document.createElement("a");
      a.href = s.url; a.textContent = s.title; a.className = "src-t";
      var k = document.createElement("span");
      k.className = "chip kind"; k.textContent = s.kind || "";
      li.appendChild(a); li.appendChild(k);
      if (s.cite) { var c = document.createElement("span"); c.className = "src-cite"; c.textContent = s.cite; li.appendChild(c); }
      if (s.background) { var b = document.createElement("span"); b.className = "chip chip-bg"; b.textContent = "미검증 배경 — 근거 아님"; li.appendChild(b); }
      srcList.appendChild(li);
    });
  }

  function paintUsage(u, model) {
    usageEl.textContent = "";
    function row(k, v) {
      var dt = document.createElement("dt"); dt.textContent = k;
      var dd = document.createElement("dd"); dd.textContent = v; dd.className = "num";
      usageEl.appendChild(dt); usageEl.appendChild(dd);
    }
    if (model) row("model", model);
    if (!u) return;
    if (u.input_tokens != null) row("input", String(u.input_tokens));
    if (u.cache_read_input_tokens != null) row("cache read", String(u.cache_read_input_tokens));
    if (u.output_tokens != null) row("output", String(u.output_tokens));
  }

  function restore() {
    var h = load();
    h.forEach(function (m) {
      var el = bubble(m.role, m.content);
      if (m.role === "assistant") renderMd(el, m.content);
    });
  }

  function ask(q) {
    if (busy || !ok) return;
    q = (q || "").trim();
    if (!q) return;
    busy = true; sendBtn.disabled = true; ta.value = "";
    var hist = load();
    bubble("user", q);
    hist.push({ role: "user", content: q });
    save(hist);
    var out = bubble("assistant", "");
    out.classList.add("is-streaming");
    var acc = "";
    paintSources([]); paintUsage(null, null);

    fetch("/api/chat", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question: q, history: hist.slice(0, -1).slice(-12) })
    }).then(function (r) {
      if (!r.ok) {
        return r.json().then(function (d) { throw new Error((d && d.error) || ("HTTP " + r.status)); });
      }
      var reader = r.body.getReader();
      var dec = new TextDecoder();
      var buf = "";
      function pump() {
        return reader.read().then(function (res) {
          if (res.done) return finish();
          buf += dec.decode(res.value, { stream: true });
          var parts = buf.split("\n\n");
          buf = parts.pop();
          parts.forEach(function (p) {
            if (p.indexOf("data: ") !== 0) return;
            var ev;
            try { ev = JSON.parse(p.slice(6)); } catch (e) { return; }
            if (ev.sources) paintSources(ev.sources);
            if (ev.t) { acc += ev.t; out.textContent = acc; log.scrollTop = log.scrollHeight; }
            if (ev.error) { acc += (acc ? "\n\n" : "") + "⚠ " + ev.error; out.textContent = acc; }
            if (ev.done) {
              paintUsage(ev.usage, ev.model);
              if (ev.refusal) acc += "\n\n(모델이 답을 거절했다: " + (ev.refusal.category || "") + ")";
            }
          });
          return pump();
        });
      }
      function finish() {
        out.classList.remove("is-streaming");
        var h = load();
        h.push({ role: "assistant", content: acc });
        save(h);
        renderMd(out, acc);
        busy = false; sendBtn.disabled = false; ta.focus();
      }
      return pump();
    }).catch(function (e) {
      out.classList.remove("is-streaming");
      out.textContent = "⚠ " + (e && e.message ? e.message : "요청 실패");
      busy = false; sendBtn.disabled = false;
    });
  }

  form.addEventListener("submit", function (e) { e.preventDefault(); ask(ta.value); });
  ta.addEventListener("keydown", function (e) {
    if (e.key === "Enter" && !e.shiftKey && !e.isComposing) { e.preventDefault(); ask(ta.value); }
  });
  Array.prototype.forEach.call(document.querySelectorAll(".chat-starter"), function (b) {
    b.addEventListener("click", function () { ta.value = b.getAttribute("data-q"); ta.focus(); if (ok) ask(ta.value); });
  });
  document.getElementById("chat-new").addEventListener("click", function () {
    if (!confirm("이 브라우저의 대화 기록을 지우고 새로 시작할까?")) return;
    save([]); log.querySelectorAll(".msg").forEach(function (m) { m.remove(); });
    if (empty) empty.hidden = false; paintSources([]); paintUsage(null, null);
  });
  document.getElementById("chat-export").addEventListener("click", function () {
    var h = load();
    if (!h.length) { alert("아직 대화가 없다."); return; }
    var out = ["# 위키와 대화 — 내보내기", "",
               "이 파일은 **브라우저에 있던 대화**를 내보낸 것이다. 답은 위키의 사본이며 인용 근거가 아니다.", ""];
    h.forEach(function (m) { out.push("## " + (m.role === "user" ? "나" : "위키 사서"), "", m.content, ""); });
    var blob = new Blob([out.join("\n")], { type: "text/markdown;charset=utf-8" });
    var url = URL.createObjectURL(blob);
    var a = document.createElement("a");
    a.href = url; a.download = "midni-chat-" + new Date().toISOString().slice(0, 10) + ".md";
    document.body.appendChild(a); a.click(); a.remove();
    window.setTimeout(function () { URL.revokeObjectURL(url); }, 1000);
  });

  restore();
})();
