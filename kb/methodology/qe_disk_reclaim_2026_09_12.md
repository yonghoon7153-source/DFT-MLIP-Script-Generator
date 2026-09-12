---
title: "QE 디스크 회수 절차 — 파동함수는 스크래치, 정본은 텍스트 (kgy 2026-09-12, 306 GB)"
date: 2026-09-12
updated: 2026-09-12
tags: [ops, disk, qe, kgy, gabia, neb, reclaim]
status: 채택
confidence: high
verificationStatus: verified
explored: false
authoredBy: agent
effort: medium
claimType: procedural
evidenceScope: single-machine
---

# QE 디스크 회수 절차

kgy 가 **95 % (남은 50 GB)** 로 찼다. 한 번에 **305.7 GB** 를 되찾았고
(793G → 487G · 남은 383 GB · 57 %), 결과값은 하나도 안 잃었다.
같은 일이 gabia·KISTI 에서도 생기므로 **순서**를 남긴다.

## 1. 왜 찼나 — 숫자가 먼저

| 종류 | 개수 | 크기 |
|---|---|---|
| `.save` 안 수집본 (`wfc*.dat`) | 3394 | **384 GB** |
| outdir 스크래치 (`*.wfc[0-9]+`) | 74 | 163 GB |
| `charge-density.dat` | 184 | 11.5 GB |

⚠ **큰 파일 top 25 를 보고 판단하면 틀린다.** top 25 는 전부 `tmp/*.wfc1`
(스크래치)이었지만 **합계는 `.save` 쪽이 2.4배**였다. 종류별 합계를 따로 세라.

## 2. 무엇이 지워도 되는가 — 세 등급

- **버린다: 파동함수.** QE 는 계산 중 k점 파동함수를 `outdir/tmp/<prefix>.wfc1` 로
  흘리고, `wf_collect` 로 `<prefix>.save/wfc*.dat` 에 모은다. 둘 다 **재시작·후처리
  (projwfc PDOS · pp.x ELF)** 에만 쓰인다.
- **남긴다: `charge-density.dat` + `data-file-schema.xml`.** 이게 있으면 nscf 를
  전하밀도에서 **다시 돌릴 수 있다** — 즉 파동함수 삭제는 되돌릴 길이 있는 삭제다.
  밴드갭 규율상 fixed-occupations nscf 가 유일한 인정 경로라 이 둘은 손대지 않는다.
- **절대 안 건드린다: `.out` · NEB `.dat`/`.int`/`.path`/`.axsf` · 도는 잡의 outdir.**

## 3. 순서 (이 순서를 바꾸지 않는다)

1. **도는 잡을 먼저 찍는다** — `pgrep -af "pw.x|neb.x|melt_quench|disorder_ensemble"`.
   ⛔ **래퍼 bash 가 살아 있는 것을 "돌고 있다" 로 읽지 마라.** 2026-09-12 에
   `run_gap_nscf_gabia.sh` 래퍼(pid 2400966)가 살아 있어 내가 실행 중으로 판단했는데,
   로그 마지막 두 줄이 `nscf_dos 완료` → `Terminated` 였다. **2일 전에 죽은 잡**이었다.
   판정 근거는 프로세스가 아니라 **로그 꼬리와 출력 mtime** 이다.
2. **정본이 무엇인지 원장에서 확인한다.** 지우기 전에 `db/properties/` 를 본다.
   · `lpsocl_dos_gap.json` → `data_source` 가 `01_relax_v0.out`·`03b_nscf_gap.out`·
     `lpsocl_v0_gap.txt` = **텍스트**. 값(2.2309 eV)은 레지스트리에 있다 → 파동함수 불필요.
   · `vgcf_hbn_neb.json` → 7개 장벽·방법·수렴이 전부 등록돼 있다 → 마찬가지.
   원장에 값이 없으면 **먼저 등록하고** 지운다.
3. **완료 여부를 출력에서 확인한다.** scf/nscf 는 `JOB DONE`, NEB 는
   `neb: convergence achieved` + `activation energy`. 미완이면 그 런은 건너뛴다
   (재시작에 파동함수가 필요하다).
4. **파동함수만 지운다.**
   ```
   find <루트> \( -path '*.save/wfc*' -o -regex '.*\.wfc[0-9]+' \) -type f -delete
   ```
5. **정본이 남았는지 되확인한다** — `.dat`/`.int` 목록 · `charge-density.dat` 개수 ·
   `grep "activation energy"` 가 여전히 읽히는지. 확인 전에는 끝난 게 아니다.

## 4. 실측 (kgy 2026-09-12)

| 대상 | 회수 | 근거 |
|---|---|---|
| `work/lpsocl_v0/tmp/lpsocl_v0.wfc1` | 14.6 GB | 정본 = `.out`, 값 등록됨, 3×3×1 캠페인 2026-09-11 닫힘 |
| `work/lpsocl_v0/tmp/lpsocl_v0.save/wfc*` | 13.6 GB | 같음. charge-density 보존 |
| `work/vgcf_hbn` 전체 (913 파일) | **305.7 GB** | NEB 7개 전부 수렴 · 값 `vgcf_hbn_neb.json` 에 등록 |

남겨둔 것(회수량이 작고 정본 위치가 불확실): `Yonghoon-DEM-DFT/tmp` d0~d6 `.save` 12 GB ·
`work/li3n_dft`+`li3n_eads` 15 GB (`JOB DONE` 6개는 확인했으나 값 등록 위치 미확인).

## 5. 안 한 것 · 하지 말 것

- **`.cache` 를 지우지 않았다** — 그때 modelc 9런의 torch inductor 컴파일 워커가 쓰고 있었다.
  MLIP MD 가 도는 중에는 `.cache`(inductor·huggingface)를 건드리지 않는다.
- **`charge-density.dat` 11.5 GB 를 남겼다** — 아끼려고 nscf 를 다시 돌릴 이유가 없다.
- **도구로 만들지 않았다.** 판단(정본이 뭔지·끝났는지)이 매번 다르고, 자동화하면
  그 판단이 생략된다. 이건 스크립트가 아니라 **절차**다.

## 반론

- *"`.save` 를 통째로 지우면 더 빠르다"* — 맞지만 `charge-density.dat` 과 스키마가 같이
  날아가고, 그러면 후처리가 필요해질 때 **scf 부터** 다시다. 파동함수만 지우면 nscf 만 다시다.
- *"top 25 만 보면 충분하다"* — 위 §1 이 반례다. 이번엔 종류별 합계가 2.4배 뒤집혔다.
- *"수렴했으면 `.out` 도 필요 없다"* — 아니다. 우리 규율에서 밴드갭·장벽의 **인정 경로가
  `.out` 의 고유값·에너지**다. `.out` 은 정본이다.
