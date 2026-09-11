#!/usr/bin/env python3
"""LLM Wiki lint — mechanical health check (mid-Ni NCA721 formation wiki).

Checks (wiki/SCHEMA.md conventions — kit checks 1–14 kept, this repo adds 15–23):
  1. every wiki page has required frontmatter keys, and type matches its folder
  2. verified pages carry verifiedAt/verifiedBy
  3. sources paths exist
  4. all wikilinks resolve to real pages (code spans/blocks excluded)
  5. each page has >= 2 distinct wikilinks (warning)
  6. index.md lists every page, lists nothing that doesn't exist, and its
     "Total pages" count is accurate
  7. raw file sha256 matches body (immutability check)
  8. orphan pages — zero inbound wikilinks from other pages (warning)
  9. stale pages — `updated` older than STALE_DAYS (warning)
 10. confidence:high pages without a Bias Check / 불확실성 section (note)
 11. enum keys carry allowed values (claimType, evidenceScope, research-question status)
 12. description frontmatter, if present, is quoted
 13. evidenceScope single-source with confidence high (warning — 근거 폭이 상한)
 14. verified pages with verifiedAt older than STALE_DAYS (warning — re-verify)
 15. no-hardcoded-branch-name — the branch rule lives in the root CLAUDE.md only
 16. no-model-identifier — no model ids in wiki pages / tools (root CLAUDE.md hard rule)
 17. parity — CLAUDE.md and AGENTS.md carry the same Essential Rules
 18. no-ncm721 — 절대 규칙 1: NCA721 을 NCM721 로 바꿔 부르지 않는다. wiki 컴파일 페이지·
     wiki 루트 문서·webapp·루트 문서·config·.claude 전부 검사. raw/ 는 면제. 금지 규칙을
     **말하는** 줄(`금지`·`않는다`·`말 것`·`forbidden` 포함)만 예외.
 19. canonical-offset — 절대 규칙 2: Li-In 을 언급하는 줄의 `±0.xx V` 는 `config/cells.yaml`
     `voltage.in_to_li_offset_v` 와 같아야 한다 (사본 drift 방지).
 20. voltage-reference — 절대 규칙 2 (warning): `x.x V` 가 있는 줄에 기준전극 표기가 없다.
     표 행은 위쪽 머리행(15줄 이내)에 기준이 있으면 통과.
 21. unit-rule — 절대 규칙 3 (warning): `mAh` 뒤에 g⁻¹·cm⁻² 계열이 붙지 않은 절대용량 표기.
 22. doi-unique — papers/ 노트: `raw:` 가 가리키는 digest 존재, `paper.bib.doi` 존재(없으면
     `doi_missing_reason`), DOI 가 노트 간에 유일.
 23. paper-note-voltage — `window_vs_li`/`cutoff_v_li` 변환값이 있으면 `reference_raw` 와
     `offset_applied_v` 도 있어야 한다 (변환값은 offset 과 함께 별도 필드 — 절대 규칙 2).

Usage: python3 wiki/tools/lint.py        (repo root 또는 어디서든)
Exit code 0 = no errors (warnings allowed), 1 = errors found.
"""
import datetime
import glob
import hashlib
import pathlib
import re
import sys

STALE_DAYS = 90

# 출력 경로도 UTF-8 로 닫는다 — Windows 콘솔(CP949)에서 em dash 를 찍다 죽지 않게.
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding='utf-8', errors='replace')
    except (AttributeError, ValueError):
        pass

BASE = pathlib.Path(__file__).resolve().parent.parent          # wiki/
ROOT = BASE.parent                                            # repo root
DIRS = ['papers', 'mechanisms', 'protocols', 'experiments', 'comparisons',
        'concepts', 'entities', 'queries', 'guides', 'questions', 'syntheses']
REQ = ['title', 'created', 'updated', 'type', 'tags', 'sources',
       'confidence', 'explored', 'verificationStatus']
TYPE_BY_DIR = {'papers': 'paper-note', 'mechanisms': 'mechanism', 'protocols': 'protocol',
               'experiments': 'experiment', 'comparisons': 'comparison',
               'concepts': 'concept', 'entities': 'entity', 'queries': 'query',
               'guides': 'guide', 'questions': 'research-question', 'syntheses': 'synthesis'}
ENUMS = {
    'confidence': {'high', 'medium', 'low'},
    'verificationStatus': {'unverified', 'verified', 'disputed'},
    'claimType': {'definition', 'empirical', 'theoretical', 'historical',
                  'prescriptive', 'interpretive', 'mixed'},
    'evidenceScope': {'single-source', 'multi-source-primary', 'multi-source-mixed',
                      'synthesis-only', 'user-original'},
}
RQ_STATUS = {'open', 'active', 'answered', 'abandoned'}

errors, warnings = [], []


def parse_fm(s):
    """얕은 frontmatter 파서 — 최상위 `key: value` 줄만 (중첩 블록은 무시)."""
    fm = {}
    for line in s.splitlines():
        m = re.match(r'^([A-Za-z][A-Za-z0-9_]*):\s*(.*)$', line)
        if m:
            fm[m.group(1)] = m.group(2).strip()
    return fm


def strip_code(text):
    text = re.sub(r'```.*?```', '', text, flags=re.S)   # fenced blocks
    text = re.sub(r'`[^`\n]*`', '', text)               # inline code
    return text


def read(p):
    return pathlib.Path(p).read_text(encoding='utf-8')


pages = {}
for d in DIRS:
    for f in glob.glob(str(BASE / d / '*.md')):
        p = pathlib.Path(f)
        pages[p.stem] = p

fm_by_page = {}
fm_text_by_page = {}
body_by_page = {}
outbound = {}
for stem, p in sorted(pages.items()):
    text = read(p)
    m = re.match(r'^---\n(.*?)\n---\n', text, re.S)
    if not m:
        errors.append(f'{p.name}: no frontmatter')
        continue
    fm = parse_fm(m.group(1))
    fm_by_page[stem] = fm
    fm_text_by_page[stem] = m.group(1)
    body_by_page[stem] = text[m.end():]
    for k in REQ:
        if k not in fm:
            errors.append(f'{p.name}: missing frontmatter key `{k}`')
    want = TYPE_BY_DIR[p.parent.name]
    if fm.get('type') != want:
        errors.append(f'{p.name}: type `{fm.get("type")}` in {p.parent.name}/ (want {want})')
    if fm.get('verificationStatus') == 'verified' and ('verifiedAt' not in fm or 'verifiedBy' not in fm):
        errors.append(f'{p.name}: verified but missing verifiedAt/verifiedBy')
    for k, allowed in ENUMS.items():
        v = fm.get(k, '')
        if v and v not in allowed:
            errors.append(f'{p.name}: `{k}: {v}` not in {sorted(allowed)}')
    if fm.get('type') == 'research-question':
        st = fm.get('status', '')
        if st and st not in RQ_STATUS:
            errors.append(f'{p.name}: `status: {st}` not in {sorted(RQ_STATUS)}')
    desc = fm.get('description', '')
    if desc and not (desc.startswith('"') and desc.endswith('"')):
        errors.append(f'{p.name}: description not quoted')
    if fm.get('evidenceScope') == 'single-source' and fm.get('confidence') == 'high':
        warnings.append(f'{p.name}: single-source but confidence high — 근거 폭이 상한 (SCHEMA Provenance)')
    src_field = fm.get('sources', '')
    srcs = re.findall(r'[\w/.-]+\.md', src_field)
    urls = re.findall(r'https?://\S+', src_field)
    if not srcs and not urls:
        errors.append(f'{p.name}: no sources parsed')
    for s in srcs:
        if not (BASE / s).exists():
            errors.append(f'{p.name}: source path missing: {s}')
    body = strip_code(text[m.end():])
    links = re.findall(r'\[\[([^\]|#]+?)(?:\|[^\]]*)?\]\]', body)
    for l in links:
        if l.strip() not in pages:
            errors.append(f'{p.name}: broken wikilink [[{l}]]')
    if len(set(links)) < 2:
        warnings.append(f'{p.name}: fewer than 2 distinct wikilinks')
    outbound.setdefault(stem, set()).update(
        l.strip() for l in links if l.strip() in pages and l.strip() != stem)

index = read(BASE / 'index.md')
idx_links = set(re.findall(r'\[\[([^\]|#]+?)(?:\|[^\]]*)?\]\]', index))
for stem in pages:
    if stem not in idx_links:
        errors.append(f'index.md: page not listed: {stem}')
for l in idx_links:
    if l not in pages:
        errors.append(f'index.md: listed but file missing: {l}')
mc = re.search(r'Total pages: (\d+)', index)
if mc and int(mc.group(1)) != len(pages):
    errors.append(f'index.md: claims {mc.group(1)} pages, actual {len(pages)}')

raws = glob.glob(str(BASE / 'raw/**/*.md'), recursive=True)
for f in raws:
    t = read(f)
    m = re.match(r'^---\n(.*?)\n---\n(.*)$', t, re.S)
    if not m:
        errors.append(f'{f}: no raw frontmatter')
        continue
    fm = parse_fm(m.group(1))
    h = hashlib.sha256(m.group(2).lstrip('\n').encode()).hexdigest()
    if fm.get('sha256') != h:
        errors.append(f'{pathlib.Path(f).name}: sha256 mismatch '
                      f'(declared {str(fm.get("sha256"))[:12]}…, actual {h[:12]}…)')

# 8. orphans
inbound = {s: 0 for s in pages}
for src, targets in outbound.items():
    for t in targets:
        inbound[t] += 1
for stem, n in sorted(inbound.items()):
    if n == 0:
        warnings.append(f'{stem}: orphan (no inbound wikilinks from other pages)')

# 9. stale
today = datetime.date.today()
for stem, fm in fm_by_page.items():
    try:
        upd = datetime.date.fromisoformat(str(fm.get('updated', '')))
        if (today - upd).days > STALE_DAYS:
            warnings.append(f'{stem}: stale (updated {upd}, {(today - upd).days}d ago)')
    except ValueError:
        errors.append(f'{stem}: unparseable `updated` date: {fm.get("updated")}')

# 14. verified but verification itself is stale
for stem, fm in fm_by_page.items():
    if fm.get('verificationStatus') != 'verified':
        continue
    try:
        va = datetime.date.fromisoformat(str(fm.get('verifiedAt', '')))
        if (today - va).days > STALE_DAYS:
            warnings.append(f'{stem}: verification stale (verifiedAt {va}) — /wiki-verify 재실행 권장')
    except ValueError:
        pass

# 10. bias-check coverage for confidence:high (note)
no_bias = [s for s, fm in fm_by_page.items()
           if fm.get('confidence') == 'high'
           and not re.search(r'불확실성|Bias Check|반대해석|한계', read(pages[s]))]

# ── 이 저장소의 추가 검사 ─────────────────────────────────────────────────
WIKI_ROOT_DOCS = [BASE / n for n in ('SCHEMA.md', 'CLAUDE.md', 'AGENTS.md', 'README.md', 'index.md', 'log.md')]
ROOT_DOCS = [ROOT / n for n in ('CLAUDE.md', 'README.md', 'BRANCHES.md')]
WEBAPP_FILES = sorted(list((ROOT / 'webapp').rglob('*.py')) + list((ROOT / 'webapp').rglob('*.html'))
                      + list((ROOT / 'webapp').rglob('*.js')) + list((ROOT / 'webapp').rglob('*.sh'))) \
    if (ROOT / 'webapp').is_dir() else []
AGENT_FILES = sorted((ROOT / '.claude').rglob('*.md')) if (ROOT / '.claude').is_dir() else []
CONFIG_FILES = sorted((ROOT / 'config').glob('*.yaml')) if (ROOT / 'config').is_dir() else []
TOOL_FILES = sorted((ROOT / 'tools').rglob('*.py')) if (ROOT / 'tools').is_dir() else []

# 15. branch names are not wiki content — the rule lives in the root CLAUDE.md.
BRANCH_RE = re.compile(r'(?<![.\w])claude/[A-Za-z0-9][A-Za-z0-9-]*')
for f in WIKI_ROOT_DOCS + sorted(pages.values()):
    if not f.exists():
        continue
    for hit in sorted(set(BRANCH_RE.findall(read(f)))):
        errors.append(f'{f.name}: hardcoded branch name `{hit}` — '
                      f'루트 CLAUDE.md 의 브랜치 하드룰을 참조하라 (drift 방지)')

# 16. no-model-identifier — 위키 페이지·도구에 모델 식별자를 적지 않는다.
#     예외 한 곳: API 호출용 모델 문자열은 webapp/chat.py 의 env 기본값 한 줄 (이 검사는 위키만 본다).
MODEL_RE = re.compile(
    r'(?<![\w-])(?:claude-(?:opus|sonnet|haiku|fable|instant)[\w.-]*'
    r'|gpt-[0-9][\w.-]*|gemini-[0-9][\w.-]*)', re.I)
for f in WIKI_ROOT_DOCS + sorted(pages.values()) + [BASE / 'tools' / 'new-page.py']:
    if not f.exists():
        continue
    for hit in sorted(set(MODEL_RE.findall(read(f)))):
        errors.append(f'{f.name}: model identifier `{hit}` — 루트 CLAUDE.md 하드룰 (위키 페이지·도구에 적지 않는다)')


# 17. Parity Contract
def _essential(path):
    if not path.exists():
        return None
    txt = read(path)
    m = re.search(r'^## Essential Rules.*?\n(.*?)(?=^## )', txt, re.S | re.M)
    return re.sub(r'\s+', ' ', m.group(1)).strip() if m else None


_c, _a = _essential(BASE / 'CLAUDE.md'), _essential(BASE / 'AGENTS.md')
if _c is None or _a is None:
    errors.append('parity: CLAUDE.md/AGENTS.md 의 `## Essential Rules` 절을 찾지 못했다')
elif _c != _a:
    errors.append('parity: CLAUDE.md 와 AGENTS.md 의 Essential Rules 가 다르다 — Parity Contract 위반 (두 파일을 함께 고친다)')

# 18. no-ncm721 — 절대 규칙 1
NCM721_RE = re.compile(r'(?<![\w-])NCM[\s\-‐–]?721', re.I)   # `no-ncm721` (검사 이름) 은 제외
RULE_LINE = re.compile(r'금지|않|말 것|forbidden|not\b|never\b', re.I)
for f in WIKI_ROOT_DOCS + sorted(pages.values()) + ROOT_DOCS + WEBAPP_FILES + AGENT_FILES + CONFIG_FILES + TOOL_FILES:
    if not f.exists() or f.resolve() == pathlib.Path(__file__).resolve():
        continue
    _lines = read(f).splitlines()
    for ln, line in enumerate(_lines, 1):
        # 금지 규칙을 말하는 문장은 다음 줄로 넘어가기도 한다 — 2줄 창으로 본다
        window = line + ' ' + (_lines[ln] if ln < len(_lines) else '')
        if NCM721_RE.search(line) and not RULE_LINE.search(window):
            errors.append(f'{f.relative_to(ROOT).as_posix()}:{ln}: `NCM721` — 절대 규칙 1: 우리 양극재는 NCA721 이다')

# 19. canonical-offset — 절대 규칙 2. 정본은 config/cells.yaml
OFFSET_RE = re.compile(r'([+\-−±])\s?(0\.\d{1,3})\s?V\b')
LIIN_RE = re.compile(r'Li[\s\-–]?In|In/Li|Li/In', re.I)
cfg = ROOT / 'config' / 'cells.yaml'
canon_offset = None
if cfg.exists():
    mo = re.search(r'in_to_li_offset_v:\s*([0-9.]+)', read(cfg))
    if mo:
        canon_offset = float(mo.group(1))
if canon_offset is None:
    errors.append('canonical-offset: config/cells.yaml 의 voltage.in_to_li_offset_v 를 찾지 못했다 (정본)')
else:
    for f in WIKI_ROOT_DOCS + sorted(pages.values()) + ROOT_DOCS + WEBAPP_FILES + AGENT_FILES + TOOL_FILES:
        if not f.exists() or f.resolve() == pathlib.Path(__file__).resolve():
            continue
        for ln, line in enumerate(read(f).splitlines(), 1):
            if not LIIN_RE.search(line):
                continue
            for sign, num in OFFSET_RE.findall(line):
                if abs(float(num) - canon_offset) > 1e-9:
                    errors.append(f'{f.relative_to(ROOT).as_posix()}:{ln}: Li-In offset `{sign}{num} V` ≠ 정본 '
                                  f'{canon_offset} V (config/cells.yaml) — 절대 규칙 2')

# 20. voltage-reference (warning) — 절대 규칙 2
VOLT_RE = re.compile(r'(?<![\w.])\d(?:\.\d+)?\s?V\b(?!\s?[-–]?class)')
REF_RE = re.compile(r'\bvs\b|Li/Li|Li[\s\-–]?In|In/Li|LTO|\bAg\b|기준|reference', re.I)
for stem, body in body_by_page.items():
    lines = strip_code(body).splitlines()
    # 문단(빈 줄 사이) 단위로 본다 — 한 문단 안에 기준전극이 한 번 있으면 그 문단의 전압은 통과
    para_ok, cur_ok, cur = {}, False, []
    for i, line in enumerate(lines):
        if not line.strip():
            for j in cur:
                para_ok[j] = cur_ok
            cur, cur_ok = [], False
            continue
        cur.append(i)
        if REF_RE.search(line):
            cur_ok = True
    for j in cur:
        para_ok[j] = cur_ok
    for i, line in enumerate(lines):
        if not VOLT_RE.search(line) or 'mV' in line:
            continue
        if para_ok.get(i):
            continue
        if line.lstrip().startswith('|'):
            head = ' '.join(lines[max(0, i - 15):i])
            if REF_RE.search(head):
                continue
        warnings.append(f'{stem}:{i + 1}: 전압에 기준전극 표기가 없다 (문단 안에도 없음) — `{line.strip()[:70]}`')

# 21. unit-rule (warning) — 절대 규칙 3
MAH_RE = re.compile(r'mAh(?!\s?(?:g|cm|/|·|kg|L\b|\(|\s?g|\s?cm|⋅))')
for stem, body in body_by_page.items():
    for i, line in enumerate(strip_code(body).splitlines(), 1):
        if '절대용량' in line or '절대 용량' in line:
            continue
        if MAH_RE.search(line):
            warnings.append(f'{stem}:{i}: `mAh` 뒤에 g⁻¹/cm⁻² 가 없다 — 절대용량 표기 금지 (절대 규칙 3): `{line.strip()[:70]}`')

def _fm_val(fmt, key):
    """frontmatter 텍스트에서 중첩 키 값을 읽는다 — 블록 스타일(`  doi: x`)과 플로우 스타일(`{doi: x, …}`) 둘 다.
    null/빈 값은 '' 로 돌려준다."""
    m = re.search(r'^\s+%s:\s*(.*)$' % re.escape(key), fmt, re.M)
    v = m.group(1).strip() if m else ''
    if not v:
        m = re.search(r'[{,]\s*%s:\s*("?)([^",}\n]*)\1' % re.escape(key), fmt)
        v = m.group(2).strip() if m else ''
    v = v.strip().strip('"\'')
    return '' if v.lower() in ('', 'null', '~', '[]', '{}') else v


# 22. doi-unique + paper-note structure
seen_doi = {}
for stem, fmt in fm_text_by_page.items():
    if fm_by_page[stem].get('type') != 'paper-note':
        continue
    raw_rel = fm_by_page[stem].get('raw', '').strip().strip('"\'')
    if not raw_rel or raw_rel == 'null':
        errors.append(f'{stem}: paper-note 에 `raw:` (digest 경로) 가 없다')
    elif not (BASE / raw_rel).exists():
        errors.append(f'{stem}: raw digest 가 없다: {raw_rel}')
    if 'paper:' not in fmt:
        errors.append(f'{stem}: paper-note 에 `paper:` 블록이 없다')
        continue
    doi = _fm_val(fmt, 'doi')
    if not doi or doi.lower() == 'null':
        reason = _fm_val(fmt, 'doi_missing_reason')
        if not reason or reason.lower() == 'null':
            errors.append(f'{stem}: DOI 가 없고 doi_missing_reason 도 없다 (중복 제거 키)')
        continue
    key = re.sub(r'^https?://(dx\.)?doi\.org/', '', doi.lower()).strip()
    if key in seen_doi:
        errors.append(f'{stem}: DOI `{doi}` 가 {seen_doi[key]} 와 중복 — 같은 논문은 노트 하나로 (기존 노트를 갱신)')
    else:
        seen_doi[key] = stem

# 23. paper-note-voltage — 변환값이 있으면 기준·offset 도 있어야 한다
for stem, fmt in fm_text_by_page.items():
    if fm_by_page[stem].get('type') not in ('paper-note', 'entity'):
        continue

    def _val(key):
        return _fm_val(fmt, key)

    if _val('window_vs_li') or _val('cutoff_v_li'):
        if not _val('reference_raw'):
            errors.append(f'{stem}: 변환 전압(window_vs_li/cutoff_v_li)이 있는데 voltage.reference_raw 가 없다 (절대 규칙 2)')
        if not _val('offset_applied_v'):
            errors.append(f'{stem}: 변환 전압이 있는데 voltage.offset_applied_v 가 없다 — 변환값은 offset 과 함께 (절대 규칙 2)')

print('=== LINT REPORT ===')
print(f'pages: {len(pages)} | raw files: {len(raws)}')
vs, ex = {}, {}
for fm in fm_by_page.values():
    vs[fm.get('verificationStatus')] = vs.get(fm.get('verificationStatus'), 0) + 1
    ex[fm.get('explored')] = ex.get(fm.get('explored'), 0) + 1
print('verificationStatus:', vs)
print('explored:', ex)
print(f'\nERRORS ({len(errors)}):')
for e in errors:
    print(' ✗', e)
print(f'\nWARNINGS ({len(warnings)}):')
for w in warnings:
    print(' ⚠', w)
if no_bias:
    print(f'\nNOTES: confidence:high without Bias Check/불확실성 section — {len(no_bias)} pages')
    print('  ' + ' · '.join(sorted(no_bias)))
if not errors:
    print('\nRESULT: 0 errors')
sys.exit(1 if errors else 0)
