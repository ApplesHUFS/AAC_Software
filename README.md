# AAC Software - 개인화된 보완대체의사소통 시스템

AAC(Augmentative and Alternative Communication) 카드를 활용한 개인화된 의사소통 지원 시스템입니다. 의사소통장애, 자폐스펙트럼장애, 지적장애를 가진 사용자들이 효과적으로 의사소통할 수 있도록 AI 기반 카드 추천 및 해석 서비스를 제공합니다.

## 프로젝트 개요

AAC Software는 의사소통에 어려움을 겪는 **소통이**와 이를 돕는 **도움이** 간의 원활한 소통을 지원하는 통합 시스템입니다.

### 핵심 기능
- **개인화된 카드 추천**: 사용자 페르소나와 상황 맥락을 분석한 맞춤형 AAC 카드 추천
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
└── dataset/            # AAC 카드 데이터셋 (별도 다운로드)
```

### 컴포넌트 구성

#### 🌐 Frontend (React)
- 사용자 인증 및 프로필 관리
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

## 프로젝트 구조

### Frontend ([상세 문서](./frontend/README.md))
```
frontend/
├── src/
│   ├── pages/          # 페이지 컴포넌트
│   ├── components/     # 재사용 컴포넌트
│   ├── services/       # API 클라이언트
│   └── styles/         # CSS 스타일
└── public/             # 정적 파일
```

### Backend ([상세 문서](./backend/README.md))
```
backend/
├── app.py              # Flask 메인 앱
├── public/             # API 연동 모듈
├── private/            # 비즈니스 로직
└── service_config.py   # 설정 파일
```

### Data Processing ([상세 문서](./data_processing/README.md))
```
data_processing/
├── data_prepare.py     # 메인 파이프라인
├── data_source/        # 처리 모듈
└── dataset_config.py   # 설정 파일
```

## 기술 스택

### 프론트엔드
- **React 18.2**: UI 라이브러리
- **JavaScript ES6+**: 프로그래밍 언어
- **CSS3**: 스타일링 및 반응형 디자인

### 백엔드
- **Flask 3.0+**: 웹 프레임워크
- **OpenAI GPT-4o**: 자연어 처리
- **LangChain**: LLM 체인 관리
- **Sentence Transformers**: 텍스트 임베딩

### 데이터 처리
- **PyTorch**: 딥러닝 프레임워크
- **CLIP**: 멀티모달 임베딩
- **scikit-learn**: 머신러닝 도구
- **OpenAI Vision API**: 이미지 분석

### 데이터 저장
- **JSON**: 사용자 데이터 및 설정
- **파일 시스템**: 이미지 및 모델 데이터

## API 엔드포인트

### 인증
- `POST /api/auth/register` - 회원가입
- `POST /api/auth/login` - 로그인
- `GET /api/auth/profile/{userId}` - 프로필 조회

### 카드 시스템
- `POST /api/cards/recommend` - 개인화된 카드 추천
- `POST /api/cards/interpret` - 선택된 카드 해석
- `GET /api/cards/history/{contextId}` - 추천 히스토리

### 상황 관리
- `POST /api/context` - 대화 상황 생성
- `GET /api/context/{contextId}` - 상황 정보 조회

### 피드백
- `POST /api/feedback/submit` - 해석 결과 피드백

## 개발 환경

### 개발 서버 실행
```bash
# 백엔드 (포트 8000)
cd backend && python app.py

# 프론트엔드 (포트 3000)
cd frontend && npm start
```

### 프로덕션 빌드
```bash
# 프론트엔드 빌드
cd frontend && npm run build

# 백엔드는 WSGI 서버(예: Gunicorn) 사용
cd backend && gunicorn app:app
```

### 코드 품질 관리
```bash
# 프론트엔드 린팅
cd frontend && npm run lint

# 백엔드 포맷팅 (권장: black, flake8)
cd backend && black . && flake8 .

# 데이터 처리 모듈 테스트
cd data_processing && python -m pytest
```

## 설정

### 백엔드 설정 (service_config.py)
- OpenAI 모델 및 파라미터
- 카드 추천 알고리즘 임계값
- 사용자 검증 규칙

### 데이터 처리 설정 (dataset_config.py)
- CLIP 모델 선택
- 클러스터링 파라미터
- 필터링 규칙

### 환경 변수
- `OPENAI_API_KEY`: OpenAI API 키 (필수)
- `REACT_APP_API_URL`: API 서버 URL (기본: http://localhost:8000)

## 성능 최적화

### 백엔드
- 클러스터링 결과 메모리 캐싱
- 이미지 직접 서빙으로 네트워크 효율성 개선
- 대화 메모리 크기 제한 (50개 항목)

### 프론트엔드
- 세션 스토리지 기반 상태 관리
- 컴포넌트 재사용 및 최적화
- 반응형 디자인으로 다양한 디바이스 지원

### 데이터 처리
- GPU 가속 임베딩 생성
- 배치 처리 및 병렬화
- 중간 결과 캐싱

## 보안

- SHA256 해시 기반 비밀번호 저장
- API 응답에서 민감 정보 제외
- CORS 설정으로 안전한 크로스 도메인 통신
- 파일 경로 검증

## 모니터링

- 헬스체크 엔드포인트 (`/health`)
- 전역 에러 핸들러
- 컴포넌트별 초기화 상태 확인
- 상세한 로깅 및 에러 추적

## 문제 해결

### 일반적인 문제
1. **OpenAI API 키 오류**: `.env` 파일에 올바른 API 키 설정 확인
2. **포트 충돌**: 백엔드(8000), 프론트엔드(3000) 포트 사용 가능 여부 확인
3. **CORS 오류**: 백엔드 CORS 설정에서 프론트엔드 URL 허용 확인
4. **데이터셋 파일 누락**: `dataset/` 디렉토리에 필수 파일 존재 여부 확인

### 디버깅
```bash
# 백엔드 디버그 모드
cd backend && python app.py  # debug=True 기본 설정

# 프론트엔드 개발자 도구 활용
# 브라우저 개발자 도구에서 네트워크 탭 확인

# 데이터 처리 파이프라인 단계별 실행
cd data_processing && python data_prepare.py --steps 1
```

## 기여하기

1. 새로운 기능 개발 시 기존 아키텍처 패턴 준수
2. 코드 스타일 가이드 준수 (ESLint, Prettier, Black)
3. 단위 테스트 작성 및 기존 테스트 통과 확인
4. API 변경 시 프론트엔드와 백엔드 호환성 확인

## 라이센스

이 프로젝트는 연구 및 교육 목적으로 제작되었습니다.

## 연락처

프로젝트 관련 문의사항이나 기술적 지원이 필요한 경우 프로젝트 메인테이너에게 연락해주세요.

---

각 모듈의 상세한 설치 및 사용 방법은 해당 디렉토리의 README.md 파일을 참조하세요.