#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""v3 원장 렌더 회귀 — **화면이 원장을 따라가는가**, 그리고 **금지값이 안 새는가**.

계기 (2026-09-09 전수 감사, 원장 CL-89):
  · 웹앱 8 영역 전부에서 기계는 최신인데 라벨이 3~15 개월 뒤였다.  원인은 상태 문장이
    전부 손으로 적힌 산문이고 `webapp/` 이 `claims.json` 을 **읽은 적이 없다**는 것.
  · 그 산문이 실제로 틀렸다 — 철회 배너 둘이 **같은 문장에서 다른 금지 세트**를 현행
    결론으로 적고 있었다 (`app.py:4035` · `seminar_deck.json`).

⇒ v3 는 상태를 원장에서 렌더한다.  이 회귀가 고정하는 계약 셋:
  ① 렌더된 HTML 에 **인용 금지 패턴이 하나도 없다** — 이 페이지가 곧 누수가 되는 것이
     가장 그럴듯한 실패 양식이다 (금지 등록부를 보여 주는 페이지이므로).
  ② 원장이 없으면 **상태를 주장하지 않는다** (있는 척하지 않는다).
  ③ 신선도 비교가 실제로 뒤처짐을 잡는다 — 감사를 기다리지 않고 화면이 스스로 말한다.

  python3 webapp/test_ledger_view.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('WEBAPP_DISABLE_AUTH', '1')

_ok, _fail = 0, []


def chk(name, cond):
    global _ok
    if cond:
        _ok += 1
        print(f'  PASS  {name}')
    else:
        _fail.append(name)
        print(f'  FAIL  {name}')


def _unmarked_bans(CRF, bans, html, where):
    """렌더된 HTML 에 **표지 없이** 사는 금지값 — `ban_sweep` 과 같은 기준.

    스윕이 소스에 적용하는 규칙(줄 ±2 안에 철회 어휘가 있으면 통과)을 **화면**에 적용한다.
    소스가 통과해도 화면이 다르게 조립될 수 있으므로 (라우트가 만든 문자열 · 매크로 ·
    JSON 삽입) 최종 산출물에서 한 번 더 본다.
    """
    lines = html.splitlines()
    out = []
    for i, ln in enumerate(lines):
        norm = CRF._ban_norm(ln)
        for b in bans:
            pat = b.get('pattern')
            if not pat or CRF._ban_norm(pat) not in norm:
                continue
            lo = max(0, i - CRF.BAN_NEAR_LINES)
            near = '\n'.join(lines[lo:i + CRF.BAN_NEAR_LINES + 1])
            if not any(m in near for m in CRF.BAN_NEAR_MARKS):
                out.append(f'{where}:{i + 1} {pat!r}')
    return out


def main():
    import ledger_view as LV

    # ── 모듈 계약 ─────────────────────────────────────────────
    chk('1) 원장을 읽는다', LV.available())
    n = LV.counts()
    chk('2) 상태 집계가 총계와 맞는다',
        sum(v for k, v in n.items() if k != 'total') == n['total'])

    live = LV.claims('live')
    chk('3) 상태 필터가 실제로 거른다',
        live and all(c.get('status') == 'live' for c in live))

    #  ★ 최신 먼저 — v3 의 전제("가장 최근·가장 중요한 것이 앞에")를 코드로 고정한다.
    order = [(c.get('date') or '', LV._num(c.get('id'))) for c in LV.claims()]
    chk('4) ★ 최신이 먼저다 (날짜 → id 번호 내림차순)', order == sorted(order, reverse=True))

    chk('5) 모르는 id 는 지어내지 않고 미등재라고 말한다',
        LV.chip('CL-99999')['known'] is False)
    known = LV.chip(LV.claims(limit=1)[0]['id'])
    chk('6) 아는 id 는 상태·날짜를 돌려준다', known['known'] and known['date'])

    #  ── 신선도 ────────────────────────────────────────────────
    newest = LV.newest_date()
    stale = LV.freshness('2020-01-01', ledger_ids=[LV.claims(limit=1)[0]['id']])
    chk('7) ★ 뒤처진 페이지를 뒤처졌다고 말한다', stale['stale'] and stale['behind'])
    fresh = LV.freshness('2999-01-01', ledger_ids=[LV.claims(limit=1)[0]['id']])
    chk('8) 앞선 페이지는 경고하지 않는다', not fresh['stale'])
    chk('9) 기준선이 원장 최신 등재다', stale['newest'] == newest)

    #  ── 금지 등록부 ───────────────────────────────────────────
    bans = LV.banned()
    chk('10) 등록부가 비어 있지 않다 (비면 이 규칙이 조용히 사라진다)', len(bans) > 0)
    summ = LV.banned_summary()
    chk('11) ★ 요약은 개수와 클레임 id 만 준다 — 값을 안 싣는다',
        all(set(r) == {'claim', 'n', 'why'} for r in summ))
    #  요약 안에 금지 문자열이 섞여 들어오지 않았는가 (why 는 원장 산문이라 값이 있을 수 있다 →
    #  그래서 화면은 why 를 **잘라서** 쓰고, 아래 ⑬ 이 최종 방어선이다).
    chk('12) 요약의 claim 필드가 클레임 id 형태다',
        all(str(r['claim']).startswith('CL-') or r['claim'] == '?' for r in summ))

    #  ── 렌더된 화면 ───────────────────────────────────────────
    import app as A
    c = A.app.test_client()
    r_led = c.get('/ledger')
    r_home = c.get('/')
    chk('13) /ledger 가 뜬다', r_led.status_code == 200)
    chk('14) / 가 뜬다', r_home.status_code == 200)

    html_led = r_led.data.decode('utf-8', 'replace')
    html_home = r_home.data.decode('utf-8', 'replace')

    #  ★★ 가장 중요한 검사 — 금지값을 보여 주는 페이지가 금지값을 **찍지 않는가.**
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    '..', 'scripts'))
    import check_review_findings as CRF
    leaked = []
    for page, html in (('/ledger', html_led), ('/', html_home)):
        norm = CRF._ban_norm(html)
        for b in bans:
            pat = b.get('pattern')
            if pat and CRF._ban_norm(pat) in norm:
                leaked.append(f'{page}: {pat!r} ({b.get("claim")})')
    chk('15) ★★ 렌더된 HTML 에 인용 금지 패턴이 하나도 없다'
        + (f'  ← 누수 {leaked}' if leaked else ''), not leaked)

    #  앞문이 실제로 세 가지를 말하는가 (감사가 없다고 지적한 바로 그것들)
    chk('16) 앞문이 "이게 뭔가" 를 말한다', '양극 복합체' in html_home)
    chk('17) ★ 앞문이 파이프라인이 둘이라고 말한다',
        'CONTACT_FREE' in html_home and 'run_mpm.sh' in html_home)
    chk('18) 앞문이 원장으로 가는 길을 준다', '/ledger' in html_home)
    chk('19) 항해에 원장이 있다', '판정 원장' in html_home)

    #  원장 페이지가 실제로 클레임을 싣는가 (빈 표를 초록으로 내면 최악)
    newest_id = LV.claims(limit=1)[0]['id']
    chk('20) /ledger 가 최신 클레임을 싣는다', newest_id in html_led)
    chk('21) /ledger 가 열린 결함을 싣는다', 'findings' in html_led)

    #  ── 신선도 배선이 실제로 화면에 닿는가 ────────────────────
    #    선언만 해 두고 템플릿이 안 부르면 아무 일도 안 일어난다 (규칙 K: 안 도는 검사).
    pages = {'group': '/group', 'predictor': '/predictor', 'eis': '/eis',
             'mpm_lab': '/mpm-lab', 'step5': '/step5'}
    chk('26) 선언한 페이지가 전부 라우트를 갖는다',
        set(pages) <= set(A.PAGE_FRESHNESS))
    bars, leaks2 = [], []
    for key, url in pages.items():
        r = c.get(url)
        html = r.data.decode('utf-8', 'replace')
        bars.append((key, r.status_code == 200 and
                     ('마지막 갱신은' in html or '검토됐다' in html)))
        leaks2 += _unmarked_bans(CRF, bans, html, url)
    chk('27) ★ 선언한 모든 페이지가 신선도 줄을 실제로 렌더한다'
        + (f'  ← {[k for k, v in bars if not v]}' if not all(v for _, v in bars) else ''),
        all(v for _, v in bars))
    #  ⚠ 여기는 15) 보다 **느슨하다** — 그리고 그것이 맞다.  리포의 규칙은 "표지 없이"
    #    금지값이 사는 것을 막는 것이지, *철회를 알리는 문장*까지 막는 것이 아니다.
    #    실제로 `/eis` 는 *"옛 문구의 +52% 는 … 철회 — claims.json CL-24"* 라고 적는데,
    #    그 문장을 지우면 독자가 옛 발표자료와 대조할 근거를 잃는다.
    #    ⇒ 스윕과 **같은 기준**(±2 줄 철회 표지)을 렌더된 화면에 적용한다.
    #    15) 만 엄격한 이유: 그 두 페이지는 **원장 산문을 통째로** 렌더하므로
    #    `redact()` 를 지나야 하고, 지나면 남을 이유가 없다.
    chk('28) ★★ 그 페이지들에 **표지 없는** 금지값이 없다 (스윕과 같은 기준)'
        + (f'  ← {leaks2}' if leaks2 else ''), not leaks2)

    #  선언 날짜가 미래면 경고가 영원히 안 뜬다 = 조용한 거짓 초록.
    import datetime as _dt
    today = _dt.date.today().isoformat()
    future = [k for k, v in A.PAGE_FRESHNESS.items() if (v.get('updated') or '') > today]
    chk('29) ★ 신선도 선언에 미래 날짜가 없다 (미래로 적으면 경고가 영원히 안 뜬다)'
        + (f'  ← {future}' if future else ''), not future)

    #  ── 원장이 없을 때 ────────────────────────────────────────
    saved_claims, saved_findings = LV.CLAIMS_PATH, LV.FINDINGS_PATH
    try:
        LV.CLAIMS_PATH = '/nonexistent/claims.json'
        LV.FINDINGS_PATH = '/nonexistent/findings.json'
        LV._cache['stamp'] = None
        chk('22) ★ 원장이 없으면 available()=False (있는 척하지 않는다)',
            LV.available() is False)
        chk('23) 없어도 안 죽는다', LV.context()['counts']['total'] == 0)
        r = c.get('/ledger')
        chk('24) ★ 원장 없이도 페이지가 뜨고 "주장하지 않는다" 고 적는다',
            r.status_code == 200 and '주장하지 않는다' in r.data.decode('utf-8', 'replace'))
    finally:
        LV.CLAIMS_PATH, LV.FINDINGS_PATH = saved_claims, saved_findings
        LV._cache['stamp'] = None
    chk('25) 복구 후 다시 읽는다 (캐시가 실패를 붙들지 않는다)', LV.available())

    print(f'\nledger_view: {_ok}/{_ok + len(_fail)} PASS')
    if _fail:
        for f in _fail:
            print(f'  ✗ {f}')
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
