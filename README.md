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
├── persona.json        # 페르소나 정의 (수동 준비)
└── processed/          # 출력 디렉토리 (자동 생성)
```

## 사용법

### 데이터셋 준비 실행
```bash
python data_prepare.py
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

### 특정 단계만 실행
`data_prepare.py`의 `main()` 함수 수정:
```python
# 1-3단계만 실행 (AI 처리 제외)
pipeline.run_partial_pipeline(
    steps=[1, 2, 3],
    confirm_filter=True,
    visualize=True
)
```

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