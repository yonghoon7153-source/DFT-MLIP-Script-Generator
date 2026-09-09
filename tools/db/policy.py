#!/usr/bin/env python3
"""policy.py — **원자료를 소비하는 도구가 마감·금지 판정을 읽는다.**

    python3 tools/db/policy.py db/properties/b2o3_md_arrhenius.json   # 이 파일 상태
    python3 tools/db/policy.py --selftest

왜 생겼나 (Codex BI-3 P0-4 · 2026-09-09)
  `db/properties/b2o3_md_arrhenius.json` 의 인용 지위를 고쳤는데,
  `tools/modelc_v3/nernst_einstein_300K.py` 에 그 파일을 주면 **정상 종료하면서**
  `Ea = 0.2241 eV` 와 300 K 외삽 D·σ 를 다시 만들고 *"비교는 비율로만"* 이라고
  권했다. 마감 카드가 그 축의 **수송 비교와 300 K 외삽을 둘 다 금지**하는데도.
  원인: 그 도구가 개명한 필드가 아니라 **다른 가지**(`⛔_RETRACTED….multiseed_3x3`)를
  키 이름으로 훑기 때문에 원자료 정정의 영향을 받지 않았다.
  ⇒ **원자료를 고치는 것만으로는 하류가 안 닫힌다. 소비자가 정책을 읽어야 한다.**

무엇을 읽나
  ① `db/properties/*_closed_*.json` · `*_closed_retrospective_*.json` — 마감 카드
     (`닫는_범위` · `금지_서술` · `근거_파일` · `확정값`)
  ② `db/properties/citation_hazards.json` — 행의 `file` 이 이 파일을 가리키고
     **금지가 살아 있으면**(`prohibition_state`, 기본 fail-closed) 걸린다.

⛔ 이 도구가 **못 하는 것**
  · 무엇을 계산하려는지 모른다. **파일 단위**로만 본다 — 같은 파일 안의 살아있는
    축(예: b2o3 의 0 K DFT)을 쓰려는 경우도 일단 막고, 호출자가 사유를 대고 넘긴다.
  · 금지 서술의 **의미**를 해석하지 않는다. 카드가 닫혔다고 말하는지만 본다.
  · 마감 카드가 `근거_파일` 에 안 적어 둔 파일은 **못 잡는다** — 원장이 근거다.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
PROPS = REPO / "db/properties"
#: 명시가 없을 때 금지가 꺼지는 유일한 level (webapp/canonical.py 와 같은 규약).
_PROHIBITION_OFF = frozenset(("RESOLVED",))


def _prohibition_active(row: dict) -> bool:
    """webapp `canonical.prohibition_active` 와 **같은 규칙**. fail-closed."""
    raw = row.get("prohibition_state")
    if raw is not None and str(raw).strip():
        return str(raw).strip().lower() != "inactive"
    return str(row.get("level", "")).upper() not in _PROHIBITION_OFF


def closure_cards(root: Path = None) -> list:
    """마감 카드 전수 → `[{path, 닫는_범위, 금지_서술, 근거_파일, 확정값}]`."""
    base = Path(root) if root else REPO
    out = []
    for f in sorted((base / "db/properties").glob("*closed*.json")):
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if not isinstance(d, dict):
            continue
        out.append({"path": f.relative_to(base).as_posix(),
                    "범위": d.get("닫는_범위") or d.get("scope") or "",
                    "금지": d.get("금지_서술") or [],
                    "근거": d.get("근거_파일") or [],
                    "확정값": d.get("확정값") or {}})
    return out


def policy_for_file(target, root: Path = None) -> dict:
    """이 원자료가 **마감/금지에 걸리는가** → `{closed, cards, hazards, why}`.

    `target` 은 repo 상대경로든 절대경로든 파일명이든 받는다 — 이름으로 맞춘다
    (근거_파일 항목이 `"db/properties/x.json ⛔라벨"` 처럼 꼬리를 달고 있어서).
    """
    base = Path(root) if root else REPO
    name = Path(str(target)).name
    cards = [c for c in closure_cards(base)
             if any(name in str(g) for g in c["근거"]) or name in str(c["범위"])]
    haz = []
    try:
        rows = json.loads((base / "db/properties/citation_hazards.json")
                          .read_text(encoding="utf-8")).get("hazards", [])
    except (OSError, ValueError):
        rows = []
    for z in rows:
        if not isinstance(z, dict):
            continue
        if name in str(z.get("file", "")) and _prohibition_active(z):
            haz.append({"id": z.get("id"), "level": z.get("level"),
                        "what": z.get("what"), "fix": z.get("fix")})
    why = [f"마감 카드 `{c['path']}` — {str(c['범위'])[:120]}" for c in cards]
    why += [f"인용위험 `{h['id']}` ({h['level']}) — {str(h['what'])[:110]}" for h in haz]
    return {"closed": bool(cards or haz), "cards": cards, "hazards": haz, "why": why}


def require_open(target, override: bool = False, what: str = "", root: Path = None) -> str:
    """닫힌 축이면 **시작하지 않는다**. `override` 면 경고를 찍고 스탬프를 돌려준다.

    돌려주는 스탬프 문자열은 호출자가 **출력·json 에 박아야** 한다 — 우회한 사실이
    산출물에 남지 않으면 우회는 조용한 위반이 된다.
    """
    p = policy_for_file(target, root=root)
    if not p["closed"]:
        return ""
    head = f"⛔ 이 원자료는 **마감·금지된 축**이다: {Path(str(target)).name}"
    body = "\n".join("   · " + w for w in p["why"])
    if not override:
        print(head, file=sys.stderr)
        print(body, file=sys.stderr)
        print("   ⇒ 시작하지 않는다. 이력·진단 목적이면 사유를 대고 넘겨라:\n"
              "      --policy_override \"<왜 그래도 돌리는가>\"", file=sys.stderr)
        raise SystemExit(2)
    stamp = (f"⛔ 마감된 축을 **우회해서** 낸 값이다 — 인용 금지. "
             f"사유: {override if isinstance(override, str) else what or '미기재'} · "
             f"근거: {' / '.join(p['why'])}")
    print(head, file=sys.stderr)
    print(body, file=sys.stderr)
    print("   ⚠ --policy_override 로 통과. 산출물에 스탬프를 박는다.", file=sys.stderr)
    return stamp


def _selftest() -> int:
    import tempfile
    ok = True
    with tempfile.TemporaryDirectory() as d:
        r = Path(d)
        (r / "db/properties").mkdir(parents=True)
        (r / "db/properties/x_closed_2026_01_01.json").write_text(json.dumps({
            "닫는_범위": "x 축 전체", "금지_서술": ["⛔ 아무것도 인용 금지"],
            "근거_파일": ["db/properties/x_data.json ⛔라벨"]}, ensure_ascii=False),
            encoding="utf-8")
        (r / "db/properties/citation_hazards.json").write_text(json.dumps({"hazards": [
            {"id": "HZ-y", "level": "SUPERSEDED", "file": "db/properties/y_data.json",
             "what": "규칙은 폐기됐지만 인용은 여전히 금지"},
            {"id": "HZ-z", "level": "RESOLVED", "file": "db/properties/z_data.json",
             "what": "해소됨"},
        ]}, ensure_ascii=False), encoding="utf-8")

        # ⛔음성 ①: 마감 카드가 가리키는 원자료를 못 잡으면 실패
        if not policy_for_file("db/properties/x_data.json", root=r)["closed"]:
            print("⛔ selftest: 마감 카드가 가리키는 파일을 못 잡았다"); ok = False
        # ⛔음성 ②: **SUPERSEDED 라도 금지는 살아 있다** (BI-3 P0-1 과 같은 규칙)
        if not policy_for_file("y_data.json", root=r)["closed"]:
            print("⛔ selftest: SUPERSEDED 인데 금지를 껐다 — P0-1 재발"); ok = False
        # ⛔음성 ③: RESOLVED 는 통과해야 한다 (과잉차단도 결함이다)
        if policy_for_file("z_data.json", root=r)["closed"]:
            print("⛔ selftest: RESOLVED 를 막았다 — 과잉차단"); ok = False
        # ⛔음성 ④: 무관한 파일을 막으면 실패
        if policy_for_file("db/properties/unrelated.json", root=r)["closed"]:
            print("⛔ selftest: 무관한 파일을 막았다"); ok = False
        # ⛔음성 ⑤: 닫힌 축은 **시작하지 않아야** 한다
        try:
            require_open("x_data.json", root=r)
            print("⛔ selftest: 닫힌 축인데 그냥 통과했다"); ok = False
        except SystemExit:
            pass
        # ⛔음성 ⑥: override 는 **스탬프를 돌려줘야** 한다 (조용한 우회 금지)
        s = require_open("x_data.json", override="진단 목적", root=r)
        if "인용 금지" not in s or "진단 목적" not in s:
            print("⛔ selftest: override 스탬프가 사유·금지를 안 담았다:", s); ok = False
    print("selftest PASS" if ok else "selftest FAIL")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("path", nargs="?", help="db/properties 의 원자료")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    if not a.path:
        ap.error("파일을 주거나 --selftest 를 써라")
    p = policy_for_file(a.path)
    print(f"{Path(a.path).name} → {'⛔ 닫힘/금지' if p['closed'] else '✅ 열려 있음'}")
    for w in p["why"]:
        print("   ·", w)
    return 1 if p["closed"] else 0


if __name__ == "__main__":
    sys.exit(main())
