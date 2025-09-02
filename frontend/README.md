# AAC 카드 해석 시스템 - 프론트엔드

개인화된 AAC (Augmentative and Alternative Communication) 카드 추천 및 해석 시스템의 React 기반 프론트엔드 애플리케이션입니다.

## 주요 기능

### 사용자 관리
- 회원가입: 개인 페르소나 정보 입력 (나이, 성별, 장애 유형, 의사소통 특성, 관심 주제)
- 로그인 및 인증
- 프로필 편집 및 업데이트

### 대화 상황 관리
- 현재 상황 입력 (장소, 대화 상대, 현재 활동)
- 상황별 맞춤 카드 추천

### 카드 추천 및 선택
- 개인 관심사 기반 카드 추천 (70% 관련 카드 + 30% 랜덤)
- 히스토리 기반 페이지 네비게이션
- 카드 재추천 (리롤) 기능
- 최대 4개 카드 선택

### AI 해석 및 피드백
- OpenAI API 기반 3가지 해석 생성
- Partner 피드백 수집
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
│   │   ├── LoginForm.js
│   │   └── RegisterForm.js
│   ├── cards/                      # 카드 관련 컴포넌트
│   │   ├── CardGrid.js
│   │   └── CardHistoryNavigation.js
│   ├── context/                    # 상황 입력 컴포넌트
│   │   └── ContextForm.js
│   ├── interpretation/             # 해석 관련 컴포넌트
│   │   ├── InterpretationDisplay.js
│   │   └── FeedbackForm.js
│   └── profile/                    # 프로필 관련 컴포넌트
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
    └── App.css                     # 메인 스타일시트
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

### 프로덕션 빌드
```bash
npm run build
```

### 코드 품질 관리
```bash
# ESLint 검사
npm run lint

# 자동 수정
npm run lint:fix

# Prettier 포맷팅
npm run format
```

## 환경 설정

`.env` 파일을 생성하여 환경 변수 설정:

```bash
REACT_APP_API_URL=http://localhost:8000
NODE_ENV=development
```

## API 엔드포인트

### 인증 (Authentication)
- `POST /api/auth/register` - 회원가입
- `POST /api/auth/login` - 로그인
- `GET /api/auth/profile/{userId}` - 프로필 조회
- `PUT /api/auth/profile/{userId}` - 프로필 업데이트

### 상황 관리 (Context)
- `POST /api/context` - 대화 상황 생성
- `GET /api/context/{contextId}` - 상황 조회

### 카드 관리 (Cards)
- `POST /api/cards/recommend` - 카드 추천
- `POST /api/cards/validate` - 선택 검증
- `POST /api/cards/interpret` - 카드 해석
- `GET /api/cards/history/{contextId}` - 히스토리 요약
- `GET /api/cards/history/{contextId}/page/{pageNumber}` - 히스토리 페이지

### 피드백 (Feedback)
- `POST /api/feedback/request` - 피드백 요청
- `POST /api/feedback/submit` - 피드백 제출

### 이미지 서빙
- `GET /api/images/{filename}` - 카드 이미지

## 주요 특징

### 사용자 친화적 디자인
- 직관적인 사용자 인터페이스
- 반응형 디자인 (모바일/태블릿/데스크톱 지원)
- 접근성 고려 (키보드 네비게이션, 스크린 리더 지원)

### 상태 관리
- localStorage 기반 세션 유지
- 페이지 새로고침 시 진행상태 복원
- 에러 상황에서 적절한 fallback 제공

### 성능 최적화
- 이미지 지연 로딩 (lazy loading)
- API 요청 재시도 로직
- 컴포넌트 메모이제이션

### 에러 처리
- 네트워크 오류 자동 재시도
- 사용자 친화적 에러 메시지
- 폴백 UI 제공

## 개발 가이드라인

### 컴포넌트 작성 원칙
1. 단일 책임 원칙 준수
2. PropTypes 또는 TypeScript 사용 권장
3. 재사용 가능한 컴포넌트 작성
4. 접근성 속성 (ARIA) 포함

### 상태 관리
- 로컬 상태는 useState 사용
- 전역 상태는 localStorage 활용
- 상태 변경 시 적절한 검증 수행

### API 호출
- 서비스 레이어 패턴 사용
- 에러 처리 필수
- 로딩 상태 관리

### 스타일링
- BEM 방법론 기반 클래스 명명
- CSS 변수 활용
- 반응형 디자인 적용

## 배포

### 개발 환경
```bash
npm start
```

### 프로덕션 환경
```bash
npm run build
npx serve -s build
```

### Docker 배포 (선택사항)
```dockerfile
FROM node:16-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npx", "serve", "-s", "build"]
```

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