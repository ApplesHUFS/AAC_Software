# AAC 카드 해석 시스템

이 시스템은 AAC(Augmentative and Alternative Communication) 카드를 사용하는 사용자들의 의사소통을 돕기 위한 지능형 해석 시스템입니다.

## 시스템 개요

사용자의 페르소나와 상황 정보를 기반으로 적절한 AAC 카드를 추천하고, 선택된 카드 조합을 해석하여 의도를 파악하는 시스템입니다.

## 주요 기능

1. **사용자 관리**: 페르소나 기반 사용자 등록 및 관리
2. **카드 추천**: 개인화된 AAC 카드 추천
3. **카드 해석**: 온라인/오프라인 환경에서의 지능형 해석
4. **피드백 학습**: 사용자 피드백을 통한 지속적 개선
5. **데이터 분석**: 사용 패턴 분석 및 통계

## 시스템 아키텍처

### 핵심 모듈

```
src/
├── user_manager.py          # 사용자 관리      -> 송민주
├── card_recommender.py      # 카드 추천 시스템 -> 김윤서
├── card_interpreter.py      # 카드 해석 엔진   -> 김윤서
├── feedback_manager.py      # 피드백 관리      -> 유연주
├── aac_interpreter_service.py # 메인 서비스    -> 
├── context_manager.py       # 상황 관리        -> 박시후
└── config_manager.py        # 설정 관리        -> 박시후
```

## 사용자 플로우

### 1. 회원 가입

```python
# 사용자 등록
service = AACInterpreterService()
result = service.register_user({
    'age': 'adolescent',
    'gender': 'male', 
    'disability_type': '지적장애',
    'communication_characteristics': '단순한 단어나 짧은 구문을 선호',
    'selection_complexity': 'simple',
    'interesting_topics': ['음식', '놀이', '가족'],
    'password': 'secure_password'
})

# Return:
{
    'status': 'success',
    'user_id': 1,
    'message': '사용자가 성공적으로 등록되었습니다.'
}
```

### 2. 사용자 인증

```python
# 로그인
auth_result = service.authenticate_user(user_id=1, password='secure_password')

# Return:
{
    'status': 'success',
    'authenticated': True,
    'user_info': {...},
    'message': '인증 성공'
}
```

### 3. 카드 추천

```python
# 카드 추천 요청
cards_result = service.recommend_cards(user_id=1, num_cards=3)

# Return:
{
    'status': 'success',
    'recommended_cards': ['2462_사과.png', '2392_가족.png', '2439_놀다.png'],
    'clusters_used': [15, 23, 8],
    'message': '카드 추천 완료'
}
```

### 4. 카드 해석

```python
# 선택된 카드 해석
interpretation_result = service.interpret_cards(
    user_id=1,
    selected_cards=['2462_사과.png', '2392_가족.png'],
    context={
        'time': '점심시간',
        'place': '집',
        'interaction_partner': '엄마',
        'current_activity': '식사 준비'
    }
)

# Return:
{
    'status': 'success',
    'interpretations': [
        '가족과 함께 사과를 먹고 싶어요',
        '엄마와 사과를 나누어 먹고 싶어요', 
        '점심 후 디저트로 사과를 먹고 싶어요'
    ],
    'feedback_id': 123,
    'method': 'online',
    'message': '해석 완료'
}
```

### 5. 피드백 제출

```python
# 올바른 해석 선택 (첫 번째 해석이 맞음)
feedback_result = service.submit_feedback(
    feedback_id=123,
    selected_interpretation_index=0
)

# 또는 직접 수정
feedback_result = service.submit_feedback(
    feedback_id=123,
    user_correction='가족과 함께 사과를 먹고 싶다는 뜻이에요'
)

# Return:
{
    'status': 'success',
    'message': '피드백이 성공적으로 기록되었습니다.'
}
```

## API 상세 명세

### UserManager

#### create_user(persona)
```python
Args:
    persona: {
        'age': str,
        'gender': str,
        'disability_type': str,
        'communication_characteristics': str,
        'selection_complexity': str,  # 'simple', 'moderate', 'complex'
        'interesting_topics': List[str],
        'password': str
    }

Returns:
    {
        'status': str,
        'user_id': int,
        'message': str
    }
```

#### authenticate_user(user_id, password)
```python
Args:
    user_id: int
    password: str

Returns:
    {
        'status': str,
        'authenticated': bool,
        'message': str
    }
```

### CardRecommender

#### recommend_cards(persona, num_cards)
```python
Args:
    persona: Dict[str, Any]
    num_cards: int (1-4)

Returns:
    {
        'status': str,
        'cards': List[str],
        'clusters_used': List[int],
        'message': str
    }
```

### CardInterpreter

#### interpret_cards(persona, context, cards, past_interpretation)
```python
Args:
    persona: Dict[str, Any]
    context: {
        'time': str,
        'place': str,
        'interaction_partner': str,
        'current_activity': str
    }
    cards: List[str] (1-4개)
    past_interpretation: str

Returns:
    {
        'status': str,
        'interpretations': List[str],  # 항상 3개
        'method': str,  # 'online' or 'offline'
        'timestamp': str,
        'message': str
    }
```

### FeedbackManager

#### record_interpretation_attempt(user_id, cards, persona, context, interpretations, method)
```python
Args:
    user_id: int
    cards: List[str]
    persona: Dict[str, Any]
    context: Dict[str, Any]
    interpretations: List[str] (3개)
    method: str

Returns:
    {
        'status': str,
        'feedback_id': int,
        'message': str
    }
```

#### record_user_feedback(feedback_id, selected_interpretation_index, user_correction)
```python
Args:
    feedback_id: int
    selected_interpretation_index: Optional[int] (0-2)
    user_correction: Optional[str]

Returns:
    {
        'status': str,
        'message': str
    }
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
export OPENAI_API_KEY="your_openai_api_key"
```

### 기본 실행
```python
from src.aac_interpreter_service import AACInterpreterService

# 서비스 초기화
service = AACInterpreterService()

# 사용자 등록
user_result = service.register_user(persona_data)

# 카드 추천 및 해석
cards_result = service.recommend_cards(user_id=1)
interpretation_result = service.interpret_cards(user_id=1, selected_cards=cards, context=context_data)
```

## 데이터 전처리 (기존 시스템)

### 실행
```bash
# 전체 파이프라인 실행 (1-8단계)
python data_prepare.py

# 확인 과정 없이 실행
python data_prepare.py --no-confirm

# 기존 데이터 덮어쓰기
python data_prepare.py --overwrite
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