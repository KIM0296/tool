"""자막이 없는 영상을 음성 인식(Whisper)으로 받아쓴다.

필요 패키지: pip install -e ".[speech]"  (yt-dlp, faster-whisper)
모든 처리는 내 PC에서 이뤄지며 별도 API 키나 비용이 들지 않는다.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

from .core import Segment, YtReadError

DEFAULT_MODEL = "small"


def is_available() -> bool:
    try:
        import faster_whisper  # noqa: F401
        import yt_dlp  # noqa: F401
    except ImportError:
        return False
    return True


def download_audio(video_id: str, out_dir: str) -> Path:
    """영상의 오디오만 내려받는다 (ffmpeg 없이 원본 포맷 그대로)."""
    import yt_dlp

    opts = {
        "format": "bestaudio/best",
        "outtmpl": str(Path(out_dir) / "%(id)s.%(ext)s"),
        "quiet": True,
        "no_warnings": True,
        "noprogress": True,
    }
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(
                f"https://www.youtube.com/watch?v={video_id}", download=True
            )
            return Path(ydl.prepare_filename(info))
    except yt_dlp.utils.DownloadError as e:
        raise YtReadError(f"오디오를 내려받지 못했습니다: {e}") from e


def transcribe(
    video_id: str,
    model_size: str = DEFAULT_MODEL,
    language: str | None = None,
) -> tuple[list[Segment], str]:
    """오디오를 내려받아 받아쓴다. 반환값: (구간 목록, 감지된 언어 코드)"""
    if not is_available():
        raise YtReadError(
            "음성 인식 기능이 설치되지 않았습니다. "
            "'pip install -e \".[speech]\"' 를 실행해 주세요."
        )
    from faster_whisper import WhisperModel

    with tempfile.TemporaryDirectory(prefix="ytread-") as tmp:
        audio = download_audio(video_id, tmp)
        print(
            f"자막이 없어 음성 인식 중입니다 (모델: {model_size}). "
            "영상 길이에 따라 몇 분 걸릴 수 있습니다...",
            file=sys.stderr,
        )
        try:
            # 처음 한 번은 모델 파일을 내려받는다 (small 기준 약 500MB)
            model = WhisperModel(model_size, device="auto", compute_type="int8")
        except Exception as e:  # noqa: BLE001 - 네트워크·모델 이름 오류 등
            raise YtReadError(
                f"음성 인식 모델({model_size})을 불러오지 못했습니다: {e}"
            ) from e
        raw_segments, info = model.transcribe(
            str(audio), language=language, vad_filter=True
        )
        # 제너레이터라서 임시 폴더가 지워지기 전에 끝까지 읽는다
        segments = [
            Segment(s.start, s.end - s.start, s.text.strip())
            for s in raw_segments
            if s.text.strip()
        ]

    if not segments:
        raise YtReadError("음성 인식 결과가 비어 있습니다 (말소리가 없는 영상일 수 있습니다).")
    return segments, info.language
