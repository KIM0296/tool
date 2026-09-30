"""YouTube 영상 정보와 자막을 가져오는 핵심 로직."""

from __future__ import annotations

import json
import re
import urllib.parse
import urllib.request
from dataclasses import dataclass, field

from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    CouldNotRetrieveTranscript,
    NoTranscriptFound,
    TranscriptsDisabled,
)

DEFAULT_LANGUAGES = ("ko", "en")

_ID_RE = re.compile(r"^[A-Za-z0-9_-]{11}$")


class YtReadError(Exception):
    """사용자에게 보여줄 수 있는 오류."""


class NoSubtitlesError(YtReadError):
    """영상에 쓸 수 있는 자막이 없음 (음성 인식으로 대신 읽을 수 있다)."""


@dataclass
class Segment:
    start: float
    duration: float
    text: str


@dataclass
class Video:
    video_id: str
    url: str
    title: str | None = None
    author: str | None = None
    language: str | None = None
    is_generated: bool | None = None
    source: str = "subtitles"  # "subtitles" 또는 "speech" (음성 인식)
    segments: list[Segment] = field(default_factory=list)

    @property
    def text(self) -> str:
        return " ".join(s.text for s in self.segments)


def extract_video_id(value: str) -> str:
    """URL 또는 영상 ID 문자열에서 11자리 영상 ID를 뽑아낸다."""
    value = value.strip()
    if _ID_RE.match(value):
        return value

    parsed = urllib.parse.urlparse(value if "://" in value else "https://" + value)
    host = (parsed.hostname or "").lower().removeprefix("www.").removeprefix("m.")
    parts = [p for p in parsed.path.split("/") if p]

    candidate = None
    if host == "youtu.be" and parts:
        candidate = parts[0]
    elif host in ("youtube.com", "music.youtube.com", "youtube-nocookie.com"):
        if parts[:1] == ["watch"]:
            candidate = urllib.parse.parse_qs(parsed.query).get("v", [None])[0]
        elif len(parts) >= 2 and parts[0] in ("shorts", "embed", "live", "v"):
            candidate = parts[1]

    if candidate and _ID_RE.match(candidate):
        return candidate
    raise YtReadError(f"유튜브 영상 주소나 ID로 인식할 수 없습니다: {value}")


def fetch_metadata(video_id: str, timeout: float = 10) -> dict:
    """oEmbed로 제목과 채널명을 가져온다. 실패하면 빈 dict."""
    watch_url = f"https://www.youtube.com/watch?v={video_id}"
    query = urllib.parse.urlencode({"url": watch_url, "format": "json"})
    try:
        with urllib.request.urlopen(
            f"https://www.youtube.com/oembed?{query}", timeout=timeout
        ) as resp:
            return json.load(resp)
    except (OSError, ValueError):
        return {}


def fetch_transcript(
    video_id: str,
    languages: tuple[str, ...] = DEFAULT_LANGUAGES,
    api: YouTubeTranscriptApi | None = None,
) -> tuple[list[Segment], str, bool]:
    """자막을 가져온다. 원하는 언어가 없으면 번역 가능한 자막을 첫 언어로 번역한다.

    반환값: (구간 목록, 언어 코드, 자동 생성 여부)
    """
    api = api or YouTubeTranscriptApi()
    try:
        transcripts = api.list(video_id)
        try:
            transcript = transcripts.find_transcript(languages)
        except CouldNotRetrieveTranscript:
            transcript = next(iter(transcripts))
            if transcript.is_translatable and languages:
                transcript = transcript.translate(languages[0])
        fetched = transcript.fetch()
    except StopIteration:
        raise NoSubtitlesError("이 영상에는 자막이 없습니다.") from None
    except (NoTranscriptFound, TranscriptsDisabled) as e:
        raise NoSubtitlesError("이 영상에는 자막이 없습니다.") from e
    except CouldNotRetrieveTranscript as e:
        raise YtReadError(f"자막을 가져오지 못했습니다: {type(e).__name__}") from e

    segments = [Segment(s.start, s.duration, s.text) for s in fetched.snippets]
    return segments, fetched.language_code, fetched.is_generated


def read_video(
    value: str,
    languages: tuple[str, ...] = DEFAULT_LANGUAGES,
    speech: str = "auto",
    model_size: str | None = None,
) -> Video:
    """영상을 읽는다.

    speech: "auto"   자막이 없으면 음성 인식으로 대신 읽는다 (설치된 경우)
            "never"  자막만 사용
            "always" 자막을 무시하고 항상 음성 인식
    """
    video_id = extract_video_id(value)
    meta = fetch_metadata(video_id)
    video = Video(
        video_id=video_id,
        url=f"https://www.youtube.com/watch?v={video_id}",
        title=meta.get("title"),
        author=meta.get("author_name"),
    )

    if speech != "always":
        try:
            video.segments, video.language, video.is_generated = fetch_transcript(
                video_id, languages
            )
            return video
        except NoSubtitlesError:
            if speech == "never":
                raise

    from . import speech as speech_mod

    if speech == "auto" and not speech_mod.is_available():
        raise NoSubtitlesError(
            "이 영상에는 자막이 없습니다. 음성 인식으로 읽으려면 "
            "'pip install -e \".[speech]\"' 를 실행해 주세요."
        )
    video.segments, video.language = speech_mod.transcribe(
        video_id, model_size or speech_mod.DEFAULT_MODEL
    )
    video.source = "speech"
    video.is_generated = True
    return video


def format_timestamp(seconds: float) -> str:
    total = int(seconds)
    h, rem = divmod(total, 3600)
    m, s = divmod(rem, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"


def to_markdown(video: Video, timestamps: bool = True) -> str:
    lines = [f"# {video.title or video.video_id}", ""]
    if video.author:
        lines.append(f"- 채널: {video.author}")
    lines.append(f"- 주소: {video.url}")
    if video.source == "speech":
        lines.append(f"- 자막: {video.language} (음성 인식 — 자막이 없어 직접 받아씀)")
    elif video.language:
        kind = "자동 생성" if video.is_generated else "수동 작성"
        lines.append(f"- 자막: {video.language} ({kind})")
    lines += ["", "## 자막", ""]
    if timestamps:
        for s in video.segments:
            t = int(s.start)
            lines.append(
                f"[{format_timestamp(s.start)}]({video.url}&t={t}s) {s.text}"
            )
    else:
        lines.append(video.text)
    return "\n".join(lines) + "\n"


def to_json(video: Video) -> str:
    data = {
        "video_id": video.video_id,
        "url": video.url,
        "title": video.title,
        "author": video.author,
        "language": video.language,
        "is_generated": video.is_generated,
        "source": video.source,
        "segments": [s.__dict__ for s in video.segments],
    }
    return json.dumps(data, ensure_ascii=False, indent=2)
