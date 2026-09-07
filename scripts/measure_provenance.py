"""측정 산출물에 **그것을 만든 코드 상태**를 봉인한다 — 한 자리에서.

    from measure_provenance import provenance
    json.dump({..., **provenance()}, fh)

⚠⚠ **왜 있나 (2026-09-07, 원장 CL-75)** — 이것이 없어서 사고가 났다.
커밋된 `docs/data/step3_transport_resolution_kit_ps_7_3_v2.json` 은 **2026-08-17** 산출물인데
파일 어디에도 그 사실이 없었다 (mtime 은 체크아웃 아티팩트다).  그 뒤 `step3_sigma.py` 에
20여 커밋이 들어가 vox 0.20 의 σ_eff 가 **0.108 %** 움직였고, 낡은 값이 정본 행세를 하며
Codex 요청서에 인용됐다.  검사는 전부 초록이었다 — 아무도 "이 숫자를 만든 코드가 언제 것인가"
를 묻지 않았기 때문이다.

⇒ **규칙: 측정 JSON 은 그것을 만든 커밋 SHA 를 자기 안에 적는다.  없으면 인용하지 않는다.**
   (CLAUDE.md 규율 ④ *"정본은 밖으로 강제되지 않으면 새어나간다"* 의 **데이터 판**.)

⚠ `code_dirty` 가 참이면 커밋되지 않은 변경 위에서 잰 것이라 **SHA 만으로 재현되지 않는다** —
  그런 산출물의 수치는 인용하지 말 것.
⚠ 이 모듈은 **한 곳**이다.  같은 걸 다시 짜지 말 것 — 실사고 전례가 있다 (`status_for_value`
  가 `_sigma_status` 를 중복하며 NaN 처리를 빠뜨렸다, CLAUDE.md 규율 ①).
"""
from __future__ import annotations

import datetime
import os
import subprocess
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _git(*args, default=None):
    try:
        return subprocess.run(('git', '-C', _ROOT) + args, capture_output=True,
                              text=True, timeout=15, check=True).stdout.strip()
    except Exception:
        return default


def provenance(extra=None, paths=('scripts/',)):
    """`{'provenance': {...}}` 를 돌려준다 — `json.dump({**d, **provenance()})` 로 합치라.

    `paths` = dirty 판정에 볼 경로들 (기본 `scripts/`).  측정이 데이터 파일에도 의존하면
    그 경로를 함께 넘겨라 — 그래야 "그 데이터가 커밋된 것인가" 까지 봉인된다.
    """
    st = _git('status', '--porcelain', '--', *paths, default=None)
    p = {
        'code_sha': _git('rev-parse', 'HEAD'),
        'code_dirty': (None if st is None else bool(st)),
        'dirty_scope': list(paths),
        'branch': _git('rev-parse', '--abbrev-ref', 'HEAD'),
        'argv': sys.argv[1:],
        'utc': datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'note': ('이 측정을 만든 코드 상태.  `code_sha` 가 없거나 `code_dirty` 가 참이면 '
                 '수치를 인용하지 말 것 (CL-75).'),
    }
    if extra:
        p.update(extra)
    return {'provenance': p}


def check(obj, where=''):
    """봉인이 인용 가능한 상태인지 판정한다.  `(ok, reason)` — 검사기·소비자용.

    ⚠ **fail-closed**: `provenance` 자체가 없으면 통과가 아니라 **거부**다.  옛 산출물이
      조용히 통과하면 이 규칙은 존재하지 않는 것과 같다.
    """
    p = (obj or {}).get('provenance')
    tag = f'{where}: ' if where else ''
    if not isinstance(p, dict):
        return False, f'{tag}provenance 가 없다 — 어느 코드가 만든 값인지 알 수 없다 (인용 금지)'
    if not p.get('code_sha'):
        return False, f'{tag}code_sha 가 비어 있다 (인용 금지)'
    if p.get('code_dirty'):
        return False, (f'{tag}커밋되지 않은 변경 위에서 측정됐다 (code_dirty) — '
                       f'SHA 만으로 재현되지 않는다 (인용 금지)')
    return True, f'{tag}{p["code_sha"][:9]} @ {p.get("utc", "?")}'
