# AAC Interpreter Service Backend

개인화된 AAC(보완대체의사소통) 카드 해석 시스템의 백엔드 서비스입니다.

## 프로젝트 개요

AAC 사용자의 페르소나와 상황 정보를 기반으로 개인화된 카드 추천 및 해석을 제공하는 REST API 서버입니다. OpenAI GPT-4o Vision API를 활용하여 카드 이미지를 분석하고, 사용자별 맞춤형 해석을 생성합니다.

## 주요 기능

- **사용자 관리**: 페르소나 기반 사용자 등록 및 인증
- **개인화 카드 추천**: 클러스터링 기반 상황별/페르소나별 카드 추천
- **AI 카드 해석**: OpenAI Vision API를 통한 다중 해석 생성
- **피드백 시스템**: Partner 확인을 통한 해석 정확도 개선
- **대화 메모리**: LangChain을 활용한 과거 해석 패턴 학습

## 시스템 아키텍처

```
backend/
├── aac_interpreter_service.py    # 메인 서비스 컨트롤러
├── app.py                       # Flask API 서버
├── service_config.py            # 서비스 설정
├── public/                      # 외부 API 모듈
│   ├── user_manager.py          # 사용자 관리
│   ├── context_manager.py       # 상황 정보 관리
│   └── feedback_manager.py      # 피드백 관리
└── private/                     # 내부 비즈니스 로직
    ├── card_recommender.py      # 카드 추천 시스템
    ├── card_interpreter.py      # AI 카드 해석
    ├── conversation_memory.py   # 대화 메모리 관리
    ├── cluster_similarity_calculator.py # 클러스터 유사도 계산
    └── llm/
        └── llm_factory.py       # OpenAI API 통합
```

## 핵심 컴포넌트

### 1. AACInterpreterService (메인 컨트롤러)
- 모든 서브 컴포넌트를 통합하는 중앙 제어기
- 사용자 등록/인증, 카드 추천/해석, 피드백 처리 워크플로우 관리

### 2. Public 모듈 (외부 인터페이스)
- **UserManager**: 사용자 페르소나 관리 및 인증
- **ContextManager**: 대화 상황 정보 생성 및 관리
- **FeedbackManager**: Partner 피드백 워크플로우 처리

### 3. Private 모듈 (내부 로직)
- **CardRecommender**: 클러스터 기반 개인화 카드 추천
- **CardInterpreter**: OpenAI Vision API 기반 카드 해석
- **ConversationSummaryMemory**: LangChain 기반 대화 패턴 학습
- **ClusterSimilarityCalculator**: 의미적 유사도 계산
- **LLMFactory**: OpenAI API 통합 관리

## 설치 및 실행

### 1. 환경 설정

```bash
# Python 가상환경 생성
python -m venv env
source env/bin/activate  # Linux/Mac
# 또는 env\Scripts\activate  # Windows

# 의존성 설치
pip install -r requirements.txt
```

### 2. 환경 변수 설정

`.env` 파일을 생성하고 OpenAI API 키를 설정하세요:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

### 3. 서버 실행

```bash
python app.py
```

서버가 `http://localhost:8000`에서 실행됩니다.

## API 엔드포인트

### 인증 관리
- `POST /api/auth/register` - 사용자 등록
- `POST /api/auth/login` - 로그인
- `GET /api/auth/profile/{userId}` - 프로필 조회
- `PUT /api/auth/profile/{userId}` - 프로필 수정

### 상황 관리
- `POST /api/context` - 대화 상황 생성
- `GET /api/context/{contextId}` - 상황 정보 조회

### 카드 관리
- `POST /api/cards/recommend` - 카드 추천
- `POST /api/cards/validate` - 카드 선택 검증
- `POST /api/cards/interpret` - 카드 해석
- `GET /api/cards/history/{contextId}` - 추천 히스토리
- `GET /api/images/{filename}` - 카드 이미지 제공

### 피드백 관리
- `POST /api/feedback/request` - Partner 확인 요청
- `POST /api/feedback/submit` - 피드백 제출

### 기타
- `GET /health` - 헬스체크
- `GET /` - API 정보

## 주요 설정

`service_config.py`에서 다음 설정들을 조정할 수 있습니다:

```python
SERVICE_CONFIG = {
    # OpenAI 설정
    'openai_model': 'gpt-4o-2024-08-06',
    'openai_temperature': 0.8,
    
    # 카드 추천 설정
    'display_cards_total': 20,
    'context_persona_ratio': 0.5,
    
    # 해석 설정
    'min_card_selection': 1,
    'max_card_selection': 4,
    'interpretation_count': 3,
    
    # 파일 경로
    'images_folder': 'dataset/images',
    'users_file_path': 'user_data/users.json',
    # ... 기타 설정
}
```

## 데이터 모델

### 사용자 페르소나
```python
{
    "name": "사용자 이름",
    "age": 나이,
    "gender": "남성/여성", 
    "disability_type": "의사소통장애/자폐스펙트럼장애/지적장애",
    "communication_characteristics": "의사소통 특징",
    "interesting_topics": ["관심사1", "관심사2"],
    "preferred_category_types": [0, 1, 2, 3, 4, 5]
}
```

### 대화 상황
```python
{
    "time": "14시 30분",
    "place": "집",
    "interaction_partner": "엄마",
    "current_activity": "점심 먹기"
}
```

## 기술 스택

- **프레임워크**: Flask 3.0.0
- **AI/ML**: OpenAI GPT-4o Vision API, LangChain, sentence-transformers
- **데이터 처리**: NumPy, scikit-learn
- **기타**: python-dotenv, flask-cors

## 개발 가이드

### 새로운 컴포넌트 추가

1. **Public 모듈**: 외부 API나 사용자 인터페이스 관련 기능
2. **Private 모듈**: 내부 비즈니스 로직이나 AI/ML 처리

### 에러 처리

모든 API 응답은 다음 형식을 따릅니다:

```python
{
    "success": True/False,
    "timestamp": "2024-01-01T00:00:00",
    "data": {...},  # 성공시
    "error": "...",  # 실패시
    "message": "..."
}
```

### 로깅

시스템 오류는 콘솔에 출력되며, 개발 환경에서는 Flask의 debug 모드가 활성화됩니다.

## 라이선스

이 프로젝트는 MIT 라이선스를 따릅니다.