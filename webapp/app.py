"""app.py — mid-Ni NCA721 formation 연구 위키 대시보드 (로컬 · 읽기 전용 + 위키 근거 대화 + 셀 요약).

무엇을 서빙하나
  wiki/ (색인·로그·논문 노트+digest·메커니즘·프로토콜·실험·질문·개념·프로젝트·가이드…) · 논문 비교표(`paper:`
  블록 + 내 DOE 겹침) · 연구 로드맵 · /cells (registry + import 요약 + cut-off 별 색 차트) · /chat (위키 절을
  근거로 Claude 와 대화 — 서버는 아무것도 저장하지 않는다).

무엇을 안 하나
  위키·데이터 쓰기. 코멘트·이름변경·업로드·하이라이트 저장이 없다. `_guard_mutation` 이 GET/HEAD/OPTIONS 외
  메서드를 막고, 예외는 `/api/chat`·`/api/md` (둘 다 파일을 쓰지 않는 POST) 뿐이다.

띄우기:  webapp/midni.sh   또는   python3 webapp/app.py   (기본 http://127.0.0.1:5100)
"""
from __future__ import annotations

import os

from flask import (Flask, Response, abort, jsonify, render_template, request,
                   send_from_directory, stream_with_context)
from markupsafe import Markup

import cells as CELLS
import chat as CH
import content as C

app = Flask(__name__)

# 템플릿·정적파일을 매 요청마다 다시 읽는다 (debug=False 로 뜨므로 명시해야 한다 — 선행 브랜치에서
# "고쳤는데 똑같다" 를 한 라운드 낭비한 함정). config 는 jinja_env 접근 전에.
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0
app.config["MAX_CONTENT_LENGTH"] = 512 * 1024      # /api/chat 본문 상한 (대화 기록 포함)

app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True

HOST = os.environ.get("WEBAPP_HOST", "127.0.0.1")
PORT = int(os.environ.get("WEBAPP_PORT", "5100"))

_SAFE_METHODS = {"GET", "HEAD", "OPTIONS"}
# 쓰기 메서드를 받는 유일한 길 — 둘 다 저장소에 아무것도 쓰지 않는다.
_POST_ALLOWED = {"/api/chat", "/api/md"}


@app.before_request
def _guard_mutation():
    """읽기 전용 게이트 — 허용 목록 밖의 쓰기 메서드는 라우트에 닿기 전에 거절 (fail-closed)."""
    if request.method in _SAFE_METHODS:
        return None
    if request.method == "POST" and request.path in _POST_ALLOWED:
        return None
    return jsonify({
        "error": "읽기 전용 앱입니다 — 쓰기 메서드를 받지 않습니다.",
        "why": "wiki/raw/ 는 sha256 봉인 불변층이고 컴파일 페이지·registry 의 정본은 저장소 파일입니다. "
               "예외는 /api/chat 과 /api/md 뿐이며 둘 다 파일을 쓰지 않습니다.",
        "method": request.method,
    }), 405


@app.after_request
def _sec_headers(resp):
    resp.headers.setdefault("X-Content-Type-Options", "nosniff")
    resp.headers.setdefault("Referrer-Policy", "same-origin")
    resp.headers.setdefault("X-Frame-Options", "SAMEORIGIN")
    # 브라우저는 이 서버와만 이야기한다. Anthropic API 호출은 서버 쪽(chat.py)에서만.
    resp.headers.setdefault(
        "Content-Security-Policy",
        "default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; "
        "script-src 'self'; connect-src 'self'; form-action 'self'; base-uri 'none'; "
        "frame-ancestors 'self'")
    return resp


def _asset_version() -> str:
    try:
        paths = []
        for sub in ("css", "js"):
            d = os.path.join(app.static_folder, sub)
            if os.path.isdir(d):
                paths += [os.path.join(d, f) for f in os.listdir(d)]
        return str(int(max(os.path.getmtime(p) for p in paths)))
    except (OSError, ValueError):
        return "1"


@app.template_filter("mdi")
def _mdi(s):
    return Markup(C.md_inline(s, C.page_index()))


@app.context_processor
def _inject():
    return {"asset_version": _asset_version(), "wl_index": C.page_index(),
            "chat_status": CH.available(), "cells_ok": CELLS.available()}


def _page_or_404(kind: str, slug: str) -> dict:
    p = C.scan_pages().get(slug)
    if not p or p["kind"] != kind:
        abort(404)
    return p


def _read(p: dict) -> tuple[dict, str]:
    text = p["path"].read_text(encoding="utf-8")
    return C.split_frontmatter(text)


# ─────────────────────────────────────────────────────────────────────────
# 홈 · 로드맵
# ─────────────────────────────────────────────────────────────────────────
@app.route("/")
def home():
    pages = C.scan_pages()
    idx_file = C.WIKI / "index.md"
    idx_html = C.render_body(idx_file.read_text(encoding="utf-8")) if idx_file.is_file() else ""
    counts: dict[str, int] = {}
    for p in pages.values():
        counts[p["kind"]] = counts.get(p["kind"], 0) + 1
    questions = sorted([p for p in pages.values() if p["kind"] == "question"],
                       key=lambda x: x["updated"], reverse=True)
    n_papers = len({p["slug"] for p in pages.values() if p["kind"] in ("paper", "paper-note")})
    return render_template("index.html", active="home", index_html=idx_html, log=C.recent_log(8),
                           counts=counts, total=len([p for p in pages.values() if p["dir"] != "raw/papers"]),
                           n_papers=n_papers, questions=questions[:4], cfg=C.config())


@app.route("/roadmap")
def roadmap():
    """연구 한 장 — 처음 온 사람(또는 미래의 나)을 위한 화면.

    ⚠ 숫자를 새로 만들지 않는다. 셀 조건·DOE 창은 `config/cells.yaml` (사용자 진술의 사본, 정본은 실험 노트·
      registry)에서 읽고, 페이지 카운트만 실물을 센다. 실험 수치는 화면에 없다.
    """
    pages = C.scan_pages()
    return render_template("roadmap.html", active="roadmap", cfg=C.config(),
                           ents=C.by_kind("entity", pages), qs=C.by_kind("question", pages),
                           mechs=sorted(C.by_kind("mechanism", pages), key=lambda p: p["slug"]),
                           protos=sorted(C.by_kind("protocol", pages), key=lambda p: p["slug"]),
                           papers=C.papers_list(), n_concepts=len(C.by_kind("concept", pages)))


# ─────────────────────────────────────────────────────────────────────────
# 논문 (노트 + digest) · 비교표
# ─────────────────────────────────────────────────────────────────────────
_FAVICON = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">'
    '<rect width="32" height="32" rx="7" fill="#175d8d"/>'
    '<text x="16" y="21.5" font-family="Helvetica,Arial,sans-serif" font-size="13" font-weight="700"'
    ' text-anchor="middle" fill="#fff">Ni</text></svg>')


@app.route("/favicon.svg")
def favicon():
    return Response(_FAVICON, mimetype="image/svg+xml")


@app.route("/papers")
def papers():
    return render_template("papers.html", active="papers", items=C.papers_list(), cfg=C.config())


@app.route("/paper/<slug>")
def paper(slug):
    """논문 한 편 = 노트(papers/, `paper:` 스키마) + digest(raw/papers/, 봉인). 둘 중 하나만 있어도 뜬다."""
    pages = C.scan_pages()
    note = C.note_for(slug, pages)
    dig = C.digest_for(slug, pages)
    if not note and not dig:
        abort(404)
    block = (note["meta"].get("paper") if note and isinstance(note["meta"].get("paper"), dict) else {}) or {}
    note_html, note_toc = "", []
    if note:
        nmeta, nbody = _read(note)
        d = C.render_digest(nbody, title=note["title"], prefix="note")
        note_html, note_toc = d["html"], d["toc"]
    body_html, toc, claims, dmeta = "", [], {}, {}
    if dig:
        dmeta, dbody = _read(dig)
        d = C.render_digest(dbody, title=dmeta.get("title") or dig["title"], prefix="h")
        body_html, toc, claims = d["html"], d["toc"], d["claims"]
    figs = C.figures_for(slug)
    cmp_cells = C.flatten_paper(block) if block else {}
    cmp_rows = [(h, cmp_cells.get(k, "")) for k, h, _d, _g in C.COMPARE_COLUMNS if cmp_cells.get(k)]
    return render_template("paper.html", active="papers", page=(note or dig), note=note, digest=dig,
                           meta=(note["meta"] if note else dmeta), dmeta=dmeta, block=block,
                           note_html=note_html, note_toc=note_toc,
                           body_html=body_html, toc=toc, claims=claims,
                           figs=figs, figmeta=C.figure_meta(slug), cmp_rows=cmp_rows,
                           flags=C.doe_flags(block) if block else None,
                           sha=str(dmeta.get("sha256") or ""), cfg=C.config())


@app.route("/compare")
def compare():
    return render_template("compare.html", active="compare", rows=C.compare_rows(),
                           columns=C.COMPARE_COLUMNS, cfg=C.config())


# ─────────────────────────────────────────────────────────────────────────
# 종류별 목록 + 문서 — mechanisms · protocols · experiments · concepts · entities
# ─────────────────────────────────────────────────────────────────────────
_LISTS = {
    # url 조각: (kind, active, 제목, eyebrow, lead)
    "mechanisms": ("mechanism", "mechanisms", "열화 메커니즘",
                   "wiki/mechanisms/ · 한 축에 한 페이지",
                   "CEI · LPSCl 산화 분해 · Ni/Co/O redox·산소 방출 · H2–H3 판별 · mid- vs high-Ni · healing · 세 계면. "
                   "지금은 전부 <b>미검증 배경</b>이다 — 논문이 들어오면 각 페이지의 '근거 상태' 가 채워진다."),
    "protocols": ("protocol", "protocols", "프로토콜",
                  "wiki/protocols/ · 사용자 진술의 사본",
                  "formation · 셀 제작 · main cycle · 보조 측정. 정본은 실험 노트와 registry 이며 여기 값은 사본이다."),
    "experiments": ("experiment", "experiments", "실험",
                    "wiki/experiments/ · DOE 와 registry",
                    "formation cut-off DOE 설계와 cell registry 규칙. 셀 데이터 자체는 <a href=\"/cells\">셀 데이터</a> 에서."),
    "concepts": ("concept", "concepts", "개념·규약",
                 "wiki/concepts/",
                 "전압 기준전극·용량 단위·충방전 용어 규약과 NCA721 표기 규칙 — 절대 규칙의 실무판."),
    "entities": ("entity", "entities", "프로젝트",
                 "wiki/entities/ · satellite",
                 "실험 프로젝트의 상태 카드. 상세 수치의 정본은 <code>data/</code> 이며 이 카드는 living reference 다."),
}
_DOC_KIND_URL = {"mechanism": "mechanism", "protocol": "protocol", "experiment": "experiment",
                 "concept": "concept", "entity": "entity"}


def _list_view(name):
    kind, active, title, eyebrow, lead = _LISTS[name]
    items = C.by_kind(kind)
    if kind in ("mechanism", "protocol"):
        items.sort(key=lambda p: p["slug"])
    return render_template("list.html", active=active, kind=kind, kind_label=C.KIND_LABEL.get(kind, kind),
                           title=title, eyebrow=eyebrow, lead=Markup(lead), items=items)


def _doc_view(kind, slug):
    p = _page_or_404(kind, slug)
    meta, body = _read(p)
    d = C.render_digest(body, title=meta.get("title") or p["title"])
    active = {"mechanism": "mechanisms", "protocol": "protocols", "experiment": "experiments",
              "concept": "concepts", "entity": "entities"}.get(kind, "")
    ours = meta.get("ours") if isinstance(meta.get("ours"), dict) else None
    ours_rows = []
    if ours:
        cells = C.flatten_paper(ours)
        ours_rows = [(h, cells.get(k, "")) for k, h, _d, _g in C.COMPARE_COLUMNS if cells.get(k)]
    return render_template("doc.html", active=active, page=p, meta=meta, body_html=d["html"], toc=d["toc"],
                           claims=d["claims"], ours_rows=ours_rows)


for _name in _LISTS:
    app.add_url_rule(f"/{_name}", f"list_{_name}", (lambda n: (lambda: _list_view(n)))(_name))
for _kind, _seg in _DOC_KIND_URL.items():
    app.add_url_rule(f"/{_seg}/<slug>", f"doc_{_kind}", (lambda k: (lambda slug: _doc_view(k, slug)))(_kind))


@app.route("/doc/<path:rel>")
def doc(rel):
    """guides · queries · syntheses · comparisons · raw/transcripts 등 — 등록부에서만 찾는다 (경로 탈출 불가)."""
    slug = rel.rstrip("/").split("/")[-1]
    pages = C.scan_pages()
    p = pages.get(slug) if not rel.startswith("raw/papers/") else pages.get("raw/papers/" + slug)
    if not p or p["url"] != "/doc/" + rel.strip("/"):
        abort(404)
    meta, body = _read(p)
    d = C.render_digest(body, title=meta.get("title") or p["title"])
    active = {"comparison": "compare"}.get(p["kind"], "")
    return render_template("doc.html", active=active, page=p, meta=meta, body_html=d["html"], toc=d["toc"],
                           claims=d["claims"], ours_rows=[])


# ─────────────────────────────────────────────────────────────────────────
# 질문 카드
# ─────────────────────────────────────────────────────────────────────────
@app.route("/questions")
def questions():
    items = []
    for p in C.scan_pages().values():
        if p["kind"] != "question":
            continue
        _meta, body = _read(p)
        secs = C.split_sections(body)
        kinds = {C.classify_section(s["title"]) for s in secs}
        items.append({**p, "has": kinds,
                      "nfor": sum(1 for s in secs if C.classify_section(s["title"]) == "for"),
                      "nagainst": sum(1 for s in secs if C.classify_section(s["title"]) == "against")})
    items.sort(key=lambda x: (x["updated"], x["slug"]), reverse=True)
    return render_template("questions.html", active="questions", items=items)


@app.route("/question/<slug>")
def question(slug):
    p = _page_or_404("question", slug)
    meta, body = _read(p)
    idx = C.page_index()
    secs = []
    for n, s in enumerate(C.split_sections(body), 1):
        secs.append({"title": s["title"], "cls": C.classify_section(s["title"]), "raw": s["body"], "id": f"s-{n}"})
    blocks, i = [], 0
    while i < len(secs):
        s = secs[i]
        nxt = secs[i + 1] if i + 1 < len(secs) else None
        if s["cls"] == "for" and nxt and nxt["cls"] == "against":
            blocks.append({"kind": "duel", "sides": [{**side, "html": C.render_body(side["raw"], idx)} for side in (s, nxt)]})
            i += 2
            continue
        if s["cls"] == "log":
            entries = C.parse_log_entries(s["raw"])
            if entries:
                blocks.append({"kind": "timeline", "title": s["title"], "cls": s["cls"], "id": s["id"],
                               "entries": [{**e, "html": C.render_body(e["body"], idx)} for e in entries]})
                i += 1
                continue
        blocks.append({"kind": "sec", **s, "html": C.render_body(s["raw"], idx)})
        i += 1
    nav = [{"id": s["id"], "title": s["title"], "cls": s["cls"]} for s in secs if s["title"]]
    return render_template("question.html", active="questions", page=p, meta=meta, blocks=blocks, nav=nav)


# ─────────────────────────────────────────────────────────────────────────
# 셀 데이터 (prototype: registry + import 요약 + 차트)
# ─────────────────────────────────────────────────────────────────────────
@app.route("/cells")
def cells():
    return render_template("cells.html", active="cells", ov=CELLS.overview())


@app.route("/cell/<cell_id>")
def cell(cell_id):
    d = CELLS.detail(cell_id)
    if not d:
        abort(404)
    return render_template("cell.html", active="cells", c=d)


@app.route("/api/cells.json")
def api_cells():
    ov = CELLS.overview()
    return jsonify({"ok": ov["ok"], "n": ov["n"], "by_cutoff": ov["by_cutoff"],
                    "cells": [{"cell_id": r["cell_id"], "formation_cutoff_v_li": r.get("formation_cutoff_v_li"),
                               "status": r.get("status"), "summary": r.get("summary")} for r in ov["rows"]]})


# ─────────────────────────────────────────────────────────────────────────
# 대화 — 위키 근거로 Claude 와
# ─────────────────────────────────────────────────────────────────────────
@app.route("/chat")
def chat():
    pages = C.scan_pages()
    starters = [
        "formation cut-off 3.6 V 와 4.6 V vs. Li/Li⁺ 가 CEI 형성에 주는 차이를 위키 근거로 정리해 줘. 근거가 없는 부분은 DB 외로 표시해 줘.",
        "우리 셀(NCA721 | LPSCl | Li-In, 100 MPa, 45 °C) 과 DB 의 논문들을 비교할 때 먼저 짚어야 할 조건 차이는?",
        "장비에서 3.78 V vs. In/Li-In 로 끊었다면 vs. Li/Li⁺ 로 몇 V 인가? 변환 방향을 설명해 줘.",
        "LPSCl 산화 분해 산물이 전압대별로 무엇인지 DB 에 근거가 있는가? 없다면 어떤 논문이 필요한가?",
        "H2–H3 상전이를 우리 데이터(dQ/dV)에서 어떻게 판별할지 절차를 제안해 줘. 'hysteresis' 는 어떻게 발음하나?",
    ]
    return render_template("chat.html", active="chat", status=CH.available(), n_pages=len(pages), starters=starters)


@app.route("/api/chat", methods=["POST"])
def api_chat():
    """SSE 스트림. 본문 {question, history:[{role, content}]}. 서버는 아무것도 저장하지 않는다."""
    data = request.get_json(silent=True) or {}
    q = str(data.get("question") or "").strip()
    if not q:
        return jsonify({"error": "질문이 비어 있다."}), 400
    if len(q) > 8000:
        return jsonify({"error": "질문이 너무 길다 (8000자 상한)."}), 400
    history = data.get("history") or []
    if not isinstance(history, list):
        history = []
    st = CH.available()
    if not st["ok"]:
        return jsonify({"error": "chat 비활성 — ANTHROPIC_API_KEY 가 없거나 SDK 가 없다.", "status": st}), 503
    gen = CH.stream_answer(q, history)
    return Response(stream_with_context(gen), mimetype="text/event-stream",
                    headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


@app.route("/api/chat/status")
def api_chat_status():
    return jsonify(CH.available())


@app.route("/api/md", methods=["POST"])
def api_md():
    """마크다운 → 우리 렌더러(raw HTML 차단 + wikilink) 로 HTML. chat 답변 표시용. 저장 없음."""
    data = request.get_json(silent=True) or {}
    text = str(data.get("text") or "")
    if len(text) > 200_000:
        return jsonify({"error": "too long"}), 400
    return jsonify({"html": C.render_body(text)})


# ─────────────────────────────────────────────────────────────────────────
# 메모 · 검색 · API
# ─────────────────────────────────────────────────────────────────────────
@app.route("/notes")
def notes():
    docs = {}
    for p in C.scan_pages().values():
        docs[p["slug"]] = {"t": p["title"], "u": p["url"]}
    return render_template("notes.html", active="notes", docs=docs)


@app.route("/search")
def search():
    q = request.args.get("q", "")
    return render_template("search.html", active="search", q=q, hits=C.search(q))


@app.route("/api/figures/<slug>.json")
def api_figures(slug):
    return jsonify({"slug": slug, "figures": C.figures_for(slug)})


@app.route("/api/palette.json")
def api_palette():
    items = [
        {"t": "홈 · 카탈로그", "u": "/", "k": "화면", "d": "wiki/index.md + 최근 활동"},
        {"t": "연구 로드맵", "u": "/roadmap", "k": "화면", "d": "NCA721 formation cut-off DOE 한 장"},
        {"t": "논문", "u": "/papers", "k": "화면", "d": "wiki/papers/ 노트 + raw/papers/ digest"},
        {"t": "논문 비교표", "u": "/compare", "k": "화면", "d": "paper: 블록 · 내 DOE 겹침"},
        {"t": "열화 메커니즘", "u": "/mechanisms", "k": "화면", "d": "wiki/mechanisms/"},
        {"t": "프로토콜", "u": "/protocols", "k": "화면", "d": "wiki/protocols/"},
        {"t": "실험", "u": "/experiments", "k": "화면", "d": "wiki/experiments/"},
        {"t": "열린 질문", "u": "/questions", "k": "화면", "d": "wiki/questions/"},
        {"t": "개념·규약", "u": "/concepts", "k": "화면", "d": "wiki/concepts/"},
        {"t": "프로젝트", "u": "/entities", "k": "화면", "d": "wiki/entities/"},
        {"t": "셀 데이터", "u": "/cells", "k": "화면", "d": "registry + import 요약 + cut-off 색 차트"},
        {"t": "위키와 대화", "u": "/chat", "k": "화면", "d": "위키 절을 근거로 Claude 와"},
        {"t": "검색", "u": "/search", "k": "화면", "d": "전문 부분 문자열 검색"},
    ]
    for p in C.scan_pages().values():
        items.append({"t": p["title"], "u": p["url"], "k": p["kind_label"], "d": p["description"] or p["relpath"], "s": p["slug"]})
    return jsonify({"items": items})


@app.route("/api/file/<path:rel>")
def api_file(rel):
    """`wiki/raw/figures/<slug>/<file>` 만 서빙 (그 밖은 404)."""
    p = C.safe_file(rel)
    if p is None:
        abort(404)
    return send_from_directory(p.parent, p.name, as_attachment=bool(request.args.get("dl")), download_name=p.name)


@app.errorhandler(404)
def _404(e):
    return render_template("404.html", active=""), 404


if __name__ == "__main__":
    print(f"  repo root : {C.ROOT}")
    print(f"  serving   : http://{HOST}:{PORT}  (읽기 전용 · chat={'on' if CH.available()['ok'] else 'off'} · cells={'on' if CELLS.available() else 'off'})")
    app.run(host=HOST, port=PORT, debug=False, threaded=True)
