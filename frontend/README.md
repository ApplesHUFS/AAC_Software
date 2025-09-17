# Frontend - 웹 애플리케이션

AAC 카드 해석 시스템의 React 기반 프론트엔드 웹 애플리케이션입니다.

## 주요 기능

- **사용자 인증 및 관리**: 도움이 회원가입/로그인, 소통이 프로필 관리
- **대화 세션 관리**: 새 세션 시작, 진행 중 세션 이어하기, 자동 저장
- **상황 설정**: 도움이가 현재 상황 입력, 소통이 맥락 정보 제공
- **AAC 카드 선택**: 개인화된 추천, 히스토리 네비게이션, 다중 선택 (1-4개)
- **AI 해석 및 피드백**: OpenAI API 해석 생성, 도움이 피드백 수집
- **애플리케이션 흐름**: 인증 → 대시보드 → 상황설정 → 카드선택 → 해석

## 기술 스택

- **React 18.2**: 사용자 인터페이스 구축
- **JavaScript ES6+**: 메인 프로그래밍 언어
- **CSS3**: 스타일링 및 반응형 디자인
- **Session Storage**: 세션 데이터 관리
- **Fetch API**: 백엔드 서버와의 HTTP 통신
- **React Hooks**: 상태 관리 (useState, useEffect)

## 아키텍처

### 디렉토리 구조

```
frontend/
├── public/                         # 정적 파일
│   ├── index.html                 # 메인 HTML 템플릿
│   └── manifest.json              # PWA 설정
├── src/                           # 소스 코드
│   ├── App.js                     # 메인 애플리케이션 컴포넌트
│   ├── index.js                   # 앱 진입점
│   ├── pages/                     # 페이지 컴포넌트
│   │   ├── AuthPage.js            # 인증 페이지
│   │   ├── DashboardPage.js       # 대시보드 페이지
│   │   ├── CardSelectionPage.js   # 카드 선택 페이지
│   │   └── InterpretationPage.js  # 해석 및 피드백 페이지
│   ├── components/                # 재사용 컴포넌트
│   │   ├── auth/                  # 인증 관련
│   │   ├── cards/                 # 카드 관련
│   │   ├── context/               # 상황 설정
│   │   ├── interpretation/        # 해석 관련
│   │   └── profile/               # 프로필 관련
│   ├── services/                  # 서비스 레이어
│   │   ├── api.js                 # API 클라이언트
│   │   ├── authService.js         # 인증 서비스
│   │   ├── cardService.js         # 카드 관련 서비스
│   │   ├── contextService.js      # 상황 설정 서비스
│   │   └── feedbackService.js     # 피드백 서비스
│   └── styles/                    # 스타일 파일
│       ├── globals.css            # 전역 스타일
│       ├── common.css             # 공통 컴포넌트 스타일
│       ├── themes.css             # 테마 설정
│       ├── auth.css               # 인증 페이지 스타일
│       ├── dashboard.css          # 대시보드 스타일
│       ├── cards.css              # 카드 관련 스타일
│       ├── interpretation.css     # 해석 페이지 스타일
│       ├── context.css            # 상황 설정 스타일
│       └── responsive.css         # 반응형 디자인
└── package.json                   # 프로젝트 설정 및 의존성
```

### 애플리케이션 흐름

1. **인증 (AUTH)**: 도움이 회원가입/로그인 → 세션 저장 → 대시보드 이동
2. **대시보드 (DASHBOARD)**: 프로필 관리, 새 세션 시작/이어하기
3. **상황 설정 (CONTEXT)**: 도움이가 상황 입력, 소통이 상태 정보 제공
4. **카드 선택 (CARDS)**: 소통이가 AAC 카드 선택, 개인화된 추천 적용
5. **해석 (INTERPRETATION)**: AI 해석 생성, 도움이 피드백 제공

## 설치 및 실행

### 사전 요구사항
- Node.js 16.0.0 이상
- npm 8.0.0 이상
- 백엔드 서버 실행 (기본: http://localhost:8000)

### 설치
```bash
npm install
```

### 개발 서버 실행
```bash
npm start
```
브라우저에서 http://localhost:3000에 접속하여 애플리케이션을 확인할 수 있습니다.

### 빌드
```bash
npm run build
```
프로덕션용 빌드 파일이 `build/` 디렉토리에 생성됩니다.

### 테스트
```bash
npm test
```

### 코드 품질 관리
```bash
npm run lint      # ESLint 검사
npm run lint:fix  # ESLint 자동 수정
npm run format    # Prettier 포맷팅
npm run analyze   # 빌드 분석
```

## 설정

### 환경 변수
- `REACT_APP_API_URL`: 백엔드 API 서버 URL (기본값: http://localhost:8000)

### 주요 특징
- **세션 관리**: sessionStorage 기반 데이터 관리, 새로고침 시 진행 상황 유지
- **상태 관리**: React Hooks 활용, 단계별 진행 상황 추적
- **API 통신**: 중앙화된 클라이언트, 재시도 로직, 30초 타임아웃
- **반응형 디자인**: 모바일/태블릿/데스크톱 지원, 터치 친화적

## 문제 해결

### 일반적인 문제

1. **API 연결 오류**: 백엔드 서버 실행 상태 및 포트(8000) 확인
2. **빌드 오류**: Node.js 버전 및 의존성 설치 상태 확인
3. **CORS 오류**: 백엔드 CORS 설정에서 프론트엔드 URL 허용 확인

### 디버깅

```bash
# 개발 모드로 실행 (기본)
npm start

# 브라우저 개발자 도구 활용
# F12 → Network 탭에서 API 요청 상태 확인
```