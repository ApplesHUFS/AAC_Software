# pre-commit run

# AAC 카드 해석 시스템

이 시스템은 AAC(Augmentative and Alternative Communication) 카드를 사용하는 사용자들의 의사소통을 돕기 위한 지능형 해석 시스템입니다.

## 시스템 흐름

### 1. 사용자 생성
사용자의 페르소나 정보를 입력하여 계정을 생성합니다.

**페르소나 구성요소:**
- `age`: 나이 (정수)
- `gender`: 성별 (male/female 선택지)
- `disability_type`: 장애 유형 (지적장애/자폐스펙트럼장애/의사소통장애 선택지)
- `communication_characteristics`: 의사소통 특징 (직접 입력)
- `interesting_topics`: 관심 주제 목록 (직접 입력)

### 2. 대화 상황 발생 (반복 가능)

#### 2.1 컨텍스트 입력
Partner가 대화 상황 정보를 입력합니다:
- `time`: 시간 (시스템에서 자동 획득)
- `place`: 장소 (직접 입력)
- `interaction_partner`: 상호작용 상대 (직접 입력, 관계 명시)
- `current_activity`: 현재 활동 (선택사항, 직접 입력)

#### 2.2 페르소나 기반 카드 추천
사용자의 `interesting_topics`를 기반으로 관련 AAC 카드를 우선 추천합니다.
- 클러스터링 데이터 활용 (`data/cluster_tagger.py`, `data/clustering.py`)
- 개인화된 카드 추천 시스템 (`src/card_recommender.py`)

#### 2.3 카드 선택
사용자가 추천된 카드들과 랜덤 카드들 중에서 1-4개를 선택합니다.

#### 2.4 카드 해석
선택된 카드 조합을 컨텍스트, 페르소나, 대화 메모리 기반으로 해석합니다.
- OpenAI API 활용 (온/오프라인 분기 없음)
- 해석 엔진: `src/card_interpreter.py`

#### 2.5 Partner 피드백 수집
Partner에게 Top-3 해석 중 올바른 해석을 확인 요청합니다.
- 3개 해석 중 선택, 또는 직접 피드백 입력
- 통합 피드백 관리: `src/feedback_manager.py`

#### 2.6 대화 메모리 저장
LangChain의 ConversationSummaryMemory를 사용하여 해석 결과를 요약 저장합니다.
- 이미지(카드) + 컨텍스트 + 최종 해석의 연관성 학습
- 메모리 관리: `src/conversation_memory.py`

## 학습 데이터 스키마

```json
{
  "id": int,
  "input": {
    "persona": {
      "age": int,
      "gender": ["male", "female"],
      "disability_type": ["의사소통 장애", "자폐스펙트럼 장애", "지적 장애"],
      "communication_characteristics": "string",
      "selection_complexity": ["simple", "moderate", "complex"],
      "interesting_topics": ["string"],
      "preferred_category_types": [cluster_id_array]
    },
    "context": {
      "time": "string",
      "place": "string",
      "interaction_partner": "string",
      "current_activity": "string"
    },
    "past_interpretation": "string",
    "AAC_card_combination": ["string"]
  },
  "output": ["string", "string", "string"]
}
```

## 시스템 아키텍처

### 핵심 모듈

```
src/
├── user_manager.py          # 사용자 페르소나 관리
├── card_recommender.py      # 개인화 카드 추천 시스템
├── card_interpreter.py      # 카드 해석 엔진
├── feedback_manager.py      # 통합 피드백 관리 (Partner + 사용자)
├── aac_interpreter_service.py # 메인 서비스 컨트롤러
├── context_manager.py       # 상황 정보 관리
├── conversation_memory.py   # 대화 메모리 관리
└── config_manager.py        # 설정 관리
```

### 데이터 처리 모듈

```
data/
├── cluster_tagger.py        # 클러스터 태깅
├── clustering.py           # K-means 클러스터링
├── dataset_generator.py    # 학습 데이터 생성
├── embeddings.py          # CLIP 임베딩 생성
├── image_filter.py        # 이미지 필터링
├── persona_card_selector.py # 페르소나 기반 카드 선택
└── schema.py              # 데이터 스키마 정의
```

## 데이터 구조

### 사용자 페르소나
```json
{
    "id": 1,
    "persona": {
        "age": "adolescent",
        "gender": "male",
        "disability_type": "지적장애",
        "communication_characteristics": "단순한 단어나 짧은 구문을 선호",
        "selection_complexity": "simple",
        "preferred_category_types": [15, 23, 8],
        "interesting_topics": ["음식", "놀이", "가족"]
    },
    "created_at": "2025-01-16T10:30:00",
    "interpretation_history": []
}
```

### 해석 피드백
```json
{
    "feedback_id": 123,
    "user_id": 1,
    "timestamp": "2025-01-16T14:20:00",
    "cards": ["2462_사과.png", "2392_가족.png"],
    "interpretations": ["해석1", "해석2", "해석3"],
    "user_selection": 0,
    "user_correction": null,
    "feedback_status": "completed"
}
```

## 설치 및 실행

### 요구사항
```bash
pip install -r requirements.txt
export OPENAI_API_KEY="your_openai_api_key"  # 또는 .env 파일에 설정
```

### 기본 사용법

```python
from src.aac_interpreter_service import AACInterpreterService

# 1. 서비스 초기화
service = AACInterpreterService()

# 2. 사용자 등록
persona_data = {
    "age": 12,
    "gender": "male",
    "disability_type": "지적장애",
    "communication_characteristics": "단순한 단어나 짧은 구문을 선호",
    "interesting_topics": ["음식", "놀이", "가족"],
    "password": "user123"
}
user_result = service.register_user(persona_data)
user_id = user_result['user_id']

# 3. 컨텍스트 설정
context_data = {
    "place": "학교 급식실",
    "interaction_partner": "급식 선생님",
    "current_activity": "점심시간"
}
service.update_user_context(user_id, **context_data)

# 4. 카드 추천 받기
cards_result = service.recommend_cards(user_id=user_id)
recommended_cards = cards_result['recommended_cards']

# 5. 카드 선택 및 해석
selected_cards = ["2462_사과.png", "2392_좋아요.png"]
interpretation_result = service.interpret_cards(
    user_id=user_id,
    selected_cards=selected_cards,
    context=context_data
)
interpretations = interpretation_result['interpretations']  # Top-3 해석

# 6. Partner 피드백 요청
partner_info = {"name": "김선생님", "relationship": "급식 선생님"}
confirmation_result = service.request_partner_confirmation(
    user_id=user_id,
    cards=selected_cards,
    context=context_data,
    interpretations=interpretations,
    partner_info=partner_info
)
confirmation_id = confirmation_result['confirmation_id']

# 7. Partner 피드백 제출
feedback_result = service.submit_partner_feedback(
    confirmation_id=confirmation_id,
    selected_interpretation_index=1  # 두 번째 해석 선택
)

# 8. 대화 메모리에 저장
final_interpretation = feedback_result['feedback_result']['selected_interpretation']
service.save_to_conversation_memory(
    user_id=user_id,
    cards=selected_cards,
    context=context_data,
    interpretation=final_interpretation
)
```

## 데이터 전처리 (학습 데이터 생성)

### 전체 파이프라인 실행
```bash
# 전체 데이터 처리 파이프라인 (1-8단계)
python data_prepare.py

# 확인 과정 없이 자동 실행
python data_prepare.py --no-confirm

# 기존 데이터 덮어쓰기
python data_prepare.py --overwrite
```

### 개별 단계 실행
```python
from data_prepare import DataPreparationPipeline
from config.dataset_config import DATASET_CONFIG

pipeline = DataPreparationPipeline(DATASET_CONFIG)

# 1. 부적절한 이미지 필터링
pipeline.step1_filter_images()

# 2. CLIP 임베딩 생성
pipeline.step2_generate_embeddings()

# 3. K-means 클러스터링
pipeline.step3_perform_clustering()

# 4. 데이터셋 스키마 생성
pipeline.step4_generate_dataset_schema()

# 5. 클러스터 태깅
pipeline.step5_tag_clusters()

# 6. 페르소나 기반 카드 선택
pipeline.step6_persona_card_selection()

# 7. 학습 데이터셋 생성
pipeline.step7_generate_dataset()

# 8. 최종 검증
pipeline.step8_validate_dataset()
```
```

### 단계별 실행
```bash
# 전처리만 (OpenAI 없이)
python data_prepare.py --steps 1 2 3 4 5 6 7

# 이미지 필터링부터 클러스터링까지
python data_prepare.py --steps 1 2 3

# 페르소나 관련 작업만
python data_prepare.py --steps 5 6 7

# 최종 데이터셋 생성만
python data_prepare.py --steps 8
```

### OpenAI 처리 범위 지정
```bash
# 100개 샘플만 처리
python data_prepare.py --steps 8 --openai-end 100

# 500번부터 1000번까지 처리
python data_prepare.py --steps 8 --openai-start 500 --openai-end 1000
```

### 전처리 단계

1. 이미지 필터링
2. 임베딩 생성
3. 클러스터링
4. 데이터셋 스키마
5. 클러스터 태깅
6. 페르소나 카테고리 할당
7. 카드 조합 생성
8. 최종 데이터셋 생성

## 구현 상태

현재 모든 모듈은 **추상화된 인터페이스**로 구현되어 있으며, 실제 로직은 향후 구현 예정입니다.

- ✅ 모듈 구조 설계 완료
- ✅ API 인터페이스 정의 완료
- ⏳ 실제 구현 (예정)
- ⏳ 테스트 코드 작성 (예정)
- ⏳ 프론트엔드 연동 (예정)



 전체 시스템 구동 방법

  1. 백엔드 서버 구동

  # AAC_Software 루트 디렉토리로 이동
  cd /home/ellt/Workspace/AAC_Software

  # 가상환경 활성화
  source env/bin/activate

  # Flask 서버 실행
  python app.py

  서버 주소: http://localhost:8000

  2. 프론트엔드 서버 구동

  # 새로운 터미널에서
  cd /home/ellt/Workspace/AAC_Software/frontend

  # React 개발 서버 실행
  npm start

  서버 주소: http://localhost:3000

  3. 구동 순서

  1. 백엔드 먼저 (포트 8000)
  2. 프론트엔드 나중 (포트 3000)
