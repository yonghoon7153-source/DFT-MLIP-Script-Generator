# Codex 적대 리뷰 판정 — DEM 웹앱 스택 **L1** (2026-09-13)

> 요청서 = `docs/reviews/codex_request_dem_webapp_stack_20260913.md`
> 기준 스냅샷 = `d4bae885ac495f974cce2cb850734738dce445f3` · 브랜치
> `claude/sdcp-dem-manuscript-si-pqwtv8`.
>
> ⚠ **아래는 받은 판정문 전문이다.**  요약·재서술하지 않는다 (규율 ③: 한정어가 값이다).
> 링크의 `C:/Users/...` 경로는 Codex 검토 workspace 사본이고, 우리 리포의 대응 파일은
> 같은 상대경로(`scripts/…`, `webapp/…`)에 있다.
>
> ★ **독립 재현 = 완료** (이 리포에서, 아래 §부록).  `L1-CX-01·02·04·05` 를 소수 자리까지
> 재현했고 `L1-CX-03` 은 시그니처·상수로 확인했다.

---

# DEM 웹앱 스택 적대 리뷰 — L1 판정 및 교정 영향

작성: 2026-09-13
기준: d4bae885ac495f974cce2cb850734738dce445f3
브랜치: claude/sdcp-dem-manuscript-si-pqwtv8

## 판정

**L1 HOLD. 단위 오류를 고쳐도 현재 Physics 면적을 "검증된 물리 접촉면적"으로 승인할 수 없다.**

DESC-03을 재발견한 것으로 세지 않았다. 그 오류를 제거한 실제 함수 호출에서도 **상한 위반·lens 정의 불일치·상별 물성 혼용**이 남는다. DEM-native 기하량까지 모두 폐기하거나 130개 DEM을 다시 돌리라는 판정은 아니다. 기하 장부와 그 위에 얹은 소성·수송 모델을 분리해야 한다.

요청서가 허용한 층별 게이트에 따라 **정식 판정은 L1까지**다. 갱신 질문 (b)(c)를 위해 하류 솔버·최종 Stage-E 저장·생산식 getter를 제한적으로 실행/추적했지만, 이를 **L2~L5 전수 통과**로 세지 않는다. Phase A Q7은 별건으로 남긴다.

검증 범위:

- 핀된 소스를 변경하지 않은 detached checkout. 수정·커밋·원격 계산 제출 없음.
- 실제 helper / coverage producer / network CLI / Stage-E 호출을 합성 입력으로 실행.
- geometry 11사례, 감도 8사례, 최종 Stage-E 저장 전후 1사례, porosity·B3 및 생산식 getter 반례.
- **130/291 실코퍼스의 atoms/contacts와 화면 사례 원자료는 없음.** 발생률, 실제 평균 변화율, 스크린샷 Δ의 원인별 기여는 미측정.
- L1-CX-01~06은 이 회신용 신규 ID다. 리포 findings.json은 변경하지 않았다.

## 1. L1-1~L1-5 답변표

| 질문 | 판정 대상과 결과 |
|---|---|
| L1-1 | "max(lower,min(caps))가 물리적 상·하한을 동시에 지킨다" **REFUTED**. 얕은 겹침부터 불가능한 bounds를 정상 면적으로 반환한다. V/h_min의 물리적 타당성도 별도 미식별이다. |
| L1-2 | "큰 Δ는 정의 차이일 뿐이다" **REFUTED**. 단위 혼용에 더해 DEM-native 기하면적/Hertz 역학면적의 명칭 혼용이 있다. 화면 세 Δ의 원인을 이 오류 하나로 확정하지는 않는다. |
| L1-3 | ε_sphere의 구 부피합 bookkeeping은 **CONFIRMED**. 현재 ε_union이 정확한 구 합집합·실변형체 공극률이라는 해석은 **REFUTED**. RECORD_ONLY는 현 등록에서 기록·닫힘 검산용이다. |
| L1-4 | 검토한 producer는 없는 상 반경 키를 **생략**한다. 이 자리에서 0 센티넬 주입은 발견하지 않았다. 그러나 별도 수확기가 없으므로 130행까지 NaN 보존을 **CONFIRMED 할 수 없다**. 기존 DESC 판정 유지. |
| L1-5 | 검토 경로에서 B3 분모 **1회 적용은 CONFIRMED**. 이중 적용을 재현하지 못했다. 반면 "실제 찌그러진 형상을 반영한 가장 믿을 만한 면적"이라는 설명은 근거 부족이다. |

주 생산자는 정정된 `webapp/app.py:3271` → analyze_contacts_bimodal → analyze_contacts → dem_analysis_core다. `webapp/app.py:3292` 경로가 별도 Physics/rough coverage를 더한다. network→Stage-E는 같은 helper를 공유하는 별도 수송 경로이지, 모든 구조량의 주 생산자가 아니다.

## 2. 단위 혼용을 제거해도 남는 새 반례

### P1 · L1-CX-01 — 상한과 하한이 충돌해도 정상 Physics 면적을 낸다

`scripts/plastic_coverage.py:292` 에서 세 cap의 min을 취하고, `scripts/plastic_coverage.py:307` 에서 Hertz/LIGGGHTS floor와 max를 취한다.

하한 L=max(A_H,A_LIGG), 상한 U=min(A_Tabor,A_volume,A_geom)일 때 **L>U이면 모든 조건을 만족하는 A는 없다.** 현재는 이를 거부하지 않고 L을 반환한다. binding 이름은 feasibility 증거가 아니다.

실제 helper에 **물리 SI**를 넣은 반례:

- 동일 반경 r=0.5 μm, δ=2.5 nm, δ/R*=0.01.
- A_LIGG는 동일 두 구의 기하학적 교차면적.
- A_final = 0.00392208208 μm².
- A_Tabor = 0.00219754346 → **1.78476배 초과**.
- A_volume = 0.000489237606 → **8.01672배 초과**.
- 정상 plastic, binding=liggghts로 반환.
- V를 정확한 전체 lens로만 교체해 계산해도 lower>upper는 남는다.

**무너지는 결론:** "체적 보존 및 Tabor 상한으로 비물리 면적을 차단했다." 단위만 고치면 L1이 닫힌다는 결론도 무너진다.

min/max 순서만 뒤집으면 하한을 깨뜨릴 뿐이다. caps가 전체 접촉면적의 한계인지, 추가로 퍼진 막의 한계인지 먼저 정해야 한다. 불가능한 조합을 cap_conflict로 기록하고 검증된 Physics 값으로 승격하지 않는 것이 최소 코드 방어다.

### P1 · L1-CX-02 — V_overlap은 이름대로의 구 교집합이 아니다

근거: `scripts/plastic_coverage.py:284`.

    V_code = π δ²(3R*−δ)/6
    동일 반경의 정확한 전체 lens = π δ²(6r−δ)/12
    R* = r/2
    V_code / V_lens = (3r−2δ)/(6r−δ)

얕은 겹침에서도 약 1/2이다.

| 입력 | 정확한 전체 lens, μm³ | 코드 V_overlap, μm³ | 실제 처리 |
|---|---:|---:|---|
| r=.5 μm, δ=.0125 μm | .000122207136 | .000060336578 | 양수지만 0.493724배 |
| r=.5 μm, δ=.95 μm | +.484361592 | **−.094509579** | 거부 없이 양의 면적 반환 |

r1=5 μm, r2=.5 μm, δ=2 μm 내포 사례에서는 Hertz floor가 hemisphere cap도 **1.81818배** 넘는다. 깊은 사례는 정의역/거부 규약 반례이지 실제 발생률 측정이 아니다. 첫 행은 깊은 겹침에 의존하지 않는다.

**무너지는 결론:** "V_overlap은 구 겹침 부피이고 이 cap이 재료 체적을 보존한다."

전체 구 교집합을 의도했다면 두 반경·중심거리 기반 piecewise lens 및 내포·동심 처리가 필요하다. 한쪽 재료에 할당되는 부피를 의도했다면 **전체 lens라고 부를 수 없고**, 상별 분담식과 근거를 명시해야 한다. 기계적으로 전체 lens로 치환하라는 물리 승인도 아니다.

### P1 · L1-CX-03 — AM–AM·SE–SE도 AM–SE/SE 물성으로 계산한다

- `scripts/coverage_physics_vs_hertzian.py:214`: 상 분류 전에 동일 helper 호출.
- `scripts/plastic_coverage.py:277`: 전역 AM–SE E* 사용.
- `scripts/plastic_coverage.py:280`: 전역 SE hardness 사용.
- `scripts/coverage_physics_vs_hertzian.py:379`: SE–SE 및 AM–AM Physics 면적으로 기록.
- `scripts/network_conductivity.py:299`: 수송 경로도 같은 helper 사용.

단위를 일관되게 유지한 실제 compute_case에 동일 반경·겹침의 AM–AM / AM–SE / SE–SE 접촉을 넣었다. 세 helper 호출이 모두 **A=0.3610932373 μm², binding=tabor**다.

코드의 물성 상수로 reduced modulus만 독립 계산하면 AM–AM **74.6667**, AM–SE **22.4149**, SE–SE **13.1868 GPa**다. hardness/소성 상태도 pair 인자로 받지 않는다. 이 비교는 저장된 상수의 연산이며, 그 상수 자체를 실측 검증한 것은 아니다.

**무너지는 결론:** "상별 실제 물성으로 보정한 Physics 면적." 특히 SE–SE 이온 경로와 전상 열 경로의 해석을 지지하지 못한다.

지원 pair를 명시하고 미지원 pair를 조용히 Physics로 내지 않는 것은 코드로 방어할 수 있다. 정식 모델은 pair별 탄소성/경도/형상 규약을 필요로 한다. SE 경도 하나를 AM–AM에 적용하는 문제는 단위 수정으로 닫히지 않는다.

### P2 · L1-CX-04 — DEM-native 기하면적과 Hertz 면적을 같은 이름으로 읽게 한다

`scripts/parse_liggghts.py:47` 는 c_cpl[22]를 contact_area로 보존하고 `scripts/coverage_physics_vs_hertzian.py:206` 는 이를 Hertz 채널로 사용한다. 덱 생성도 contactArea를 요청한다: `scripts/make_heckel_inputs.py:64`.

공식 LIGGGHTS 문서는 contactArea를 역학 해가 아닌 **기하학적 교차면적**으로 구분한다. 공개 add_pair 구현도 두 반경·중심거리로 교차 원판을 계산한다. (공식 문서 `compute_pair_gran_local`, 공식 구현 `compute_pair_gran_local.cpp#L509-L517`)

동일 반경 구에서는:

    A_LIGG = π(rδ−δ²/4)
    A_Hertz = π(r/2)δ
    A_LIGG / A_Hertz = 2−δ/(2r)

r=.5 μm, δ/R*=.05이면 **1.9875배**다. 배포 fork/build와 실 dump는 확보하지 못했으므로 공식 구현 규약의 합성 입력임을 명시한다.

또 `scripts/plastic_coverage.py:273` 의 elastic 반환은 LIGG floor를 쓰지 않는다. δ/R*=yield/2 호출에서 Physics/DEM-native는 **0.50003536**이었다. "Physics는 항상 DEM-native보다 크다"도 전 구간 계약이 아니다.

**무너지는 결론:** Hertz라는 이름을 πR*δ로 해석하거나 두 열 차이를 "추가 소성면적"으로만 읽는 것. native 값 자체가 무의미하다는 뜻은 아니다.

권고 구분은 A_dem_geometric / A_hertz_elastic / A_plastic_model이다. 기존 키와 frozen feature를 세대 표시 없이 바꾸면 안 된다.

### P2 · L1-CX-05 — ε_union은 정확한 union이 아니라 pair-only 차감이다

`scripts/dem_analysis_core.py:72` 에서 pair lens를 합하고 `scripts/dem_analysis_core.py:94` 에서 구 부피합에서 뺀다. 삼중 이상 겹침의 inclusion–exclusion 항은 없다.

실제 함수 반례:

- 반경 1인 구 네 개, 중심은 한 변 .1인 정사면체. 모두 한 변 4인 상자 안에 완전히 들어 있다.
- 여섯 δ는 실제 중심거리에서 계산.
- ε_sphere = **73.8201%**, 반환 ε_union = **110.1472%**.
- 계산 union volume은 **−6.49420**.
- 실제 union은 구 하나를 포함하므로 최소 부피 4.18879, 공극률은 **93.4550% 이하**.
- 구 두 개 control은 정확한 lens와 일치.

이는 극단 입력의 범위 반례이지 실코퍼스 오차율 추정이 아니다. 삼중 겹침이 있으면 극단적이지 않아도 정확한 union과 다른 양이다.

`scripts/recompute_porosity_dual.py:337` 는 기존 porosity를 다시 앵커로 사용하고, `scripts/recompute_porosity_dual.py:344` 는 sphere 범위만 검사한다. 위 sphere 값은 검사 창 안이므로 해당 조건만으로 union>100을 막지 못한다. 이 fixture로 CLI 전체 반입을 실행한 것은 아니다.

**무너지는 결론:** 이 열을 정확한 합집합/실변형체 공극률로 바로 문헌과 비교하는 것. `webapp/app.py:8703` 의 "항상 살짝 크다"도 보장되지 않는다.

정확한 구 union이 필요하면 상자/주기 경계를 포함한 union 계산 또는 수렴 검증된 voxel/적분법이 필요하다. 실제 소성 형상의 공극률은 또 별개다. 음의 ε_sphere는 실제 음의 빈 공간이 아니라 구 부피합·상자·변형 가정의 적용범위 문제다.

### P2 · L1-CX-06 — B3는 실제 변형 형상을 측정하지 않는다

`scripts/dem_analysis_core.py:28` 의 phase 상수 AM_P=1.40, AM_S=1.10, SE=1.05를 쓴다. 원 생산 coverage는 `scripts/dem_analysis_core.py:172` 의 기본 apply_shape_factor=False이고, 비교기 `scripts/coverage_physics_vs_hertzian.py:278` 에서 rough 분모를 만든다.

비포화·양의 분모에서:

    raw   = A_Physics / (S_sphere − A_AMAM_native)
    rough = A_Physics / (α S_sphere − A_AMAM_native)

실제 producer 호출에서 α를 1로 바꾸면 Hertz/Physics raw는 그대로이고 rough만 raw와 같아졌다. AM_P rough/raw **0.71301253**, AM_S **0.90857469**로 위 식과 일치한다. AM–AM 공제 때문에 단순 1/α도 아니다.

검토한 network/Stage-E는 rough coverage를 σ 입력으로 직접 쓰지 않는다. **이 경로에서 B3 이중 적용은 발견하지 않았다.** 앱의 모든 소비자 전수 승인은 아니다.

**무너지는 결론:** `webapp/app.py:8737` 의 "찌그러진 모양까지 반영한 가장 믿을 만한" 값이라는 설명. 실제 입자 형상을 복원하지 않고 phase 상수로 분모를 바꾼다. 규약 감도로 병기는 가능하지만 검증된 형상 측정값으로 승격할 수 없다.

## 3. 갱신 질문 (a) — 단위를 고친 V/h_min은 올바른 cap인가?

**조건부 체적 예산으로는 가능하지만, 현재 전체 접촉면적 cap으로는 정당화되지 않는다.**

두께 h(x)≥h_min인 막이 A_film 위에 있고, 사용 가능한 재료 부피 V_available이 독립적으로 정해지면:

    V_film = ∫ h(x) dA ≥ h_min A_film
    A_film ≤ V_available / h_min

이 부등식은 맞다. 현재는 다음 연결이 없다.

1. 가상 구 겹침 부피가 어느 상의 이동 가능한 재료량인가.
2. 막이 기존 elastic contact와 별개인가, 전체 load-bearing 면적인가.
3. 5 nm가 해당 재료·압력·온도·길이 범위의 최소 두께인가.
4. 재구성한 Hertz force가 연화 DEM의 하중·잔류변형·이력과 양립하는가.

고정 h_min 자체가 차원적으로 틀리지는 않는다. **반드시 h(a)로 바꿔야 한다는 결론도 아니다.** 고정 두께가 독립적으로 검증됐다면 하나의 모델이 될 수 있다. 반대로 임의의 접촉반경 함수로 바꾼다고 물리가 생기지는 않는다.

코드가 5 nm 근거로 지목한 Sakuda 2013 본문은 Li2S–P2S5 glass의 성형·밀착·밀도/탄성률 등을 다룬다. 본문에서 **LPSCl 전체 접촉면적용 5 nm 최소막 cap을 제시하지 않는다.** 이 인용만으로 해당 상수를 앵커했다고 할 수 없다. 보충자료와 모든 후속 논문까지 부재를 증명했다는 뜻은 아니다. (Sakuda et al., Scientific Reports 3, 2261)

현재 softened-DEM δ·두 반경만으로 실제 소성 접촉을 유일하게 복원할 수 없다. 탄성 회복, pile-up/sink-in, 압쇄·거칠기 상태를 식별할 정보가 부족하다. **기하 지표 보존은 가능하지만 이 한 식을 실제 소성면적으로 승인하는 것은 불가능**하다.

대체 방향은 pair별 검증된 탄소성 contact law와 하중/잔류상태를 함께 추적하는 모델, 또는 독립적으로 검증한 형상 해석이다. 구–평면 탄소성 연구도 접촉면적·하중·평균압의 전이를 함께 다룬다. 그 모델이 LPSCl/AM에 그대로 검증됐다는 뜻은 아니다. (Kogut & Etsion 2002)

## 4. 갱신 질문 (b) — coverage와 σ는 얼마나 움직이는가?

### "교정 후 대부분 volume이 binding"은 아직 증명되지 않았다

저자의 단위 반례는 **A_LIGG=A_Hertz로 놓은 입력에서 유효**하며 철회할 이유가 없다. 같은 r=.5 μm, δ/R*=.05에 공식 LIGGGHTS 기하면적을 넣으면:

- A_LIGG/A_Hertz = 1.9875.
- 단위 교정 후 코드 volume cap/A_Hertz = 1.229167.
- 따라서 최종 선택은 volume이 아닌 **LIGG floor**다.
- 이전 toy의 .78206456% → .38411458%와 달리 이 입력은 **.78206456% → .62109375%**다.

단위·lens·상별 모델 변경은 서로 다른 intervention이다. 아래는 H_FILM_MIN의 좌표 단위만 일관화한 영향이며 정확한 lens 교체 등은 포함하지 않는다.

### 실제 coverage 및 network의 합성 실행

scale=1000 메모리에서 H_FILM_MIN을 5e−9 → 5e−6으로 바꿨다. 이는 sim 좌표의 5 nm를 표현한 테스트이지 모든 생산 상수를 5e−6으로 바꾸라는 패치가 아니다.

세 줄 모두 동일 구의 기하 교차면적을 입력했고 원 접촉망은 전후 동일하다.

| 합성 조건 r / δ/R* | Physics coverage: 현행 → 단위만 교정 | raw graph 이온 σ_Physics 변화 |
|---|---:|---:|
| .5 μm / .05 | .78206456 → .62109375% | **−6.7115%** |
| .1 μm / .4 | 17.69610 → 4.75000% | **+204.1240%** |
| .5 μm / .005 | .06246094 → 동일 | **0%** |

Hertz-명명 coverage/σ는 세 줄에서 불변이다. 별도 elastic·geom-binding control도 단위 영향 0이었다.

면적이 줄어도 σ가 증가하는 이유는 현재 Physics edge 저항이 `scripts/network_conductivity.py:396` 에서 **1/[2a(1−a/r)^1.5]**를 사용해 비단조이기 때문이다. 이 법칙의 물리적 타당성 및 전체 L2는 승인하지 않는다. 위 표는 기존 코드의 실행 응답이다.

### 최종 Stage-E 저장값까지 확인한 1사례

Stage-E는 coverage 숫자에 비례해 σ를 곱하지 않는다. `scripts/run_network_full_corrections.py:399` 에서 원접촉의 **contact_area와 δ를 함께 수정**해 network CLI를 다시 실행한다.

위 .1 μm / .4 사례:

| 단계 | 현행 → 단위만 교정, mS/cm |
|---|---:|
| raw graph Physics | .016513 → .050220 |
| Stage-E contact-resolve 중간값 | .041903 → .049967 |
| **최종 run_one 저장값** | **.0138859318 → .049967** |
| 최종 Hertz-명명 값 | .082544 → .082544 |

최종 Physics 변화는 **+259.8390%**다. 각 variant의 raw baseline을 새로 생성한 뒤 원본 run_one을 실행했다. 과거 캐시와 혼합한 비교가 아니다.

현행은 중간값이 1.1×baseline을 넘어 `scripts/run_network_full_corrections.py:757` / `:801` 의 weighted-factor fallback으로 바뀌고, 교정판은 solver 값을 저장한다. 중간 +19.2444%와 최종 +259.8390%를 섞으면 안 된다.

**실코퍼스 평균·최대오차·물리 예측이 아니다.** "σ도 coverage의 제곱근만큼 줄 것"이라는 환산을 반증한다. 화면 +281.6/+299.4/+270.3% 사례에 이 변화율을 적용하지 않는다.

실제 규모를 닫으려면 원자료별로 다음을 재계산해야 한다.

- 상 쌍·δ/R*별 census, cap_conflict·음수 volume·elastic 반환 수.
- 최종 binding/면적 분포, coverage clipping 전후.
- raw network와 최종 Stage-E의 양 채널 σ 및 solver/fallback 선택.
- 입력·scale·상자·타입맵·코드/규약 세대와 결과의 1:1 연결.

GPU 130개 DEM 재실행이 먼저 필요한 것은 아니다. 보존된 atoms/contacts로 가능한 후처리부터 재계산한다. 원자료/하중 이력이 부족해 새 물리 모델을 식별하지 못하는 부분은 추가 해석·측정 문제로 분리한다.

## 5. 갱신 질문 (c) — 재적합 대상

**Hertz feature이면 안전하다는 추론은 틀린다. feature와 target을 따로 봐야 한다.**

| 생산식 | 실제 의존성 | 단위만 교정했을 때 |
|---|---|---|
| 이온 T1, cov^0.5 | y는 **Physics Stage-E 우선**, coverage는 Hertz-명명 우선 | 정상 행도 y가 변할 수 있다. 기존 계수의 새 데이터 오차부터 재평가. 영향 행이 있으면 기존 고정 구조 안의 LIVE 재적합 후속이 필요하다. |
| 전자 22.5, sqrt(A_AMAM) | y는 Hertz Stage-E/raw 우선. 면적은 원 contact_area의 AM–AM 평균 | 보통 직접 불변. 그러나 Hertz 후보 탈락 뒤 **Physics fallback 행**은 y/포함집합이 달라질 수 있다. 실제 y·X·ID 대조 없이 "영향 없음"으로 닫지 않는다. |
| 열 T1 | y는 Physics 우선. 두 area_*_physics 선형 feature와 Physics 관련 항 사용 | y와 X 모두 바뀔 수 있다. 새 X/y의 성능 재평가 및 동일 등록 구조 내 LIVE 재적합 대상이다. |

근거:

- 이온: `scripts/generate_comparison_plots.py:4222` · `:4687` · `:4689`.
- 전자: `scripts/generate_comparison_plots.py:5799` · `:5816` · `:5953` · `:6050`.
- AM–AM 면적 원천: `scripts/dem_analysis_core.py:355` · `scripts/analyze_contacts.py:440`.
- 열: `scripts/generate_comparison_plots.py:6741` · `:6783` · `:6835`.

실제 getter를 합성 입력으로 실행:

    (ionic y, cov feature, electronic y)
    Physics 수정 전: (3, 0.1, 11)
    Physics 수정 후: (6, 0.1, 11)
    electronic Physics fallback: 12 → 24

소스 문자열 검사가 아니라 해당 함수 return의 실행 결과다. 전체 fitting/코퍼스 재적합은 하지 않았다.

주의:

1. native 면적을 πR*δ로 바꾸는 것은 **단위 수정이 아닌 feature 정의 변경**이다. 이때 위 "보통 Hertz 불변"을 적용할 수 없다.
2. thermal ridge는 면적 선형 열을 표준화하지 않는다. 단순 단위 재표현도 계수/penalty를 일관되게 바꾸지 않으면 같은 α에서 적합 결과가 달라질 수 있다.

### 별도 사전등록 사안 — 계수 변경을 승인한 것이 아니다

후속 결과를 보기 **전**에 평가·재적합 절차를 등록한다. 기존 데이터를 이미 보았으므로 최초 사전등록으로 소급 주장하지 않고 **오류 교정 후속 프로토콜**로 표시한다.

- 새 면적/체적/상별 모델·단위 API, 구규약 병행 보존.
- 동일 ID·실패/결측·fallback 처리와 포함집합 비교.
- **LOCKED 지수, EXCL, φ_c, endpoints/drop set 및 검증 분할 유지**.
- 먼저 기존 계수를 새 데이터에 그대로 평가. 다음으로 등록된 LIVE 계수만 재적합한 결과를 별도 보고.
- 유리한 모델/지수/문턱 재선택을 버그 수정에 끼워 넣지 않는다. 필요하면 별도 모델 변경으로 등록한다.
- 새 계수·원고 채택은 별도 검토. 이번 합성 감도는 채택 승인이 아니다.

`scripts/run_network_full_corrections.py:706` / `:734` 의 unity 분기는 기존 baseline을 재사용한다. 따라서 **coverage·raw Physics network → Stage-E → 생산식 데이터셋** 순으로 새 세대를 만들어야 한다. Stage-E만 돌려 값이 같았다는 것은 불변성 증명이 아니다.

## 6. ε_sphere·mono와 기존 디스크립터 판정의 연결

- ε_sphere = 100(1−Σ 4πr_i³/3 / V_box). 구 겹침을 빼지 않는 규약이다. AM+SE와 동일 상자 조건에서 φ_SE+φ_AM+ε_sphere/100=1이므로 독립 target으로 세지 않는다.
- 현 등록은 RECORD_ONLY를 기록/검산으로 정했다: `docs/lhs_design_dataset_20260818.md:219`. 다른 연구에서 공극률을 타깃으로 삼는 것 자체를 금지한다는 뜻은 아니다.
- 1.251%p는 해당 자료의 차이지 일반 보정 상수가 아니다. pair overlap도 배치마다 다르고 정확 union/변형체 부피와도 구별해야 한다.
- 없는 상 반경은 `scripts/analyze_contacts.py:346` 의 if sub에서 키가 생략된다. 없는 상 N/A와 존재상 접촉 0을 구분한다.
- end-to-end 수확기가 없으므로 새로운 NaN 보존 보증은 발행하지 않는다. 기존 DESC-01/02의 φ 누락·τ 문제도 단위 교정으로 닫히지 않는다.
- 이 회신은 기존 디스크립터 판정을 대체하지 않는다.

## 7. 국소 교정과 모델 교체의 경계

| 코드·계측 교정 가능 | 현재 입력·연산자로 물리 승인 불가 |
|---|---|
| helper 경계 SI 통일, 면적 반환 단위·scale 동치 검사 | softened DEM 최종 overlap만으로 실제 소성 접촉 복원 |
| 전체 lens가 필요하면 정확식·내포/동심 처리 | lens를 모든 상의 이동 가능한 film 부피로 자동 해석 |
| cap_conflict·비유한·상 미지원 상태 구분 및 전파 | 하나의 AM–SE/SE E*/H로 모든 상 쌍을 물리 보정 |
| native/Hertz/model/B3 이름 및 cache 세대 분리 | B3 상수로 실제 변형 형상을 측정했다고 주장 |
| sphere-sum·pair proxy·정확 union 구분 | 구 union을 실변형체 물질 보존 공극률로 승격 |

**전체 스택 재작성부터 시작할 필요는 없다.** 기하 ledger를 보존하고 모델 면적 연산자와 단위·상·실패 계약을 먼저 분리한다. 실제 물리 면적이 필요하면 pair별 탄소성/형상 모델과 독립 면적·하중 증거를 갖춘 대체 연산자가 필요하다.

L1 해제 검토에는 단위 동치뿐 아니라 shallow cap 충돌, lens 해석, native/Hertz 구분, pair 지원 범위를 닫은 diff·실행 증거가 필요하다. 경험적 규약 모델로 남기려면 검증된 물리라는 라벨을 철회하고 불확실성·적용범위를 그에 맞게 제한해야 한다.

## 8. 재현 및 증거

합성 입력만 사용한다. source는 읽고 fixture 산출물은 임시 폴더에 쓴다. numpy/scipy/pandas/networkx 사용.

재현기 4개(`probe_contact_geometry.py` · `probe_porosity_b3.py` · `probe_refit_getters.py` ·
`probe_stack_sensitivity.py`) 모두 rc=0.  이는 **반례 재현이 정상 종료했다는 뜻**이지 대상
모델 PASS가 아니다. check_all 전체는 이번 회신에서 재실행하지 않았으며, 자기검사 초록을
물리 타당성 증거로 사용하지 않았다.

---

## 부록 — 이 리포에서의 독립 재현 (2026-09-13, claude)

판정문의 반례를 **우리 트리의 실제 함수**로 돌렸다.  Codex 사본이 아니라 `HEAD` 다.

### L1-CX-01 — 하한 > 상한인데 정상 반환 ✅ **소수 자리까지 일치**

`plastic_coverage.film_area_from_overlap` 에 **SI** 로 r=0.5 µm · δ/R\*=0.01 ·
`ligg_area` = 동일 두 구의 기하 교차 원판 `π(rδ − δ²/4)` 를 넣으면:

```
regime=plastic  binding=liggghts   A_final = 3.92208207847e-15 m²
lower L = 3.92208207847e-15   upper U = 4.89237605950e-16   L > U ?  True
A_final / A_tabor  = 1.784757     (판정문 1.78476)
A_final / A_volume = 8.016722     (판정문 8.01672)
```

⇒ **모든 cap 을 동시에 만족하는 A 가 없는데 거부하지 않고 하한을 돌려준다.**
`binding` 이름(`liggghts`)은 feasibility 증거가 아니다 — 판정문 그대로다.

### L1-CX-02 — `V_overlap` 이 참 lens 가 아니다 ✅ **음수까지 재현**

| δ | 정확한 전체 lens (µm³) | 코드 `V_overlap` (µm³) | 비 |
|---|---:|---:|---:|
| 0.0125 µm | +0.000122207136 | +0.000060336578 | **0.493724** |
| 0.9500 µm | +0.484361592352 | **−0.094509578995** | −0.195122 |

해석식 `(3r−2δ)/(6r−δ)` 를 δ=0.0125 µm 에 넣으면 **0.493724** — 실측과 같다.
⇒ 얕은 겹침에서도 **절반**이고, 깊어지면 **음수 부피**가 되는데 **거부 없이 양의 면적**이 나온다.

### L1-CX-03 — 상 쌍을 인자로 받지 않는다 ✅ 확인

```
시그니처: ['delta', 'R_star', 'R_min', 'ligg_area', 'mode', 'k_spread', 'return_components']
→ phase/pair/E*/hardness 인자: 없음
본문이 쓰는 전역 상수: E_REAL · E_STAR · E_STAR_AM_SE · H_FILM_MIN · H_REAL_SE
  E_REAL_AM = 1.40e11 · E_REAL_SE = 2.40e10 · E_STAR_AM_SE = 2.2414943e10 · H_REAL_SE = 8.5e8
```
⇒ AM–AM·SE–SE 접촉도 **AM–SE 의 E\* 와 SE 의 경도**로 계산된다.  상 쌍을 받을 자리 자체가 없다.

### L1-CX-04 — `contact_area` 는 Hertz 가 아니라 기하 교차면적 ✅ 일치

```
A_LIGG / A_Hertz  실측 1.987500   해석 2 − δ/(2r) = 1.987500   (판정문 1.9875)
```

★★ **이것이 오늘 쓴 수확기에 직접 걸린다** — `lhs_descriptor_harvest.py` 가 등록 별칭
`coverage_AM_*_hertz_pct` 의 분자로 `c_cpl[22]` 를 쓴다.  docstring 은 *"LIGGGHTS 가 보고한
`contact_area` 다 — `πR*δ` 를 다시 계산하는 것이 아니다"* 라고 이미 옳게 적었지만, **별칭의
`hertz` 라는 낱말이 오해를 물려받는다**.  ⇒ `area_channel` 필드를 출력에 추가해
`dem_geometric_c_cpl22 (NOT hertz-elastic πR*δ; ratio 2−δ/2r)` 를 매 행에 박는다.
(별칭 자체는 등록된 이름이라 바꾸지 않는다 — 판정문도 *"기존 키와 frozen feature 를 세대
표시 없이 바꾸면 안 된다"* 고 적었다.)

### L1-CX-05 — `ε_union` 이 100 % 를 넘는다 ✅ **소수 자리까지 일치**

반경 1 인 구 4개를 한 변 0.1 정사면체로 놓고 (한 변 4 상자 안에 완전히 들어간다)
실제 `calc_porosity_dual` 에 여섯 접촉 δ 를 주면:

```
ε_sphere = 73.8201 %            (판정문 73.8201)
ε_union  = 110.1472 %  > 100    (판정문 110.1472)
union 부피 = −6.49420           (판정문 −6.49420)
참 union 하한(구 1개) = 4.18879 ⇒ 참 ε ≤ 93.4550 %   (판정문 93.4550)
[대조] 2구 lens 코드 = 3.874892739 = 정확값 3.874892739  ✓ 일치
```
⇒ 2구 대조가 **정확히 맞으므로** 결함이 **삼중 이상 겹침의 inclusion–exclusion 부재**로
특정된다.  일반적인 식 오류가 아니다.

### 내 요청서가 틀린 곳 — 판정문이 고친 것

1. *"큰 Δ 는 정의 차이뿐"* → **REFUTED** (이미 `DESC-03` 에서 철회했고, 여기서 **명칭 혼용**이
   추가됐다: DEM 기하면적 ↔ Hertz 역학면적).
2. *"Physics 는 항상 DEM-native 보다 크다"* → **전 구간 계약이 아니다**
   (`plastic_coverage.py:273` elastic 반환은 LIGG floor 를 안 쓴다 — 비 0.50003536).
3. *"교정하면 대부분 volume 이 binding"* → **미증명**.  내 반례가 `A_LIGG = A_Hertz` 를 가정한
   입력이어서다.  공식 LIGGGHTS 기하면적을 넣으면 최종 선택은 **LIGG floor** 이고
   0.78206456 % → **0.62109375 %** 다 (내 toy 의 0.38411458 % 가 아니다).
   ⚠ 내 `DESC-03` 반례 자체는 **철회되지 않는다** — 판정문이 *"그 입력에서 유효하며 철회할
   이유가 없다"* 고 명시했다.  적용 범위가 좁혀진 것이다.
4. *"Hertz 전용 타깃이면 안전"* → **틀렸다**.  feature 는 Hertz-명명이어도 **y(타깃)가
   Physics Stage-E 우선**이라 이온·열은 영향을 받는다.

### ⚠ 섞지 말 것

`coverage −73.2 %` 인데 최종 Stage-E `σ +259.8390 %` — **부호가 반대**다.  원인은
`network_conductivity.py:396` 의 `1/[2a(1−a/r)^1.5]` 가 **비단조**이고 Stage-E 가
1.1×baseline 초과 시 **weighted-factor fallback** 으로 갈아타기 때문이다.
⇒ *"σ 는 coverage 의 제곱근만큼 움직인다"* 는 환산은 **반증됐다**.
⛔ 이 비율을 화면 Δ(+281.6/+299.4/+270.3 %)나 실코퍼스에 **적용하지 않는다** — 전부 합성
입력이고 발생률은 미측정이다.
