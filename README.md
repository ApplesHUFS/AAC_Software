# AAC 카드 해석 시스템

AAC(보완대체의사소통) 카드를 이용한 AI 해석 시스템입니다. 현재는 데이터셋 준비 단계를 구현했습니다.

## 설치

1. 패키지 설치:
```bash
pip install torch transformers sklearn matplotlib tqdm openai python-dotenv pillow huggingface-hub
```

2. `.env` 파일 생성:
```
HUGGINGFACE_TOKEN=your_token_here
OPENAI_API_KEY=your_openai_key_here
```

3. 데이터 구조 준비:
```
data/
├── images/              # AAC 카드 이미지 (PNG 형식)
├── persona.json        # 페르소나 정의
└── processed/          # 출력 디렉토리 (자동 생성)
```

## 사용법

### 전체 파이프라인 실행
```bash
python data_prepare.py
```

### 특정 단계만 실행
```bash
# 1-3단계만 실행 (이미지 처리 + 임베딩 + 클러스터링)
python data_prepare.py --steps 1 2 3

# 4-5단계만 실행 (스키마 생성 + 카드 조합)
python data_prepare.py --steps 4 5

# 6단계만 실행 (OpenAI 처리, 처음 10개 샘플만)
python data_prepare.py --steps 6 --openai-start 0 --openai-end 10
```

### 추가 옵션
```bash
# 도움말 보기
python data_prepare.py --help

# 확인 과정 건너뛰기
python data_prepare.py --no-confirm

# 시각화 건너뛰기
python data_prepare.py --no-visualize

# OpenAI 처리 범위 지정
python data_prepare.py --steps 6 --openai-start 100 --openai-end 200
```

### 설정 변경
`config/dataset_config.py`에서 설정 수정:
```python
DATASET_CONFIG = {
    'images_folder': 'data/images',
    'samples_per_persona': 200,    # 페르소나당 샘플 수
    'n_clusters': 96,              # 클러스터 수
    'skip_openai': False           # True로 설정하면 AI 처리 건너뛰기
}
```

## 처리 과정

1. **이미지 필터링** (`--steps 1`): 부적절한 이미지 제거
2. **CLIP 인코딩** (`--steps 2`): 이미지-텍스트 임베딩 생성
3. **클러스터링** (`--steps 3`): 유사한 카드 그룹화
4. **스키마 생성** (`--steps 4`): 데이터셋 구조 생성
5. **카드 조합** (`--steps 5`): 의미있는 카드 시퀀스 생성
6. **AI 완성** (`--steps 6`): OpenAI로 상황과 해석 생성

## 이미지 요구사항

이미지 파일명 형식: `{번호}_{키워드}.png`
- 예시: `001_사과.png`, `002_행복.png`
- 키워드는 텍스트 임베딩 생성에 사용됩니다

## 출력 파일

- `embeddings.json`: CLIP 임베딩 데이터
- `clustering_results.json`: 클러스터링 결과
- `dataset_completed.json`: 최종 완성된 데이터셋
- `cluster_visualization.png`: 클러스터 시각화

## 향후 계획

- **Phase 2**: 모델 훈련 파이프라인
- **Phase 3**: 실시간 카드 해석 시스템

## 프로젝트 구조

```
project/
├── config/               # 설정 파일
├── data_src/            # 핵심 모듈
├── data_prepare.py      # 데이터 준비 파이프라인
└── README.md
```