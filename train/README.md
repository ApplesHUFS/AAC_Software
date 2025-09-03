# AAC 멀티모달 모델 훈련

OpenAI API를 대체할 1-3B 규모의 멀티모달 모델을 훈련하는 코드입니다.

## 🎯 목표

- **OpenAI GPT-4 Vision 대체**: 로컬에서 실행 가능한 경량 모델
- **AAC 특화**: Augmentative and Alternative Communication 카드 해석에 특화
- **페르소나 기반 개인화**: 사용자 특성을 고려한 개인화된 해석 생성
- **효율적인 학습**: LoRA를 활용한 메모리 효율적인 파인튜닝

## 🏗️ 아키텍처

- **기반 모델**: Microsoft Phi-3.5-Vision (3.8B parameters)
- **멀티모달**: 이미지 + 텍스트 입력 → 자연어 해석 출력
- **특화 기능**:
  - 페르소나 임베딩 레이어
  - 컨텍스트 어텐션 메커니즘
  - 클러스터 정보 활용
  - 해석 스타일 분류

## 📁 프로젝트 구조

```
train/
├── config/
│   └── train_config.py     # 학습 설정
├── models/
│   └── aac_multimodal_model.py  # 멀티모달 모델 정의
├── data/
│   └── dataset.py          # 데이터셋 및 데이터로더
├── utils/
│   └── metrics.py          # 평가 메트릭
├── checkpoints/            # 모델 체크포인트 저장
├── logs/                   # 학습 로그
├── train.py               # 메인 학습 스크립트
├── requirements.txt       # 패키지 의존성
└── README.md             # 이 파일
```

## 🚀 빠른 시작

### 1. 환경 설정

```bash
# 필수 패키지 설치
pip install -r train/requirements.txt

# CUDA 버전 확인 (GPU 사용시)
python -c "import torch; print(torch.cuda.is_available())"
```

### 2. 데이터 준비

먼저 기존 데이터 준비 파이프라인을 실행하세요:

```bash
# AAC 데이터셋 생성
python data_prepare.py --steps 1 2 3 4 5 6 7 8
```

필요한 파일들:
- `dataset/processed/dataset_completed.json` - 완성된 훈련 데이터
- `dataset/images/` - AAC 카드 이미지들
- `dataset/processed/clustering_results.json` - 클러스터링 결과

### 3. 훈련 시작

```bash
# 기본 훈련
python train/train.py

# Weights & Biases 로깅 포함
python train/train.py --wandb

# 커스텀 설정 파일 사용
python train/train.py --config my_config.json
```

## ⚙️ 주요 설정

`train/config/train_config.py`에서 다음 설정들을 조정할 수 있습니다:

### 모델 설정
- `model_type`: 'phi3_vision' (기본값)
- `model_size`: '3.8B'
- `use_lora`: LoRA 파인튜닝 사용 여부 (기본: True)

### 훈련 설정
- `batch_size`: 배치 크기 (기본: 4)
- `learning_rate`: 학습률 (기본: 2e-5)
- `num_epochs`: 에포크 수 (기본: 10)
- `gradient_accumulation_steps`: 그래디언트 누적 (기본: 8)

### 하드웨어 설정
- `device`: 'cuda' 또는 'cpu'
- `use_fp16`: Mixed precision 사용 (기본: True)

## 📊 평가 메트릭

모델 성능은 다음 메트릭으로 평가됩니다:

### 기본 텍스트 생성 메트릭
- **BLEU-4**: 정확도 기반 평가
- **ROUGE-1/2/L**: 재현률 기반 평가
- **의미 유사도**: Sentence-BERT 기반

### AAC 특화 메트릭
- **페르소나 일관성**: 사용자 특성과의 일치도
- **컨텍스트 관련성**: 상황 정보와의 연관성

## 💾 체크포인트 관리

- 체크포인트는 `train/checkpoints/`에 저장됩니다
- `best_model.pt`: 검증 성능이 가장 좋은 모델
- `checkpoint_step_*.pt`: 정기적인 중간 체크포인트

## 🔧 문제 해결

### GPU 메모리 부족
```python
# train_config.py에서 다음 설정 조정:
'batch_size': 2,  # 더 작은 배치 크기
'gradient_accumulation_steps': 16,  # 더 많은 누적
'use_lora': True,  # LoRA 사용 필수
```

### 데이터셋 오류
```bash
# 데이터 준비 다시 실행
python data_prepare.py --steps 8 --overwrite
```

### CUDA 메모리 오류
```bash
# 환경 변수 설정
export CUDA_VISIBLE_DEVICES=0
export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:128
```

## 📈 모니터링

### Weights & Biases
- 실시간 손실 그래프
- 메트릭 변화 추이
- 하이퍼파라미터 비교

### TensorBoard (선택사항)
```bash
tensorboard --logdir train/logs/
```

## 🚀 추론 사용법

훈련된 모델을 사용하여 AAC 카드를 해석하는 방법:

```python
from train.models.aac_multimodal_model import AACMultimodalModel
from train.config.train_config import TRAIN_CONFIG

# 모델 로드
model = AACMultimodalModel.load_model('train/checkpoints/best_model.pt', TRAIN_CONFIG)

# 해석 생성
interpretations = model.generate_interpretation(
    images=[image1, image2],  # PIL 이미지 리스트
    persona_info={'age': 25, 'gender': 'female', ...},
    context_info="상황 설명"
)
```

## 🤝 기여하기

1. 이슈 등록: 버그 리포트나 기능 요청
2. 코드 기여: Pull Request 환영
3. 문서 개선: README나 코드 주석 개선

## 📄 라이센스

이 프로젝트는 MIT 라이센스 하에 배포됩니다.