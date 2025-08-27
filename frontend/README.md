# AAC 카드 해석 시스템 - Frontend

React를 사용한 AAC 카드 해석 시스템의 프론트엔드 애플리케이션입니다.

## 주요 기능

### 1. 사용자 관리
- **회원가입**: 사용자 페르소나 정보 입력 및 계정 생성
- **로그인**: 사용자 인증 (최대 5회 시도 제한)
- **프로필 관리**: 페르소나 정보 수정

### 2. 대화 세션 관리
- **컨텍스트 입력**: 대화 상황 정보 설정
  - 장소 (필수)
  - 대화 상대 (필수)
  - 현재 활동 (선택사항)

### 3. 카드 추천 및 선택
- **개인화된 추천**: 사용자의 관심사를 기반으로 한 카드 추천 (70%)
- **랜덤 카드**: 다양성을 위한 랜덤 카드 (30%)
- **히스토리 관리**: 이전 추천 내역 조회 가능
- **재추천**: 마음에 들지 않을 경우 새로운 카드 세트 요청
- **카드 선택**: 1-4개 카드 선택 (실시간 검증)

### 4. 카드 해석
- **AI 해석**: OpenAI API를 통한 3가지 해석 생성
- **컨텍스트 고려**: 현재 상황과 사용자 페르소나를 반영한 해석
- **과거 이력 반영**: 이전 대화 메모리를 활용한 개선된 해석

### 5. Partner 피드백
- **해석 선택**: 3가지 해석 중 올바른 것 선택
- **직접 피드백**: 적절한 해석이 없을 경우 직접 입력
- **메모리 저장**: 피드백을 통한 학습 데이터 누적

## 프로젝트 구조

```
src/
├── components/           # 재사용 가능한 컴포넌트들
│   ├── auth/            # 인증 관련 컴포넌트
│   ├── cards/           # 카드 관련 컴포넌트
│   ├── context/         # 컨텍스트 입력 컴포넌트
│   └── interpretation/  # 해석 및 피드백 컴포넌트
├── pages/               # 메인 페이지 컴포넌트들
├── services/            # API 통신 서비스들
├── styles/              # CSS 스타일 파일들
├── App.js              # 메인 앱 컴포넌트
└── index.js            # 앱 진입점
```

## 설치 및 실행

### 1. 의존성 설치
```bash
npm install
```

### 2. 개발 서버 실행
```bash
npm start
```

앱이 [http://localhost:3000](http://localhost:3000)에서 실행됩니다.

### 3. 백엔드 서버 실행 필요
이 프론트엔드 앱은 Python Flask 백엔드와 연동됩니다.
백엔드 서버가 [http://localhost:8000](http://localhost:8000)에서 실행되어야 합니다.

## API 연동

### 백엔드 엔드포인트
- **인증**: `/api/auth/*`
  - POST `/api/auth/register` - 회원가입
  - POST `/api/auth/login` - 로그인
  - GET `/api/auth/profile/{userId}` - 프로필 조회
  - PUT `/api/auth/profile/{userId}` - 프로필 업데이트

- **컨텍스트**: `/api/context/*`
  - POST `/api/context` - 컨텍스트 생성
  - GET `/api/context/{contextId}` - 컨텍스트 조회

- **카드**: `/api/cards/*`
  - POST `/api/cards/recommend` - 카드 추천
  - POST `/api/cards/validate` - 카드 선택 검증
  - POST `/api/cards/interpret` - 카드 해석
  - GET `/api/cards/history/{contextId}` - 히스토리 조회

- **피드백**: `/api/feedback/*`
  - POST `/api/feedback/request` - 파트너 피드백 요청
  - POST `/api/feedback/submit` - 파트너 피드백 제출

- **이미지**: `/api/images/{filename}` - AAC 카드 이미지 서빙

## 사용 흐름

1. **계정 생성/로그인**
   - 새 사용자: 페르소나 정보와 함께 회원가입
   - 기존 사용자: 아이디/비밀번호로 로그인

2. **대화 세션 시작**
   - 대시보드에서 "대화 시작하기" 클릭
   - 현재 상황 정보 입력 (장소, 대화상대, 활동)

3. **카드 선택**
   - 개인화된 20개 카드 세트 제공
   - 1-4개 카드 선택 (최대 4개까지)
   - 필요시 재추천 요청 가능

4. **해석 및 피드백**
   - AI가 생성한 3가지 해석 확인
   - Partner가 올바른 해석 선택 또는 직접 입력
   - 시스템이 학습을 위해 피드백 저장

5. **세션 완료**
   - 최종 해석 결과 확인
   - 새로운 대화 세션 시작 가능

## 기술 스택

- **Frontend**: React 18, JavaScript ES6+
- **HTTP 클라이언트**: Fetch API
- **상태 관리**: React Hooks (useState, useEffect)
- **스타일링**: CSS3 (Flexbox, Grid)
- **빌드 도구**: Create React App

## 브라우저 지원

- Chrome (최신)
- Firefox (최신)
- Safari (최신)
- Edge (최신)

## 개발자 정보

이 프론트엔드는 백엔드 API와 완벽하게 동기화되어 설계되었으며, 
모든 API 엔드포인트와 데이터 형식이 백엔드 명세와 일치합니다.