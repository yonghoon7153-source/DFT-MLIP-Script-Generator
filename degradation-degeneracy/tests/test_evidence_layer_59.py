"""59차 ε (M14·M15) — 증언의 **범위**를 실행 전체로.

58차 L11·L12 는 증거를 실행 안으로 옮겼다 (child 가 자기 report 에 자기가 본
환경을 적는다). 리뷰어는 그 증언의 **범위**가 아직 좁다고 지적했다.

    M14  탐침은 `sitecustomize.__file__` 의 바이트만 잰다. 그 파일이
         `import mypatch` 를 하면 `mypatch.py` 는 목록 밖이고, 그것을 바꿔도
         증언이 안 움직인다 — 58차가 닫았다고 한 바로 그 형태다.
    M15  `environment_tag()` 는 영수증의 `startup` 한 필드만 해시한다. 그래서
         child 가 증언하는 것은 환경 일부뿐이고, `packages`·`env`·묶인 입력은
         여전히 "조각 옆에 적힌 값" 이다 (L12 가 닫으려던 그 자리).

`[해석]` 둘 다 "목록" 의 문제다. 이름을 세는 대신 **인터프리터가 실제로 올린
것 전부**를 재고(M14), 증언의 대상을 **영수증 전체**로 넓힌다(M15).
"""
from __future__ import annotations

import json
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
if str(REPO / "docs" / "22p_gap") not in sys.path:
    sys.path.insert(0, str(REPO / "docs" / "22p_gap"))


def _mr():
    import mutation_replay as mr

    return mr


# ── M14 ───────────────────────────────────────────────────────────────────
def test_the_startup_probe_binds_what_sitecustomize_pulls_in(tmp_path):
    """★ M14 — `sitecustomize` 가 **끌어오는 것**까지 증언에 들어와야 한다.

    58차 탐침은 `site`·`sitecustomize`·`usercustomize` **세 이름**의 파일만
    해시한다. 그 파일이 다른 module 을 import 하면 그 바이트는 목록 밖이다.
    리뷰어 반례를 그대로 옮긴다: `sitecustomize.py` 는 한 글자도 안 바꾸고
    그것이 import 하는 파일만 바꾼다.

    이름을 하나 더하는 수정은 하지 않는다 (그러면 그 파일이 import 하는 다음
    파일이 또 남는다). 인터프리터가 **시작 시 실제로 올린 module 전부**를
    재면 겹수와 무관해진다.
    """
    mr = _mr()

    def _facts(site_dir: Path) -> dict:
        src = mr._ENV_PROBE_BODY + (
            "\nimport json\n"
            f"print(json.dumps(_env_facts({mr._probe_names()!r}), "
            "sort_keys=True, ensure_ascii=False))\n")
        env = dict(mr.replay_env())
        env["PYTHONPATH"] = str(site_dir)
        r = subprocess.run([sys.executable, "-c", src], env=env,
                           capture_output=True, text=True, timeout=300)
        assert r.returncode == 0, r.stderr[-500:]
        return json.loads(r.stdout.strip().splitlines()[-1])

    d = tmp_path / "sitedir"
    d.mkdir()
    (d / "sitecustomize.py").write_text("import _patchmod\n", encoding="utf-8")
    (d / "_patchmod.py").write_text("VALUE = 'ALPHA'\n", encoding="utf-8")
    a = _facts(d)
    (d / "_patchmod.py").write_text("VALUE = 'BETA-LONG'\n", encoding="utf-8")
    b = _facts(d)

    assert a != b, (
        "`sitecustomize.py` 가 끌어오는 파일을 바꿨는데 시작 증언이 그대로다 — "
        "그 바이트가 재생이 올리는 코드인데 증거 밖이다 (M14)")


# ── M15 ───────────────────────────────────────────────────────────────────
def test_the_environment_tag_covers_the_whole_receipt():
    """★ M15 — 증언은 영수증 **전체**를 덮어야 한다.

    58차 tag 는 `startup` 하나만 해시했다. 그러면 `packages`·`env`·묶인 입력이
    바뀌어도 child 의 증언은 그대로이고, 그 필드들은 다시 "조각 옆에 적힌 값" 이
    된다 — L12 가 닫으려던 자리로 되돌아간다.
    """
    mr = _mr()
    base = mr._execution_receipt()
    t0 = mr.environment_tag(base)

    for field, changed in (
            ("interpreter", "0.0.0"),
            ("packages", {"made-up": "9.9"}),
            ("env", {"MADE_UP": "1"}),
            ("inputs", {"made/up.txt": "0" * 16}),
    ):
        if field not in base:
            pytest.skip(f"영수증에 `{field}` 가 없다 — 이 시험의 전제가 바뀌었다")
        other = dict(base)
        other[field] = changed
        assert mr.environment_tag(other) != t0, (
            f"영수증의 `{field}` 를 바꿨는데 증언 tag 가 그대로다 — 그 필드는 "
            "실행이 증언하지 않는다 (M15)")


def test_the_planted_attestation_measures_the_whole_receipt(tmp_path,
                                                            monkeypatch):
    """★ M15 — 심는 증언 node 도 **같은 규칙으로** 재야 한다.

    tag 의 범위만 넓히고 child 가 여전히 `startup` 만 재면, 정상 실행이
    자기 증언과 불일치해 전부 빨개진다. 규칙은 부모와 자식이 **하나**여야 한다.

    그러므로 심어 놓은 node 를 실제로 돌려 본다 — 통과해야 정상이다.

    ★ production 배치를 그대로 만든다: 부모도 자식도 **sandbox** 를 뿌리로
      재야 한다 (`_sandboxed(ROOT)`). 뿌리가 갈리면 `inputs` 가 달라져 시험이
      **틀린 이유로** 빨개진다 — 처음 판이 그랬다 (빈 tmp 를 sandbox 라 부르고
      부모는 실제 저장소를 쟀다).
    """
    import shutil

    mr = _mr()
    sandbox = tmp_path / "sb"
    (sandbox / "tests").mkdir(parents=True)
    for pat in mr.BOUND_INPUT_GLOBS:
        for f in sorted(REPO.glob(pat)):
            if f.is_file():
                dst = sandbox / f.relative_to(REPO)
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(f, dst)
    monkeypatch.setattr(mr, "SANDBOX", sandbox)
    tag = mr.environment_tag()
    mr._write_env_attestation(sandbox, tag)
    planted = sandbox / "tests" / f"test_mutation_env_{tag}.py"
    assert planted.is_file()

    r = subprocess.run([sys.executable, "-m", "pytest", str(planted), "-q"],
                       cwd=REPO, env=mr.replay_env(),
                       capture_output=True, text=True, timeout=900)
    assert r.returncode == 0, (
        "심은 증언 node 가 자기 환경을 재서 tag 와 대조했는데 실패했다 — "
        f"부모와 자식의 규칙이 갈렸다 (M15):\n{r.stdout[-2000:]}")
