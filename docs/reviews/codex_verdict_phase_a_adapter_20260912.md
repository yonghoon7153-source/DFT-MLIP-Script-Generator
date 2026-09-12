# Codex 적대 리뷰 판정 — Phase A payload→판정기 어댑터 (2026-09-12)

> 요청서 = `docs/reviews/codex_request_phase_a_adapter_20260912.md`
> 기준 스냅샷 = `2474446c9b833b0a318bdd71c7d0c8a618044c71` · 대상 브랜치
> `claude/sdcp-dem-manuscript-si-pqwtv8`.  Codex 는 원격 브랜치를 가져와 그 커밋의 **별도 사본**
> 에서 검토했고, 이후 HEAD 변경은 이 판정에 포함하지 않는다.
>
> ⚠ **아래는 받은 판정문 전문이다.**  요약·재서술하지 않는다 (규율 ③: 한정어가 값이다).

---

## 결론과 범위

**현재 어댑터를 판정용 입력의 검증 경계로 신뢰할 수 없다. 판정 경로에 걸리는 P1 반례가 있다.** 기존 32팔이 실제로 잘못 계산됐다는 뜻은 아니다. 등록된 96 primary·QC 8팔, 격자·문턱·실행 예산의 재심도 아니다.

최우선 결함은 다음과 같다.

| ID | 등급 | 재현한 문제 | 무너지는 보장 |
|---|---|---|---|
| PA12-01 | P1 | 반복 횟수만 있거나 `converged=False`여도 최종 `ORDER-ROBUST`; 실제 `cg_resid`는 버림 | 수렴을 모르는 팔은 판정에 못 들어온다 |
| PA12-02 | P1 | receipt와 payload의 stamp·bridge·vox 불일치, p1 plate도 수용 | 등록 규약의 팔만 변환한다 |
| PA12-03 | P1 | 잘못된 반-복셀 집합 수용; 조성별 receipt 순열만으로 판정 역전 | origin 번호가 동일한 물리 nuisance를 뜻한다 |
| PA12-04 | P1 | 동일 σ·입력에 조성 메타/파일명만 같이 바꾸면 다른 조성으로 수용 | 조성 교차확인이 독립 증거다 |
| PA12-05 | P1 | QC를 primary로 만들고 같은 출력의 primary를 덮어씀 | 남은 QC 8팔도 이 경로로 판정기에 전달된다 |
| PA12-06 | P1 | 재사용 출력에 누락된 옛 팔이 남아 새 디렉터리의 결손을 감춤 | 현재 입력 목록이 최종 판정 대상과 일치한다 |
| PA12-07 | P1 | QC 8개 중 1개만 남겨도 `ORDER-ROBUST`; primary 중복은 마지막 값 사용 | QC 전수·유일한 설계 셀을 판정기가 보증한다 |
| PA12-08 | P1 | `add_rng_per_phase=False`도 통과하고 그 필드가 사라짐 | STEP2 RNG 규약 봉인이 판정까지 연결된다 |
| PA12-09 | P2 | origin guard를 퇴행시킨 변이가 selftest 15/15 | 음성대조 ⑨가 해당 guard를 독립 보증한다 |

P1은 판정·조성·규약 증거가 달라지거나 최종 연결이 막히는 결함에 붙였다. 예외 메시지·표시 문제만을 같은 등급으로 올리지 않았다.

### 실제 수행과 한계

- 어댑터 selftest **15/15**, 판정기 selftest **17/17** 재현.
- 커밋된 32팔의 판정: **`REFUSED`, 설계 셀 64개 결손** 재현.
- 32개 flat 팔과 보존 추출본의 σ·vox·물리 shift·VGCF 라벨 대조: **불일치 0**.
- 기존 `run_contract`로 32개 raw manifest의 protocol ID 재계산·대조 **32/32**, receipt 대조 **32/32**, receipt digest 재계산 일치.
- **full payload 32개와 실제 STEP2 metrics/materialized 배열은 이 검토 자료에 없다.** 따라서 full payload의 SHA를 다시 계산하거나 실제 솔버 잔차·phase 질량을 재검증한 것은 아니다.
- 보존 flat 및 추출본에는 솔버 잔차가 **0/32**다. 이는 미수렴 증거가 아니라 **재검증 증거의 결손**이다.
- 이번에 전체 `check_all.sh`를 다시 돌린 것은 아니다. 위 두 자기검사와 별도 반례 재현기 네 개를 실행했다. 대상 소스는 변경하지 않았다.

아래 `ORDER-ROBUST` 반례는 **합성 primary → 실제 어댑터 → 실제 flat loader → 실제 판정기**를 사용한다. QC 역할 결함을 다른 결함과 분리하기 위해 정상적인 flat QC 8개를 별도 시험 입력으로 제공했다. **QC가 현 어댑터에서 생성됐거나 GPU replay를 실제 실행했다는 뜻이 아니다.** QC가 1개인 반례는 그 수를 명시한다.

재현기 네 개는 이 문서와 같은 증거 폴더에 있다. 리뷰 사본 루트에서 Python 3/numpy가 있는 환경:

```bash
python ../phase_a_adapter_evidence_20260912/probe_origin_tests.py --repo .
python ../phase_a_adapter_evidence_20260912/probe_convergence_seals.py .
python ../phase_a_adapter_evidence_20260912/probe_composition_rng.py --repo .
python ../phase_a_adapter_evidence_20260912/probe_import_qc.py
```

## Q1 — origin 색인 매핑

**판정: 부분 동의. "격자별 순서가 다르면 곧바로 ORDER가 달라진다"는 걱정은 과도하지만, 실제 매핑 계약에는 P1이 있다.**

### 공통 순열은 무해하다 — 여기까지는 CONFIRMED

러너는 `scripts/sdcp_gain_vox015_8arm.sh:434` 에서 `expected_origins_for(vox)`로 receipt의 배열을 만들고, 같은 러너의 594행 및 774행 이후 X→Y→Z 순회와 일치한다. 정본 집합 생성은 `scripts/run_contract.py:270` 이다.

판정기는 `scripts/phase_a_order_verdict.py:152` 에서 **같은 h 안의 조성끼리** 비교한다. 서로 다른 h 사이에서 origin 번호로 쌍대응하지 않는다.

그러므로 h별 순열이 달라도 **그 h의 네 조성에 같은 순열**이 적용되면 비교집합은 그대로다. 재현기에서 정순/격자별 역순 모두 `ORDER-UNRESOLVED`, 위반 3건, 최악 −10%였고 번호만 0→7로 바뀌었다. 0.10·0.125라는 물리값 변화 자체도 h별로 올바른 집합을 사용하면 문제가 아니다.

### 반례 A — 잘못된 h의 물리 shift를 8팔로 승인 [PA12-03]

`scripts/phase_a_arms_from_payload.py:88` 는 receipt의 origins가 비어 있지 않고 중복이 없는지만 본다. **8개·유한한 3성분·해당 h의 `{0,h/2}³`인지 검사하지 않는다.** 126행은 step3와 manifest의 vox만 비교하며 receipt의 vox는 비교하지 않는다. 153행은 배열 위치를 팔 번호로 승격한다.

h=.20/.25의 step3와 manifest vox를 서로 맞게 두고, receipt·물리 shift에는 .15의 `{0,.075}³`를 재사용했다.

- 어댑터 수용: primary 96.
- receipt vox 불일치: **64팔**.
- 해당 h의 정본 집합에 없는 물리 shift: **56팔**.
- 판정: **`ORDER-ROBUST`**.

0..7 숫자가 있다는 사실로 등록된 nuisance 집합을 돌았다고 보증할 수 없다.

### 반례 B — 조성별 receipt 순열만으로 최종 판정 역전 [PA12-03]

현재 `build()`는 조성별 부분 반입을 허용한다. w2의 receipt에서 첫 두 origin만 교환하고, **σ와 payload의 물리 shift는 전혀 바꾸지 않았다.**

```text
w1 물리 origin별 σ = [10, 1, 2, 3, 4, 5, 6, 7]
w2 물리 origin별 σ = [ 9,11,12,13,14,15,16,17]
w3 = 30, w4 = 40

정본 pairing:             ORDER-UNRESOLVED, 최악 −10%
w2 receipt 번호만 교환:  ORDER-ROBUST,     최악 +10%
```

네 조성을 한 receipt로 한 번에 처리하면 이 특정 변이는 생기지 않는다. 그러나 현재 도구는 그 사용 조건을 강제하지 않으며, 반입 합치기에서도 receipt별 번호 의미를 검사하지 않는다.

**실행 대안:** `run_contract.expected_origins_for(payload_vox)`의 정본 물리 벡터로 canonical origin을 산출하고 receipt의 vox·집합을 대조하되, receipt 배열 위치는 출처로만 보존하라.

## Q2 — 조성 교차확인이 독립적인가

**판정: REFUTED. 라벨 불일치 검사는 유효하지만 독립 조성 증거는 아니다. [PA12-04]**

`scripts/phase_a_arms_from_payload.py:135` 는 VGCF의 `wt_pct`와 파일명을 비교한다. `vgcf_n_objects`는 168행에서 복사할 뿐 검사하지 않는다.

실보존 1 wt% 추출값의 구조로 만든 **합성 fixture**에서, `wt_pct:1→4`와 파일명 조성만 함께 바꿨다. 수렴 부재와 혼동하지 않도록 이 fixture에만 정상 `cg_info`를 제공했다.

```text
어댑터 입력 라벨 1 wt% → 4 wt%: 수용
σ_e             0.0021237680850586874  (그대로)
input_digest    7fbb89f40de8b4ec       (그대로)
VGCF n_objects  26816                 (그대로)
VGCF vol_um3    4738.79               (그대로)
```

이것은 실제 4 wt% 팔이 잘못되었다는 증거가 아니라 **같은 침대가 라벨 두 곳의 공통 오류로 다른 조성이 될 수 있는 경계 결함**이다.

제안한 추가 축들도 독립성을 구분해야 한다.

- `scripts/additives.py:171` 의 `recipe_counts_real`에서 `wt_pct`, 목표 개수, 목표 부피분율은 같은 recipe 산술로 나온다.
- `scripts/mpm3d_compaction.py:2326` 의 VGCF `n_objects`는 실제 `unique(fid)`가 아니라 목표 `nobj`다. 실제 개체 소실/제외가 가능한 경로에서 두 수의 무조건 등식은 정상 팔을 과잉차단할 수 있다.
- `scripts/mpm_webapp_payload.py:2728` 의 materialized `phase==code` 점수 계산은 더 독립적이다. 그러나 점수는 질량이 아니다.
- `dilate_z`는 recipe별 기하 규약 교차검사에는 유용하지만 조성 실측을 대신하지 못한다.
- 상별 질량은 실제 phase·입자 체적(`pvol_p`)·AM 체적·밀도에서 재계산해야 한다. `scripts/mpm3d_compaction.py:2294` 는 phase 체적을 실제 점의 `pvs`에 분배한다.

실행 가능 범위도 구분한다. `--save-phase`는 phase 배열만 쓰며(3641행), `pvol_p`는 별도 state 저장 경로에 있다(3677행). 따라서 일반 phase/fibre 파일만 회수해 놓고 질량까지 독립 재계산했다고 말할 수는 없다. 기존 캠페인에는 우선 **등록 recipe와 실제 source-bundle의 일대일 연결**을 검증하고, per-point 체적이 보존되지 않았다면 실제 질량수지는 미검증으로 남긴다. 요청된 recipe 함량을 처치 축으로 쓰는 것과 실현된 물질 질량을 직접 측정했다는 주장은 별개다.

**실행 대안:** 결과값과 독립적으로 고정한 "조성·역할 → STEP2 source-bundle 해시" 대응을 요구하고, 실제 phase/체적 질량수지와 배열 census의 증거를 그 번들에 연결하라; 같은 producer가 복사한 세 숫자의 일치를 독립 검증이라고 부르지 마라.

## Q3 — 수렴 계약을 판정기도 fail-closed로 바꿔야 하나

**판정: 바꿔야 한다. 현재 비대칭은 방어층이 아니라 fail-open 연결이다. [PA12-01]**

생산자는 `scripts/mpm_webapp_payload.py:1766` 에서 실제 잔차를 **`cg_resid`**로 기록한다. 어댑터의 `scripts/phase_a_arms_from_payload.py:53` `CONV_KEYS`에는 그 키가 없다.

`scripts/phase_a_arms_from_payload.py:157` 는 인정한 키가 하나라도 존재하면 통과하고, manifest의 같은 이름 필드를 step3 결과 위에 덮어쓴다. 판정기는 `scripts/phase_a_order_verdict.py:86` 에서 `unconverged`와 `int(cg_info or 0)`만 본다.

96 primary 중 한 팔만 다음과 같이 바꾼 최종 재현:

| 한 팔의 수렴 증거 | 어댑터 | 최종 |
|---|---|---|
| 수렴 키 전부 없음 | 거부 | 미발행 |
| `n_iter=1`만 있음 | 수용 | ORDER-ROBUST |
| `converged=False`만 있음 | 수용 | ORDER-ROBUST |
| `resid=1e6`만 있음 | 수용 | ORDER-ROBUST |
| `cg_info=0.5 / None / False` | 수용 | ORDER-ROBUST |
| `cg_resid=1.0 / NaN` | **잔차 버림** | ORDER-ROBUST |
| step3는 `cg_info=99, unconverged=True`, manifest는 `0,False` | **manifest로 덮음** | ORDER-ROBUST |

이미 있는 `scripts/run_contract.py:593` 의 `conv_ok(cg_info, unconverged, resid)`는 이 사례를 모두 거부한다. 새로운 수렴 문턱을 발명할 필요가 없다.

**실행 대안:** 생산 키 세 개 `cg_info/unconverged/cg_resid`를 손실 없이 전달하고 어댑터와 판정기 모두 기존 `conv_ok`를 호출하게 하며, 계층별 증거 충돌은 덮어쓰지 말고 거부하라.

이는 등록된 δ_num·설계 격자·순서 판정의 변경이 아니라 **이미 선언된 수치 유효성 조건의 복구**다. R9 검토필은 그 이후 발견된 직접 반례를 무시할 이유가 아니다.

현재 32팔의 잔차는 flat과 추출본 모두에 없다. 실제 full payload 또는 해시와 연결된 솔버 원기록에서 회수해야 한다. 없으면 0을 채우지 말고 `UNKNOWN`으로 남긴다. 이 결손만으로 현재 32팔을 미수렴이라고 판정하거나 즉시 전부 재실행하라고 요구하는 것은 아니다.

## Q4 — 음성대조 11개가 정말 발화하는가

**판정: 부분 CONFIRMED. 현재의 거부 이유는 맞지만, "해당 guard의 퇴행을 잡는다"는 보장은 REFUTED다. [PA12-09]**

먼저 셈은 **정상 assertion 5개 + 음성대조 10개**다. ①–④에 더해 ⑮는 깨끗한 출력의 파일 목록을 검사한다(`scripts/phase_a_arms_from_payload.py:265`). 오염 파일을 넣어 거부되는지 시험하는 음성대조가 아니다.

현재 ⑤–⑭의 예외 사유를 모두 기록했다. 각각 의도한 수렴 부재·조성 불일치·PTFE 봉인·vox 불일치·origin 부재·비물리 σ·중복·receipt 봉인·receipt 부재·빈 glob로 거부됐다.

메모리 AST에서 guard를 하나씩 제거한 결과:

| 변이 | selftest |
|---|---|
| 수렴 표지 부재 guard 제거 | **⑤만 FAIL**, 14/15 |
| 설계 셀 중복 guard 제거 | **⑪만 FAIL**, 14/15 |
| 정확 origin 소속 검사를 nearest-neighbor 선택으로 변경 | **15/15 PASS** |

마지막 변이에서 ⑨의 `[9,9,9]`는 다른 기존 팔과 번호가 겹쳐 **origin 부재가 아니라 중복 거부**를 일으킨다. `scripts/phase_a_arms_from_payload.py:270` 의 `neg()`는 어떤 `SystemExit`든 성공으로 세므로 퇴행을 놓친다.

그 변이체에 정본 origin 각각을 `+1e-4` 이동시킨 비정본 32팔을 주면 중복이 없어 모두 수용한다. 원본은 거부한다. 즉 현재 origin 함수가 이미 잘못됐다는 말이 아니라 **그 함수를 실제로 약화해도 자기시험은 초록**이라는 증명이다.

**실행 대안:** ⑨가 정확한 `ORIGIN_NOT_REGISTERED` 오류를 요구하게 하고, 다른 guard에 걸리지 않는 미등록 shift·조성별 receipt 순열·세 격자 간 receipt 교환·실제 출력 오염을 각각 별도 회귀로 묶어라.

## Q5 — QC를 생산 조성 3 wt%로 정하면 빈칸 채우기인가

**판정: 조건부 수용. 3 wt%는 가능한 선택이지만 "원래 사전등록에 명시된 그대로"라고 부르면 안 된다.**

`docs/reviews/phase_a_6mah_order_prereg_20260907.md:383` 은 QC 8팔 @.15를 명시하지만 조성은 쓰지 않는다. 그러나 기록 전체가 처음부터 완전히 비어 있었던 것도 아니다: 폐기된 `scripts/phase_a_plan.py:134` 는 QC를 **1 wt%**로 만들었고 판정기의 기본 QC fixture도 1 wt%다(230행). 다만 v2가 그 생성기를 명시적으로 폐기했으므로 이를 현행 실행 권한으로 되살릴 수도 없다. 시험 fixture의 기본값도 곧 등록 상수는 아니다.

따라서 3 wt% 선택은 **primary 결과 일부를 본 이후의 QC 구현 명세 보완**으로 남기는 것이 정확하다. 생산 조성이라는 사전의 외생적 근거는 타당할 수 있지만, secondary의 "생산 조성" 문구가 QC 조성까지 자동으로 지정하지는 않는다.

권고 기록:

- 이미 h=.15 primary 32팔을 관찰했다는 사실과 결정 시점을 명시한다.
- QC 대상을 `VGCF 3 wt% + PTFE 1 wt%, h=.15, canonical origins 0..7`로 지금 고정한다.
- primary의 실제 **materialized STEP2 배열 해시와 규약**을 QC의 쌍둥이로 지정한다.
- primary를 선택해 복사하는 것이 아니라 **같은 입력을 다른 출력 경로에서 실제 재계산**한다.
- QC 실패를 보고 조성·쌍둥이·문턱을 바꾸지 않는다고 명시한다.
- "70:27:3"라는 명목 원고 조성이 실제 scaffold 조성과 같다는 보장은 별도다. 여기서는 선택한 **실제 3+1 킷/source-bundle**을 정확히 가리키면 된다.

**실행 대안:** 3 wt%를 선택한다면 "결과 관찰 후, QC 실행 전의 명세 보완"으로 날짜·이유·8개 대상 셀·쌍둥이 입력 해시를 승인·봉인하고 δ_num 및 primary 규칙은 그대로 유지하라.

### 그런데 현 어댑터는 그 QC를 전달할 수 없다 [PA12-05]

`scripts/phase_a_arms_from_payload.py:164` 는 **항상 `role='primary'`**다. CLI에도 role 또는 등록 실행계획 입력이 없다. 출력명 205행에도 역할 구분이 없다.

별도 QC payload 8개를 넣어도 결과 역할은 전부 primary다. 같은 out에 변환하면 `arm_w3_v0.15_o0.json` 등을 덮어쓰고, 판정기는 QC가 0개라 계속 HOLD한다. 합성 replay 값을 0.1% 바꾼 시험에서도 실제 primary σ가 새 replay 값으로 덮였음을 재현했다. 이것을 정상 replay 검증이라고 부를 수 없다.

**실행 대안:** 값을 보지 않는 등록된 batch-role/쌍둥이 대응을 입력 계약에 추가하고, 출력 ID·중복 키에 역할을 포함하여 primary와 QC를 각각 보존하라.

### R9 이후에도 남은 QC 완전성 구멍 [PA12-07]

`scripts/phase_a_order_verdict.py:137` 는 QC가 0개인지·orphan·중복인지만 검사한다. **등록된 8개가 모두 있는지는 검사하지 않는다.**

합성 완전체에서 정상 QC **7개를 제거하고 1개만 남겨도 `ORDER-ROBUST`**다. 새 어댑터가 QC를 연결할 때 이 경계를 그대로 두면 replay 일부만으로 전체를 승인한다.

**실행 대안:** 위에서 고정한 QC 대상 셀 집합과 실제 집합이 정확히 일치하도록 검증하라; 이는 8팔을 새로 요구하는 것이 아니라 이미 등록된 8팔을 강제하는 것이다.

## Q6 — add_rng_per_phase 봉인이 실제로 있는가

**판정: STEP2 기록 코드는 CONFIRMED, 현재 판정 경로의 봉인은 REFUTED. [PA12-08]**

`scripts/mpm3d_compaction.py:2156` 에서 플래그가 실제 시딩에 사용되고, `scripts/mpm3d_compaction.py:3448` 에서 STEP2 metrics에 `bool(args.add_rng_per_phase)`를 기록한다. **"STEP2에도 기록 코드가 없다"는 진단은 틀리다.**

그러나 STEP3 manifest는 seed만 일부 전달하며(`scripts/mpm_webapp_payload.py:2675`), raw metrics 복사 목록 `scripts/mpm_webapp_payload.py:2876` 에도 해당 필드가 없다. 어댑터는 검사도 전달도 하지 않는다.

합성 fixture에서 이 키가 **부재 / False / True**인 경우를 각각 넣었고 모두 수용됐다. 출력 arm에는 모두 해당 키가 없다.

킷 5개에 플래그가 있는 것은 실행 명령의 증거다. 실제 실행된 STEP2가 ON이었다는 사실은 해당 원 metrics와 배열 번들에 연결해야 한다. 보존 추출본의 STEP2 metrics 식별자는 다음과 같다.

| VGCF wt% | `input_files.metrics_json` |
|---|---|
| 1 | `a4b827d7669c0c9c` |
| 2 | `e10bc781d1e9838d` |
| 3 | `ea18be14135b29c9` |
| 4 | `bf21719946c90d50` |

이는 현재 남아 있는 짧은 입력 식별자다. 원본을 회수할 때 해당 코드의 기존 digest 규약과 대조하고 새 이관 증서에는 전체 SHA-256도 기록해야 한다.

**실행 대안:** 원 STEP2 metrics를 회수해 해시 연결과 `add_rng_per_phase is True`를 확인하고 arm까지 전달하라; 원본이 없으면 킷의 플래그로 실제 실행 증거를 대신 채우지 마라.

### 해석 한계 — ON은 PTFE 형상의 byte 동일을 보장하지 않는다

사전등록 `docs/reviews/phase_a_6mah_order_prereg_20260907.md:511` 의 "PTFE 형상이 바이트 동일"은 per-phase RNG만으로 성립하지 않는다.

`scripts/mpm3d_compaction.py:2180` 는 PTFE nucleation에 먼저 만든 carbon points를 사용한다. `scripts/additives.py:790` 의 실제 시더에서도 carbon attractor가 시작점/대상을 바꾼다. 상별 난수 스트림을 고정해도 이 입력은 조성과 함께 달라진다.

실제 `additives.seed_fibres`에 PTFE seed/phase `[3,4]`, 개수 40 및 다른 인자를 고정하고 carbon attractor만 이동했다.

- 같은 입력 반복: byte 동일.
- attractor만 변경: 두 출력 모두 14,773점이지만 SHA가 `67436ba4…`와 `5fe3be54…`로 다름. 전체 SHA는 재현기 출력에 있다.

이것은 **난수 소비 위치의 상간 누설 차단**과 **다른 상의 형상 고정**이 다른 주장이라는 반례다. 등록된 §4의 **생산 파이프라인 total effect** 설계를 바꾸라는 근거가 아니다.

**실행 대안:** 현 런은 변경하지 않고 해석을 "상간 RNG 소비 누설은 차단하되 PTFE 개체수·carbon-dependent nucleation·기하 응답은 조성과 함께 변한다"로 제한하라.

## SELF-19 — receipt에 없는 plate_rule을 payload에서 복원할 것인가

**판정: 조건부 동의. 부재를 자동 기본값으로 채우는 것은 반대하며, 전수 근거가 있는 별도 이관은 가능하다.**

더 먼저 고칠 결함이 있다. `scripts/phase_a_arms_from_payload.py:98` 은 receipt의 stamp·bridge가 상수와 같은지만 본다. payload와 receipt를 대조하지 않는다. 따라서 **receipt만 정상이고 payload는 다른 규약인 팔도 통과**한다. [PA12-02]

```text
receipt fibre_stamp=segment   / payload point       → 통과
receipt ptfe_stamp=centerline / payload volume      → 통과
receipt bridge_um=.24        / payload .99         → 통과
payload plate_rule 없음                            → 통과
payload p1 plate + p1 stored protocol ID            → 통과
```

각 변이를 한 primary에 넣은 완전체가 모두 `ORDER-ROBUST`였다. 기존 `scripts/run_contract.py:290` `receipt_match` 및 `scripts/run_contract.py:445` `protocol_ok`는 해당 모순을 검출하지만 어댑터가 호출하지 않는다.

권고 이관 절차:

1. **원본 receipt와 기존 digest를 그대로 보존**한다.
2. 별도 migration attestation에 원 receipt SHA, 전수 파일 목록, 각 full/extract SHA, 필드 경로, 검증 코드 commit을 기록한다.
3. 모든 팔에서 실제 `plate_rule`이 존재하고 **`p2-occupied-surface-first`**인지 검사한다. 첫 팔 값을 다른 팔에 복사하지 않는다.
4. raw manifest에서 protocol ID를 재계산해 저장된 ID와 대조한다.
5. receipt의 선언 축은 각 payload와 `receipt_match`로 대조한다.
6. 검증된 plate 규칙·protocol 증거·이관 출처를 flat 출력까지 전달한다.

**주의:** ID의 `p2-` 접두사는 plate 값 자체를 증명하지 않는다. 잘못된 plate 문자열을 넣고 해시를 다시 계산해도 p2 계열 ID는 만들 수 있다. **허용 plate 값과 해시 일치 둘 다** 필요하다.

현재 보존된 32개 추출 manifest의 plate 값·protocol 재계산·receipt 대조는 통과했다. 따라서 이 축은 **추출본 기준으로 복원 가능한 상태**이며, 이 이유로 32팔 전체를 다시 돌릴 근거는 없다. 다만 추출본과 원 full payload의 source SHA 연결은 원본 부재 때문에 이번에 다시 검증하지 못했다.

## 추가로 발견한 어댑터 출력 경계

### 같은 out을 재사용하면 결손을 옛 팔이 메운다 [PA12-06]

`scripts/phase_a_arms_from_payload.py:203` 은 기존 `arms/`를 허용하고 이번 팔만 개별 쓰기한다. 이전에 존재하던 다른 팔을 제거하거나 현 batch 소속인지 검증하지 않는다. summary·receipt도 마지막 batch의 것으로 덮는다.

합성 3개 격자의 96 primary를 같은 out에 정상 반입하고, 명시적인 flat QC 8개를 제공한 뒤 .15 입력의 한 팔만 제거해 다시 반입했다.

```text
새 h=.15 입력:       31팔
최신 summary:       n_arms=31
최종 loader가 읽음: primary 96 + QC 8 (옛 누락 팔이 남아 있음)
재사용 out 판정:    ORDER-ROBUST

동일한 현재 입력들을 빈 out에 반입: REFUSED
missing: [2.0, 0.15, 7]
```

세 격자의 합치기 자체가 불법이라는 말이 아니다. **명시적인 merge 계약 없이 같은 폴더에 누적하는 것이 현재 입력의 완전성을 증명하지 못한다**는 뜻이다. 현재 판정기는 adapter summary를 읽지 않는다.

**실행 대안:** 기본 반입은 비어 있는 staging 디렉터리에 전량 작성·검증 후 공개하고 기존 out을 거부하되, 누적이 필요하면 역할·조성·h·origin·출처 해시의 명시적 batch merge를 별도 검증하라.

### 판정기가 primary 중복을 마지막 값으로 덮는다 [PA12-07]

어댑터의 중복 검사는 한 번의 `build()` 안에서는 발화한다. 그러나 최종 `scripts/phase_a_order_verdict.py:95` 는 집합으로 coverage를 세고, 156행은 dict의 마지막 값을 사용한다. 합쳐진 flat 디렉터리의 primary 중복을 거부하지 않는다.

동일한 잘못된 중복 셀을 이름만 바꿔 넣었다.

```text
primary 97 + QC 8
000_duplicate.json → ORDER-ROBUST
zzz_duplicate.json → ORDER-UNRESOLVED
```

파일명의 정렬 순서가 결론을 고른다. 이는 일반 판정기 전수 감사가 아니라 **새 어댑터의 여러 batch를 최종 소비하는 경계**에서 재현한 결함이다.

**실행 대안:** 최종 loader/판정기에서 `(role, composition, vox, canonical origin)`의 중복을 거부하고 승인된 batch 목록·해시 집합 외의 파일을 소비하지 않게 하라.

## 부수 수치 대조 — §6의 ±는 origin SD가 아니다 [P2]

커밋된 flat 팔에서 인접 조성의 8개 쌍대응비를 다시 계산했다. 평균은 요청과 맞는다.

| 인접 조성 | 평균 | 표본 SD | SD/√8 |
|---|---:|---:|---:|
| 1→2 | 7.187814 | 0.063349 | 0.022397 |
| 2→3 | 3.986913 | 0.021880 | 0.007736 |
| 3→4 | 2.155484 | 0.012536 | 0.004432 |

요청의 **±0.0224·±0.0077·±0.0044는 SD/√8**과 일치한다. origin 산포인 SD보다 √8배 작다. 그 수가 무엇인지 명시하지 않고 "8팔 산포"로 읽히게 하면 안 된다. 특히 등록상 8 origin은 임의 표본이 아닌 완전 nuisance 집합이므로 이 값을 모집단 평균의 추론적 오차막대로 사용할 근거가 없다.

이는 순서 판정을 뒤집는 지적이 아니다. **평균·SD/범위는 기술 통계로, 판정은 등록된 최악 팔로** 유지하면 된다. 현재 32팔의 실제 원자료 재계산이 아니라 커밋된 flat 산출물의 독립 산술 대조라는 범위도 함께 남긴다.

## 필요한 조치의 끝선

런 계획을 바꾸거나 결과를 다시 고를 필요는 없다. **어댑터 수정·증거 회수·QC 연결을 마치기 전에는 이 flat 파일들만으로 최종 판정을 확정하지 말아야 한다.**

수정의 핵심은 기존 계약의 재사용과 증거 보존이다: canonical origins, `conv_ok`, `receipt_match`, `protocol_ok`, STEP2 source-bundle 연결, 역할/셀/배치 유일성, QC 8개 전수. 원 full payload·STEP2 metrics/배열·솔버 잔차는 검증된 최소 증거 묶음을 만들기 전에 폐기하지 않는 것이 맞다.

이 문서는 과거 리뷰의 "검토필" 표지를 근거로 통과를 인정하지 않았고, 새 guard를 제안할 때도 등록된 설계나 통계 문턱을 변경하지 않았다. 모든 코드 변이는 메모리 또는 별도 임시 파일에서 수행했으며 검토 대상 소스는 그대로다.
