# AAC Software - 개인화된 보완대체의사소통 시스템

AAC(Augmentative and Alternative Communication) 카드를 활용한 개인화된 의사소통 지원 시스템입니다. 의사소통장애, 자폐스펙트럼장애, 지적장애를 가진 사용자들이 효과적으로 의사소통할 수 있도록 AI 기반 카드 추천 및 해석 서비스를 제공합니다.

## 프로젝트 개요

AAC Software는 의사소통에 어려움을 겪는 **소통이**와 이를 돕는 **도움이** 간의 원활한 소통을 지원하는 통합 시스템입니다.

### 핵심 기능
- **개인화된 카드 추천**: 소통이 프로필과 상황 맥락을 분석한 맞춤형 AAC 카드 추천
- **AI 기반 해석**: GPT-4o를 활용한 선택된 카드의 의미 해석
- **실시간 피드백**: 도움이의 피드백을 통한 지속적인 해석 정확도 개선
- **대화 메모리**: 과거 대화 패턴 학습을 통한 개인화 서비스 향상

### 사용자 역할
- **도움이**: 소통이를 돕는 보호자, 교사, 치료사 등의 보조자
- **소통이**: 의사소통에 어려움을 겪는 주 사용자

## 시스템 아키텍처

```
AAC_Software/
├── frontend/           # React 웹 애플리케이션
├── backend/            # Flask API 서버
├── data_processing/    # 데이터 처리 파이프라인
├── user_data/         # 사용자 데이터 저장
└── dataset/            # AAC 카드 데이터셋
```

### 컴포넌트 구성

#### 🌐 Frontend (React)
- 사용자 인증 및 소통이 프로필 관리
- AAC 카드 선택 인터페이스
- AI 해석 결과 표시 및 피드백 수집
- **포트**: 3000 (개발), 빌드 후 정적 배포

#### 🚀 Backend (Flask)
- RESTful API 서버
- 사용자 관리 및 인증
- 카드 추천 알고리즘
- OpenAI API 기반 카드 해석
- **포트**: 8000

#### 🔬 Data Processing (Python)
- AAC 카드 이미지 필터링 및 분류
- CLIP 기반 멀티모달 임베딩 생성
- 계층적 클러스터링 및 자동 태깅
- **실행**: 배치 처리 파이프라인

## 빠른 시작

### 사전 요구사항
- Python 3.8+
- Node.js 16.0+
- OpenAI API 키

### 1. 저장소 클론
```bash
git clone <repository-url>
cd AAC_Software
```

### 2. 환경 설정
```bash
# 백엔드 및 데이터 처리용 .env 파일 생성
echo "OPENAI_API_KEY=your_openai_api_key_here" > backend/.env
echo "OPENAI_API_KEY=your_openai_api_key_here" > data_processing/.env
```

### 3. 데이터셋 준비
```bash
# 데이터셋 다운로드 스크립트 실행
cd data_processing
chmod +x download_dataset.sh
./download_dataset.sh

# 데이터 처리 파이프라인 실행
pip install -r requirements.txt
python data_prepare.py
```

### 4. 백엔드 서버 실행
```bash
cd backend
pip install -r requirements.txt
python app.py
```

### 5. 프론트엔드 애플리케이션 실행
```bash
cd frontend
npm install
npm start
```

### 6. 애플리케이션 접속
브라우저에서 `http://localhost:3000`에 접속하여 시스템을 사용할 수 있습니다.

## 기술 스택

- **Frontend**: React 18.2, JavaScript ES6+, CSS3
- **Backend**: Flask 3.0+, OpenAI GPT-4o, LangChain, Sentence Transformers
- **Data Processing**: PyTorch, CLIP, scikit-learn, OpenAI Vision API
- **Data Storage**: JSON 파일, 파일 시스템

## 환경 변수 설정
- `OPENAI_API_KEY`: OpenAI API 키 (필수)
- `REACT_APP_API_URL`: API 서버 URL (기본: http://localhost:8000)

## 문제 해결

### 일반적인 문제
1. **OpenAI API 키 오류**: `.env` 파일에 올바른 API 키 설정 확인
2. **포트 충돌**: 백엔드(8000), 프론트엔드(3000) 포트 사용 가능 여부 확인
3. **CORS 오류**: 백엔드 CORS 설정에서 프론트엔드 URL 허용 확인
4. **데이터셋 파일 누락**: `dataset/` 디렉토리에 필수 파일 존재 여부 확인

## 라이센스

이 프로젝트는 연구 및 교육 목적으로 제작되었습니다.

---

각 모듈의 상세한 설치 및 사용 방법은 해당 디렉토리의 README를 참조하세요:
- [Frontend 상세 문서](./frontend/README.md)
- [Backend 상세 문서](./backend/README.md)
- [Data Processing 상세 문서](./data_processing/README.md)
