# AAC 데이터셋 전처리 시스템

## 설치

```bash
pip install -r requirements.txt
export OPENAI_API_KEY="your_openai_api_key"
```

## 실행

### 기본 실행
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

### 시각화 옵션
```bash
# 시각화 없이 실행
python data_prepare.py --no-visualize

# 시각화 포함 실행 (기본값)
python data_prepare.py
```

## 단계

1. 이미지 필터링
2. 임베딩 생성
3. 클러스터링
4. 데이터셋 스키마
5. 클러스터 태깅
6. 페르소나 카테고리 할당
7. 카드 조합 생성
8. 최종 데이터셋 생성
