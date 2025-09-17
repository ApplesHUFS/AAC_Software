# Data Processing - 데이터 처리 파이프라인

AAC 카드 이미지를 자동으로 분류하고 태깅하는 AI 기반 데이터 처리 시스템입니다.

## 주요 기능

- **이미지 필터링**: 부적절하거나 AAC에 적합하지 않은 이미지 제거
- **CLIP 임베딩 생성**: 이미지와 텍스트를 통합한 멀티모달 벡터 표현 생성
- **계층적 클러스터링**: Spherical K-means를 이용한 2단계 클러스터링
- **자동 태깅**: OpenAI Vision API를 활용한 클러스터별 주제 태그 생성
- **배치 처리**: 대용량 이미지 데이터의 효율적인 일괄 처리
- **설정 기반**: 코드 수정 없이 설정 파일로 동작 변경 가능

## 기술 스택

- **PyTorch**: 딥러닝 프레임워크
- **Transformers**: Hugging Face 트랜스포머 모델
- **Sentence Transformers**: 문장 임베딩 모델
- **OpenAI API**: Vision API 및 GPT 모델
- **scikit-learn**: 머신러닝 유틸리티 (PCA, 실루엣 스코어)
- **Pillow**: 이미지 처리

## 아키텍처

### 디렉토리 구조

```
data_processing/
├── data_prepare.py             # 메인 파이프라인 클래스
├── dataset_config.py           # 시스템 설정 및 하이퍼파라미터
├── requirements.txt            # Python 의존성 패키지 목록
├── .env                        # 환경 변수 (OpenAI API 키)
└── data_source/                # 핵심 데이터 처리 모듈
    ├── image_filter.py         # ImageFilter: 다중 기준 이미지 필터링
    ├── embeddings.py           # CLIPEncoder: CLIP 기반 멀티모달 임베딩
    ├── clustering.py           # Clusterer: 계층적 클러스터링
    └── cluster_tagger.py       # ClusterTagger: OpenAI Vision API 태깅
```

### 처리 단계

1. **이미지 필터링**: 9개 카테고리 기준으로 부적절한 이미지 제거
2. **임베딩 생성**: 이미지 60% + 텍스트 40% 가중치로 CLIP 임베딩 생성
3. **클러스터링**: 거시적 대분류 → 미시적 세분화로 2단계 클러스터링
4. **태깅**: 각 클러스터에서 대표 이미지 5개 선택하여 OpenAI Vision API로 태깅

## 설치 및 실행

### 1. 환경 설정

```bash
# Python 가상환경 생성 및 활성화
python -m venv env
source env/bin/activate  # Linux/Mac
# 또는 env\Scripts\activate  # Windows

# 의존성 설치
pip install -r requirements.txt
```

### 2. 환경 변수 설정

`.env` 파일을 생성하고 OpenAI API 키를 설정:

```bash
echo "OPENAI_API_KEY=your_openai_api_key_here" > .env
```

### 3. 데이터 처리 파이프라인 실행

#### 전체 파이프라인 실행
```bash
python data_prepare.py
```

#### 특정 단계만 실행
```bash
# 1단계: 이미지 필터링만
python data_prepare.py --steps 1

# 2-3단계: 임베딩 생성 + 클러스터링
python data_prepare.py --steps 2 3

# 확인 없이 자동 실행
python data_prepare.py --no-confirm

# 시각화 없이 실행 (빠른 처리)
python data_prepare.py --no-visualize

# 기존 파일 덮어쓰기 허용
python data_prepare.py --overwrite
```

## 설정

### 주요 설정 항목 (dataset_config.py)

- **경로 설정**: 입력/출력 폴더 경로
- **CLIP 모델**: 사용할 Hugging Face CLIP 모델명 (기본: clip-vit-large-patch14)
- **임베딩 가중치**: 이미지/텍스트 임베딩 융합 비율 (기본 0.6:0.4)
- **클러스터링 파라미터**: 대분류/소분류 클러스터 수, 최소 클러스터 크기
- **OpenAI 설정**: GPT 모델, temperature, 요청 간격

### 출력 파일

파이프라인 실행 시 다음 파일들이 생성됩니다:

```
dataset/processed/
├── embeddings.json             # CLIP 임베딩 벡터 (이미지+텍스트)
├── clustering_results.json     # 클러스터 할당 결과
├── cluster_tags.json           # 각 클러스터의 주제 태그
└── cluster_visualization.png   # 클러스터링 결과 2D 시각화
```

## 문제 해결

### 일반적인 문제

1. **GPU 메모리 부족**: `dataset_config.py`에서 `device: 'cpu'` 설정
2. **OpenAI API 한도**: `request_delay` 값을 증가시켜 요청 간격 조절
3. **클러스터링 시간 오래 걸림**: `--no-visualize` 옵션 사용
4. **빈 클러스터 발생**: `min_cluster_size` 값 조정

### 성능 최적화

- **GPU 가속**: CUDA 지원으로 임베딩 생성 속도 향상
- **배치 처리**: 메모리 효율적인 대량 이미지 처리
- **병렬 처리**: 다중 코어 활용 클러스터링
- **캐싱**: 중간 결과 저장으로 재실행 시 시간 단축

### 로그 확인

파이프라인 실행 중 각 단계별 진행 상황과 결과가 콘솔에 출력됩니다.