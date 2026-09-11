"""content.py — 위키(`wiki/`)의 마크다운·그림과 셀 요약을 읽어 화면용 자료구조로 만든다.

이 모듈은 **읽기만** 한다. 쓰기 함수는 없다 (없는 게 설계다 — README "왜 읽기 전용인가").
`wiki/raw/` 는 sha256 으로 봉인된 불변층이고, 컴파일 페이지의 정본은 저장소 파일이다.

선행 브랜치 webapp/content.py 에서 가져온 것: 경로 탈출 차단(허용 뿌리 + resolve + is_relative_to),
마크다운 raw HTML 차단 + href/src scheme 재검사, 우리가 만드는 제목 id, 4구분 표기 클래스,
질문 카드 절 분류, 그림 색인 키 정규화, 부분 문자열 검색, /chat 근거 검색.
이 저장소에서 더한 것: 디렉터리 4종(papers·mechanisms·protocols·experiments), 논문 = 노트(`paper:`) +
digest(`raw/papers/`) 두 파일의 결합, `paper:` 평탄화 비교표 + **DOE 겹침 판정**, callout 렌더,
chat 근거에 서지(1저자·연도·저널) 좌표와 우리 셀(`ours:`)·셀 요약 통계 첨부.
"""
from __future__ import annotations

import html as _html
import json
import re
import sys
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
CONFIG = ROOT / "config" / "cells.yaml"

# /api/file 이 열어 주는 뿌리. 이 밖은 404 — 저장소 안이어도 안 준다.
_FILE_ROOTS = (WIKI / "raw" / "figures",)

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
try:
    from tools.cells import cellio as _cellio
except Exception:  # pandas 없어도 앱은 뜬다 (셀 요약만 비활성)
    _cellio = None


# ─────────────────────────────────────────────────────────────────────────
# 설정 (정본: config/cells.yaml)
# ─────────────────────────────────────────────────────────────────────────
def config() -> dict:
    if _cellio is not None:
        try:
            return _cellio.load_config(CONFIG)
        except Exception:
            pass
    d: dict = {}
    if yaml is not None and CONFIG.is_file():
        try:
            d = yaml.safe_load(CONFIG.read_text(encoding="utf-8")) or {}
        except Exception:
            d = {}
    d.setdefault("voltage", {"in_to_li_offset_v": 0.62, "raw_reference": "vs. In/Li-In", "target_reference": "vs. Li/Li+"})
    d.setdefault("doe", {"formation_cutoffs_v_li": [3.6, 3.8, 4.0, 4.2, 4.4, 4.6], "main_window_v_li": [2.5, 4.4], "overlap_tolerance_v": 0.05})
    d.setdefault("cell", {})
    d.setdefault("colors", {"default": "#7f7f7f"})
    return d


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
    if not meta:
        for line in raw.splitlines():
            if ":" not in line or line.lstrip().startswith("#") or line.startswith(" "):
                continue
            k, _, v = line.partition(":")
            meta[k.strip()] = v.strip().strip('"').strip("'")
    return meta, body


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
    """마크다운 → HTML. raw HTML 통과는 끈다 + href/src 를 허용 scheme 만 통과 (attr_list 도 안 켠다)."""
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
# 디렉터리 → (종류, URL 접두사). raw/papers 는 등록부 키가 `raw/papers/<slug>` 다 —
# 같은 slug 의 논문 노트(papers/)와 충돌하지 않게 하면서 URL 은 둘 다 /paper/<slug> 로 모은다.
_DIRS: dict[str, tuple[str, str]] = {
    "papers": ("paper-note", "/paper/"),
    "mechanisms": ("mechanism", "/mechanism/"),
    "protocols": ("protocol", "/protocol/"),
    "experiments": ("experiment", "/experiment/"),
    "entities": ("entity", "/entity/"),
    "concepts": ("concept", "/concept/"),
    "questions": ("question", "/question/"),
    "comparisons": ("comparison", "/doc/comparisons/"),
    "guides": ("guide", "/doc/guides/"),
    "queries": ("query", "/doc/queries/"),
    "syntheses": ("synthesis", "/doc/syntheses/"),
    "raw/papers": ("paper", "/paper/"),
    "raw/transcripts": ("transcript", "/doc/raw/transcripts/"),
    "raw/articles": ("article", "/doc/raw/articles/"),
    "raw/repositories": ("repository", "/doc/raw/repositories/"),
}
_SKIP_NAMES = {"README", "SCHEMA", "CLAUDE", "AGENTS", "index", "log"}
KIND_LABEL = {
    "paper-note": "논문 노트", "paper": "논문 digest", "mechanism": "열화 메커니즘", "protocol": "프로토콜",
    "experiment": "실험", "entity": "프로젝트", "concept": "개념", "question": "열린 질문",
    "comparison": "비교", "guide": "절차", "query": "질의 기록", "synthesis": "종합",
    "transcript": "세션 기록", "article": "글", "repository": "저장소 감사",
}
# 종류 → 목록 화면 URL (빵부스러기·팔레트용)
LIST_URL = {
    "paper-note": "/papers", "paper": "/papers", "mechanism": "/mechanisms", "protocol": "/protocols",
    "experiment": "/experiments", "entity": "/entities", "concept": "/concepts", "question": "/questions",
    "comparison": "/compare", "guide": "/", "query": "/", "synthesis": "/",
    "transcript": "/", "article": "/", "repository": "/",
}


def layer_of(kind: str) -> str:
    if kind in ("paper", "transcript", "article", "repository"):
        return "1층 · 불변 · sha256 봉인"
    if kind == "question":
        return "2층 · 미결"
    if kind in ("protocol", "experiment", "entity"):
        return "2층 · 사용자 진술의 사본 (정본은 실험 노트·registry)"
    return "2층 · 우리가 원전에서 내린 판단"


def _mtime(p: Path) -> float:
    try:
        return p.stat().st_mtime
    except OSError:
        return 0.0


def scan_pages() -> dict[str, dict]:
    """`wiki/` 를 훑어 key → 페이지 메타 사전을 만든다. 요청마다 다시 훑는다 (파일이 정본)."""
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
            key = f"raw/papers/{slug}" if rel == "raw/papers" else slug
            pages[key] = {
                "key": key,
                "slug": slug,
                "kind": kind,
                "kind_label": KIND_LABEL.get(kind, kind),
                "layer": layer_of(kind),
                "dir": rel,
                "path": f,
                "relpath": f.relative_to(ROOT).as_posix(),
                "url": prefix + slug,
                "meta": meta,
                "title": str(meta.get("title") or _first_h1(_body) or slug),
                "description": str(meta.get("description") or ""),
                "updated": str(meta.get("updated") or meta.get("ingested") or meta.get("created") or ""),
                "background": ("[!note] 미검증 배경" in _body) or (str(meta.get("evidenceScope")) == "synthesis-only"),
                "mtime": _mtime(f),
                "bytes": f.stat().st_size if f.exists() else 0,
            }
    return pages


_BODY_H1 = re.compile(r"^\s*#\s+(.+?)\s*$", re.M)


def _first_h1(body: str) -> str:
    m = _BODY_H1.search(body or "")
    return m.group(1).strip() if m else ""


def page_index() -> dict[str, str]:
    """wikilink 해석용 slug → URL. 컴파일 페이지가 우선, `raw/papers/foo` 경로 표기도 받는다."""
    idx: dict[str, str] = {}
    pages = scan_pages()
    for key, p in pages.items():
        if p["dir"] == "raw/papers":
            continue
        idx[p["slug"]] = p["url"]
        idx[f'{p["dir"]}/{p["slug"]}'] = p["url"]
        idx[f'{p["dir"]}/{p["slug"]}.md'] = p["url"]
    for key, p in pages.items():
        if p["dir"] == "raw/papers":
            idx.setdefault(p["slug"], p["url"])
            idx[f'raw/papers/{p["slug"]}'] = p["url"]
            idx[f'raw/papers/{p["slug"]}.md'] = p["url"]
    return idx


def by_kind(kind: str, pages: dict | None = None) -> list[dict]:
    pages = pages if pages is not None else scan_pages()
    items = [p for p in pages.values() if p["kind"] == kind]
    items.sort(key=lambda x: (x["updated"], x["slug"]), reverse=True)
    return items


# ─────────────────────────────────────────────────────────────────────────
# wikilink · callout · 렌더
# ─────────────────────────────────────────────────────────────────────────
_WL = re.compile(r"\[\[([^\[\]|]+?)(?:\|([^\[\]]+?))?\]\]")
_FENCE = re.compile(r"(^```.*?^```|^~~~.*?^~~~)", re.S | re.M)
_CODESPAN = re.compile(r"(`+)(?:.|\n)*?\1")


def linkify_wikilinks(text: str, index: dict[str, str]) -> str:
    """`[[slug]]` · `[[slug|label]]` → 마크다운 링크. 코드는 건드리지 않는다. 없는 페이지는 링크하지 않는다."""
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
# Obsidian 식 callout: `> [!note] 제목` — 이 위키는 note(미검증 배경) · question · warning 셋을 쓴다.
_CALLOUT = re.compile(r"<blockquote>\s*<p>\[!(note|question|warning|info|tip)\]\s*", re.I)


def _callouts(html: str) -> str:
    def _sub(m):
        kind = m.group(1).lower()
        label = {"note": "미검증 배경", "question": "질문", "warning": "주의", "info": "참고", "tip": "팁"}.get(kind, kind)
        return (f'<blockquote class="callout callout-{kind}"><p><span class="callout-tag">{label}</span> ')
    return _CALLOUT.sub(_sub, html)


def render_body(text: str, index: dict[str, str] | None = None) -> str:
    idx = page_index() if index is None else index
    html = md_html(linkify_wikilinks(text, idx))

    def _miss(m):
        label = _html.escape(_html.unescape(m.group(1)))
        return f'<span class="wl-missing" title="이 위키에 없는 페이지">{label}</span>'
    return _callouts(_WLMISS.sub(_miss, html))


# ─────────────────────────────────────────────────────────────────────────
# 한 줄 markdown (표 칸·설명문) — escape 먼저, 우리 태그만 되살린다
# ─────────────────────────────────────────────────────────────────────────
_MD_CODE = re.compile(r"`([^`\n]+)`")
_MD_BOLD = re.compile(r"\*\*(?!\s)([^*\n]+?)(?<!\s)\*\*")
_MD_ITAL = re.compile(r"(?<![\w*])\*(?!\s)([^*\n]+?)(?<!\s)\*(?![\w*])")
_MD_LINK = re.compile(r"\[([^\]\n]+)\]\((https?://[^\s)]+|/[^\s)]*)\)")
_MD_WL = re.compile(r"\[\[([^\[\]|]+?)(?:\|([^\[\]]+?))?\]\]")


def md_inline(s, index: dict[str, str] | None = None) -> str:
    if s is None or s == "":
        return ""
    out = _html.escape(str(s), quote=False)
    holes: list[str] = []

    def _stash(m):
        holes.append(m.group(1))
        return f"\x00{len(holes) - 1}\x00"

    out = _MD_CODE.sub(_stash, out)
    if index:
        def _wl(m):
            t, lab = m.group(1).strip(), (m.group(2) or m.group(1)).strip()
            u = index.get(t)
            return f'<a href="{u}">{lab}</a>' if u else f'<span class="wl-missing">{lab}</span>'
        out = _MD_WL.sub(_wl, out)
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
CLAIM_KINDS = {
    "인쇄": ("printed", "원문에 글자로 인쇄된 것"),
    "도표": ("figure", "그림에서 눈으로 읽은 근사값 — 원 데이터가 아니다"),
    "해석": ("ours", "digest 를 쓰며 붙인 판단 — 논문의 주장이 아니다"),
    "재현": ("repro", "원문 값을 이 위키에서 산술로 옮긴 것 — 계산식 병기"),
}
_CLAIM_LEAD = re.compile(r"(<(?:p|li)\b[^>]*)(>)\s*<code>\[(인쇄|도표|해석|재현)(?:[,，][^\]]*)?\]</code>")
_CLAIM_ANY = re.compile(r"<code>\[(인쇄|도표|해석|재현)((?:[,，][^\]]*)?)\]</code>")


def mark_claims(html: str) -> tuple[str, dict]:
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
        if (_LIST_LINE.match(ln) and out and out[-1].strip() and not _LIST_LINE.match(out[-1])):
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
        out.append({"date": m.group(1), "suffix": (m.group(2) or "").strip(),
                    "state": (st.group(1).lower() if st else ""), "held": bool(st and st.group(2)),
                    "body": text})
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
            "key": _figkey(kind, label), "kind": kind, "label": label,
            "title": ("Table " if kind == "table" else "Scheme " if kind == "scheme" else "Fig. ") + label,
            "page": f.get("page"), "caption": str(f.get("caption") or ""),
            "rel": f"{slug}/{name}", "w": f.get("w"), "h": f.get("h"),
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
# 논문 = 노트(papers/, `paper:`) + digest(raw/papers/, 봉인) — 같은 slug, 같은 URL
# ─────────────────────────────────────────────────────────────────────────
def note_for(slug: str, pages: dict | None = None) -> dict | None:
    pages = pages if pages is not None else scan_pages()
    p = pages.get(slug)
    return p if p and p["kind"] == "paper-note" else None


def digest_for(slug: str, pages: dict | None = None) -> dict | None:
    pages = pages if pages is not None else scan_pages()
    return pages.get(f"raw/papers/{slug}")


def papers_list() -> list[dict]:
    """논문 목록 — 노트가 있으면 노트 기준, 없으면 digest 만 있는 논문도 싣는다."""
    pages = scan_pages()
    seen, items = set(), []
    for p in list(pages.values()):
        if p["kind"] not in ("paper-note", "paper"):
            continue
        slug = p["slug"]
        if slug in seen:
            continue
        seen.add(slug)
        note = note_for(slug, pages)
        dig = digest_for(slug, pages)
        block = (note["meta"].get("paper") if note and isinstance(note["meta"].get("paper"), dict) else {}) or {}
        bib = block.get("bib") or {}
        figs = figures_for(slug)
        base = note or dig
        items.append({
            **base,
            "has_note": note is not None, "has_digest": dig is not None,
            "first_author": _s(bib.get("first_author")), "year": _s(bib.get("year")),
            "journal": _s(bib.get("journal")), "doi": _s(bib.get("doi")),
            "cathode": _s((block.get("cathode") or {}).get("composition_verbatim")),
            "electrolyte": _s((block.get("electrolyte") or {}).get("type")),
            "anode": _s((block.get("anode") or {}).get("type")),
            "window": _s((block.get("voltage") or {}).get("raw_text")),
            "reference_raw": _s((block.get("voltage") or {}).get("reference_raw")),
            "nfig": len(figs), "nsi": sum(1 for f in figs if str(f["label"]).upper().startswith("S")),
            "sha12": str((dig or {}).get("meta", {}).get("sha256") or "")[:12],
            "ingested": str((dig or {}).get("meta", {}).get("ingested") or base["updated"] or ""),
            "flags": doe_flags(block),
            "short": short_cite(block, base["title"]),
        })
    items.sort(key=lambda x: (x["ingested"] or "", x["slug"]), reverse=True)
    return items


def _s(v) -> str:
    if v is None:
        return ""
    if isinstance(v, bool):
        return "예" if v else "아니오"
    if isinstance(v, (list, tuple)):
        return ", ".join(_s(x) for x in v if x is not None)
    if isinstance(v, dict):
        return "; ".join(f"{k}: {_s(x)}" for k, x in v.items() if x is not None)
    return str(v)


def short_cite(block: dict, fallback: str = "") -> str:
    bib = (block or {}).get("bib") or {}
    fa, yr = _s(bib.get("first_author")), _s(bib.get("year"))
    if fa and yr:
        return f"{fa} {yr}"
    return fallback if len(fallback) < 40 else fallback[:38] + "…"


def cite_of(block: dict) -> str:
    """(1저자 연도, 저널) — chat 인용 형식의 머리."""
    bib = (block or {}).get("bib") or {}
    parts = [x for x in (_s(bib.get("first_author")), _s(bib.get("year"))) if x]
    head = " ".join(parts)
    if _s(bib.get("journal")):
        head += f", {_s(bib.get('journal'))}"
    return head


# 비교표 열 — `paper:` 평탄화. (key, 머리, 설명, 묶음)
COMPARE_COLUMNS: list[tuple[str, str, str, str]] = [
    ("cathode", "양극 (원문 표기)", "조성 · 결정 · 코팅", "양극"),
    ("electrode", "전극 공정 · 조성비", "dry/slurry/powder · AM:SE:C", "양극"),
    ("loading", "로딩", "mg cm⁻² · mAh cm⁻²", "양극"),
    ("electrolyte", "전해질", "", "셀"),
    ("anode", "음극", "종류 (조성)", "셀"),
    ("voltage_raw", "전압창 (원문 + 기준)", "raw_text · reference_raw", "전압"),
    ("voltage_li", "전압창 vs. Li/Li⁺", "변환값 (offset 병기)", "전압"),
    ("formation", "Formation", "cut-off · C-rate · cycles · rest · T", "전압"),
    ("formation_cutoff_li", "Formation cut-off vs. Li/Li⁺", "정렬·거르기 축", "전압"),
    ("main", "Main cycle", "C-rate · T · 압력(제작/구동) · cycles", "사이클"),
    ("perf", "성능", "초기 방전 · ICE · retention · 과전압/hysteresis", "성능"),
    ("techniques", "분석 기법", "", "근거"),
    ("mechanisms", "열화 메커니즘 주장", "주장 · 산물 · 전압대 · 근거", "근거"),
]


def _numlist(v) -> list[float]:
    if isinstance(v, (list, tuple)):
        out = []
        for x in v:
            try:
                out.append(float(x))
            except (TypeError, ValueError):
                pass
        return out
    return []


def _num(v):
    try:
        return None if v is None else float(v)
    except (TypeError, ValueError):
        return None


def doe_flags(block: dict, cfg: dict | None = None) -> dict:
    """내 DOE 창과의 겹침 판정 — 전압 창만 본다 (loading·압력은 표의 다른 열이 말한다)."""
    cfg = cfg or config()
    doe = cfg.get("doe") or {}
    lo_my, hi_my = (doe.get("main_window_v_li") or [2.5, 4.4])[:2]
    tol = float(doe.get("overlap_tolerance_v") or 0.05)
    cuts = _numlist(doe.get("formation_cutoffs_v_li") or [])
    b = block or {}
    win = _numlist((b.get("main_cycle") or {}).get("window_vs_li") or (b.get("voltage") or {}).get("window_vs_li"))
    cut = _num((b.get("formation") or {}).get("cutoff_v_li"))
    out = {"main": "unknown", "main_label": "전압창 미상", "formation": "unknown", "formation_label": "formation 미기재",
           "upper": None, "cutoff": cut}
    if len(win) == 2:
        lo, hi = sorted(win)
        out["upper"] = hi
        if abs(hi - hi_my) <= tol and abs(lo - lo_my) <= tol:
            out["main"], out["main_label"] = "same", f"내 창과 같음 ({lo_my}–{hi_my} V vs. Li/Li⁺)"
        elif hi > hi_my + tol:
            out["main"], out["main_label"] = "beyond", f"상한이 내 창 위 (+{hi - hi_my:.2f} V)"
        elif hi < hi_my - tol:
            out["main"], out["main_label"] = "below", f"상한이 내 창 아래 (−{hi_my - hi:.2f} V)"
        else:
            out["main"], out["main_label"] = "inside", "상한 같음 · 하한 다름"
    if cut is not None:
        if cuts and (min(cuts) - tol) <= cut <= (max(cuts) + tol):
            near = min(cuts, key=lambda c: abs(c - cut))
            out["formation"], out["formation_label"] = "in", f"내 DOE 안 (가까운 수준 {near} V vs. Li/Li⁺)"
        else:
            out["formation"], out["formation_label"] = "out", "내 DOE 범위 밖"
    elif (b.get("formation") or {}).get("described") is False:
        out["formation_label"] = "formation 별도 기술 없음"
    return out


def flatten_paper(block: dict) -> dict[str, str]:
    """`paper:` 블록 → 비교표 칸 문자열. 없는 값은 빈 문자열 (물음표를 채우지 않는다)."""
    b = block or {}
    c, e, a = b.get("cathode") or {}, b.get("electrolyte") or {}, b.get("anode") or {}
    v, f, m, p = b.get("voltage") or {}, b.get("formation") or {}, b.get("main_cycle") or {}, b.get("performance") or {}

    def j(*parts, sep=" · "):
        return sep.join(x for x in parts if x)

    cath = j(_s(c.get("composition_verbatim")),
             {"single": "single-crystal", "poly": "poly-crystal"}.get(_s(c.get("crystal")), _s(c.get("crystal"))),
             ("코팅 " + (_s(c.get("coating_type")) or "있음")) if c.get("coating") is True else ("코팅 없음" if c.get("coating") is False else ""))
    electrode = j(_s(c.get("electrode_process")), _s(c.get("composite_ratio")))
    loading = j((_s(c.get("loading_mg_cm2")) + " mg cm⁻²") if c.get("loading_mg_cm2") is not None else "",
                (_s(c.get("loading_mah_cm2")) + " mAh cm⁻²") if c.get("loading_mah_cm2") is not None else "")
    electrolyte = j(_s(e.get("type")), _s(e.get("detail")))
    anode = j(_s(a.get("type")), f"({_s(a.get('composition'))})" if a.get("composition") else "")
    vraw = j(_s(v.get("raw_text")), _s(v.get("reference_raw")))
    win = _numlist(v.get("window_vs_li") or m.get("window_vs_li"))
    vli = ""
    if len(win) == 2:
        vli = f"{win[0]:g}–{win[1]:g} V vs. Li/Li⁺"
        if v.get("offset_applied_v") is not None:
            vli += f" (offset {float(v.get('offset_applied_v')):+g} V)"
    form = ""
    if f.get("described") is False:
        form = "별도 기술 없음"
    else:
        form = j(_s(f.get("cutoff_v_raw")), _s(f.get("c_rate")),
                 f"{_s(f.get('cycles'))} cycles" if f.get("cycles") is not None else "",
                 f"rest {_s(f.get('rest_h'))} h" if f.get("rest_h") is not None else "",
                 f"{_s(f.get('temperature_c'))} °C" if f.get("temperature_c") is not None else "")
    fcut = f"{float(f.get('cutoff_v_li')):g} V vs. Li/Li⁺" if _num(f.get("cutoff_v_li")) is not None else ""
    main = j(_s(m.get("window_raw")), _s(m.get("c_rate")),
             f"{_s(m.get('temperature_c'))} °C" if m.get("temperature_c") is not None else "",
             f"제작 {_s(m.get('pressure_fab_mpa'))} MPa" if m.get("pressure_fab_mpa") is not None else "",
             f"구동 {_s(m.get('pressure_op_mpa'))} MPa" if m.get("pressure_op_mpa") is not None else "",
             f"{_s(m.get('cycles'))} cycles" if m.get("cycles") is not None else "")
    perf = j(f"초기 방전 {_s(p.get('initial_discharge_mah_g'))} mAh g⁻¹" if p.get("initial_discharge_mah_g") is not None else "",
             f"ICE {_s(p.get('ice_pct'))} %" if p.get("ice_pct") is not None else "",
             (f"retention {_s(p.get('retention_pct'))} %" + (f" @ {_s(p.get('retention_cycles'))} cyc" if p.get("retention_cycles") is not None else "")) if p.get("retention_pct") is not None else "",
             f"과전압 {_s(p.get('overpotential_trend'))}" if p.get("overpotential_trend") else "",
             f"hysteresis {_s(p.get('hysteresis_trend'))}" if p.get("hysteresis_trend") else "")
    techs = ", ".join(_s(t) for t in (b.get("techniques") or []))
    mechs = []
    for mm in (b.get("mechanisms") or []):
        if not isinstance(mm, dict):
            continue
        mechs.append(j(_s(mm.get("claim")), ("산물 " + _s(mm.get("products"))) if mm.get("products") else "",
                       _s(mm.get("voltage_range")), ("근거 " + _s(mm.get("evidence"))) if mm.get("evidence") else "",
                       ("[" + ", ".join(_s(t) for t in (mm.get("tags") or [])) + "]") if mm.get("tags") else "",
                       sep=" — "))
    return {
        "cathode": cath, "electrode": electrode, "loading": loading, "electrolyte": electrolyte, "anode": anode,
        "voltage_raw": vraw, "voltage_li": vli, "formation": form, "formation_cutoff_li": fcut, "main": main,
        "perf": perf, "techniques": techs, "mechanisms": " ⏐ ".join(mechs),
    }


def compare_rows() -> list[dict]:
    """`paper:`(논문 노트) + `ours:`(프로젝트 카드) → 표 행. 우리가 먼저, 그다음 논문 (상한 전압 내림차순)."""
    cfg = config()
    rows = []
    for p in scan_pages().values():
        block = None
        if p["kind"] == "paper-note" and isinstance(p["meta"].get("paper"), dict):
            block = p["meta"]["paper"]
        elif p["kind"] == "entity" and isinstance(p["meta"].get("ours"), dict):
            block = p["meta"]["ours"]
        if block is None:
            continue
        flags = doe_flags(block, cfg)
        rows.append({**p, "cells": flatten_paper(block), "flags": flags, "is_ours": p["kind"] == "entity",
                     "short": short_cite(block, p["title"]), "cite": cite_of(block),
                     "doi": _s((block.get("bib") or {}).get("doi")),
                     "sort_upper": flags["upper"] if flags["upper"] is not None else -1,
                     "sort_cutoff": flags["cutoff"] if flags["cutoff"] is not None else -1})
    ours = [r for r in rows if r["is_ours"]]
    papers = sorted([r for r in rows if not r["is_ours"]], key=lambda r: (-r["sort_upper"], r["updated"]), reverse=False)
    return ours + papers


# ─────────────────────────────────────────────────────────────────────────
# 검색 — 단순 전문(부분 문자열)
# ─────────────────────────────────────────────────────────────────────────
def _corpus() -> list[dict]:
    docs = []
    for key, p in scan_pages().items():
        docs.append({"title": p["title"], "url": p["url"], "kind": p["kind_label"],
                     "path": p["relpath"], "file": p["path"], "slug": key})
    for name in ("index.md", "log.md"):
        f = WIKI / name
        if f.is_file():
            docs.append({"title": f"wiki/{name}", "url": "/", "kind": "wiki", "path": f"wiki/{name}", "file": f, "slug": name})
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
        snips, start = [], 0
        for _ in range(min(3, n)):
            i = low.find(needle, start)
            if i < 0:
                break
            a, b = max(0, i - 110), min(len(text), i + len(q) + 110)
            snips.append({"pre": " ".join(text[a:i].split()), "hit": text[i:i + len(q)],
                          "post": " ".join(text[i + len(q):b].split())})
            start = i + len(q)
        hits.append({"title": d["title"], "url": d["url"], "kind": d["kind"], "path": d["path"], "count": n, "snips": snips})
    hits.sort(key=lambda h: -h["count"])
    return hits[:limit]


# ─────────────────────────────────────────────────────────────────────────
# /chat 근거 검색 — 위키 절을 인용 좌표(서지 포함)와 함께 고른다
# ─────────────────────────────────────────────────────────────────────────
_TOK = re.compile(r"[A-Za-z0-9가-힣₂⁻⁺°µ%.\-]+")
_STOP = {"그리고", "그래서", "무엇", "어떻게", "왜", "the", "and", "for", "with", "this", "that", "what", "how",
         "why", "is", "are", "of", "to", "in", "on", "논문", "위키", "우리", "대해", "대한", "있는", "없는", "것",
         "수", "좀", "더", "관련", "알려줘", "설명", "해줘", "비교"}


def _tokens(q: str) -> list[str]:
    out = []
    for t in _TOK.findall((q or "").lower()):
        t = t.strip(".-")
        if len(t) < 2 or t in _STOP:
            continue
        out.append(t)
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
            s += (1 + min(n, 30) ** 0.5) * (1 + 0.15 * min(len(t), 12))
    return s


def _heading_anchor_map(body: str) -> list[tuple[str, str]]:
    out, n = [], 0
    for m in re.finditer(r"^(##|###)\s+(.+?)\s*$", body, re.M):
        n += 1
        out.append((m.group(2).strip(), f"h-{n}"))
    return out


def ours_block() -> dict | None:
    for p in scan_pages().values():
        if p["kind"] == "entity" and isinstance(p["meta"].get("ours"), dict):
            return {"page": p, "ours": p["meta"]["ours"]}
    return None


def cells_summary_text() -> str:
    """셀 요약 통계만 (raw 없음). pandas/registry 가 없으면 빈 문자열."""
    if _cellio is None:
        return ""
    try:
        cfg = _cellio.load_config(CONFIG)
        reg = _cellio.load_registry(cfg=cfg)
        summ = _cellio.load_summaries(cfg)
        if not reg and not summ:
            return ""
        return _cellio.llm_summary(summ, reg, cfg)
    except Exception:
        return ""


def chat_context(question: str, max_pages: int = 6, max_chars: int = 42000) -> dict:
    """질문 → {chunks, sources, tokens, ours, cells}. chunk 하나 = 페이지의 절 하나 (제목·앵커·서지·본문)."""
    toks = _tokens(question)
    pages = scan_pages()
    scored = []
    for key, p in pages.items():
        try:
            text = p["path"].read_text(encoding="utf-8")
        except OSError:
            continue
        meta, body = split_frontmatter(text)
        low = (p["title"] + " " + p["description"] + " " + body).lower()
        s = _score(low, toks) if toks else 0.0
        s += 3.0 * _score((p["title"] + " " + p["description"]).lower(), toks)
        if p["kind"] in ("paper-note", "paper"):
            s *= 1.15                                   # 논문이 근거의 정본 — 살짝 우대
        if s > 0 or not toks:
            scored.append((s, key, p, body, meta))
    scored.sort(key=lambda x: -x[0])
    picked = scored[:max_pages]

    chunks, sources, budget = [], [], max_chars
    idx = WIKI / "index.md"
    if idx.is_file():
        it = idx.read_text(encoding="utf-8")[:6000]
        chunks.append({"slug": "index", "title": "위키 색인 (wiki/index.md)", "url": "/", "section": "", "text": it, "kind": "색인"})
        budget -= len(it)

    for s, key, p, body, meta in picked:
        secs = split_sections(body)
        a_of = {t: a for t, a in _heading_anchor_map(body)}
        ranked = []
        for sec in secs:
            sl = (sec["title"] + " " + sec["body"]).lower()
            ranked.append((_score(sl, toks) if toks else 1.0, sec))
        ranked.sort(key=lambda x: -x[0])
        take = ranked[:4] if p["kind"] in ("paper", "paper-note") else ranked[:5]
        # 서지 좌표 — 노트의 paper: 에서, digest 면 같은 slug 의 노트에서
        block = None
        if p["kind"] == "paper-note":
            block = meta.get("paper") if isinstance(meta.get("paper"), dict) else None
        elif p["kind"] == "paper":
            nt = note_for(p["slug"], pages)
            block = nt["meta"].get("paper") if nt and isinstance(nt["meta"].get("paper"), dict) else None
        cite = cite_of(block) if block else ""
        used_any = False
        for sc, sec in take:
            if sc <= 0 and toks:
                continue
            body_txt = sec["body"].strip()
            if not body_txt:
                continue
            per = 9000 if p["kind"] in ("paper", "paper-note") else 5000
            if len(body_txt) > per:
                body_txt = body_txt[:per] + "\n…(절이 길어 잘랐다 — 원문은 페이지에서)"
            if len(body_txt) > budget:
                break
            anchor = a_of.get(sec["title"], "")
            url = p["url"] + (f"#{anchor}" if anchor else "")
            chunks.append({"slug": key, "title": p["title"], "url": url, "section": sec["title"], "text": body_txt,
                           "kind": p["kind_label"], "cite": cite, "background": p["background"],
                           "meta": {k: str(p["meta"].get(k)) for k in ("confidence", "verificationStatus", "evidenceScope", "status")
                                    if p["meta"].get(k) is not None}})
            budget -= len(body_txt)
            used_any = True
        if used_any:
            sources.append({"slug": key, "title": p["title"], "url": p["url"], "kind": p["kind_label"],
                            "cite": cite, "background": p["background"], "score": round(s, 1)})
        if budget < 1500:
            break
    ob = ours_block()
    ours_txt = ""
    if ob:
        ours_txt = json.dumps(ob["ours"], ensure_ascii=False, indent=0)[:4000]
    return {"chunks": chunks, "sources": sources, "tokens": toks, "ours": ours_txt,
            "ours_url": ob["page"]["url"] if ob else "", "cells": cells_summary_text()}
