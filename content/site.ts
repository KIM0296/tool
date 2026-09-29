// 랜딩페이지의 모든 문구와 링크는 이 파일에서 수정합니다.
// 페이지 코드(app/page.tsx)는 건드리지 않아도 됩니다.

export const site = {
  name: "Tool",
  title: "Tool — 반복 업무를 자동으로 끝내는 가장 쉬운 방법",
  description:
    "Tool은 매일 반복되는 업무를 몇 번의 클릭으로 자동화해 주는 앱입니다. 지금 무료로 시작해 보세요.",

  // 구매/가입 버튼이 이동할 주소
  cta: {
    primaryLabel: "무료로 시작하기",
    primaryHref: "https://example.com/signup",
    secondaryLabel: "기능 살펴보기",
    secondaryHref: "#features",
  },

  hero: {
    badge: "새로운 버전 출시",
    headline: "반복 업무는 Tool에게,\n당신은 중요한 일에 집중하세요",
    subheadline:
      "복잡한 설정 없이 몇 분 만에 업무 흐름을 자동화하세요. 설치부터 첫 자동화까지 5분이면 충분합니다.",
    note: "신용카드 없이 14일 무료 체험",
  },

  stats: [
    { value: "10,000+", label: "사용 중인 팀" },
    { value: "주 8시간", label: "평균 절약 시간" },
    { value: "4.9 / 5", label: "사용자 평점" },
  ],

  features: [
    {
      icon: "⚡",
      title: "클릭 몇 번으로 자동화",
      body: "코딩 없이 드래그 앤 드롭으로 업무 흐름을 만들 수 있습니다.",
    },
    {
      icon: "🔗",
      title: "자주 쓰는 도구와 연동",
      body: "메일, 캘린더, 스프레드시트, 메신저 등 이미 쓰는 서비스와 바로 연결됩니다.",
    },
    {
      icon: "📊",
      title: "한눈에 보는 대시보드",
      body: "진행 상황과 절약된 시간을 실시간으로 확인하세요.",
    },
    {
      icon: "👥",
      title: "팀과 함께 사용",
      body: "권한 관리와 공유 기능으로 팀 전체의 업무 흐름을 맞출 수 있습니다.",
    },
    {
      icon: "🔒",
      title: "안전한 데이터 보호",
      body: "모든 데이터는 암호화되어 저장되고 전송됩니다.",
    },
    {
      icon: "📱",
      title: "어디서나 접속",
      body: "PC, 태블릿, 모바일 어디서든 같은 화면으로 이어서 작업하세요.",
    },
  ],

  steps: [
    { title: "가입하기", body: "이메일로 30초 만에 계정을 만드세요." },
    { title: "도구 연결하기", body: "평소 쓰는 서비스를 클릭 한 번으로 연결합니다." },
    { title: "자동화 켜기", body: "템플릿을 고르거나 직접 만들어 바로 실행하세요." },
  ],

  pricing: [
    {
      name: "무료",
      price: "₩0",
      period: "/월",
      features: ["자동화 3개", "기본 연동", "커뮤니티 지원"],
      ctaLabel: "무료로 시작",
      ctaHref: "https://example.com/signup",
      highlighted: false,
    },
    {
      name: "프로",
      price: "₩9,900",
      period: "/월",
      features: ["자동화 무제한", "모든 연동", "우선 지원", "고급 대시보드"],
      ctaLabel: "프로 구매하기",
      ctaHref: "https://example.com/checkout/pro",
      highlighted: true,
    },
    {
      name: "팀",
      price: "₩29,900",
      period: "/월",
      features: ["프로의 모든 기능", "팀원 10명", "권한 관리", "전담 매니저"],
      ctaLabel: "팀 플랜 구매",
      ctaHref: "https://example.com/checkout/team",
      highlighted: false,
    },
  ],

  faq: [
    {
      q: "무료 체험 후 자동으로 결제되나요?",
      a: "아니요. 체험 기간이 끝나도 직접 유료 플랜을 선택하기 전까지는 결제되지 않습니다.",
    },
    {
      q: "언제든지 해지할 수 있나요?",
      a: "네. 설정 화면에서 언제든지 해지할 수 있으며, 남은 기간까지는 계속 사용할 수 있습니다.",
    },
    {
      q: "개발 지식이 없어도 쓸 수 있나요?",
      a: "네. 대부분의 자동화는 템플릿과 클릭만으로 만들 수 있도록 설계되었습니다.",
    },
    {
      q: "데이터는 안전한가요?",
      a: "모든 데이터는 전송 및 저장 시 암호화되며, 외부에 공유되지 않습니다.",
    },
  ],

  finalCta: {
    headline: "오늘부터 반복 업무에서 벗어나세요",
    body: "지금 가입하면 14일 동안 모든 기능을 무료로 사용할 수 있습니다.",
  },

  footer: {
    company: "© 2026 Tool. All rights reserved.",
    links: [
      { label: "이용약관", href: "#" },
      { label: "개인정보처리방침", href: "#" },
      { label: "문의하기", href: "mailto:hello@example.com" },
    ],
  },
};
