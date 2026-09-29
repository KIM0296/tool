"""Claude로 자막을 요약하거나 자막에 대해 질문한다."""

from __future__ import annotations

from .core import Video, format_timestamp

MODEL = "claude-opus-5-5"

SYSTEM = (
    "당신은 유튜브 영상 자막을 읽고 내용을 정리하는 도우미입니다. "
    "자막에 있는 내용만 근거로 답하고, 자막에 없는 내용은 추측하지 마세요. "
    "중요한 부분에는 [mm:ss] 형식의 타임스탬프를 붙이세요. 한국어로 답하세요."
)

DEFAULT_PROMPT = (
    "이 영상을 요약해 주세요. 한 문단 핵심 요약, 주요 내용 목차(타임스탬프 포함), "
    "기억할 만한 포인트 순서로 정리해 주세요."
)


def _transcript_block(video: Video) -> str:
    header = f"제목: {video.title or '(알 수 없음)'}\n채널: {video.author or '(알 수 없음)'}\n"
    body = "\n".join(f"[{format_timestamp(s.start)}] {s.text}" for s in video.segments)
    return f"<transcript>\n{header}\n{body}\n</transcript>"


def ask_claude(video: Video, question: str | None = None) -> str:
    import anthropic

    client = anthropic.Anthropic()
    with client.beta.messages.stream(
        model=MODEL,
        max_tokens=64000,
        system=SYSTEM,
        output_config={"effort": "medium"},
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",
        messages=[
            {
                "role": "user",
                "content": f"{_transcript_block(video)}\n\n{question or DEFAULT_PROMPT}",
            }
        ],
    ) as stream:
        message = stream.get_final_message()

    if message.stop_reason == "refusal":
        raise RuntimeError("Claude가 이 요청을 거절했습니다.")
    return "".join(b.text for b in message.content if b.type == "text")
