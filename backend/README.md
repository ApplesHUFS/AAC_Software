# Backend - API 서버

AAC 카드 해석 시스템의 Flask 기반 백엔드 API 서버입니다.

## 주요 기능

### 🎯 핵심 기능
- **개인화된 카드 추천**: 사용자 페르소나 기반 클러스터링을 통한 맞춤형 카드 추천
- **AI 기반 카드 해석**: GPT-4o를 활용한 상황별 카드 의미 해석
- **실시간 피드백**: Partner 피드백을 통한 해석 정확도 개선
- **대화 메모리**: 과거 대화 패턴 학습을 통한 지속적인 개선

### 🔐 사용자 관리
- 회원가입/로그인 (비밀번호 해시 처리)
- 페르소나 정보 관리 (나이, 성별, 장애유형, 의사소통 특성, 관심 주제)
- 선호 카테고리 자동 계산 및 업데이트

### 📍 상황 인식
- 실시간 대화 상황 컨텍스트 생성
- 장소, 대화 상대, 현재 활동 정보 수집
- 시간별 상황 추적

### 🎨 카드 시스템
- 20개 카드 선택 인터페이스 제공
- 1-4개 카드 다중 선택 지원
- 히스토리 기반 카드 추천 개선

## 기술 스택

### 웹 프레임워크 & API
- **Flask 3.0+**: 경량 웹 프레임워크
- **Flask-CORS**: Cross-Origin Resource Sharing 지원
- **RESTful API**: React 프론트엔드와의 통신

### AI/ML 스택
- **OpenAI GPT-4o**: 카드 해석 및 자연어 처리
- **LangChain**: LLM 체인 관리 및 프롬프트 엔지니어링
- **Sentence Transformers**: 텍스트 임베딩 및 유사도 계산
- **NumPy**: 수치 계산 및 데이터 처리
- **PyTorch**: 머신러닝 모델 추론

### 데이터 관리
- **JSON**: 사용자 데이터, 설정, 클러스터링 결과 저장
- **파일 시스템**: 이미지 및 데이터셋 관리

## 아키텍처

### 디렉토리 구조

```
backend/
├── app.py                    # Flask 메인 애플리케이션
├── aac_interpreter_service.py # 메인 서비스 컨트롤러
├── service_config.py         # 서비스 설정 파일
├── requirements.txt          # Python 의존성 목록
├── public/                   # 공개 모듈 (API와 직접 연동)
│   ├── __init__.py
│   ├── user_manager.py       # 사용자 관리
│   ├── context_manager.py    # 상황 정보 관리
│   └── feedback_manager.py   # 피드백 관리
└── private/                  # 내부 비즈니스 로직
    ├── __init__.py
    ├── card_recommender.py   # 카드 추천 시스템
    ├── card_interpreter.py   # 카드 해석 시스템
    ├── conversation_memory.py # 대화 메모리 관리
    └── cluster_similarity_calculator.py # 클러스터 유사도 계산
```

### 컴포넌트 구조

#### 🔧 Service Layer (메인 컨트롤러)
- **AACInterpreterService**: 전체 시스템의 메인 컨트롤러로 모든 컴포넌트를 조율

#### 🌐 Public Module (API 연동)
- **UserManager**: 사용자 인증, 페르소나 관리, 선호 카테고리 계산
- **ContextManager**: 대화 상황 정보 생성 및 관리
- **FeedbackManager**: Partner 피드백 수집 및 처리

#### 🔒 Private Module (핵심 로직)
- **CardRecommender**: 페르소나/상황 기반 카드 추천 알고리즘
- **CardInterpreter**: GPT-4o 기반 카드 의미 해석
- **ConversationSummaryMemory**: 대화 패턴 학습 및 메모리 관리
- **ClusterSimilarityCalculator**: 의미적 유사도 기반 클러스터 계산

## API 엔드포인트

### 인증 관련
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

프로젝트 루트에 `.env` 파일 생성:

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

### service_config.py 주요 설정

```python
SERVICE_CONFIG = {
    # OpenAI API 설정
    'openai_model': 'gpt-4o-2024-08-06',
    'openai_temperature': 0.8,
    'interpretation_max_tokens': 400,

    # 카드 추천 시스템
    'display_cards_total': 20,
    'context_similarity_threshold': 0.25,
    'persona_similarity_threshold': 0.3,
    'context_persona_ratio': 0.5,  # 상황:페르소나 = 0.5:0.5

    # 카드 선택 및 해석
    'min_card_selection': 1,
    'max_card_selection': 4,
    'interpretation_count': 3,

    # 사용자 검증
    'valid_genders': ['남성', '여성'],
    'valid_disability_types': [
        '의사소통장애',
        '자폐스펙트럼장애',
        '지적장애'
    ],
    'min_age': 1,
    'max_age': 100,
}
```

## 개발 가이드

### 코드 구조 원칙

1. **관심사의 분리**: Public(API 연동) vs Private(비즈니스 로직)
2. **단일 책임 원칙**: 각 모듈은 하나의 명확한 역할
3. **의존성 주입**: 설정과 컴포넌트 간 느슨한 결합
4. **에러 핸들링**: 모든 메서드는 일관된 응답 형식 반환

### 응답 형식 표준

```python
{
    "success": true,
    "data": {...},
    "message": "성공 메시지",
    "timestamp": "2024-01-01T12:00:00"
}
```

### 컴포넌트 간 통신

```python
# 메인 서비스에서 컴포넌트 조율
result = self.card_recommender.get_card_selection_interface(persona, context, context_id)
if result['status'] == 'success':
    # 성공 처리
else:
    # 오류 처리
```

## 성능 최적화

### 메모리 관리
- 클러스터링 결과 메모리 캐싱
- 사용자 데이터 지연 로딩
- 대화 메모리 크기 제한 (50개 항목)

### API 최적화
- CORS 설정으로 프론트엔드 통신 최적화
- 이미지 직접 서빙으로 네트워크 효율성 개선
- 페이지네이션으로 대용량 데이터 처리

## 보안

### 인증 및 권한
- SHA256 해시 기반 비밀번호 저장
- 로그인 시도 제한 (5회)
- 계정 잠금 기능

### 데이터 보호
- 사용자 개인정보 암호화 저장
- API 응답에서 민감 정보 제외
- 파일 경로 검증

## 모니터링 및 로깅

### 에러 처리
- 전역 에러 핸들러로 예외 상황 관리
- 상세한 오류 메시지와 스택 트레이스 로깅
- 클라이언트 친화적 오류 응답

### 헬스체크
- `/health` 엔드포인트로 서비스 상태 모니터링
- 컴포넌트별 초기화 상태 확인

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

### 개발 환경 디버깅

```bash
# 디버그 모드로 실행
python app.py  # debug=True가 기본 설정

# 컴포넌트 초기화 확인
# 서버 시작 시 각 컴포넌트 로딩 상태 출력됨
```

## 라이센스

이 프로젝트는 연구 및 교육 목적으로 제작되었습니다.

## 기여 가이드

1. 새로운 기능 개발 시 기존 아키텍처 패턴 준수
2. 모든 메서드에 타입 힌트 및 독스트링 추가
3. 에러 핸들링 및 로깅 표준 준수
4. API 응답 형식 일관성 유지

---

더 자세한 정보나 기술적 문의사항은 프로젝트 메인테이너에게 연락해주세요.