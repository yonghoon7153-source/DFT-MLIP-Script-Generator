"""content.py — 위키(`wiki/`)의 마크다운·그림을 읽어 화면용 자료구조로 만든다.

이 모듈은 **읽기만** 한다. 쓰기 함수는 없다 (없는 게 설계다 — README "왜 읽기 전용인가").
`wiki/raw/` 는 sha256 으로 봉인된 불변층이고, 컴파일 페이지의 정본은 저장소 파일이다.

선행 브랜치 webapp/content.py 에서 가져온 것: 경로 탈출 차단(허용 뿌리 + resolve +
is_relative_to), 마크다운 raw HTML 차단 + href/src scheme 재검사, 우리가 만드는 제목 id,
3구분 표기 클래스, 질문 카드 절 분류, 그림 색인 키 정규화, 부분 문자열 검색.
이 저장소에서 더한 것: `[재현]` 4번째 표기, digest `compare:` 표(`compare_rows`),
/chat 용 근거 검색(`chat_context`).
버린 것: Phase/CSV/게이트 원장/스윕 차트 (열화 프로젝트 전용).
"""
from __future__ import annotations

import html as _html
import json
import re
from pathlib import Path

try:
    import yaml
except Exception:  # PyYAML 이 없어도 앱은 뜬다 (frontmatter 만 얕게 읽는다)
    yaml = None

try:
    import markdown as _md
except Exception:
    _md = None

ROOT = Path(__file__).resolve().parent.parent          # 저장소 루트
WIKI = ROOT / "wiki"
FIGROOT = WIKI / "raw" / "figures"

# /api/file 이 열어 주는 뿌리. 이 밖은 404 — 저장소 안이어도 안 준다.
_FILE_ROOTS = (WIKI / "raw" / "figures",)


# ─────────────────────────────────────────────────────────────────────────
# 경로 안전
# ─────────────────────────────────────────────────────────────────────────
def safe_file(rel: str) -> Path | None:
    """허용 뿌리 안의 **파일**만 돌려준다. 경로 탈출·심볼릭 탈출 차단."""
    rel = (rel or "").lstrip("/")
    if not rel or "\x00" in rel:
        return None
    for base in _FILE_ROOTS:
        try:
            p = (base / rel).resolve()
            b = base.resolve()
        except OSError:
            continue
        if p.is_relative_to(b) and p.is_file():
            return p
    return None


# ─────────────────────────────────────────────────────────────────────────
# frontmatter + 마크다운
# ─────────────────────────────────────────────────────────────────────────
_FM_RE = re.compile(r"\A---\r?\n(.*?)\r?\n---\r?\n?", re.S)


def split_frontmatter(text: str) -> tuple[dict, str]:
    m = _FM_RE.match(text or "")
    if not m:
        return {}, text or ""
    raw, body = m.group(1), (text or "")[m.end():]
    meta: dict = {}
    if yaml is not None:
        try:
            got = yaml.safe_load(raw)
            if isinstance(got, dict):
                meta = got
        except Exception:
            meta = {}
    if not meta:                                    # PyYAML 없거나 파싱 실패 시 얕은 파서
        for line in raw.splitlines():
            if ":" not in line or line.lstrip().startswith("#"):
                continue
            k, _, v = line.partition(":")
            meta[k.strip()] = v.strip().strip('"').strip("'")
    return meta, body


# 마크다운 파서에서 raw HTML 을 끄고, 그 뒤 URL scheme 을 한 번 더 거른다.
_URL_ATTR = re.compile(r"""(?P<a>\b(?:href|src)\s*=\s*)(?P<q>["'])(?P<v>[^"']*)(?P=q)""", re.I)
_URL_OK = re.compile(r"""^\s*(?:https?:|mailto:|/|\#|\./|\.\./|[^:]*$)""", re.I)


def _sanitize_urls(html: str) -> str:
    def _fix(m):
        v = (m.group("v") or "").strip()
        plain = _html.unescape(v).replace("\t", "").replace("\n", "").replace("\r", "")
        if _URL_OK.match(plain):
            return m.group(0)
        return f'{m.group("a")}{m.group("q")}#blocked-url{m.group("q")} data-blocked-url="1"'
    return _URL_ATTR.sub(_fix, html)


def md_html(text: str) -> str:
    """마크다운 → HTML. raw HTML 통과는 끈다 + href/src 를 허용 scheme 만 통과."""
    if _md is None:
        return "<pre>" + _html.escape(text or "") + "</pre>"
    md = _md.Markdown(extensions=["tables", "fenced_code", "sane_lists"])
    for name in ("html_block",):
        try:
            md.preprocessors.deregister(name)
        except (KeyError, ValueError):
            pass
    for name in ("html", "raw_html"):
        try:
            md.inlinePatterns.deregister(name)
        except (KeyError, ValueError):
            pass
    return _sanitize_urls(md.convert(text or ""))


# ─────────────────────────────────────────────────────────────────────────
# 페이지 등록부 (wikilink 해석의 정본)
# ─────────────────────────────────────────────────────────────────────────
_DIRS: dict[str, tuple[str, str]] = {
    "entities": ("entity", "/entity/"),
    "concepts": ("concept", "/concept/"),
    "questions": ("question", "/question/"),
    "guides": ("guide", "/doc/guides/"),
    "queries": ("query", "/doc/queries/"),
    "syntheses": ("synthesis", "/doc/syntheses/"),
    "comparisons": ("comparison", "/doc/comparisons/"),
    "raw/papers": ("paper", "/paper/"),
    "raw/transcripts": ("transcript", "/doc/raw/transcripts/"),
    "raw/articles": ("article", "/doc/raw/articles/"),
    "raw/repositories": ("repository", "/doc/raw/repositories/"),
}
_SKIP_NAMES = {"README", "SCHEMA", "CLAUDE", "AGENTS", "index", "log"}

KIND_LABEL = {
    "entity": "프로젝트", "concept": "개념", "question": "열린 질문", "guide": "절차",
    "query": "질의·발표", "synthesis": "종합", "comparison": "비교", "paper": "논문 digest",
    "transcript": "세션 기록", "article": "글", "repository": "저장소 감사",
}


def _mtime(p: Path) -> float:
    try:
        return p.stat().st_mtime
    except OSError:
        return 0.0


def scan_pages() -> dict[str, dict]:
    """`wiki/` 를 훑어 slug → 페이지 메타 사전을 만든다. 요청마다 다시 훑는다 (파일이 정본)."""
    pages: dict[str, dict] = {}
    for rel, (kind, prefix) in _DIRS.items():
        d = WIKI / rel
        if not d.is_dir():
            continue
        for f in sorted(d.glob("*.md")):
            if f.stem in _SKIP_NAMES:
                continue
            try:
                text = f.read_text(encoding="utf-8")
            except OSError:
                continue
            meta, _body = split_frontmatter(text)
            slug = f.stem
            pages[slug] = {
                "slug": slug,
                "kind": kind,
                "kind_label": KIND_LABEL.get(kind, kind),
                "dir": rel,
                "path": f,
                "relpath": f.relative_to(ROOT).as_posix(),
                "url": prefix + slug,
                "meta": meta,
                "title": str(meta.get("title") or _first_h1(_body) or slug),
                "description": str(meta.get("description") or ""),
                "updated": str(meta.get("updated") or meta.get("ingested") or meta.get("created") or ""),
                "mtime": _mtime(f),
                "bytes": f.stat().st_size if f.exists() else 0,
            }
    return pages


_BODY_H1 = re.compile(r"^\s*#\s+(.+?)\s*$", re.M)


def _first_h1(body: str) -> str:
    m = _BODY_H1.search(body or "")
    return m.group(1).strip() if m else ""


def page_index() -> dict[str, str]:
    """wikilink 해석용 slug → URL. `raw/papers/foo` 같은 경로 표기도 받는다."""
    idx = {}
    for slug, p in scan_pages().items():
        idx[slug] = p["url"]
        idx[f'{p["dir"]}/{slug}'] = p["url"]
        idx[f'{p["dir"]}/{slug}.md'] = p["url"]
    return idx


# ─────────────────────────────────────────────────────────────────────────
# wikilink
# ─────────────────────────────────────────────────────────────────────────
_WL = re.compile(r"\[\[([^\[\]|]+?)(?:\|([^\[\]]+?))?\]\]")
_FENCE = re.compile(r"(^```.*?^```|^~~~.*?^~~~)", re.S | re.M)
_CODESPAN = re.compile(r"(`+)(?:.|\n)*?\1")


def linkify_wikilinks(text: str, index: dict[str, str]) -> str:
    """`[[slug]]` · `[[slug|label]]` → 마크다운 링크. 코드는 건드리지 않는다."""
    stash: list[str] = []

    def _hide(m):
        stash.append(m.group(0))
        return "\x00%d\x00" % (len(stash) - 1)

    s = _FENCE.sub(_hide, text or "")
    s = _CODESPAN.sub(_hide, s)

    def _sub(m):
        target = (m.group(1) or "").strip()
        label = (m.group(2) or target).strip()
        url = index.get(target) or index.get(target.lower())
        if not url:
            return f"<<WLMISS:{label}>>"
        return f"[{label}]({url})"

    s = _WL.sub(_sub, s)
    s = re.sub(r"\x00(\d+)\x00", lambda m: stash[int(m.group(1))], s)
    return s


_WLMISS = re.compile(r"(?:&lt;|<){2}WLMISS:(.*?)(?:&gt;|>){2}")


def render_body(text: str, index: dict[str, str] | None = None) -> str:
    idx = page_index() if index is None else index
    html = md_html(linkify_wikilinks(text, idx))

    def _miss(m):
        label = _html.escape(_html.unescape(m.group(1)))
        return f'<span class="wl-missing" title="이 위키에 없는 페이지">{label}</span>'
    return _WLMISS.sub(_miss, html)


# ─────────────────────────────────────────────────────────────────────────
# 한 줄 markdown (표 칸·설명문) — escape 먼저, 우리 태그만 되살린다
# ─────────────────────────────────────────────────────────────────────────
_MD_CODE = re.compile(r"`([^`\n]+)`")
_MD_BOLD = re.compile(r"\*\*(?!\s)([^*\n]+?)(?<!\s)\*\*")
_MD_ITAL = re.compile(r"(?<![\w*])\*(?!\s)([^*\n]+?)(?<!\s)\*(?![\w*])")
_MD_LINK = re.compile(r"\[([^\]\n]+)\]\((https?://[^\s)]+|/[^\s)]*)\)")


def md_inline(s) -> str:
    if s is None or s == "":
        return ""
    out = _html.escape(str(s), quote=False)
    holes: list[str] = []

    def _stash(m):
        holes.append(m.group(1))
        return f"\x00{len(holes) - 1}\x00"

    out = _MD_CODE.sub(_stash, out)
    out = _MD_LINK.sub(lambda m: f'<a href="{m.group(2)}">{m.group(1)}</a>', out)
    out = _MD_BOLD.sub(r"<strong>\1</strong>", out)
    out = _MD_ITAL.sub(r"<em>\1</em>", out)
    for i, code in enumerate(holes):
        out = out.replace(f"\x00{i}\x00", f"<code>{code}</code>")
    return out


_SAFE_ID = re.compile(r"[^a-z0-9]+")


def slug_id(name: str, fallback: str = "h") -> str:
    s = _SAFE_ID.sub("-", (name or "").lower()).strip("-")
    return s or fallback


# ─────────────────────────────────────────────────────────────────────────
# 제목 앵커 + 목차 — id 는 우리가 만든다 (h-1, h-2 …)
# ─────────────────────────────────────────────────────────────────────────
_HTAG = re.compile(r"<h([1-4])>(.*?)</h\1>", re.S)
_TAGSTRIP = re.compile(r"<[^>]+>")


def anchor_headings(html: str, levels=(2, 3), prefix: str = "h") -> tuple[str, list[dict]]:
    pre = slug_id(prefix, "h")
    toc: list[dict] = []
    n = 0

    def _sub(m):
        nonlocal n
        lvl, inner = int(m.group(1)), m.group(2)
        if lvl not in levels:
            return m.group(0)
        n += 1
        hid = f"{pre}-{n}"
        text = _html.unescape(_TAGSTRIP.sub("", inner)).strip()
        toc.append({"id": hid, "level": lvl, "text": text})
        return f'<h{lvl} id="{hid}" class="anchored">{inner}'\
               f'<a class="hanchor" href="#{hid}" aria-label="이 절 링크">#</a></h{lvl}>'

    return _HTAG.sub(_sub, html), toc


# ─────────────────────────────────────────────────────────────────────────
# digest 의 4구분 표기 — 원문 주장과 우리 판단을 화면에서 갈라 보인다
# ─────────────────────────────────────────────────────────────────────────
# `[인쇄]` 원문에 글자로 있는 것 / `[도표]` 그림에서 눈으로 읽은 근사값 /
# `[해석]` digest 를 쓰며 붙인 판단 / `[재현]` 원문 값을 산술로 옮긴 것 (식 병기).
CLAIM_KINDS = {
    "인쇄": ("printed", "원문에 글자로 인쇄된 것"),
    "도표": ("figure", "그림에서 눈으로 읽은 근사값 — 원 데이터가 아니다"),
    "해석": ("ours", "digest 를 쓰며 붙인 판단 — 논문의 주장이 아니다"),
    "재현": ("repro", "원문 값을 이 위키에서 산술로 옮긴 것 — 계산식 병기"),
}
_CLAIM_LEAD = re.compile(r"(<(?:p|li)\b[^>]*)(>)\s*<code>\[(인쇄|도표|해석|재현)(?:[,，][^\]]*)?\]</code>")
_CLAIM_ANY = re.compile(r"<code>\[(인쇄|도표|해석|재현)((?:[,，][^\]]*)?)\]</code>")


def mark_claims(html: str) -> tuple[str, dict]:
    """4구분 표기에 클래스를 달고 종류별 개수를 센다. `[인쇄, §3.1]` 처럼 좌표가 붙어도 잡는다."""
    counts = {k: 0 for k in CLAIM_KINDS}

    def _lead(m):
        kind = m.group(3)
        cls = CLAIM_KINDS[kind][0]
        return f'{m.group(1)} class="claim claim-{cls}"{m.group(2)}' \
               f'<code class="ctag ct-{cls}" title="{CLAIM_KINDS[kind][1]}">[{kind}]</code>'

    out = _CLAIM_LEAD.sub(_lead, html)

    def _any(m):
        kind, rest = m.group(1), m.group(2) or ""
        cls = CLAIM_KINDS[kind][0]
        counts[kind] += 1
        return f'<code class="ctag ct-{cls}" title="{CLAIM_KINDS[kind][1]}">[{kind}{_html.escape(rest)}]</code>'

    out = _CLAIM_ANY.sub(_any, out)
    for kind in counts:
        counts[kind] += out.count(f'class="claim claim-{CLAIM_KINDS[kind][0]}"')
    return out, counts


_LEAD_H1 = re.compile(r"\A\s*<h1[^>]*>(.*?)</h1>\s*", re.S | re.I)


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "")).strip().lower()


def drop_leading_h1(html: str, title: str = "") -> str:
    m = _LEAD_H1.match(html)
    if not m:
        return html
    inner = re.sub(r"<[^>]+>", "", m.group(1))
    if _norm(inner) != _norm(title):
        return html
    return html[m.end():]


def render_digest(text: str, index: dict[str, str] | None = None,
                  prefix: str = "h", title: str = "") -> dict:
    """본문 + 목차 + 4구분 개수. 한 화면에 두 번 부르면 `prefix` 를 다르게 준다."""
    html = render_body(text, index)
    html = drop_leading_h1(html, title)
    html, counts = mark_claims(html)
    html, toc = anchor_headings(html, prefix=prefix)
    return {"html": html, "toc": toc, "claims": counts}


# ─────────────────────────────────────────────────────────────────────────
# Status Log → 타임라인 · 절 분해 · 질문 카드 절 분류
# ─────────────────────────────────────────────────────────────────────────
_LOG_ITEM = re.compile(r"^-\s+\*{0,2}\[(\d{4}-\d{2}-\d{2})([^\]]*)\]\*{0,2}\s*", re.M)
_LOG_STATE = re.compile(r"^(open|active|answered|parked|closed|abandoned)(\s*유지)?\b", re.I)
_LIST_LINE = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s")


def _dedent_rest(first: str, rest: list[str]) -> str:
    filled = [ln for ln in rest if ln.strip()]
    pad = min((len(ln) - len(ln.lstrip(" ")) for ln in filled), default=0)
    lines = [first] + [ln[pad:] if ln.strip() else "" for ln in rest]
    out: list[str] = []
    for ln in lines:
        if (_LIST_LINE.match(ln) and out and out[-1].strip()
                and not _LIST_LINE.match(out[-1])):
            out.append("")
        out.append(ln)
    return "\n".join(out)


def parse_log_entries(body: str) -> list[dict]:
    marks = list(_LOG_ITEM.finditer(body or ""))
    if not marks:
        return []
    out = []
    for i, m in enumerate(marks):
        end = marks[i + 1].start() if i + 1 < len(marks) else len(body)
        chunk = body[m.end():end].rstrip()
        first, _, rest = chunk.partition("\n")
        text = _dedent_rest(first, rest.split("\n")) if rest else first
        st = _LOG_STATE.match(first.strip())
        out.append({
            "date": m.group(1),
            "suffix": (m.group(2) or "").strip(),
            "state": (st.group(1).lower() if st else ""),
            "held": bool(st and st.group(2)),
            "body": text,
        })
    return out


def split_sections(body: str, level: str = "##") -> list[dict]:
    pat = re.compile(r"^%s\s+(.+?)\s*$" % re.escape(level), re.M)
    marks = list(pat.finditer(body or ""))
    out = []
    if not marks:
        return [{"title": "", "body": body or ""}]
    if marks[0].start() > 0:
        out.append({"title": "", "body": body[: marks[0].start()]})
    for i, m in enumerate(marks):
        end = marks[i + 1].start() if i + 1 < len(marks) else len(body)
        out.append({"title": m.group(1), "body": body[m.end():end]})
    return out


_QCLASS = (
    ("for", re.compile(r"evidence\s*for", re.I)),
    ("against", re.compile(r"evidence\s*against", re.I)),
    ("gap", re.compile(r"\bgap\b|빈 근거", re.I)),
    ("log", re.compile(r"status\s*log", re.I)),
    ("method", re.compile(r"답하는 방법|설계", re.I)),
    ("hypo", re.compile(r"가설|hypothes", re.I)),
)


def classify_section(title: str) -> str:
    for name, rx in _QCLASS:
        if rx.search(title or ""):
            return name
    return "plain"


# ─────────────────────────────────────────────────────────────────────────
# 그림
# ─────────────────────────────────────────────────────────────────────────
def _figkey(kind: str, label: str) -> str:
    """figref.js 의 keyOf 와 같은 규칙: 종류 첫 글자(소문자) + 라벨 대문자."""
    c = (kind or "figure").lower()[:1]
    p = "t" if c == "t" else "s" if c == "s" else "f"
    return p + str(label or "").upper()


def figures_for(slug: str) -> list[dict]:
    d = FIGROOT / slug
    j = d / "figures.json"
    if not j.is_file():
        return []
    try:
        data = json.loads(j.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []
    out = []
    for f in data.get("figures") or []:
        name = str(f.get("file") or "")
        if not name or not (d / name).is_file():
            continue
        kind = str(f.get("kind") or "figure")
        label = str(f.get("label") or "")
        out.append({
            "key": _figkey(kind, label),
            "kind": kind,
            "label": label,
            "title": ("Table " if kind == "table" else "Scheme " if kind == "scheme" else "Fig. ") + label,
            "page": f.get("page"),
            "caption": str(f.get("caption") or ""),
            "rel": f"{slug}/{name}",
            "w": f.get("w"), "h": f.get("h"),
        })
    return out


def figure_meta(slug: str) -> dict:
    j = FIGROOT / slug / "figures.json"
    if not j.is_file():
        return {}
    try:
        d = json.loads(j.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return {k: d.get(k) for k in ("dpi", "maxpx", "generated", "sources", "si_note") if k in d}


# ─────────────────────────────────────────────────────────────────────────
# 위키 로그 / 홈
# ─────────────────────────────────────────────────────────────────────────
_LOG_H = re.compile(r"^##\s+\[(\d{4}-\d{2}-\d{2})\]\s+(\w+)\s*\|\s*(.+?)\s*$", re.M)


def recent_log(limit: int = 12) -> list[dict]:
    p = WIKI / "log.md"
    if not p.is_file():
        return []
    text = p.read_text(encoding="utf-8")
    marks = list(_LOG_H.finditer(text))
    out = []
    for i, m in enumerate(marks):
        end = marks[i + 1].start() if i + 1 < len(marks) else len(text)
        out.append({"date": m.group(1), "action": m.group(2), "subject": m.group(3),
                    "body": text[m.end():end].strip()})
    out.reverse()
    return out[:limit]


# ─────────────────────────────────────────────────────────────────────────
# 논문 비교표 — digest frontmatter `compare:` 가 정본 (SCHEMA 특칙)
# ─────────────────────────────────────────────────────────────────────────
COMPARE_COLUMNS: list[tuple[str, str, str]] = [
    # (key, 표 머리, 짧은 설명)
    ("system", "계", "액체 / ASSB 등"),
    ("electrolyte", "전해질", ""),
    ("cathode", "양극 조성", "활물질:SE:탄소, 바인더"),
    ("li2s_source", "Li2S 출처·입도", ""),
    ("mixing", "혼합·성형", "순서 · 장비 · 압력"),
    ("loading_mg_cm2", "로딩 (mg cm⁻², Li2S)", ""),
    ("li2s_wt_pct", "Li2S wt%", ""),
    ("anode", "음극", ""),
    ("first_charge", "첫 충전 조건", "컷오프 · C-rate"),
    ("first_discharge_mAh_gS", "첫 방전 (S)", "mAh g⁻¹(S)"),
    ("first_discharge_mAh_gLi2S", "첫 방전 (Li2S)", "mAh g⁻¹(Li2S)"),
    ("cycle_capacity_mAh_gS", "사이클 용량 (S)", ""),
    ("cycle_capacity_mAh_gLi2S", "사이클 용량 (Li2S)", ""),
    ("areal_mAh_cm2", "면적용량", "mAh cm⁻²"),
    ("cycles", "사이클 수 · 유지율", ""),
    ("temperature_C", "온도 (°C)", ""),
    ("mechanism", "기전·관측", ""),
    ("our_axis", "우리 축에서", "이식 가능 / 불가"),
]


def compare_rows() -> list[dict]:
    """`compare:` 블록을 가진 페이지(논문 digest + 우리 entity)를 표 행으로.

    값이 없는 칸은 빈 문자열로 둔다 — 물음표를 채우지 않는다 (SCHEMA).
    우리 자신(entity)이 먼저, 그다음 논문을 ingested 최신순.
    """
    rows = []
    for p in scan_pages().values():
        c = p["meta"].get("compare")
        if not isinstance(c, dict):
            continue
        cells = {k: ("" if c.get(k) is None else str(c.get(k))) for k, _h, _d in COMPARE_COLUMNS}
        rows.append({**p, "cells": cells, "is_ours": p["kind"] == "entity",
                     "short": _short_title(p)})
    rows.sort(key=lambda r: (0 if r["is_ours"] else 1, r["updated"] or ""), reverse=False)
    ours = [r for r in rows if r["is_ours"]]
    papers = sorted([r for r in rows if not r["is_ours"]], key=lambda r: r["updated"] or "", reverse=True)
    return ours + papers


_SHORT = re.compile(r"^([A-Za-z\-']+(?:\s+et\s+al\.)?\s+\d{4})")


def _short_title(p: dict) -> str:
    """'Kim et al. 2023 — …' → 'Kim et al. 2023'. 없으면 slug."""
    m = _SHORT.match(p["title"] or "")
    return m.group(1) if m else (p["title"] if len(p["title"]) < 28 else p["slug"])


# ─────────────────────────────────────────────────────────────────────────
# 검색 — 단순 전문(부분 문자열)
# ─────────────────────────────────────────────────────────────────────────
def _corpus() -> list[dict]:
    docs = []
    for slug, p in scan_pages().items():
        docs.append({"title": p["title"], "url": p["url"], "kind": p["kind"],
                     "path": p["relpath"], "file": p["path"], "slug": slug})
    for name in ("index.md", "log.md"):
        f = WIKI / name
        if f.is_file():
            docs.append({"title": f"wiki/{name}", "url": "/", "kind": "wiki",
                         "path": f"wiki/{name}", "file": f, "slug": name})
    return docs


def search(q: str, limit: int = 60) -> list[dict]:
    q = (q or "").strip()
    if len(q) < 2:
        return []
    needle = q.lower()
    hits = []
    for d in _corpus():
        try:
            text = d["file"].read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        low = text.lower()
        n = low.count(needle)
        if not n:
            continue
        snips = []
        start = 0
        for _ in range(min(3, n)):
            i = low.find(needle, start)
            if i < 0:
                break
            a, b = max(0, i - 110), min(len(text), i + len(q) + 110)
            snips.append({"pre": " ".join(text[a:i].split()),
                          "hit": text[i:i + len(q)],
                          "post": " ".join(text[i + len(q):b].split())})
            start = i + len(q)
        hits.append({"title": d["title"], "url": d["url"], "kind": d["kind"],
                     "path": d["path"], "count": n, "snips": snips})
    hits.sort(key=lambda h: -h["count"])
    return hits[:limit]


# ─────────────────────────────────────────────────────────────────────────
# /chat 근거 검색 — 위키 본문에서 질문과 관련된 절을 골라 인용 좌표와 함께 준다
# ─────────────────────────────────────────────────────────────────────────
# ⚠ 이것은 RAG 의 최소형이다: 형태소 분석도 임베딩도 없다. 질문을 공백·구두점으로
#   쪼갠 토큰(2자 이상)의 출현 빈도로 페이지 → 절 순으로 고른다. 위키가 수십 페이지인
#   동안은 충분하고, 커지면 이 함수 하나만 바꾸면 된다 (app.py 와 chat.py 는 결과
#   형태만 본다).
_TOK = re.compile(r"[A-Za-z0-9가-힣₂⁻⁺°µ%.\-]+")
_STOP = {"그리고", "그래서", "무엇", "어떻게", "왜", "the", "and", "for", "with", "this", "that",
         "what", "how", "why", "is", "are", "of", "to", "in", "on", "논문", "위키", "우리",
         "대해", "대한", "있는", "없는", "것", "수", "좀", "더", "관련", "알려줘", "설명"}


def _tokens(q: str) -> list[str]:
    out = []
    for t in _TOK.findall((q or "").lower()):
        t = t.strip(".-")
        if len(t) < 2 or t in _STOP:
            continue
        out.append(t)
    # 중복 제거, 순서 유지
    seen, uniq = set(), []
    for t in out:
        if t not in seen:
            seen.add(t)
            uniq.append(t)
    return uniq[:24]


def _score(text_low: str, toks: list[str]) -> float:
    s = 0.0
    for t in toks:
        n = text_low.count(t)
        if n:
            # 흔한 토큰이 점수를 독식하지 않게 로그 스케일 + 길이 가중
            s += (1 + min(n, 30) ** 0.5) * (1 + 0.15 * min(len(t), 12))
    return s


def _heading_anchor_map(body: str) -> list[tuple[str, str]]:
    """digest 렌더가 붙이는 h-N 앵커와 같은 순서로 (제목, 앵커) 를 만든다 (h2/h3 만).

    anchor_headings 는 렌더된 HTML 의 <h2>/<h3> 순서에 번호를 매기므로, 원문의 `##`/`###`
    순서를 그대로 세면 같은 번호가 나온다. `#` 은 h1 이라 세지 않는다.
    """
    out, n = [], 0
    for m in re.finditer(r"^(##|###)\s+(.+?)\s*$", body, re.M):
        n += 1
        out.append((m.group(2).strip(), f"h-{n}"))
    return out


def chat_context(question: str, max_pages: int = 6, max_chars: int = 42000) -> dict:
    """질문 → {chunks: [...], sources: [...], tokens: [...]}.

    chunk 하나 = 페이지의 절 하나 (제목 · 앵커 URL · 본문). 논문 digest 는 절이 길어
    한 절을 통째로 주되 총량 예산(max_chars)으로 자른다. 항상 index.md 요약을 앞에 둔다
    (모델이 "무엇이 위키에 있는가" 를 알아야 "없다" 고 말할 수 있다).
    """
    toks = _tokens(question)
    pages = scan_pages()
    scored = []
    for slug, p in pages.items():
        try:
            text = p["path"].read_text(encoding="utf-8")
        except OSError:
            continue
        meta, body = split_frontmatter(text)
        low = (p["title"] + " " + p["description"] + " " + body).lower()
        s = _score(low, toks) if toks else 0.0
        # 제목·설명 일치는 본문보다 가중
        s += 3.0 * _score((p["title"] + " " + p["description"]).lower(), toks)
        if s > 0 or not toks:
            scored.append((s, slug, p, body))
    scored.sort(key=lambda x: -x[0])
    picked = scored[:max_pages]

    chunks, sources, budget = [], [], max_chars
    idx = WIKI / "index.md"
    if idx.is_file():
        it = idx.read_text(encoding="utf-8")
        it = it[:6000]
        chunks.append({"slug": "index", "title": "위키 색인 (wiki/index.md)", "url": "/",
                       "section": "", "text": it})
        budget -= len(it)

    for s, slug, p, body in picked:
        secs = split_sections(body)
        anchors = _heading_anchor_map(body)
        a_of = {t: a for t, a in anchors}
        # 절 점수 → 상위 몇 절
        ranked = []
        for sec in secs:
            sl = (sec["title"] + " " + sec["body"]).lower()
            ranked.append((_score(sl, toks) if toks else 1.0, sec))
        ranked.sort(key=lambda x: -x[0])
        take = ranked[:4] if p["kind"] == "paper" else ranked[:5]
        used_any = False
        for sc, sec in take:
            if sc <= 0 and toks:
                continue
            body_txt = sec["body"].strip()
            if not body_txt:
                continue
            per = 9000 if p["kind"] == "paper" else 5000
            if len(body_txt) > per:
                body_txt = body_txt[:per] + "\n…(절이 길어 잘랐다 — 원문은 페이지에서)"
            if len(body_txt) > budget:
                break
            anchor = a_of.get(sec["title"], "")
            url = p["url"] + (f"#{anchor}" if anchor else "")
            chunks.append({"slug": slug, "title": p["title"], "url": url,
                           "section": sec["title"], "text": body_txt,
                           "kind": p["kind_label"], "meta": {
                               k: str(p["meta"].get(k)) for k in
                               ("confidence", "verificationStatus", "evidenceScope", "status")
                               if p["meta"].get(k) is not None}})
            budget -= len(body_txt)
            used_any = True
        if used_any:
            sources.append({"slug": slug, "title": p["title"], "url": p["url"],
                            "kind": p["kind_label"], "score": round(s, 1)})
        if budget < 1500:
            break
    return {"chunks": chunks, "sources": sources, "tokens": toks}
