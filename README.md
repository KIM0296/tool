# ytread — 유튜브 컨텐츠 리더

유튜브 영상 주소를 넣으면 **제목·채널·자막 전문**을 가져오고, 원하면 **Claude로 요약하거나 질문**할 수 있는 명령줄 도구입니다.

## 가장 쉬운 사용법: Claude Code 스킬

이 저장소를 내 PC에 받아서 Claude Code로 열면 `youtube-reader` 스킬이 자동으로 켜집니다.
채팅에 유튜브 링크를 붙여 넣고 "요약해줘"라고 하면 Claude가 자막을 가져와 정리합니다 (API 키 불필요).

```bash
git clone https://github.com/KIM0296/tool.git
cd tool
pip install -e ".[speech]"   # 자막 없는 영상도 읽으려면 [speech] 포함
claude          # Claude Code 실행 후: "https://youtu.be/... 이 영상 요약해줘"
```

> 유튜브는 클라우드 서버 접속을 자주 차단하므로 **내 PC에서 실행**해야 잘 동작합니다.

## 설치 (명령어로 직접 쓰기)

```bash
pip install -e .            # 기본 (자막 읽기)
pip install -e ".[speech]"  # 자막 없는 영상도 음성 인식으로 읽기
pip install -e ".[ai]"      # Claude API 요약 기능까지
```

## 사용법

```bash
# 자막을 마크다운으로 출력 (타임스탬프를 누르면 해당 시점으로 이동)
ytread https://youtu.be/VIDEO_ID

# 순수 텍스트 / JSON 으로
ytread https://www.youtube.com/watch?v=VIDEO_ID -f text
ytread VIDEO_ID -f json -o result.json

# 자막 언어 우선순위 지정 (기본 ko,en — 없으면 번역 자막 사용)
ytread VIDEO_ID -l en,ko

# Claude로 요약 / 질문 (ANTHROPIC_API_KEY 필요)
export ANTHROPIC_API_KEY=...
ytread VIDEO_ID --summarize
ytread VIDEO_ID --ask "이 영상에서 추천하는 도구들을 표로 정리해줘"
```

## 자막이 없는 영상

자막이 없으면 영상의 음성을 내려받아 **내 PC에서 Whisper로 직접 받아씁니다** (무료, API 키 불필요).

```bash
ytread VIDEO_ID                 # 자막이 없으면 자동으로 음성 인식
ytread VIDEO_ID -m medium       # 더 정확한 모델 (더 느림)
ytread VIDEO_ID --speech        # 자막이 있어도 음성 인식 사용
ytread VIDEO_ID --no-speech     # 음성 인식 끄기
```

- 모델: `tiny` < `base` < `small`(기본) < `medium` < `large-v3` — 클수록 정확하지만 느립니다. 한국어는 `small` 이상을 권장합니다.
- 처음 실행할 때 모델 파일을 한 번 내려받습니다 (small 약 500MB).
- 일반 PC(CPU)에서 `small` 모델은 영상 길이의 대략 1/3~1배 시간이 걸립니다. NVIDIA GPU가 있으면 훨씬 빠릅니다.

지원하는 주소 형식: `youtube.com/watch?v=`, `youtu.be/`, `/shorts/`, `/embed/`, `/live/`, 모바일(`m.youtube.com`), 영상 ID 11자리.

## 파이썬에서 쓰기

```python
from ytread.core import read_video, to_markdown

video = read_video("https://youtu.be/VIDEO_ID")
print(video.title, video.author)
print(video.text)          # 자막 전체 텍스트
print(to_markdown(video))
```

## 참고

- 클라우드 서버 IP는 유튜브가 차단하는 경우가 많아, 개인 PC에서 실행하는 것을 권장합니다.
- 요약은 `claude-opus-5-5` 모델을 사용합니다 (`ytread/summarize.py`의 `MODEL`).

## 테스트

```bash
pip install -e ".[dev]"
pytest
```
