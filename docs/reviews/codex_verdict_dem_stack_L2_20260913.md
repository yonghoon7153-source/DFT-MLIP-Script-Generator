# Codex 적대 리뷰 판정 — DEM 웹앱 스택 **L2** (2026-09-13)

> 요청서 = `docs/reviews/codex_request_dem_webapp_stack_20260913.md` + L2~L5 후속 프롬프트.
> 기준 스냅샷 = `570d040391f610f43876a609716821bbfba218cc`.
> 선행 = `docs/reviews/codex_verdict_dem_stack_L1_20260913.md` (L1 HOLD).
>
> ⚠ **아래는 받은 판정문 전문이다.**  요약·재서술하지 않는다 (규율 ③).
> 링크의 `C:/Users/...` 는 Codex workspace 사본이고 우리 대응 파일은 같은 상대경로에 있다.
>
> ★ **독립 재현 = 완료** (§부록).  `P1-L2-01` 의 다섯 수치와 `P2-L2-08` 을 **자리 하나까지**
> 재현했고, ψ 가 분모에 있다는 것을 소스에서 확인했다.

---

# DEM 웹앱 스택 L2 판정 — 저항식·Stage-E·CONTACT_FREE·Kirchhoff

작성: 2026-09-13
대상: claude/sdcp-dem-manuscript-si-pqwtv8 @ **570d040391f610f43876a609716821bbfba218cc**
범위: 후속 요청에서 허용한 **L2-a~d 먼저**. L3~L5 전체 판정, 새 LHS 수확기, Phase A Q7은 이번 회신에 포함하지 않는다.

## 0. 결론

**L2 HOLD. 신규 판정 차단 항목 P1 6그룹과 독립 P2 4건.**

L1의 면적·단위 결함만 고쳐서는 L2가 닫히지 않는다. 이번 반례는 저항식을 제외하면 주로 Hertz-명명 채널에서도 재현되므로, Physics 가지를 끄는 것으로도 전부 해결되지 않는다.

핵심은 다음 세 가지다.

- 문헌의 보정계수 ψ는 저항에 **곱한다**. 현행 Physics 식은 **나누며**, 유한접촉 극한을 다루는 방식도 불연속이다.
- 정상 미퍼콜을 양의 fallback으로 바꾸거나, 파괴로 지운 접촉을 unity-skip이 통째로 무시한다. 최종 검사 표지가 초록이어도 이 두 반례가 통과한다.
- Kirchhoff의 작은 양저항 선형해는 맞지만, 경계 fallback·자동 전극저항·실패 상태 분류 때문에 그 값을 "고정된 물리 전극 사이의 전도도"라고 읽을 수 없다.

이는 기존 실침대의 모든 숫자가 특정 비율로 틀렸다는 판정이 아니다. **코드의 일반적 계산·판정 계약을 반박한 것**이다. 실코퍼스의 발생률, CL-81 n=157의 중앙값·산포, 수정 후 원고 수치의 변화량은 원자료가 없어 재계산하지 않았다.

| 요청 | 판정 | 답 |
|---|---|---|
| L2-a 저항식 | **REFUTED** | ψ 역수 적용, 적용범위 밖 확장, 면적 종류의 혼용. 문헌식으로 단순 교체해도 전체 모델 승인은 아니다. |
| L2-b Stage-E fallback | **REFUTED** | 정상 미퍼콜과 실패를 섞어 양수 복원. grain unity가 fracture까지 항등임을 뜻하지 않는다. |
| L2-c CONTACT_FREE | **조건부 CONFIRMED / 해석 REFUTED** | 같은 접촉망의 bulk-only 모델. 모델 내부 상한은 조건부 유지되지만 Bruggeman·실측·고정 전극에서 협착만 제거한 효과는 아니다. |
| L2-d Kirchhoff | **부분 CONFIRMED / 생산 계약 REFUTED** | 작은 정상망의 해석해·floating 제외는 통과. 벽·전극저항·실패 상태의 계약은 깨진다. |

### 증거의 종류

실제 원본 함수를 호출한 합성 검증이다. 작은 정상망은 독립 직렬·병렬 해석식과 대조했다. 실제 builder·실제 network CLI·실제 Stage-E 저장 경로를 실행한 반례와, 수렴 사고를 의도적으로 주입한 게이트 시험을 아래에서 구분한다. 주석·매니페스트의 자기신고로 정답을 정하지 않았다.

소스와 기존 산출물을 고치지 않았다. 별도 고정 worktree와 증거 폴더만 만들었다. 설치된 수치 라이브러리를 사용했고, GPU/DEM 런·계수 재적합·원장 수정·커밋은 하지 않았다.

## 1. L2-a — 저항식의 출처와 면적 계약

### [P1-L2-01] ψ의 자리가 뒤집혔다. 큰 접촉에서는 저항이 증가하다가 0으로 떨어진다

**위치:** `scripts/network_conductivity.py:323` · `:391`, 특히 **395~401행**.
**재현:** 부록 명령 A.

원문을 시각 대조했다. Yovanovich, *Thermal Contact Correlations* (1982), 인쇄 p.86 식 (1)~(3)은 두 반공간의 조화평균 전도도 k_s에 대해 다음 형태다.

~~~text
R_c = ψ / (2 k_s a)
ψ = (1 − a/b)^(3/2),  0 < a/b ≤ 0.3
k_s = 2 k1 k2 / (k1 + k2)
~~~

a는 접촉 spot 반경, b는 연관된 flux-tube 반경이다. **b를 입자 반경 r로 놓는 것은 별도의 기하 가정**이지 위 식이 보증하는 동일성이 아니다. 원문의 소접촉/거시적으로 맞닿은 거친 표면 가정을 임의로 깊게 겹친 두 구의 전체 접촉에 확장할 수 없다.

Yovanovich의 2005 연구자 리뷰, 인쇄 p.187 식 (7)~(9)도 접촉 **conductance** h_c의 분모에 ψ를 둔다. 저항의 분모라는 뜻이 아니다. 이 원문 역시 근사 유효범위를 0<ε<0.3으로 명시한다. 코드의 "Mikić 1974" 주석만으로 현재 구현을 정당화할 수 없다. Mikić 1974 전문을 읽었다고 주장하는 것은 아니며, 여기서 직접 검증한 수식 근거는 위 1982 및 2005 원문이다.

Holm/Maxwell 소접촉 형태 R_H=1/(2σa)와의 관계는 **R_ref=ψ·R_H**다. 현행 코드는 **R_code=R_H/ψ**다. 같은 무차원 인자 s를 대입했을 때 R_code/R_ref=(1−s)^−3이며, 이 오류는 깊은 겹침을 요구하지 않는다.

원본 build_network를 호출하되 L1 면적 모델과 분리하기 위해 입력 면적 반환만 메모리에서 통제했다. 물리 반경 1 µm, 정규화된 전도비 1인 transfer-kernel 시험이다. 여기서 r=b라는 비교 좌표를 쓴 것은 두 구현의 ψ 위치를 대조하기 위해서이지 그 기하 동일성의 승인이 아니다.

| a/r | 원본 R_code | ψ·R_H | 의미 |
|---:|---:|---:|---|
| 0.1 | 5.85606974 | 4.26907484 | 코드/원문형 1.371742 |
| 0.2 | 3.49385621 | 1.78885438 | 1.953125 |
| 0.3 | 2.84578240 | 0.97610336 | **2.915452** |
| 0.4 | 2.68957177 | 비교 승인 범위 밖 | 현행 함수의 최소점 |
| 0.8 | 6.98771243 | 비교 승인 범위 밖 | 면적을 늘렸는데 저항 증가 |

단위는 코드의 µm 길이·정규화 비저항 규약이다. 표의 비는 물성 단위를 바꾸어도 그대로다. 문헌 근사를 0.3 너머의 참값으로 사용하지 않았다.

**질문의 "a→r 발산"은 구현과 수식을 갈라 답해야 한다.**

- 절단 없는 현행 함수 1/[2σrs(1−s)^1.5]는 s=0.4에서 최소이고 이후 증가·발산한다.
- 실제 구현은 ψ≤10⁻⁴이면 R_c=0으로 바꾼다. 전환점은 **s*=0.99784556531**.
- 실제 실행에서 s*−10⁻⁸의 R_c=**5010.76059484**, s*+10⁻⁸에서는 **0**이다.
- 따라서 "발산을 끝까지 구현했다"도, "매끄럽게 full-contact limit로 접근한다"도 틀리다.

**무너지는 결론:** Physics σ 변화의 부호·크기를 접촉 증가의 물리 효과로 해석하는 것. 이 지적 자체는 Hertz-명명 가지의 R_H를 부정하는 것이 아니지만, L1의 Hertz 라벨/면적 문제와 아래 공통 solver·Stage-E 문제는 따로 남는다.

### 무엇을 먼저 정해야 하는가 — L1과 L2를 연결하는 결정을 먼저

먼저 "하한/상한을 어느 숫자로 바꿀까"가 아니라 **L2에 넘길 면적 A가 무엇인가**를 정해야 한다.

현행 `scripts/network_conductivity.py:323` 는 A를 원판 면적으로 읽어 a=√(A/π)를 만든다. 그런데 Physics의 2πr² 표면 cap을 넣으면 a=√2r가 되고, 395행에서 다시 r로 잘린다. **구 표면 피복 면적과 평면 전류 통과 원판은 같은 양이 아니다.**

권고 결정 순서:

1. **수송 접촉의 정의:** 두 입자 사이 실제 전류/열이 통과하는 patch인지, 입자 표면의 피복인지, 퍼진 막의 추가 면적인지 구분한다. 분리된 여러 patch의 총면적만으로 협착저항이 유일하게 결정되지는 않는다.
2. **접촉 연산자와 영역:** 작은 원판 접촉의 반공간 모델을 쓸지, 유한한 두 입자/neck/막을 푸는 모델을 쓸지 정한다. a, b, 재료쌍, pair conductivity, 입자 bulk 항과의 경계 분할을 함께 명시한다.
3. 그 계약에 맞춰 **SI 일관성·lens·재료쌍별 상수·면적 제약**을 L1에서 수정한다. 추가 막 면적이면 그것을 총 원판 면적이라고 바로 넘기지 않는다.
4. 두 입자·균일 neck·극한 사례에서 연속성, 단조성, 단위변환, 독립 전도해를 확인한 뒤 bed 수준으로 간다.

**고칠 수 있는 것:** ψ 위치·유효범위 판정·단위·실패 상태·정확한 경계 적용.
**숫자 패치만으로 못 고치는 것:** 표면 피복/분리막을 단일 원판 반경으로 간주해 유한구의 수송을 대표한다는 가정. 이 가정을 유지할 근거가 없다면, 명시적 patch/neck 기하의 FE/FV 해 또는 그 해에 대해 독립 검증된 contact-conductance 연산자로 대체해야 한다.

따라서 ψ를 곱셈으로 바꾸는 것은 필요한 정정이지만, 그것만으로 "물리 모델 검증 완료"라고 쓰면 안 된다.

## 2. L2-b — Stage-E는 solver 값을 안전하게 보존하지 않는다

### [P1-L2-02] 정상 미퍼콜(valid_null)을 양의 fallback으로 복원한다

**위치:** `scripts/run_network_full_corrections.py:717` 의 상태 미사용, `:757` 의 값-only 분류, **784~789 / 804~806행**의 대체와 823/828행 저장.
**재현:** 부록 B, 결과 case=actual_cut_AM_P.

36구·30접촉 합성망에서 AM 3기둥의 중앙 bridge 3개를 실제 fracture classifier가 pulverization으로 분류하도록 하였다. 실제 apply_corrections가 그 접촉을 삭제한다. 수정 후 AM 그래프의 경계 reachability를 별도 계산했고, 실제 network CLI도 호출했다.

| 항목 | 실행 결과 |
|---|---|
| 수정 AM 그래프의 위아래 연결 | **없음** |
| 직접 network의 전자 출력 | None / **valid_null / AM 망 미퍼콜** |
| raw 전자 Hertz-명명 σ | 0.103889 mS/cm |
| fallback factor | 0.8015 |
| 최종 Stage-E 전자 σ | **0.0832670335 mS/cm** |
| 최종 source | fallback_weighted_factor |
| 상태/게이트 | run_one 성공, 결손 키 0, **trustworthy_overall=true** |

이는 "수치 솔버가 불안정해서 None였을 것"이라는 추정이 아니다. **실제 절단망이 비관통**이고 solver도 정상 미퍼콜로 분류했다. 그런 망의 전극 간 DC 전도는 0이다. 저장 표현 None를 양의 추정치로 바꾸면 다른 문제의 답이 된다.

손상 force는 실제 classifier의 regime을 고르는 연산자 시험이다. DEM force–overlap 관계나 fracture 물성의 타당성까지 검증한 실침대라고 주장하지 않는다.

**무너지는 결론:** "Stage-E σ는 해당 수정 접촉망을 푼 값이다"; "초록 validation이면 양의 수송이 실재한다."

**처방:** no_through_component, not_applicable, not_run, solver_failed를 구별한다. 정상 미퍼콜은 명시적인 0과 근거를 보존한다. 진짜 실패 때 근사를 내더라도 원 solver 상태와 원값을 보존한 **별도 estimate 열**이어야 하며 같은 primary σ를 채우지 않는다.

### [P1-L2-03] grain factor=1이면 파괴로 망이 끊겨도 계산을 생략한다

**위치:** `scripts/run_network_full_corrections.py:651`, 특히 **661~663행**, 696/708/719행.
**재현:** 부록 B, case=actual_cut_AM_S.

위와 같은 중앙 bridge 3개 절단인데 AM_S·SE 반경 1 µm를 사용했다.

- 독립 reachability=false, 수정망 직접 solve=None / valid_null.
- 실제 run_one 안에서 solver 호출 **0회**.
- 전자 σ가 raw **0.140619 → Stage-E 0.140619 mS/cm**, 그대로다.
- source=baseline_no_correction. 동시에 fracture 원장에는 pulverization 3개가 남는다.
- 실제 UI 행 생성 함수는 **"Direct solver (all channels + both modes valid)"**를 낸다. `webapp/app.py:1386`.

원인은 "grain factor 항등"을 "fracture×grain 전체 연산자 항등"으로 바꿔 읽는 것이다. 손상 기록이 없었던 것이 아니라 **있는데 계산에서 무시했다.**

**무너지는 결론:** Stage-E가 AM_S 전자망의 파괴를 반영한다는 주장.
**처방:** 해당 채널의 최종 간선 집합·접촉 면적·δ·전도도 등 실제 solver 입력이 원본과 동일할 때만 skip한다. grain factor 하나만 비교해서는 안 된다.

### 1.1×baseline은 오차막대나 물리적 복구 근거가 아니다

이번 검토에서 10%를 수렴 오차·실험 오차·증명된 근사 오차로 정한 독립 근거를 확보하지 못했다. 구현상 역할은 **다른 추정식으로 갈아타는 선택자**다.

실제 run_one에 반환값만 통제한 별도 시험:

| 주입한 이온 solver 값, baseline=1 | 최종값 | 표지 |
|---|---:|---|
| 1.1−10⁻⁹ | 1.099999999 | solver |
| 1.1+10⁻⁹ | 0.825 | fallback |
| 0, valid_zero | 0.825 | fallback |
| None, valid_null | 0.825 | fallback |
| NaN, failed | 0.825 | fallback |

임계 전후 2×10⁻⁹ 차이가 약 **25% 출력 불연속**을 만든다. 이 시험에서는 trustworthy_overall도 false→true가 된다. 실제 솔버가 이만큼 흔들렸다는 측정이 아니라 **선택 규칙의 반례**다.

"모든 간선 conductance가 감소하고 경계가 고정되어 있다"면 망 전도도는 증가하지 않는다는 검사를 쓸 수 있다. 그러나 그 조건을 실제 간선·경계에서 확인해야 한다. 현재 L2-a의 비단조 R(A)와 L2-d의 자동 경계 변경 아래에서 factor≤1이라는 주석만으로 그 전제를 얻을 수 없다. 1.1 문턱을 넓히는 처방은 권고하지 않는다.

### source는 일부 보존되지만, 과학적 소비자는 사용하지 않는다

"fallback 표지가 전부 사라진다"는 결론도 틀리다.

| 자리 | 실행/코드 추적 결과 |
|---|---|
| full_metrics | `run_network_full_corrections.py:811` 에서 채널×H/P source를 보존한다. |
| master CSV exporter | source를 stage_e_source.sigma_* 열로 flatten해 보존한다. |
| 상세 화면 | source가 있으면 이온 행의 H/P fallback 표지와 요약을 보여준다. 전자·열에는 별도 suppression도 있다. |
| grade 전자/이온 getter | `scripts/grade_engine.py:715` 와 741행. 수치 우선순위로 선택하며 source를 사용하지 않는다. |
| 생산 이온 target getter | `scripts/generate_comparison_plots.py:4222`. fallback인 양수도 target으로 반환한다. |
| attempt 원자료 | 대체 전 Stage-E 값·상태·reason·잔차가 최종 JSON에 별도 보존되지 않는다. Hertz fallback 이유는 stdout에 있으나 Physics 쪽은 같은 메시지도 추가하지 않는다. |

그 결과 어느 행이 fallback인지는 **정상 source가 보존된 파일에서는 식별 가능**하지만, 왜/어느 값에서/어떤 수렴 상태에서 대체했는지 완전한 재판정은 못 한다. 원본 네트워크 JSON의 raw baseline이 있는 것과 **수정망 solve attempt의 원값**이 있는 것은 다르다.

추가 입력 계약 시험에서 빈 source 사전도 `webapp/pipeline_service.py:205` 의 타입 검사를 통과하며 화면은 direct solver로 표시했다. 현재 코퍼스에 빈 source가 몇 개인지는 측정하지 않았다.

### [P2-L2-09] fallback이 채널 밖 접촉을 평균에 넣는다

**위치:** `scripts/run_network_full_corrections.py:435`~450행.
**재현:** 부록 B, irrelevant_AM_contacts_False/True.

같은 atoms·같은 SE 망에서 AM–AM 접촉 기록만 추가했다. 실제 raw 이온 σ는 양쪽 모두 0.008437 mS/cm이다. 이후 동일하게 backend 실패를 주입했다.

- SE–SE만: factor=0.65 → 이온 estimate=0.00548405.
- 같은 SE–SE + AM–AM: factor=0.825 → 0.006960525.
- 이온 전류를 운반하지 않는 접촉 때문에 **+26.9231%**.

P1-L2-02를 고쳐 정상 미퍼콜 복원을 금지하더라도, 진짜 수치 실패에 estimate를 유지하면 이 결함은 남는다. 최소한 채널 마스크가 필요하며 contact_area 가중이 실제 conductance/소산 감도를 대표하는지는 별도 문제다.

## 3. L2-c — CONTACT_FREE의 뜻과 인용 범위

### 연산은 조건부 CONFIRMED

`scripts/network_conductivity.py:1020` 의 FULL과 1024행 CONTACT_FREE는 **같은 입자·접촉 그래프**를 쓴다. bulk_only는 R_bulk만 선택한다(558~559행). 접촉이 존재해야 그래프에 들어오므로 "접촉 그래프를 없앤 모델"은 아니다.

별도 Bruggeman 항은 `scripts/network_conductivity.py:1036` 의 φ^1.5다.

| 키 | 실제 계산량 |
|---|---|
| sigma_full[_mScm] | R_bulk+R_constriction 망 |
| sigma_bulk_net[_mScm] | 같은 망의 bulk-only / CONTACT_FREE |
| sigma_bruggeman[_mScm] | φ^1.5×σ_bulk |
| R_brug_over_full | **CONTACT_FREE/FULL** |
| R_bruggeman_over_full | **Bruggeman/FULL** |

CF≥FULL은 양의 R_bulk, 비음수 R_constriction, 같은 그래프·전극 노드·정규화, 정상 수치해에 조건부다. 다만 현행 593~610행은 mode마다 전극 conductance까지 다시 계산한다. 고정 전극 정리를 그대로 인용할 수는 없다. 정상 저항이면 내부 g와 그 sum/max로 만든 전극 g가 함께 증가하므로 **증강 망의 단조성**으로 상한 관계는 설명할 수 있다.

이것은 실험의 상한도, 고정 전극에서 협착만 제거한 물리 기여분도 아니다. NaN·거부된 해·상이한 graph/경계/상 전도도 사이 비교에는 이 설명을 적용할 수 없다.

### [P2-L2-07] CONTACT_FREE/FULL을 Bruggeman/실측으로 설명한다

**위치:** `scripts/network_conductivity.py:1095` · `scripts/grade_engine.py:340` · `webapp/app.py:8763` · `webapp/templates/single.html:1960`.
**재현:** 부록 C, producer_four_spheres.

기하가 일관된 동일 4구(r=1, 거리 1.9, δ=0.1, 상자 10×10×7.7)를 실제 run_decomposition에 넣었다. σ_bulk=0.003 S/cm:

| 가지 | σ, mS/cm |
|---|---:|
| FULL Hertz-명명 | 0.034749 |
| CONTACT_FREE | 0.126754 |
| Bruggeman | 0.009630 |

CF/FULL=**3.6477**이지만 Bruggeman/FULL=**0.2771**이다. 하나는 1보다 크고 다른 하나는 작다. "간단한 이론식이 실제보다 전도도를 몇 배 과대"라는 설명은 분자와 분모 모두 바꿔 읽는다. 기본 화면 일부는 이미 Contact-free / Full로 올바르게 라벨하지만, grade 설명과 tooltip의 잘못된 의미는 남아 있다.

**무너지는 결론:** 이 비로 Bruggeman의 실측 대비 과대율을 정량화했다는 해석. 이 P2는 FULL의 수치 자체를 바꾸는 연산 오류와는 구분한다.

CL-81의 4.04/6.69배 및 2.3~13.6배 분포는 이번에 재계산하지 않았다. 해당 원자료 키가 CF/FULL이면 그 수치는 **그 접촉 모델/그래프 내부의 민감도**이지 실험 오차 분포가 아니다. 산포가 크다고 하나의 보정 배수로 다른 MPM/voxel 솔버에 이식할 수는 없다.

### [P2-L2-08] "협착이 전체 저항의 45%"는 실제 전력 기여도가 아니다

**위치:** `scripts/network_conductivity.py:1010` · `webapp/app.py:2483` · `webapp/app.py:8765`.
**재현:** 부록 C, diamond.

원본 통계는 간선별 R_bulk/(R_bulk+R_c)의 **비가중 산술평균**이다.

두 병렬 경로가 각각 2개 직렬 간선이고 모든 R_bulk=1, 경로 A의 R_c=9, B의 R_c=0인 합성망:

- 화면의 협착 비율: **45%**.
- 실제 FULL 해의 내부 소산 비율 ΣI²R_c / ΣI²R_total: **8.1818%**.
- 가상 전극까지 분모에 포함하면 **8.1008%**.
- CF로 바꾸면 A 경로 전류 몫은 9.09%→50%다. 단순한 전체 배수 변경이 아니다.

현재 통계를 유지하려면 "접촉별 협착 저항 비율의 비가중 평균"으로 명명한다. 거시 기여도라면 동일 FULL field에서 I²R 원장을 계산하고 전극 포함 여부를 명시해야 한다.

### 절대값 인용 문구

계산 계약이 고쳐지고 독립 검증된 뒤에도 한정어는 필요하다.

> Conductivities are estimates from a DEM-derived contact-resistor network, conditional on the specified phase conductivities, contact law and electrode boundary conditions; they are not direct measurements.

> CONTACT_FREE denotes the bulk-only solution on the same contact graph. Its ratio to FULL is a model-internal comparison, not a Bruggeman-to-experiment error factor. In the present implementation, it also includes changes in the numerical electrode links.

**이 문구를 붙이는 것만으로 현 스냅샷의 P1이 해제되지는 않는다.** 현행 값은 디버그/민감도 기록으로 보존하되, 검증된 절대값으로 승격하지 않는다.

## 4. L2-d — 올바르게 푼 "다른 경계 문제"가 섞인다

### [P1-L2-04] 실제 벽에 닿지 않는 입자 사슬을 관통으로 만든다

**위치:** `scripts/network_conductivity.py:207`~231행, 특히 **224~231행**.
**재현:** 부록 D, actual_build_detached_chain.

상자 10×10×10, 벽 z=0/10. 같은 상의 6구(r=0.1)는 z=4.00, 4.19, 4.38, 4.57, 4.76, 4.95에만 있다. 접촉 거리·δ·원판 면적은 일관되게 구성했다.

- 원자료에서 계산한 아래/위 벽 접촉: **0/0**.
- 실제 builder가 만든 아래/위 집합: 첫 구/마지막 구.
- 실제 decomposition: percolating_fraction=**1**, sigma_full=**0.00090514**(σ/σ_bulk), status=computed.

"벽에 닿는 입자가 3개보다 적다"는 이유로 내부 관측 z 범위의 15/85% 위치에 전극을 다시 놓기 때문이다. 전도도 정규화 길이는 여전히 입력 plate_z다.

**무너지는 결론:** 양의 σ와 관통 분율이 입력한 물리 벽 사이의 수송을 뜻한다는 주장.
**처방:** 알려진 벽에서는 fallback을 금지한다. 경계를 모르면 boundary_unknown, 알려진 벽과 분리되면 정상 zero. 내부 슬래브 전극을 별도 정의하려면 그 경계와 길이를 함께 기록하고 벽 기준 전도도와 다른 estimand로 낸다.

### [P1-L2-05] 전류가 0인 막다른 가지가 σ를 약 4% 바꾼다

**위치:** `scripts/network_conductivity.py:593`~616행, 특히 **607~610행**.
**재현:** 부록 D, one_resistor / add_zero_current_dangling_conductor.

R=1인 단일 경로에 실제 코드가 붙이는 전극 링크는 각각 R=1/50이다.

- baseline G=**0.96153846153846**, 해석해 1/(1+2/50)와 일치.
- 시작 노드에 R=0.001인 막다른 가지 하나를 추가.
- 가지 전류는 **0**인데 G=**0.99996004156128**, **+3.995844%**.
- 이유: 모든 간선의 sum/max를 보아 g_boundary가 50→50050으로 바뀐다.

새 해도 바뀐 경계저항을 넣은 해석해와 일치한다. 수치 불안정에 의한 우연이 아니다. **고정한 문제가 달라졌다.**

**무너지는 결론:** 서로 다른 접촉망의 σ 차이가 내부 수송의 차이만을 반영한다는 해석.
**처방:** 실제 Dirichlet 전극을 정확히 소거하거나, 별도로 정한 물리 전극저항을 사용한다. conditioning은 행렬 스케일링/전처리로 다루고 해석 문제의 경계저항으로 대신하지 않는다. 수정 후 막다른 가지 불변성과 저항 단위 스케일링을 시험한다.

### [P1-L2-06] 수치 사고를 정상 미퍼콜로, thermal NaN을 computed로 분류한다

**위치:** `scripts/network_conductivity.py:687`~691행 · `:1226`~1251행 · `:1290`.
**재현:** 부록 D, 마지막 두 상태 시험. 동일 반환 계약의 하위 반례 두 개다.

1. **명시적 solver fault injection:** 정상 관통망의 spsolve만 RuntimeError를 내도록 한다. 실제 orchestration은 이온·전자·열 모두 **valid_null**을 낸다. 예외를 None로 바꾸고 다시 None를 "정상 미퍼콜"로 분류한 결과다.
2. **실제 원자료 음성대조, solver 무변조:** 정상 SE/AM 경로에 x=NaN인 추가 AM 노드와 SE–AM 간선만 넣는다. 열 그래프에는 포함되나 NaN 저항 간선은 행렬에서 빠져 singular가 된다. 실제 결과는 **thermal_sigma_full=NaN인데 thermal_status=computed**. 정상 SE-only/AM-only는 computed다.

둘째는 잘못된 원자료의 거부 시험이지 실제 덤프에 NaN이 있었다는 증거가 아니다. 이온/전자 NaN을 failed로 막는 기존 분류기는 작동한다. thermal만 그 공통 분류를 사용하지 않는다. 웹앱의 더 뒤쪽 게시 게이트가 별도로 막는지까지 이 시험에서 승인/반박하지 않는다.

**무너지는 결론:** valid_null이 물리적 미퍼콜의 증거이고 computed가 유한한 성공값이라는 계약.
**처방:** 숫자 부재만으로 원인을 추론하지 않는다. 유효한 전기 그래프의 reachability, 실제 solve 성공, finite·잔차/KCL 검사를 각각 통과한 상태를 명시적으로 전달한다.

### [P2-L2-10] 0 저항 단락을 간선 삭제로 처리한다

**위치:** 생산 가능한 R_c=0은 `scripts/network_conductivity.py:401`. CONSTRICTION_ONLY 선택과 조립은 **560~567행**.
**재현:** 부록 D, legitimate_zero_constriction_in_series 및 zero_constriction_short_parallel_to_two_resistors.

- 직렬 R_c=[0,1]: 단락을 합치면 유효한 경로인데 실제는 간선을 지워 singular/NaN.
- 0 저항 직접 간선과 1+1 저항 우회 경로: 실제는 단락을 삭제하고 **G=0.49504950 / computed**, 단락 간선의 기록 전류는 0.
- NaN/음수 저항 병렬 간선을 넣어도 조용히 삭제한 뒤 finite computed가 가능하다.

**무너지는 결론:** CONSTRICTION_ONLY가 생산 가능한 0 접촉저항 극한을 올바르게 푼다는 주장. FULL의 모든 기존 결과가 이 반례에 해당하는 것은 아니다.

finite R 검증과 해당 모드의 전기 그래프 구성을 먼저 하고, R=0은 명시적인 노드 합체 등 단락 처리가 필요하다. 음수/NaN은 거부, +inf는 명시적 절연 상태로 구분한다.

### 통과한 범위 — "솔버 전부 폐기"라는 결론은 아니다

| 독립 대조 | 결과 |
|---|---|
| 양저항 1개 및 1+2 직렬 | 생산 전극 링크를 포함한 해석해와 오차 약 10⁻¹⁵ |
| 서로 분리된 두 관통 성분 | 둘을 모두 병렬로 합산 |
| 완전히 floating인 성분과 고립 노드 추가 | baseline G와 **비트 단위 동일** |
| 실제 비관통 두 성분 | 정상 미퍼콜 경로 존재 |
| 추가 고전도 막다른 가지 | 잔차 약 7.28×10⁻¹²; 위 σ 변화가 바뀐 경계 문제 때문임을 확인 |

기존 "고립 노드 때문에 singular" 이력을 그대로 재보고한 것이 아니다. 정상 floating 성분 제외는 통과했다. 다만 저항 필터 전후 그래프 불일치는 새 문제다.

30,000노드 이상 CG/ILU 분기, 실침대의 conditioning 분포는 이 작은망 검증으로 승인하지 않는다. bottom∩top 메타데이터가 거부를 강제하지 않는 추상 그래프 반례도 상세 보고서에 보존했으나 실침대 발생을 입증한 사례로 세지 않았다.

## 5. 수정·재검증 순서와 동결 규약

1. **L1↔L2 면적/수송 접촉 계약을 먼저 정한다.** SI·lens 수정과 별개로 원판/막/표면 면적 및 finite-contact 모델 선택이 필요하다.
2. **boundary/state/0R 계약을 복구한다.** 고정 벽, 정확한 전극 조건, channel-aware 유효 그래프, 정상 zero와 실패 구분을 회귀로 만든다.
3. **Stage-E 계산과 추정을 분리한다.** fracture 포함 최종 입력이 동일할 때만 skip. 정상 미퍼콜의 양수 복원 금지. attempt 원값·이유를 보존한다.
4. **consumer를 명시적 선택으로 바꾼다.** primary solver 값·정상 zero·실패·별도 estimate가 같은 양수 우선순위 getter에 섞이지 않게 한다. source map의 존재/타입만으로 충분하지 않다.
5. 대표 raw cases를 고정해 **수정 전후 재추출**한다. 채널·H/P·경계·fallback별 발생률과 σ 변화는 이때 재계산한다. 기존 산출물은 삭제하지 말고 계산 세대를 나눈다.
6. 이후에만 **별도 사전등록된 재적합**을 검토한다. 이번 회신은 LIVE 계수 재적합도, LOCKED 지수·EXCL·φ_c 변경도 승인하지 않는다.

L1을 고친 후 Hertz 특징이 그대로라는 이유만으로 등록된 모델이 안전하다고 결론내리면 안 된다. 이 L2는 **목표 y 자체**, 채택 행, 정상 zero의 보존 여부를 바꿀 수 있다. 어떤 생산식이 실제로 어느 y를 먹는지는 다음 L3에서 callsite별로 판정해야 한다.

다음 L3에 넘길 독립 단서: 동일 레코드에 Physics Stage-E=0, raw Physics=0.7을 넣으면 grade 이온 getter는 0, 생산 target getter는 **0.7**을 반환했다. 이는 부록 B의 bounded consumer 시험이다. L3 전체 구조·CV 검증을 완료했다는 뜻은 아니다.

## 6. 남은 범위

- **L3:** 등록식 구조, EXCL·LOCKED·φ_c 단일화, callsite와 CV 누설 — 미판정.
- **L4:** tau 라벨·grade·validation 전체 — 미판정. 이번에는 L2 산출물을 소비하는 소수 경로만 호출했다.
- **L5:** nested 선택, free_products, use_porosity — 미판정.
- **LHS 130 새 수확기 / Phase A Q7:** 별건 그대로 미판정.

이번 L2 HOLD는 위 요청을 취소하는 뜻이 아니다. 다만 이를 함께 통과했다고 쓰거나 자동으로 재적합/재실행을 시작해서는 안 된다.

## 부록 A~D. 재현 명령과 증거

재현기 넷(`probe_l2_resistance.py` · `probe_l2_fallback.py` · `probe_l2_contactfree.py` ·
`probe_l2_kirchhoff.py`) 모두 exit code 0. 이는 "소스가 통과"했다는 의미가 아니라 위
반례·대조값을 재현했다는 뜻이다.

원문 PDF는 읽기 전용으로 관련 전체 페이지를 렌더링해 수식의 분자·분모와 적용범위를 확인했다.

- 1982 PDF SHA256: 20757c6459f63befc151d4d220a683c2038f7844de128f69dfb9933c9b8ab88d.
- 2005 PDF SHA256: 6bb0d574c605f7d37588f6dc950c33ef39d06c55fbaf4d769c8bb2f65936073e.

종결: **현 스냅샷에서 L2의 검증된 절대 전도도 인용은 HOLD. 계산 계약 수정 및 별도 재검증이 필요하다. L3~L5와 별건 두 개는 아직 승인하지 않았다.**

---

## 부록 — 이 리포에서의 독립 재현 (2026-09-13, claude)

### P1-L2-01 — ψ 가 **분모에** 있다 ✅ 소스로 확인 + 수치 자리 일치

`scripts/network_conductivity.py:395-401` 원문:

```python
a_eff = min(a_contact, r_min_real)
psi   = max(1.0 - a_eff / r_min_real, 0.0) ** 1.5
if psi > 1e-4:
    R_constriction = 1.0 / (sigma_rel_contact * k_weight * 2 * a_eff * psi)   # = R_H / ψ
else:
    R_constriction = 0.0                                                       # 불연속
```

문헌형은 `R_c = ψ / (2 k a)` = **`ψ · R_H`** ⇒ 코드는 **역수 적용**이다.

| a/r | 원본 R_code | ψ·R_H | 비 | `(1−s)^−3` |
|---:|---:|---:|---:|---:|
| 0.1 | **5.85606974** | 4.26907484 | 1.371742 | 1.371742 |
| 0.2 | **3.49385621** | 1.78885438 | 1.953125 | 1.953125 |
| 0.3 | **2.84578240** | 0.97610336 | **2.915452** | 2.915452 |

⇒ 판정문의 세 값·세 비가 **전부 일치**하고 해석식 `(1−s)^−3` 과도 일치한다.
**깊은 겹침을 요구하지 않는다** — `a/r = 0.1` 에서 이미 1.37배다.

**비단조·불연속도 재현**:
```
절단 없는 1/[2 a (1−a/r)^1.5] 의 최소점  s = 0.4000   (판정문 0.4)
  s=0.4 → R = 2.68957177        s=0.8 → R = 6.98771243   (면적↑인데 저항↑)
ψ ≤ 1e-4 절단점  s* = 1 − (1e-4)^(2/3) = 0.99784556531   (판정문과 자리 일치)
  s*−1e-8 → R = 5010.76059484        s*+1e-8 → R = 0
```
⇒ *"발산을 끝까지 구현했다"* 도 *"매끄럽게 full-contact limit 로 간다"* 도 **둘 다 틀리다**.

### P2-L2-08 — "협착 45 %" 는 전력 기여도가 아니다 ✅ 자리 일치

두 병렬 경로 × 2 직렬 간선, 모든 `R_bulk = 1`, A 의 `R_c = 9` · B 의 `R_c = 0`:

```
간선별 R_bulk/(R_bulk+R_c) 비가중 평균  →  협착 몫  45 %      (화면 통계)
실제 ΣI²R_c / ΣI²R_total               →          8.1818 %   (판정문 8.1818)
```
⇒ **5.5배** 차이다.  같은 망에서 통계량 정의만 바꾼 것이므로 논쟁의 여지가 없다.

### 확인한 코드 사실 (실행 없이 소스로)

- `:323` — `a_contact = sqrt(A_contact/π)` 로 **A 를 원판 면적으로 읽는다**.
  Physics 의 `2πR_min²` 표면 cap 을 넣으면 `a = √2·r` 가 되고 `:394` 에서 다시 `r` 로 잘린다
  ⇒ **구 표면 피복 면적과 평면 전류 원판이 같은 양으로 취급**된다.
- `:400` 의 `R_constriction = 0.0` 주석이 *"Full contact limit: spreading vanishes"* 인데,
  위에서 보듯 그 직전 값이 **5010.76** 이다 — 극한이 아니라 **절벽**이다.

### ⚠ 아직 재현하지 않은 것 (정직하게)

`P1-L2-02`(valid_null → 0.0832670335) · `P1-L2-03`(fracture skip) · `P1-L2-04`(분리 사슬
관통) · `P1-L2-05`(막다른 가지 +3.995844 %) · `P1-L2-06`(thermal NaN = computed) ·
`P2-L2-09`(채널 밖 접촉 +26.9231 %) · `P2-L2-10`(0 저항 삭제) 은 **합성 침대와 실제 CLI 실행**이
필요해 이 자리에서 돌리지 않았다.  소스 위치는 전부 실재를 확인했다.

### 내 요청서·기록이 틀린 곳

1. **`CL-81` 의 서술을 좁혀야 한다.** 원장은 `R_brug_over_full` 의 n=157 중앙값
   **4.04×(Hertz) · 6.69×(소성면적)**, 범위 2.3~13.6× 를 적고 kim2025 EIS 의 GB-only
   **3.75×** 와 *"8 % 안에서 만난다"* 고 했다.  판정문: 그 키는 **CONTACT_FREE/FULL** 이고
   **그 접촉 모델·그래프 내부의 민감도**이지 실험 오차 분포가 아니다.  ⇒ **문헌 삼각측량
   문장은 지지되지 않는다.**  ⚠ 다만 CL-81 의 *"복셀 FV 는 접촉망의 `CONTACT_FREE` 가지 위에
   있다"* 라는 **구조적 결론 자체**는 이 판정이 부정하지 않았다 (오히려 CF 가 같은 접촉망의
   bulk-only 임을 확인했다).  무너진 것은 **그 배수를 실험 대비 과대율로 읽은 것**이다.
2. **"협착 45 %" 류 화면 문구** — 거시 기여도가 아니라 *"접촉별 협착 저항 비율의 비가중
   평균"* 으로 불러야 한다.
3. `L2-a` 질문에 내가 *"a → r 에서 발산하는 것이 의도인가"* 라고 물었는데, **발산도 극한도
   아니고 `ψ ≤ 1e-4` 에서 0 으로 떨어지는 절벽**이 답이었다.
