#!/usr/bin/env python3
"""smoke.py — webapp 라우트 전수 점검 (서버·포트 없이 Flask test_client 로).

무엇을 보나 (전부 실행 결과로 — 목록을 손으로 적지 않는다)
  1. content.py 등록부가 아는 **모든** 페이지 URL → 200        (위키가 자라도 따라온다)
  2. 고정 화면·API → 200
  3. figures.json 에 등록된 **모든** 그림이 `/api/file/` 로 서빙되나 (아직 0장이면 그 사실만 적는다)
  4. 정적 자산(css/js/fonts) → 200
  5. 읽기 전용 게이트: 허용 밖 쓰기 메서드 → 405 + 우리 JSON 본문 (Flask 자체 405 와 구분)
  6. 경로 탈출·허용 뿌리 밖 파일 → 404
  7. 보안 헤더(CSP·nosniff·X-Frame) 존재
  8. `/api/md` 가 raw HTML 을 이스케이프하고 wikilink 를 해석하나
  9. /compare 에 우리 행(ours:)이 있고 DOE 겹침 칩이 그려지나 · /cells 가 registry 상태를 보이나
 10. 절대 규칙: 화면 어디에도 `NCM721` 이 없다 (금지 문장 제외)

쓰기:  python3 webapp/smoke.py        (0 = 통과, 1 = 실패)
"""
from __future__ import annotations

import json
import os
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
os.environ.setdefault("MIDNI_CHAT_FAKE", "0")

import app as A          # noqa: E402
import content as C      # noqa: E402

fails: list[str] = []
checked = 0


def check(name: str, cond: bool, detail: str = "") -> None:
    global checked
    checked += 1
    if not cond:
        fails.append(f"{name}{(' — ' + detail) if detail else ''}")


def main() -> int:
    cl = A.app.test_client()
    get = cl.get

    # 1. 등록부가 아는 모든 페이지
    pages = C.scan_pages()
    check("registry non-empty", len(pages) > 0, f"scan_pages() -> {len(pages)}")
    for key, p in sorted(pages.items()):
        r = get(p["url"])
        check(f"page {p['url']}", r.status_code == 200, f"status {r.status_code}")

    # 2. 고정 화면 · API
    fixed = ["/", "/roadmap", "/papers", "/compare", "/mechanisms", "/protocols", "/experiments", "/questions",
             "/concepts", "/entities", "/cells", "/chat", "/notes", "/search?q=NCA721", "/favicon.svg",
             "/api/palette.json", "/api/chat/status", "/api/cells.json"]
    for url in fixed:
        r = get(url)
        check(f"route {url}", r.status_code == 200, f"status {r.status_code}")

    pal = get("/api/palette.json").get_json()
    check("palette lists pages", len(pal.get("items", [])) >= len(pages))

    # 3. 그림
    figroot = C.WIKI / "raw" / "figures"
    n_fig = 0
    for j in sorted(figroot.glob("*/figures.json")):
        meta = json.loads(j.read_text(encoding="utf-8"))
        slug = meta.get("slug", j.parent.name)
        api = get(f"/api/figures/{slug}.json")
        check(f"figures api {slug}", api.status_code == 200, f"status {api.status_code}")
        for f in meta.get("figures", []):
            rel = f"{slug}/{f.get('file', '')}"
            r = get(f"/api/file/{rel}")
            check(f"figure {rel}", r.status_code == 200, f"status {r.status_code}")
            n_fig += 1

    # 4. 정적 자산
    static = pathlib.Path(A.app.static_folder)
    n_static = 0
    for sub in ("css", "js", "fonts"):
        d = static / sub
        if not d.is_dir():
            continue
        for f in sorted(d.iterdir()):
            if f.suffix in (".css", ".js", ".woff2"):
                r = get(f"/static/{sub}/{f.name}")
                check(f"static {sub}/{f.name}", r.status_code == 200, f"status {r.status_code}")
                n_static += 1
    check("static found", n_static > 0)

    # 5. 읽기 전용 게이트 — 응답 본문까지 본다 (Flask 자체 405 와 구분)
    for meth, url in (("POST", "/"), ("DELETE", "/roadmap"), ("PUT", "/api/chat"),
                      ("POST", "/api/palette.json"), ("POST", "/api/cells.json"), ("POST", "/cells")):
        r = cl.open(url, method=meth)
        body = r.get_json(silent=True) or {}
        check(f"guard {meth} {url}", r.status_code == 405 and "읽기 전용" in str(body.get("error", "")),
              f"status {r.status_code} body {str(body)[:60]!r}")
    r = cl.post("/api/md", json={"text": "x"})
    check("allow POST /api/md", r.status_code == 200, f"status {r.status_code}")
    r = cl.post("/api/chat", json={"question": "x"})
    check("POST /api/chat without key -> 503 (not 405)", r.status_code in (503, 200), f"status {r.status_code}")

    # 6. 경로 탈출 · 허용 뿌리 밖
    for url in ("/api/file/../../etc/passwd", "/api/file/wiki/raw/papers/anything.md", "/concept/../../etc/passwd",
                "/doc/../CLAUDE.md", "/concept/does-not-exist", "/mechanism/nope", "/cell/nope", "/paper/nope"):
        r = get(url)
        check(f"deny {url}", r.status_code == 404, f"status {r.status_code}")

    # 7. 보안 헤더
    h = get("/").headers
    for key, must in (("Content-Security-Policy", "default-src 'self'"), ("X-Content-Type-Options", "nosniff"),
                      ("X-Frame-Options", "SAMEORIGIN"), ("Referrer-Policy", "same-origin")):
        check(f"header {key}", must in h.get(key, ""), f"got {h.get(key)!r}")

    # 8. /api/md
    r = cl.post("/api/md", json={"text": "<script>alert(1)</script>"})
    html = r.get_json().get("html", "")
    check("md escapes script", "<script>" not in html, f"got {html[:80]!r}")
    r = cl.post("/api/md", json={"text": "[[formation-cutoff-doe]] and [[no-such-page]]"})
    html = r.get_json().get("html", "")
    check("md resolves wikilink", "/experiment/formation-cutoff-doe" in html)
    check("md marks missing wikilink", "wl-missing" in html)
    r = cl.post("/api/md", json={"text": "> [!note] 미검증 배경\n> 본문"})
    check("md renders callout", "callout-note" in r.get_json().get("html", ""))

    # 9. compare / cells
    html = get("/compare").get_data(as_text=True)
    check("compare has ours row", "is-ours" in html and "우리 (사본)" in html)
    check("compare shows DOE chips", 'class="flag fl-same"' in html or 'class="flag fl-' in html)
    rows = C.compare_rows()
    ours = [r for r in rows if r["is_ours"]]
    check("ours flags: main window same as DOE", bool(ours) and ours[0]["flags"]["main"] == "same",
          f"{ours[0]['flags'] if ours else 'no ours row'}")
    html = get("/cells").get_data(as_text=True)
    check("cells page mentions registry", "registry" in html)
    api = get("/api/cells.json").get_json()
    check("cells api ok", api.get("ok") is True and "by_cutoff" in api)

    # 10. 절대 규칙 — 화면에 NCM721 이 없다 (금지 문장 제외)
    bad = []
    for url in ["/", "/roadmap", "/compare", "/cells", "/chat"] + [p["url"] for p in pages.values()]:
        text = get(url).get_data(as_text=True)
        for m in re.finditer(r"(?<![\w-])NCM[\s\-‐–]?721", text, re.I):
            ctx = text[max(0, m.start() - 80): m.end() + 80]
            if not re.search(r"금지|않|말 것|forbidden|not\b|never\b", ctx, re.I):
                bad.append(url)
                break
    check("no NCM721 on any screen (절대 규칙 1)", not bad, f"seen at {bad[:5]}")

    print(f"=== WEBAPP SMOKE ===\n검사 {checked}건 (페이지 {len(pages)} · 그림 {n_fig} · 정적 {n_static})")
    if n_fig == 0:
        print("  (그림 0장 — raw/figures 가 아직 비어 있다; 첫 /paper 뒤에 그림 서빙 검사가 살아난다)")
    if fails:
        print(f"\nFAILURES ({len(fails)}):")
        for f in fails:
            print(" ✗", f)
        return 1
    print("\nRESULT: 0 failures")
    return 0


if __name__ == "__main__":
    sys.exit(main())
