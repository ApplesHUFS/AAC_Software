# Backend - API 서버

AAC 카드 해석 시스템의 Flask 기반 백엔드 API 서버입니다.

## 주요 기능

- **개인화된 카드 추천**: 소통이 프로필 기반 클러스터링을 통한 맞춤형 카드 추천
- **AI 기반 카드 해석**: GPT-4o를 활용한 상황별 카드 의미 해석
- **실시간 피드백**: 도움이 피드백을 통한 해석 정확도 개선
- **대화 메모리**: 과거 대화 패턴 학습을 통한 지속적인 개선
- **사용자 관리**: 회원가입/로그인, 소통이 프로필 관리
- **상황 인식**: 실시간 대화 상황 컨텍스트 생성 및 추적

## 기술 스택

- **Flask 3.0+**: 웹 프레임워크
- **OpenAI GPT-4o**: 카드 해석 및 자연어 처리
- **LangChain**: LLM 체인 관리
- **Sentence Transformers**: 텍스트 임베딩 및 유사도 계산
- **JSON**: 사용자 데이터 및 설정 저장

## 아키텍처

### 디렉토리 구조

```
backend/
├── app.py                    # Flask 메인 애플리케이션
├── aac_interpreter_service.py # 메인 서비스 컨트롤러
├── service_config.py         # 서비스 설정 파일
├── requirements.txt          # Python 의존성 목록
├── public/                   # 공개 모듈 (API와 직접 연동)
│   ├── user_manager.py       # 사용자 관리
│   ├── context_manager.py    # 상황 정보 관리
│   └── feedback_manager.py   # 피드백 관리
└── private/                  # 내부 비즈니스 로직
    ├── card_recommender.py   # 카드 추천 시스템
    ├── card_interpreter.py   # 카드 해석 시스템
    ├── conversation_memory.py # 대화 메모리 관리
    └── cluster_similarity_calculator.py # 클러스터 유사도 계산
```

### 주요 컴포넌트

- **AACInterpreterService**: 메인 서비스 컨트롤러
- **UserManager**: 사용자 인증 및 소통이 프로필 관리
- **ContextManager**: 대화 상황 정보 생성 및 관리
- **CardRecommender**: 소통이 프로필/상황 기반 카드 추천
- **CardInterpreter**: GPT-4o 기반 카드 의미 해석

## API 엔드포인트

### 인증
- `POST /api/auth/register` - 회원가입
- `POST /api/auth/login` - 로그인
- `GET /api/auth/profile/{userId}` - 프로필 조회
- `PUT /api/auth/profile/{userId}` - 프로필 업데이트

### 상황 관리
- `POST /api/context` - 대화 상황 생성
- `GET /api/context/{contextId}` - 상황 정보 조회

### 카드 시스템
- `POST /api/cards/recommend` - 카드 추천
- `POST /api/cards/validate` - 카드 선택 검증
- `POST /api/cards/interpret` - 카드 해석
- `GET /api/cards/history/{contextId}` - 추천 히스토리
- `GET /api/cards/history/{contextId}/page/{pageNumber}` - 히스토리 페이지

### 피드백
- `POST /api/feedback/request` - 피드백 요청
- `POST /api/feedback/submit` - 피드백 제출

### 기타
- `GET /health` - 헬스체크
- `GET /api/images/{filename}` - 이미지 서빙

## 설치 및 실행

### 1. 의존성 설치

```bash
pip install -r requirements.txt
```

### 2. 환경 설정

백엔드 디렉토리에 `.env` 파일 생성:

```bash
OPENAI_API_KEY=your_openai_api_key_here
```

### 3. 데이터셋 준비

- `dataset/` 디렉토리에 AAC 카드 이미지 배치
- `dataset/processed/` 디렉토리에 클러스터링 결과 파일 배치
  - `cluster_tags.json`: 클러스터별 태그 정보
  - `embeddings.json`: 카드 임베딩 벡터
  - `clustering_results.json`: 클러스터링 결과

### 4. 서버 실행

```bash
python app.py
```

서버는 `http://localhost:8000`에서 실행됩니다.

## 설정

### 주요 설정 (service_config.py)

- **OpenAI API**: GPT-4o 모델, temperature 0.8, 최대 토큰 400
- **카드 추천**: 20개 카드 표시, 상황:소통이 프로필 = 0.5:0.5 비율
- **카드 선택**: 최소 1개, 최대 4개
- **사용자 검증**: 나이 1-100세, 3개 장애유형 지원

## 문제 해결

### 일반적인 문제

1. **OpenAI API 키 오류**
   ```bash
   # .env 파일에 올바른 API 키 설정 확인
   OPENAI_API_KEY=sk-...
   ```

2. **데이터셋 파일 누락**
   ```bash
   # 필수 파일들이 올바른 경로에 있는지 확인
   dataset/processed/clustering_results.json
   dataset/processed/cluster_tags.json
   ```

3. **CORS 오류**
   ```python
   # app.py에서 CORS 설정 확인
   CORS(app, origins=["http://localhost:3000"])
   ```

### 디버깅

```bash
# 디버그 모드로 실행
python app.py  # debug=True가 기본 설정

# 컴포넌트 초기화 확인
# 서버 시작 시 각 컴포넌트 로딩 상태 출력됨
```