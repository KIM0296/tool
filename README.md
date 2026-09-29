# Tool 랜딩페이지

Next.js(App Router)로 만든 앱/소프트웨어 제품 랜딩페이지입니다.

## 문구·링크 수정

모든 문구, 요금제, FAQ, 구매/가입 링크는 **`content/site.ts`** 한 파일에 있습니다.
특히 아래 주소를 실제 가입·결제 페이지로 바꿔주세요.

- `cta.primaryHref`: 상단, 히어로, 하단의 "무료로 시작하기" 버튼
- `pricing[].ctaHref`: 요금제별 구매 버튼

## 로컬 실행

```bash
npm install
npm run dev   # http://localhost:3000
```

## Vercel 배포

1. https://vercel.com/new 에서 이 GitHub 저장소를 Import합니다.
2. 설정은 기본값(Framework: Next.js) 그대로 두고 Deploy를 누릅니다.
3. 이후에는 브랜치에 push할 때마다 자동으로 배포됩니다.
