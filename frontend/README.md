# AAC 카드 해석 시스템 - 프론트엔드

개인화된 AAC (Augmentative and Alternative Communication) 카드 추천 및 해석 시스템의 React 기반 프론트엔드 애플리케이션입니다.

## 주요 기능

### 사용자 관리
- 회원가입: 사용자의 페르소나 정보 입력 (나이, 성별, 장애 유형, 의사소통 특성, 관심 주제)
- 로그인 및 사용자 인증
- 프로필 편집 및 페르소나 업데이트

### 대화 상황 관리
- 현재 상황 입력 (장소, 대화 상대, 현재 활동)

### 카드 추천 및 선택
- 개인 관심사와 상황 기반 카드 추천 (50% 상황 관련 카드 + 50% 관심사 관련 카드)
- 히스토리 기반 페이지 네비게이션
- 카드 재추천 (리롤) 기능
- 최소 1개, 최대 4개 카드 선택

### AI 해석 및 피드백
- OpenAI API 기반 3가지 해석 생성
- Partner의 피드백 작성
- 해석 결과 저장 및 학습

## 기술 스택

- **Frontend**: React 18.2.0
- **HTTP Client**: Native Fetch API with custom wrapper
- **Styling**: CSS3 with CSS Grid and Flexbox
- **State Management**: React Hooks (useState, useEffect)
- **Storage**: localStorage for session management

## 프로젝트 구조

```
src/
├── App.js                          # 메인 애플리케이션 컴포넌트
├── index.js                        # 앱 진입점
│
├── pages/                          # 페이지 컴포넌트
│   ├── AuthPage.js                 # 로그인/회원가입 페이지
│   ├── DashboardPage.js            # 메인 대시보드
│   ├── CardSelectionPage.js        # 카드 선택 페이지
│   └── InterpretationPage.js       # 해석 및 피드백 페이지
│
├── components/                     # 재사용 컴포넌트
│   ├── auth/                       # 인증 관련 컴포넌트
│   │   ├── LoginForm.js            # 사용자 로그인 컴포넌트
│   │   └── RegisterForm.js         # 회원가입 컴포넌트
│   ├── cards/                      # 카드 관련 컴포넌트
│   │   ├── CardGrid.js
│   │   └── CardHistoryNavigation.js
│   ├── context/                    # 상황 입력 컴포넌트
│   │   └── ContextForm.js
│   ├── interpretation/             # 해석 관련 컴포넌트
│   │   └── InterpretationDisplay.js   
│   └── profile/                    # 프로필 수정 관련 컴포넌트
│       └── ProfileEditForm.js
│
├── services/                       # API 서비스
│   ├── api.js                      # 기본 API 클라이언트
│   ├── authService.js              # 인증 서비스
│   ├── cardService.js              # 카드 관리 서비스
│   ├── contextService.js           # 상황 관리 서비스
│   └── feedbackService.js          # 피드백 관리 서비스
│
└── styles/                         # 스타일시트
    ├── auth.css                    # 인증 페이지 스타일
    ├── cards.css                   # 카드 선택 페이지 스타일
    ├── common.css                  # 공통 컴포넌트
    ├── context.css                 # 컨텍스트 폼 스타일
    ├── dashborad.css               # 대시보드 페이지 스타일
    ├── globals.css                 # 전역 설정
    ├── interpretation.css          # 해석 페이지 스타일
    ├── responsive.css              # 반응현 디자인
    └── themes.css                  # 도움이 (partner) 테마

```

## 설치 및 실행

### 사전 요구사항
- Node.js 16.0.0 이상
- npm 8.0.0 이상
- 백엔드 서버 (localhost:8000)

### 설치
```bash
npm install
```

### 개발 서버 실행
```bash
npm start
```
브라우저에서 http://localhost:3000 접속

## 라이센스

이 프로젝트는 MIT 라이센스 하에 배포됩니다.

## 기여

프로젝트 개선을 위한 기여를 환영합니다. 다음 절차를 따라주세요:

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 지원

문제가 발생하거나 문의사항이 있으면 이슈를 생성해주세요.