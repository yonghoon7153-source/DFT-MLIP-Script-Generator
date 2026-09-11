#!/usr/bin/env python3
"""Scaffold a new wiki page with correct frontmatter (wiki/SCHEMA.md).

Usage:
  python3 wiki/tools/new-page.py <type> <slug> [--title "Display Title"]

  type: paper-note | mechanism | protocol | experiment | concept | entity | comparison |
        query | guide | research-question | synthesis
  slug: lowercase-hyphens (becomes the filename and [[wikilink]] target)

Creates the file with today's dates, explored: false, verificationStatus: unverified,
and a body skeleton for the type. Refuses to overwrite. Reminds you of the SCHEMA
follow-ups (index/log/links). No model identifier is written anywhere (root hard rule).
"""
import argparse
import datetime
import pathlib
import re
import sys

BASE = pathlib.Path(__file__).resolve().parent.parent
FOLDER = {'paper-note': 'papers', 'mechanism': 'mechanisms', 'protocol': 'protocols',
          'experiment': 'experiments', 'concept': 'concepts', 'entity': 'entities',
          'comparison': 'comparisons', 'query': 'queries', 'guide': 'guides',
          'research-question': 'questions', 'synthesis': 'syntheses'}

PAPER_BLOCK = """raw: raw/papers/{slug}.md
paper:
  bib:
    first_author: null
    authors: null
    year: null
    journal: null
    title: null
    doi: null
    doi_missing_reason: null
  supplementary:
    files: []
    raw: null
  cathode:
    composition_verbatim: null
    ni_content: null
    crystal: null
    coating: null
    coating_type: null
    electrode_process: null
    loading_mg_cm2: null
    loading_mah_cm2: null
    composite_ratio: null
  electrolyte:
    type: null
    detail: null
  anode:
    type: null
    composition: null
  voltage:
    raw_text: null
    reference_raw: null
    window_vs_li: null
    offset_applied_v: null
    notes: null
  formation:
    described: null
    cutoff_v_raw: null
    cutoff_v_li: null
    c_rate: null
    cycles: null
    rest_h: null
    temperature_c: null
  main_cycle:
    window_raw: null
    window_vs_li: null
    c_rate: null
    temperature_c: null
    pressure_fab_mpa: null
    pressure_op_mpa: null
    cycles: null
  performance:
    initial_discharge_mah_g: null
    ice_pct: null
    retention_pct: null
    retention_cycles: null
    overpotential_trend: null
    hysteresis_trend: null
    notes: null
  techniques: []
  mechanisms: []
"""

# type-specific frontmatter lines (SCHEMA.md 타입별 추가 키)
EXTRA_FM = {
    'research-question': 'status: open\nfeedsInto:\n',
    'synthesis': 'targetVenue:\n',
    'paper-note': PAPER_BLOCK,
}

SKELETON = {
    'paper-note': ("## 한 문단 요약\n\n\n## 핵심 주장과 근거 (figure/page)\n\n| # | 주장 | 근거 | 메커니즘 태그 |\n|---|---|---|---|\n\n"
                   "## 우리 연구와의 접점\n\n(전압 기준전극·양극 조성·온도·압력·loading 차이를 먼저 적는다)\n\n"
                   "## 우리 DOE 창과의 관계\n\n\n## 비판·공백\n\n"),
    'mechanism': ("> [!note] 미검증 배경 — 근거 논문이 ingest 되기 전에는 인용 근거가 아니다.\n\n"
                  "## 정의\n\n\n## 왜 이 연구에서 중요한가\n\n\n## 관측 지표 (무엇을 재면 보이는가)\n\n\n"
                  "## formation cut-off 와의 관계 (가설)\n\n\n## 근거 상태\n\n- 위키에 근거 논문: 없음\n- 투입 예정 논문:\n\n"),
    'protocol': "## 목적\n\n\n## 조건 (사용자 진술의 사본 — 정본은 실험 노트·registry)\n\n| 항목 | 값 |\n|---|---|\n\n## 절차\n\n\n## 기록해야 할 것\n\n",
    'experiment': "## 설계\n\n\n## 변수와 고정 조건\n\n| 변수 | 수준 |\n|---|---|\n\n## 측정·산출물\n\n\n## 상태\n\n",
    'concept': "## 정의\n\n\n## 왜 중요한가\n\n\n## 이 위키에서의 적용\n\n",
    'entity': "## 개요\n\n\n## 핵심 사실\n\n\n## 이 위키와의 관계\n\n",
    'comparison': "## 비교 이유\n\n\n## 비교표\n\n| 기준 | A | B |\n|---|---|---|\n\n## 결론\n\n\n## 불확실성\n\n",
    'query': "## 질문\n\n\n## 짧은 답\n\n\n## 근거\n\n\n## 다음 행동\n\n",
    'guide': "## 목적\n\n\n## 절차\n\n",
    'research-question': ("> [!question] 질문 한 문장\n>\n\n## 왜 중요한가\n\n\n"
                          "## 가설\n- H1:\n\n## Evidence For\n\n\n## Evidence Against\n\n\n"
                          "## Status Log\n- [YYYY-MM-DD] open —\n"),
    'synthesis': ("## Thesis\n(방어하는 한 문장 주장)\n\n## Argument\n\n\n"
                  "## Counter-arguments\n(경쟁 가설·반론 — 삭제하지 않고 보존)\n\n"
                  "## Gap\n(아직 빈 근거, 추가 조사 지점)\n\n"),
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('type', choices=FOLDER)
    ap.add_argument('slug')
    ap.add_argument('--title', default=None)
    args = ap.parse_args()

    if not re.fullmatch(r'[a-z0-9]+(-[a-z0-9]+)*', args.slug):
        sys.exit(f'slug must be lowercase-hyphens: {args.slug!r}')

    path = BASE / FOLDER[args.type] / f'{args.slug}.md'
    if path.exists():
        sys.exit(f'refusing to overwrite existing page: {path}')

    title = args.title or args.slug.replace('-', ' ').title()
    today = datetime.date.today().isoformat()
    extra = EXTRA_FM.get(args.type, '').format(slug=args.slug)
    fm = f"""---
title: {title}
description: ""
created: {today}
updated: {today}
type: {args.type}
tags: []
sources: []
confidence: medium
explored: false
verificationStatus: unverified
claimType:
evidenceScope:
{extra}---

# {title}

{SKELETON[args.type]}
## 관련
-
-
"""
    path.write_text(fm, encoding='utf-8')
    print(f'created {path.relative_to(BASE.parent)}')
    print('SCHEMA follow-ups:')
    print('  1. tags 를 wiki/SCHEMA.md taxonomy 에서 채우기')
    print('  2. sources 에 근거 raw 파일 경로 넣기 (근거 없는 배경이면 confidence: low + evidenceScope: synthesis-only)')
    print('  3. [[wikilink]] 2개 이상 + 관련 페이지에 역링크')
    print(f'  4. wiki/index.md 에 [[{args.slug}]] 등록 (Total pages +1)')
    print(f'  5. wiki/log.md 에 `## [{today}] create | {title}` append')
    print('  6. python3 wiki/tools/lint.py')


if __name__ == '__main__':
    main()
