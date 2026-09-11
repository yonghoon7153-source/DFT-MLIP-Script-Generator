"""chat.py — 위키 근거 대화 (/chat 의 서버 쪽).

무엇을 하나
  질문 → content.chat_context 로 위키 절을 고른다 (논문 노트·digest 는 서지 좌표를 달고, 우리 셀 `ours:` 와
  셀 요약 통계도 붙는다) → 시스템 프롬프트에 넣고 Claude 에게 답을 시킨다 → 답을 SSE 로 브라우저에 흘린다.

무엇을 안 하나
  저장. 대화 기록은 브라우저(localStorage)에만 있고, 서버는 요청마다 기록을 **받아서** 넘길 뿐 어디에도 쓰지 않는다.
  raw CSV 는 넘기지 않는다 — cells 요약 통계만.

키
  `ANTHROPIC_API_KEY` 환경변수(또는 SDK 가 아는 다른 자격증명)만 쓴다. 파일·저장소에 키를 두지 않는다.

설정 (환경변수)
  MIDNI_CHAT_MODEL      기본값은 아래 MODEL 한 줄 (모델 문자열은 저장소에서 이 자리 하나뿐 — 루트 CLAUDE.md 하드룰)
  MIDNI_CHAT_EFFORT     low|medium|high|max — 기본 high (SDK 가 output_config 를 모르면 자동으로 뺀다)
  MIDNI_CHAT_MAX_TOKENS 기본 8000 (스트리밍)
  MIDNI_CHAT_FAKE       1 이면 API 를 부르지 않고 고른 근거를 그대로 돌려준다 (오프라인 점검용)
"""
from __future__ import annotations

import json
import os
from typing import Iterator

import content as C

MODEL = os.environ.get("MIDNI_CHAT_MODEL", "claude-opus-5")
EFFORT = os.environ.get("MIDNI_CHAT_EFFORT", "high")
MAX_TOKENS = int(os.environ.get("MIDNI_CHAT_MAX_TOKENS", "8000"))
FAKE = os.environ.get("MIDNI_CHAT_FAKE", "0") == "1"

try:
    import anthropic  # noqa: F401
    _SDK = True
except Exception:  # SDK 가 없어도 앱은 뜬다 — /chat 만 비활성
    _SDK = False


def available() -> dict:
    """화면 상단 배지용 상태. 키의 존재만 보고, 값은 절대 돌려주지 않는다."""
    has_key = bool(os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN"))
    return {"ok": FAKE or (_SDK and has_key), "sdk": _SDK, "key": has_key, "fake": FAKE,
            "model": MODEL if not FAKE else "fake (오프라인 점검)", "effort": EFFORT}


# ── 시스템 프롬프트 (고정 부분 — 프롬프트 캐시의 접두사가 된다) ────────────────
SYSTEM_STATIC = """당신은 sulfide 기반 all-solid-state battery(ASSB) 에서 mid-Ni 양극재 NCA721 의 formation(pre-conditioning)
프로토콜을 연구하는 실험자의 **위키 사서이자 토론 상대**다. 근거는 아래 <wiki> 에 주어진 위키 절들(논문 노트·digest·
메커니즘·프로토콜·질문 카드)과 <ours>(우리 셀 조건), <cells>(우리 셀 요약 통계) 뿐이다.

절대 규칙 (어기면 답이 틀린 것이다)
A. 우리 실험의 양극재는 전부 **NCA721** 이다. NCM721 로 바꿔 부르거나 해석하지 않는다. 논문 속 양극 조성은 원문 표기
   (NCM622, NCM85, NCA …) 그대로 두고 NCA↔NCM 을 서로 바꾸지 않는다.
B. 전압에는 항상 기준전극을 붙인다. 변환식: vs. Li/Li⁺ = vs. In/Li-In + 0.62 V (방향 혼동 금지). 논문 값은 원문 값과
   원문 기준전극을 그대로 인용하고, 변환했으면 "(+0.62 V 환산)" 처럼 offset 을 적는다.
C. 비용량(mAh g⁻¹)과 면적용량(mAh cm⁻²)을 혼동하지 않는다. 절대용량(mAh)으로 보고하지 않는다. 비용량의 분모(활물질/
   복합체)를 안다면 적는다.
D. 충전 = delithiation, 방전 = lithiation.

답변 규칙
1. **모든 주장에 출처**를 붙인다: `(1저자 연도, 저널, Fig. N / p. M)` — chunk 의 cite 속성과 본문의 [인쇄, p.x]·Fig. 좌표에서
   가져온다. 좌표를 모르면 `(1저자 연도, 저널)` 까지만 쓰고 "figure/page 미상" 이라고 적는다. 가능하면 절의 URL 도
   마크다운 링크로 준다: `[제목 › 절](URL)`.
2. **DB 외 일반 지식/추론** 표시: 위키에 근거가 없는 내용은 문장 앞에 `[DB 외 일반 지식/추론]` 을 붙인다. background="true"
   인 chunk(`미검증 배경` 페이지)의 내용도 근거가 아니므로 같은 표시를 붙인다. 근거가 없으면 없다고 말하고 지어내지 않는다.
3. **비교할 때 자동 지적**: 논문끼리, 또는 논문과 우리 실험을 비교하면 답의 첫머리에 표 하나로 다섯 차이를 짚는다 —
   전압 기준전극(및 offset) · 양극 조성(원문 표기) · 온도 · 압력(제작압/구동압) · loading(mg cm⁻² / mAh cm⁻²).
   우리 조건은 <ours> 에서, 모르는 값은 "미기재" 로 둔다.
4. **표기 등급을 옮긴다**: digest 의 [인쇄](원문 글자) / [도표](그림 판독 근사값) / [해석](위키 필자 판단) / [재현](산술
   환산) 구분을 답에서도 유지한다. [도표] 값은 "그림에서 읽은 근사값" 이라고 말하고, [해석] 은 논문의 주장이 아니라고 밝힌다.
5. **페이지의 품질 축을 존중한다**: chunk meta 의 confidence·verificationStatus·evidenceScope 가 low / unverified /
   single-source / synthesis-only / user-original 이면 그렇게 밝히고 단정하지 않는다.
6. **연구 상대로서 답한다**: 실험 설계·해석 질문이면 위키 근거 → 우리 셀에의 함의(<ours>, <cells>) → 가장 값싼 다음 실험
   순으로. 열린 질문 카드가 관련되면 어느 가설(H1…)에 근거가 붙는지 말한다. 우리 셀 수치는 <cells> 의 요약뿐이며
   정본은 data/ 라고 밝힌다.
7. **언어**: 한국어로 답하되 전문 용어는 영어를 유지한다. 영어 용어를 **설명할 때**는 IPA 발음기호와 강세 위치를
   함께 적는다 (예: delithiation /diːˌlɪθiˈeɪʃən/, 강세 -a-).
8. 장식적 서두·맺음 없이 바로 답한다. 표가 도움이 되면 쓴다. 위키를 고치라는 제안은 해도 되지만 당신은 파일을 쓰지
   못한다 — 사용자가 Claude Code 에서 /wiki-query 또는 /paper 로 한다고 안내한다.
"""


def _wiki_block(ctx: dict) -> str:
    parts = ["<wiki>"]
    for i, ch in enumerate(ctx["chunks"], 1):
        meta = ch.get("meta") or {}
        mtxt = " · ".join(f"{k}={v}" for k, v in meta.items())
        head = f'<chunk n="{i}" page="{ch["title"]}" section="{ch.get("section") or "-"}" url="{ch["url"]}"'
        if ch.get("kind"):
            head += f' kind="{ch["kind"]}"'
        if ch.get("cite"):
            head += f' cite="{ch["cite"]}"'
        if ch.get("background"):
            head += ' background="true"'
        if mtxt:
            head += f' meta="{mtxt}"'
        head += ">"
        parts.append(head)
        parts.append(ch["text"])
        parts.append("</chunk>")
    parts.append("</wiki>")
    if ctx.get("ours"):
        parts.append(f'<ours url="{ctx.get("ours_url", "")}">\n{ctx["ours"]}\n</ours>')
    if ctx.get("cells"):
        parts.append("<cells>\n" + ctx["cells"] + "\n</cells>")
    return "\n".join(parts)


def _messages(history: list[dict], question: str) -> list[dict]:
    msgs = []
    for h in (history or [])[-12:]:
        role = "assistant" if h.get("role") == "assistant" else "user"
        text = str(h.get("content") or "").strip()
        if not text:
            continue
        if not msgs and role != "user":
            continue
        msgs.append({"role": role, "content": text})
    msgs.append({"role": "user", "content": question})
    return msgs


def _sse(obj: dict) -> str:
    return "data: " + json.dumps(obj, ensure_ascii=False) + "\n\n"


def stream_answer(question: str, history: list[dict]) -> Iterator[str]:
    """SSE 조각을 yield 한다. 이벤트: {sources} · {t: 텍스트} · {done, sources, usage, model} · {error}."""
    ctx = C.chat_context(question)
    yield _sse({"sources": ctx["sources"], "tokens": ctx["tokens"]})

    if FAKE:
        txt = ["(FAKE 모드 — API 를 부르지 않았다. 아래는 이 질문에 대해 고른 근거 절이다.)\n"]
        for ch in ctx["chunks"][1:]:
            tag = " [DB 외 일반 지식/추론 — 미검증 배경]" if ch.get("background") else ""
            txt.append(f"- [{ch['title']} › {ch.get('section') or '-'}]({ch['url']}){(' — ' + ch['cite']) if ch.get('cite') else ''}{tag}")
        if ctx.get("cells"):
            txt.append("\n<cells> 요약이 함께 넘어간다 (raw 없음).")
        for piece in "\n".join(txt):
            yield _sse({"t": piece})
        yield _sse({"done": True, "sources": ctx["sources"], "model": "fake"})
        return

    if not _SDK:
        yield _sse({"error": "anthropic SDK 가 없다 — `.venv/bin/pip install anthropic`"})
        return

    import anthropic

    client = anthropic.Anthropic()
    system = [
        {"type": "text", "text": SYSTEM_STATIC, "cache_control": {"type": "ephemeral"}},
        {"type": "text", "text": _wiki_block(ctx)},
    ]
    kwargs = dict(model=MODEL, max_tokens=MAX_TOKENS, system=system, messages=_messages(history, question))
    try:
        try:
            streamer = client.messages.stream(output_config={"effort": EFFORT}, **kwargs)
        except TypeError:                      # 구형 SDK — output_config 를 모른다
            streamer = client.messages.stream(**kwargs)
        with streamer as stream:
            for text in stream.text_stream:
                yield _sse({"t": text})
            final = stream.get_final_message()
        usage = getattr(final, "usage", None)
        u = {}
        if usage is not None:
            for k in ("input_tokens", "output_tokens", "cache_read_input_tokens", "cache_creation_input_tokens"):
                v = getattr(usage, k, None)
                if v is not None:
                    u[k] = v
        done = {"done": True, "sources": ctx["sources"], "usage": u, "model": getattr(final, "model", MODEL),
                "stop_reason": getattr(final, "stop_reason", None)}
        if getattr(final, "stop_reason", None) == "refusal":
            sd = getattr(final, "stop_details", None)
            done["refusal"] = {"category": getattr(sd, "category", None), "explanation": getattr(sd, "explanation", None)}
        yield _sse(done)
    except anthropic.AuthenticationError:
        yield _sse({"error": "API 키가 유효하지 않다 (ANTHROPIC_API_KEY 확인)."})
    except anthropic.RateLimitError as e:
        ra = e.response.headers.get("retry-after", "?") if getattr(e, "response", None) else "?"
        yield _sse({"error": f"요청 한도 초과 — {ra}s 뒤 다시."})
    except anthropic.BadRequestError as e:
        yield _sse({"error": f"요청 오류: {getattr(e, 'message', str(e))}"})
    except anthropic.APIStatusError as e:
        yield _sse({"error": f"API 오류 {getattr(e, 'status_code', '?')}: {getattr(e, 'message', str(e))}"})
    except anthropic.APIConnectionError:
        yield _sse({"error": "네트워크 오류 — Anthropic API 에 닿지 못했다."})
    except Exception as e:  # noqa: BLE001 — 화면이 죽는 것보다 이유를 보이는 편이 낫다
        yield _sse({"error": f"예상 못 한 오류: {type(e).__name__}: {e}"})
