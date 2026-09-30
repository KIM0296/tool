import json
from types import SimpleNamespace

import pytest
from youtube_transcript_api._errors import NoTranscriptFound

from ytread import cli, core

VID = "dQw4w9WgXcQ"


@pytest.mark.parametrize(
    "value",
    [
        VID,
        f"https://www.youtube.com/watch?v={VID}",
        f"https://youtube.com/watch?feature=share&v={VID}&t=10s",
        f"https://m.youtube.com/watch?v={VID}",
        f"https://youtu.be/{VID}?si=abc",
        f"youtu.be/{VID}",
        f"https://www.youtube.com/shorts/{VID}",
        f"https://www.youtube.com/embed/{VID}",
        f"https://www.youtube.com/live/{VID}",
    ],
)
def test_extract_video_id(value):
    assert core.extract_video_id(value) == VID


@pytest.mark.parametrize("value", ["", "hello", "https://example.com/watch?v=" + VID])
def test_extract_video_id_invalid(value):
    with pytest.raises(core.YtReadError):
        core.extract_video_id(value)


def test_format_timestamp():
    assert core.format_timestamp(5.9) == "00:05"
    assert core.format_timestamp(125) == "02:05"
    assert core.format_timestamp(3725) == "1:02:05"


class FakeTranscript:
    def __init__(self, lang, generated=False, translatable=True):
        self.language_code = lang
        self.is_generated = generated
        self.is_translatable = translatable

    def translate(self, lang):
        return FakeTranscript(lang, self.is_generated)

    def fetch(self):
        return SimpleNamespace(
            language_code=self.language_code,
            is_generated=self.is_generated,
            snippets=[
                SimpleNamespace(start=0.0, duration=2.0, text="안녕하세요"),
                SimpleNamespace(start=65.2, duration=3.0, text="반갑습니다"),
            ],
        )


class FakeList:
    def __init__(self, items):
        self.items = items

    def __iter__(self):
        return iter(self.items)

    def find_transcript(self, languages):
        for lang in languages:
            for t in self.items:
                if t.language_code == lang:
                    return t
        raise NoTranscriptFound(VID, languages, self)


class FakeApi:
    def __init__(self, items):
        self._list = FakeList(items)

    def list(self, video_id):
        return self._list


def test_fetch_transcript_prefers_language():
    api = FakeApi([FakeTranscript("en"), FakeTranscript("ko", generated=True)])
    segments, lang, generated = core.fetch_transcript(VID, ("ko", "en"), api)
    assert lang == "ko" and generated is True
    assert [s.text for s in segments] == ["안녕하세요", "반갑습니다"]


def test_fetch_transcript_translates_when_missing():
    api = FakeApi([FakeTranscript("ja")])
    _, lang, _ = core.fetch_transcript(VID, ("ko",), api)
    assert lang == "ko"


def test_fetch_transcript_none_available():
    with pytest.raises(core.YtReadError):
        core.fetch_transcript(VID, ("ko",), FakeApi([]))


@pytest.fixture
def fake_network(monkeypatch):
    monkeypatch.setattr(
        core, "fetch_metadata",
        lambda vid: {"title": "테스트 영상", "author_name": "테스트 채널"},
    )
    api = FakeApi([FakeTranscript("ko")])
    orig = core.fetch_transcript
    monkeypatch.setattr(
        core, "fetch_transcript", lambda vid, langs: orig(vid, langs, api)
    )


def test_cli_markdown(fake_network, capsys):
    assert cli.main([f"https://youtu.be/{VID}"]) == 0
    out = capsys.readouterr().out
    assert "# 테스트 영상" in out
    assert "채널: 테스트 채널" in out
    assert f"[01:05](https://www.youtube.com/watch?v={VID}&t=65s) 반갑습니다" in out


def test_cli_json(fake_network, capsys):
    assert cli.main([VID, "-f", "json"]) == 0
    data = json.loads(capsys.readouterr().out)
    assert data["video_id"] == VID and len(data["segments"]) == 2


def test_cli_text_to_file(fake_network, tmp_path):
    out = tmp_path / "out.txt"
    assert cli.main([VID, "-f", "text", "-o", str(out)]) == 0
    assert out.read_text(encoding="utf-8") == "안녕하세요 반갑습니다\n"


def test_cli_invalid_url(capsys):
    assert cli.main(["not a url"]) == 1
    assert "오류" in capsys.readouterr().err


# --- 자막이 없을 때 음성 인식으로 대신 읽기 ---

from ytread import speech  # noqa: E402


@pytest.fixture
def no_subtitles(monkeypatch):
    monkeypatch.setattr(core, "fetch_metadata", lambda vid: {"title": "자막 없는 영상"})

    def fetch_transcript(vid, langs):
        raise core.NoSubtitlesError("이 영상에는 자막이 없습니다.")

    monkeypatch.setattr(core, "fetch_transcript", fetch_transcript)


@pytest.fixture
def fake_speech(monkeypatch):
    calls = []

    def transcribe(video_id, model_size):
        calls.append(model_size)
        return [core.Segment(1.0, 2.0, "음성으로 받아쓴 문장")], "ko"

    monkeypatch.setattr(speech, "is_available", lambda: True)
    monkeypatch.setattr(speech, "transcribe", transcribe)
    return calls


def test_falls_back_to_speech(no_subtitles, fake_speech, capsys):
    assert cli.main([VID]) == 0
    out = capsys.readouterr().out
    assert "음성 인식" in out and "음성으로 받아쓴 문장" in out
    assert fake_speech == ["small"]


def test_speech_model_option(no_subtitles, fake_speech):
    assert cli.main([VID, "-m", "medium", "-f", "text"]) == 0
    assert fake_speech == ["medium"]


def test_no_speech_option(no_subtitles, fake_speech, capsys):
    assert cli.main([VID, "--no-speech"]) == 1
    assert "자막이 없습니다" in capsys.readouterr().err
    assert fake_speech == []


def test_speech_not_installed(no_subtitles, monkeypatch, capsys):
    monkeypatch.setattr(speech, "is_available", lambda: False)
    assert cli.main([VID]) == 1
    assert ".[speech]" in capsys.readouterr().err


def test_force_speech_skips_subtitles(fake_network, fake_speech, capsys):
    assert cli.main([VID, "--speech", "-f", "json"]) == 0
    data = json.loads(capsys.readouterr().out)
    assert data["source"] == "speech"
    assert data["segments"][0]["text"] == "음성으로 받아쓴 문장"


def test_transcripts_disabled_is_no_subtitles():
    from youtube_transcript_api._errors import TranscriptsDisabled

    class Api:
        def list(self, video_id):
            raise TranscriptsDisabled(video_id)

    with pytest.raises(core.NoSubtitlesError):
        core.fetch_transcript(VID, ("ko",), Api())
