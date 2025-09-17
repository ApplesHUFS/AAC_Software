# Frontend - 웹 애플리케이션

AAC 카드 해석 시스템의 React 기반 프론트엔드 웹 애플리케이션입니다.

### 사용자 역할
- **도움이**: 소통이를 돕는 보호자, 교사, 치료사 등
- **소통이**: 의사소통에 어려움을 겪는 사용자

## 주요 기능

### 1. 사용자 인증 및 관리
- 도움이 회원가입/로그인 시스템
- 소통이 프로필 관리 (나이, 성별, 장애 유형, 의사소통 특성, 관심 주제)
- 프로필 편집 및 업데이트

### 2. 대화 세션 관리
- 새로운 대화 세션 시작
- 진행 중인 세션 이어하기
- 세션 상태 자동 저장 및 복원

### 3. 상황 설정 (Context)
- 도움이가 현재 상황 입력 (장소, 대화 상대, 활동 내용)
- 소통이의 현재 상태 및 맥락 정보 제공

### 4. AAC 카드 선택
- 개인화된 카드 추천 (관심사 50% + 상황 맥락 50%)
- 히스토리 기반 페이지 네비게이션
- 카드 재추천 (리롤) 기능
- 다중 카드 선택 (최소 1개, 최대 4개)

### 5. AI 해석 및 피드백
- OpenAI API 기반 다양한 해석 생성
- 도움이의 피드백 작성 및 저장
- 해석 결과 학습 데이터 축적

## 기술 스택

- **React 18.2.0**: 사용자 인터페이스 구축
- **JavaScript (ES6+)**: 메인 프로그래밍 언어
- **CSS3**: 스타일링 및 반응형 디자인
- **Session Storage**: 세션 데이터 관리
- **Fetch API**: 백엔드 서버와의 HTTP 통신
- **React Hooks**: 상태 관리 (useState, useEffect)

## 프로젝트 구조

```
frontend/
├── public/                         # 정적 파일
│   ├── index.html                 # 메인 HTML 템플릿
│   └── manifest.json              # PWA 설정
├── src/                           # 소스 코드
│   ├── App.js                     # 메인 애플리케이션 컴포넌트
│   ├── index.js                   # 앱 진입점
│   │
│   ├── pages/                     # 페이지 컴포넌트
│   │   ├── AuthPage.js            # 인증 페이지 (로그인/회원가입)
│   │   ├── DashboardPage.js       # 대시보드 페이지
│   │   ├── CardSelectionPage.js   # 카드 선택 페이지
│   │   └── InterpretationPage.js  # 해석 및 피드백 페이지
│   │
│   ├── components/                # 재사용 가능한 컴포넌트
│   │   ├── auth/                  # 인증 관련 컴포넌트
│   │   │   ├── LoginForm.js       # 로그인 폼
│   │   │   └── RegisterForm.js    # 회원가입 폼
│   │   ├── cards/                 # 카드 관련 컴포넌트
│   │   │   ├── CardGrid.js        # 카드 그리드 표시
│   │   │   └── CardHistoryNavigation.js # 카드 히스토리 네비게이션
│   │   ├── context/               # 상황 설정 컴포넌트
│   │   │   └── ContextForm.js     # 상황 입력 폼
│   │   ├── interpretation/        # 해석 관련 컴포넌트
│   │   │   └── InterpretationDisplay.js # 해석 결과 표시
│   │   └── profile/               # 프로필 관련 컴포넌트
│   │       └── ProfileEditForm.js # 프로필 편집 폼
│   │
│   ├── services/                  # 서비스 레이어
│   │   ├── api.js                 # API 클라이언트
│   │   ├── authService.js         # 인증 서비스
│   │   ├── cardService.js         # 카드 관련 서비스
│   │   ├── contextService.js      # 상황 설정 서비스
│   │   └── feedbackService.js     # 피드백 서비스
│   │
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
│
├── package.json                   # 프로젝트 설정 및 의존성
├── package-lock.json              # 의존성 잠금 파일
├── .gitignore                     # Git 무시 파일 설정
└── README.md                      # 프로젝트 문서
```

## 애플리케이션 흐름

### 1. 인증 단계 (AUTH)
- 도움이가 회원가입 또는 로그인
- 사용자 정보 세션에 저장
- 대시보드로 자동 이동

### 2. 대시보드 단계 (DASHBOARD)
- 사용자 프로필 관리 및 편집
- 새 대화 세션 시작
- 진행 중인 세션 이어하기

### 3. 상황 설정 단계 (CONTEXT)
- 도움이가 소통 상황 및 맥락 입력
- 소통이의 현재 상태 정보 제공
- 카드 선택 단계로 진행

### 4. 카드 선택 단계 (CARDS)
- 소통이가 의사를 표현할 AAC 카드 선택
- 개인화된 카드 추천 알고리즘 적용
- 선택된 카드들이 서버로 전송

### 5. 해석 단계 (INTERPRETATION)
- AI가 선택된 카드를 분석하여 의사소통 내용 해석
- 도움이가 해석 결과 확인 및 피드백 제공
- 피드백 데이터 학습 시스템에 저장

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
# ESLint 검사
npm run lint

# ESLint 자동 수정
npm run lint:fix

# Prettier 코드 포맷팅
npm run format

# 빌드 분석
npm run analyze
```

## 주요 특징

### 세션 관리
- `sessionStorage`를 사용한 세션 데이터 관리
- 사용자 새로고침 시에도 진행 상황 유지
- 최소한의 로컬 저장소 사용으로 개인정보 보호

### 상태 관리
- React의 `useState`와 `useEffect`를 활용한 상태 관리
- 단계별 진행 상황 추적 (AUTH → DASHBOARD → CARDS → INTERPRETATION)
- 컴포넌트 간 props를 통한 데이터 전달

### API 통신
- 중앙화된 API 클라이언트 (`src/services/api.js`)
- 재시도 로직 및 에러 처리
- 타임아웃 설정 (30초)으로 안정성 향상
- HTTP 상태 코드별 에러 메시지 매핑

### 반응형 디자인
- 모바일, 태블릿, 데스크톱 지원
- CSS Grid 및 Flexbox 활용
- 터치 친화적 인터페이스

## 환경 설정

### 환경 변수
- `REACT_APP_API_URL`: 백엔드 API 서버 URL (기본값: http://localhost:8000)

### 프록시 설정
개발 환경에서는 `package.json`의 `proxy` 설정을 통해 백엔드 서버로 API 요청을 프록시합니다.

## 브라우저 지원

### Production
- 사용률 0.2% 이상의 브라우저
- 더 이상 지원되지 않는 브라우저 제외
- Opera Mini 제외

### Development
- 최신 Chrome, Firefox, Safari

## 개발 가이드라인

### 코드 스타일
- ESLint 규칙 준수
- Prettier를 통한 일관된 코드 포맷팅
- React 함수형 컴포넌트 사용

### 컴포넌트 구조
- 단일 책임 원칙 적용
- Props를 통한 데이터 전달
- 재사용 가능한 컴포넌트 설계

### 네이밍 컨벤션
- 컴포넌트: PascalCase (예: `CardGrid.js`)
- 함수: camelCase (예: `handleCardSelection`)
- 상수: UPPER_SNAKE_CASE (예: `APP_STEPS`)

## 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 연관 프로젝트

- **백엔드 서버**: `../backend/` - FastAPI 기반 API 서버
- **데이터 처리**: `../data_processing/` - AAC 카드 데이터 및 AI 모델 처리