# Data Processing - 데이터 처리 파이프라인

AAC 카드 이미지를 자동으로 분류하고 태깅하는 AI 기반 데이터 처리 시스템입니다.

## 개요

대용량 AAC 카드 데이터셋을 다음과 같은 단계로 처리합니다:
1. **이미지 필터링**: 부적절하거나 AAC에 적합하지 않은 이미지 제거
2. **CLIP 임베딩 생성**: 이미지와 텍스트를 통합한 멀티모달 벡터 표현 생성
3. **계층적 클러스터링**: Spherical K-means를 이용한 2단계 클러스터링
4. **자동 태깅**: OpenAI Vision API를 활용한 클러스터별 주제 태그 생성

## 주요 기능

### 1. AAC 이미지 필터링 (`image_filter.py`)
- **다중 카테고리 필터링**: 부적절한 용어, 의료/기술 용어, 학술/과학 용어, 문화 특수 용어, 행정/법률 용어, 지역명, 도구/객체, 개념, 기타 등 9개 카테고리
- **정규표현식 기반 매칭**: 한글과 영어 키워드를 정확히 매칭하는 최적화된 패턴 매칭
- **중복 제거**: 동일 키워드를 가진 중복 이미지 자동 감지 및 제거
- **실시간 확인**: 필터링 전 사용자 확인 옵션

### 2. CLIP 임베딩 생성 (`embeddings.py`)
- **멀티모달 인코딩**: 이미지와 해당 키워드를 동시에 인코딩하여 의미적 일관성 확보
- **가중치 조정 가능**: 이미지와 텍스트 임베딩의 융합 비율 설정 가능 (기본값: 이미지 60%, 텍스트 40%)
- **대용량 처리 최적화**: GPU 지원 및 배치 처리로 효율적인 대용량 데이터 처리
- **모델 선택**: OpenAI CLIP 다양한 모델 지원 (기본: `clip-vit-large-patch14`)

### 3. 계층적 Spherical K-means 클러스터링 (`clustering.py`)
- **2단계 계층 구조**: 거시적 대분류 → 미시적 세분화로 체계적 분류
- **자동 클러스터 수 결정**: 실루엣 스코어 기반 최적 클러스터 수 자동 선택
- **코사인 유사도 기반**: 정규화된 임베딩에 최적화된 spherical k-means 알고리즘
- **시각화 지원**: PCA를 이용한 2D 클러스터링 결과 시각화

### 4. OpenAI Vision API 클러스터 태깅 (`cluster_tagger.py`)
- **대표 샘플 선택**: 각 클러스터에서 medoid 기반 가장 대표적인 5개 이미지 선택
- **멀티모달 분석**: 이미지와 키워드를 종합한 컨텍스트 기반 태깅
- **계층 정보 활용**: 클러스터 크기와 대분류 정보를 포함한 구조화된 프롬프트
- **일관성 보장**: 낮은 temperature(0.2) 설정으로 안정적인 태깅 결과

## 프로젝트 구조

```
data_processing/
├── data_prepare.py             # 메인 파이프라인 클래스 (DataPreparationPipeline)
├── dataset_config.py           # 시스템 설정 및 하이퍼파라미터
├── requirements.txt            # Python 의존성 패키지 목록
├── .env                        # 환경 변수 (OpenAI API 키)
│
└── data_source/                # 핵심 데이터 처리 모듈
    ├── image_filter.py         # ImageFilter: 다중 기준 이미지 필터링
    ├── embeddings.py           # CLIPEncoder: CLIP 기반 멀티모달 임베딩
    ├── clustering.py           # Clusterer + SphericalKMeans: 계층적 클러스터링
    └── cluster_tagger.py       # ClusterTagger: OpenAI Vision API 태깅
```

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

## 설정 파일 (`dataset_config.py`)

시스템의 모든 하이퍼파라미터와 설정을 중앙 관리:

### 주요 설정 항목
- **경로 설정**: 입력/출력 폴더 경로
- **CLIP 모델**: 사용할 Hugging Face CLIP 모델명
- **임베딩 가중치**: 이미지/텍스트 임베딩 융합 비율 (기본 0.6:0.4)
- **클러스터링 파라미터**: 대분류/소분류 클러스터 수, 최소 클러스터 크기
- **OpenAI 설정**: GPT 모델, temperature, 요청 간격
- **유사도 임계값**: 페르소나 매칭용 임계값

## 출력 파일

파이프라인 실행 시 다음 파일들이 생성됩니다:

```
dataset/processed/
├── embeddings.json             # CLIP 임베딩 벡터 (이미지+텍스트)
├── clustering_results.json     # 클러스터 할당 결과
├── cluster_tags.json           # 각 클러스터의 주제 태그
└── cluster_visualization.png   # 클러스터링 결과 2D 시각화
```

## 성능 및 확장성

### 최적화 기능
- **GPU 가속**: CUDA 지원으로 임베딩 생성 속도 향상
- **배치 처리**: 메모리 효율적인 대량 이미지 처리
- **병렬 처리**: 다중 코어 활용 클러스터링
- **캐싱**: 중간 결과 저장으로 재실행 시 시간 단축

### 확장성
- **모듈형 설계**: 각 단계별 독립적 실행 가능
- **설정 기반**: 코드 수정 없이 설정 파일로 동작 변경
- **API 통합**: OpenAI API 외 다른 LLM API 쉽게 교체 가능
- **다국어 지원**: 키워드 매칭 로직의 언어별 확장 가능

## 주요 의존성

- **torch**: PyTorch 딥러닝 프레임워크
- **transformers**: Hugging Face 트랜스포머 모델
- **sentence-transformers**: 문장 임베딩 모델
- **scikit-learn**: 머신러닝 유틸리티 (PCA, 실루엣 스코어)
- **openai**: OpenAI GPT API 클라이언트
- **Pillow**: 이미지 처리
- **matplotlib**: 시각화
- **tqdm**: 진행률 표시

## 기술적 특징

### 1. 멀티모달 임베딩
- 이미지와 텍스트를 동일한 벡터 공간에 매핑
- 가중 평균을 통한 모달리티별 기여도 조절
- L2 정규화로 코사인 유사도 기반 연산 최적화

### 2. 계층적 클러스터링
- 대분류 20-100개 → 소분류 최대 6개 구조
- 실루엣 스코어 기반 최적 클러스터 수 자동 결정
- 최소 클러스터 크기(20개) 보장으로 통계적 안정성 확보

### 3. 지능형 태깅
- Medoid 기반 대표 샘플 선택으로 클러스터 특성 정확히 반영
- 구조화된 JSON 스키마로 일관된 태그 형식 보장
- 계층 정보와 클러스터 크기를 고려한 컨텍스트 태깅

## 트러블슈팅

### 일반적인 문제
- **GPU 메모리 부족**: `dataset_config.py`에서 `device: 'cpu'` 설정
- **OpenAI API 한도**: `request_delay` 값을 증가시켜 요청 간격 조절
- **클러스터링 시간 오래 걸림**: `--no-visualize` 옵션 사용
- **빈 클러스터 발생**: `min_cluster_size` 값 조정

### 로그 확인
파이프라인 실행 중 각 단계별 진행 상황과 결과가 콘솔에 출력됩니다.

---

**개발자**: AAC 소프트웨어 팀
**라이선스**: MIT
**버전**: 1.0.0