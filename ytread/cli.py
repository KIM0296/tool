"""명령줄 인터페이스: ytread <유튜브 주소>"""

from __future__ import annotations

import argparse
import sys

from . import __version__
from .core import DEFAULT_LANGUAGES, YtReadError, read_video, to_json, to_markdown


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="ytread", description="유튜브 영상의 제목과 자막을 읽어옵니다."
    )
    p.add_argument("video", help="유튜브 주소 또는 11자리 영상 ID")
    p.add_argument(
        "-l", "--lang", default=",".join(DEFAULT_LANGUAGES),
        help="선호 자막 언어, 쉼표로 구분 (기본: ko,en)",
    )
    p.add_argument(
        "-f", "--format", choices=["markdown", "text", "json"], default="markdown",
        help="출력 형식 (기본: markdown)",
    )
    speech = p.add_mutually_exclusive_group()
    speech.add_argument(
        "--speech", dest="speech", action="store_const", const="always", default="auto",
        help="자막을 무시하고 항상 음성 인식으로 읽기",
    )
    speech.add_argument(
        "--no-speech", dest="speech", action="store_const", const="never",
        help="자막이 없어도 음성 인식을 하지 않기",
    )
    p.add_argument(
        "-m", "--model", default=None,
        help="음성 인식 모델: tiny, base, small(기본), medium, large-v3 "
             "(클수록 정확하지만 느림)",
    )
    p.add_argument("-o", "--output", help="결과를 저장할 파일 경로")
    p.add_argument(
        "-s", "--summarize", action="store_true",
        help="Claude로 요약 (ANTHROPIC_API_KEY 필요)",
    )
    p.add_argument("-a", "--ask", metavar="질문", help="영상 내용에 대해 Claude에게 질문")
    p.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    languages = tuple(x.strip() for x in args.lang.split(",") if x.strip())

    try:
        video = read_video(args.video, languages, args.speech, args.model)
    except YtReadError as e:
        print(f"오류: {e}", file=sys.stderr)
        return 1

    if args.summarize or args.ask:
        from .summarize import ask_claude

        try:
            result = ask_claude(video, args.ask)
        except Exception as e:  # noqa: BLE001 - CLI에서 오류 메시지만 보여준다
            print(f"오류: Claude 호출 실패 - {e}", file=sys.stderr)
            return 1
        title = video.title or video.video_id
        result = f"# {title}\n\n{video.url}\n\n{result}\n"
    elif args.format == "json":
        result = to_json(video) + "\n"
    elif args.format == "text":
        result = video.text + "\n"
    else:
        result = to_markdown(video)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(result)
        print(f"저장했습니다: {args.output}", file=sys.stderr)
    else:
        sys.stdout.write(result)
    return 0


if __name__ == "__main__":
    sys.exit(main())
