"""chat.py — 위키 근거 대화 (/chat 의 서버 쪽).

무엇을 하나
  질문 → content.chat_context 로 위키 절을 고른다 → 그 절들을 **인용 좌표와 함께** 시스템
  프롬프트에 넣고 Claude 에게 답을 시킨다 → 답을 SSE 로 브라우저에 흘린다.

무엇을 안 하나
  저장. 대화 기록은 브라우저(localStorage)에만 있고, 서버는 요청마다 기록을 **받아서**
  넘길 뿐 어디에도 쓰지 않는다. 위키 파일도 건드리지 않는다.

키
  `ANTHROPIC_API_KEY` 환경변수(또는 SDK 가 아는 다른 자격증명)만 쓴다. 파일·저장소에 키를
  두지 않는다. 키가 없으면 `available()` 이 False 이고 화면은 안내만 보인다.

설정 (환경변수)
  LI2S_CHAT_MODEL      기본 claude-opus-5
  LI2S_CHAT_EFFORT     low|medium|high|xhigh|max — 기본 high
  LI2S_CHAT_MAX_TOKENS 기본 8000 (스트리밍)
  LI2S_CHAT_FALLBACKS  1(기본)이면 서버측 refusal fallback 을 켠다 (beta)
  LI2S_CHAT_FAKE       1 이면 API 를 부르지 않고 고른 근거를 그대로 돌려준다 (오프라인 점검용)
"""
from __future__ import annotations

import json
import os
from typing import Iterator

import content as C

MODEL = os.environ.get("LI2S_CHAT_MODEL", "claude-opus-5")
EFFORT = os.environ.get("LI2S_CHAT_EFFORT", "high")
MAX_TOKENS = int(os.environ.get("LI2S_CHAT_MAX_TOKENS", "8000"))
FALLBACKS = os.environ.get("LI2S_CHAT_FALLBACKS", "1") != "0"
FAKE = os.environ.get("LI2S_CHAT_FAKE", "0") == "1"

try:
    import anthropic  # noqa: F401
    _SDK = True
except Exception:  # SDK 가 없어도 앱은 뜬다 — /chat 만 비활성
    _SDK = False


def available() -> dict:
    """화면 상단 배지용 상태. 키의 존재만 보고, 값은 절대 돌려주지 않는다."""
    has_key = bool(os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN"))
    return {
        "ok": FAKE or (_SDK and has_key),
        "sdk": _SDK,
        "key": has_key,
        "fake": FAKE,
        "model": MODEL if not FAKE else "fake (오프라인 점검)",
        "effort": EFFORT,
        "fallbacks": FALLBACKS,
    }


# ── 시스템 프롬프트 (고정 부분 — 프롬프트 캐시의 접두사가 된다) ────────────────
SYSTEM_STATIC = """당신은 Li2S 양극 all-solid-state Li–S 전지 연구실의 **위키 사서이자 토론 상대**다.
근거는 아래 <wiki> 에 주어진 위키 절들이고, 그 밖의 일반 지식은 "위키 밖 일반 지식" 이라고
분명히 표시한 뒤에만 보조로 쓴다.

규칙
1. **인용을 붙인다.** 사실을 말할 때마다 어느 절에서 왔는지 `[제목 › 절]` 형식으로 적고,
   가능하면 그 절의 URL 도 함께 준다 (마크다운 링크 `[제목 › 절](URL)`). 근거가 위키에 없으면
   "위키에 근거가 없다" 고 말하고 지어내지 않는다.
2. **표기 등급을 옮긴다.** 논문 digest 의 `[인쇄]`(원문 글자) / `[도표]`(그림 판독 근사값) /
   `[해석]`(위키 필자의 판단) / `[재현]`(산술 환산) 구분을 답에서도 유지한다. `[도표]` 값은
   "그림에서 읽은 근사값" 이라고 말한다. `[해석]` 은 논문의 주장이 아니라고 밝힌다.
3. **단위 규율.** 비용량은 `mAh g⁻¹(S)` 인지 `mAh g⁻¹(Li2S)` 인지 항상 적는다 (환산 ×0.698).
   전압은 `vs Li/Li⁺` 인지 `vs Li–In` 인지 적는다. 위키가 단위를 안 적었으면 그 사실을 말한다.
4. **페이지의 품질 축을 존중한다.** 절 머리의 meta(confidence·verificationStatus·evidenceScope)
   가 unverified / single-source / user-original 이면 그렇게 밝히고 단정하지 않는다.
5. **연구 상대로서 답한다.** 사용자는 실험자다. 질문이 실험 설계·해석이면 위키 근거 → 우리
   셀에의 함의 → 가장 값싼 다음 실험 순으로 답한다. 열린 질문 카드(questions/)가 관련되면
   어느 가설(H1…)에 근거가 붙는지 말한다.
6. 한국어로, 기술 용어는 원어 병기. 장식적 서두·맺음 없이 바로 답한다. 표가 도움이 되면 쓴다.
7. 위키를 **고치라는 제안**은 해도 되지만 (예: "이 답을 queries/ 에 file-back 할 가치가 있다"),
   당신은 파일을 쓰지 못한다 — 사용자가 Claude Code 에서 /wiki-query 로 한다고 안내한다.
"""


def _wiki_block(ctx: dict) -> str:
    parts = ["<wiki>"]
    for i, ch in enumerate(ctx["chunks"], 1):
        meta = ch.get("meta") or {}
        mtxt = " · ".join(f"{k}={v}" for k, v in meta.items())
        head = f'<chunk n="{i}" page="{ch["title"]}" section="{ch.get("section") or "-"}" url="{ch["url"]}"'
        if ch.get("kind"):
            head += f' kind="{ch["kind"]}"'
        if mtxt:
            head += f' meta="{mtxt}"'
        head += ">"
        parts.append(head)
        parts.append(ch["text"])
        parts.append("</chunk>")
    parts.append("</wiki>")
    return "\n".join(parts)


def _messages(history: list[dict], question: str) -> list[dict]:
    """브라우저가 보낸 이전 턴(role/content 문자열)을 API 형식으로. 최근 12턴만."""
    msgs = []
    for h in (history or [])[-12:]:
        role = "assistant" if h.get("role") == "assistant" else "user"
        text = str(h.get("content") or "").strip()
        if not text:
            continue
        # 같은 role 연속은 API 가 합쳐 주지만, 첫 메시지는 user 여야 한다
        if not msgs and role != "user":
            continue
        msgs.append({"role": role, "content": text})
    msgs.append({"role": "user", "content": question})
    return msgs


def _sse(obj: dict) -> str:
    return "data: " + json.dumps(obj, ensure_ascii=False) + "\n\n"


def stream_answer(question: str, history: list[dict]) -> Iterator[str]:
    """SSE 조각을 yield 한다. 이벤트: {t: 텍스트} · {done, sources, usage, model} · {error}."""
    ctx = C.chat_context(question)
    yield _sse({"sources": ctx["sources"], "tokens": ctx["tokens"]})

    if FAKE:
        # 오프라인 점검 — API 없이 고른 근거를 돌려준다 (배선 확인용)
        txt = ["(FAKE 모드 — API 를 부르지 않았다. 아래는 이 질문에 대해 고른 근거 절이다.)\n"]
        for ch in ctx["chunks"][1:]:
            txt.append(f"- [{ch['title']} › {ch.get('section') or '-'}]({ch['url']})")
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
    kwargs = dict(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        system=system,
        messages=_messages(history, question),
        output_config={"effort": EFFORT},
    )
    try:
        if FALLBACKS:
            # 서버측 refusal fallback — 정책상 거절이 나면 같은 호출 안에서 다른 모델이 잇는다.
            # (beta 헤더는 scalar 'default' 형식과 짝이다.)
            streamer = client.beta.messages.stream(
                betas=["server-side-fallback-2026-07-01"], fallbacks="default", **kwargs)
        else:
            streamer = client.messages.stream(**kwargs)
        with streamer as stream:
            for text in stream.text_stream:
                yield _sse({"t": text})
            final = stream.get_final_message()
        usage = getattr(final, "usage", None)
        u = {}
        if usage is not None:
            for k in ("input_tokens", "output_tokens", "cache_read_input_tokens",
                      "cache_creation_input_tokens"):
                v = getattr(usage, k, None)
                if v is not None:
                    u[k] = v
        done = {"done": True, "sources": ctx["sources"], "usage": u,
                "model": getattr(final, "model", MODEL),
                "stop_reason": getattr(final, "stop_reason", None)}
        if getattr(final, "stop_reason", None) == "refusal":
            sd = getattr(final, "stop_details", None)
            done["refusal"] = {"category": getattr(sd, "category", None),
                               "explanation": getattr(sd, "explanation", None)}
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
