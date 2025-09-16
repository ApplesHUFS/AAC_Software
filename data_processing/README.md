# AAC 카드 해석 시스템 - 데이터 처리

AAC 시스템에 사용되는 카드 데이터를 처리하는 알고리즘입니다.

## 주요 기능

### AAC 이미지 필터링
- 기준(부적절한 용어, 의료/기술 용어 등)을 통해 AAC 카드에 부적합한 이미지들을 필터

### CLIP 임베딩 생성
- 이미지-키워드를 동시에 인코딩해 멀티모달 임베딩을 생성
- dataset_config에서 설정을 전달받음

### 계층적 Spherical K-means 클러스터링 생성
- 코사인 유사도 기반의 클러스터링 수행

### 클러스터 태깅
- OpenAI Vision API를 사용
- 각 클러스터의 대표 이미지를 분석 후 태그(공통 주제) 생성


## 프로젝트 구조

```
data_processing/
├── data_prepare.py             # AAC 클러스터링 데이터 준비 파이프라인
├── dataset_config.py           # AAC 클러스터링 시스템 설정
│
└── data_source/                # 이미지 데이터 처리 컴포넌트
    ├── cluster_tagger.py       # 계층적 클러스터 태깅
    ├── clustering.py           # 고차원 임베딩용 Spherical K-means 알고리즘
    ├── embeddings.py           # CLIP 모델을 사용한 이미지-텍스트 임베딩 생성
    └── image_filter.py         # AAC 이미지 필터링 시스템

```