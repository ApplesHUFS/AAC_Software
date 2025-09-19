<div align="center">
    ![alt text](image\logo.png)
</div>

# 소통,이룸 (AAC Software) - 개인화된 보완대체의사소통 시스템

AAC(Augmentative and Alternative Communication) 카드를 활용한 개인화된 의사소통 지원 시스템입니다. 의사소통장애, 자폐스펙트럼장애, 지적장애를 가진 사용자들이 효과적으로 의사소통할 수 있도록 AI 기반 카드 추천 및 해석 서비스를 제공합니다.

## 프로젝트 개요

AAC Software는 의사소통에 어려움을 겪는 **소통이**와 이를 돕는 **도움이** 간의 원활한 소통을 지원하는 통합 시스템입니다.

### 사용자 역할
- **도움이**: 소통이를 돕는 보호자, 교사, 치료사 등의 보조자
- **소통이**: 의사소통에 어려움을 겪는 주 사용자

### 핵심 기능 및 용례

- **회원가입**: 사용자 ID와 비밀번호를 포함한 계정 정보뿐만 아니라, 소통이의 의사소통 특징 및 관심 주제 등의 정보 입력 과정도 포함되어 있습니다. 이를 통해 프로그램은 소통이의 정보를 기억한 뒤, 개인화된 카드 추천 및 해석에 사용합니다.
<img width="80%" src="https://github.com/user-attachments/assets/f7affc4f-1945-4e34-aaaf-53d13011b8a9"/>

- **로그인 및 정보 수정**: 회원가입 시 입력한 정보로 로그인 및 정보 수정을 진행할 수 있습니다.
<img width="80%" src="https://github.com/user-attachments/assets/198623d7-af1c-4eba-919b-1fa2cfabc33a"/>

- **대화 상황 입력**: 현재 장소, 대화 상대, 현재 활동을 입력하면 시스템이 상황 맥락에 적절한 해석을 생성하는 데 사용합니다.
<img width="80%" src="https://github.com/user-attachments/assets/f0e214b3-eed5-4de2-a7c3-41b8764c6680"/>

- **개인화된 추천 카드 선택**: 시스템이 소통이의 정보를 분석하여 맞춤형 AAC 카드를 추천해줍니다. 소통이는 추천된 20개의 카드 중 최대 4개의 카드까지 자유로이 선택이 가능하며, 카드 묶음이 마음에 들지 않을 경우 다른 카드들을 추가로 추천받을 수 있습니다.
<img width="80%" src="https://github.com/user-attachments/assets/5a8d3cd6-740d-4cd8-931c-f5f0a88a62bd"/>

- **개인화된 카드 해석**: GPT-4o가 현재 대화 상황과 과거 대화 기록, 선택된 카드를 바탕으로 세 가지의 서로 다른 해석을 생성하여 도움이에게 보여줍니다. 도움이는 세 개의 해석 중 옳다고 생각되는 해석 하나를 선택하거나, 직접 올바른 의미를 입력할 수 있습니다.

*제시된 해석

<img width="80%" src="https://github.com/user-attachments/assets/e3205696-15fb-4390-9593-01e4d7068cce"/>

*직접 입력

<img width="80%" src="https://github.com/user-attachments/assets/a75d017b-63c5-425b-b662-282935959a5b"/>

- **총 정리 및 피드백 저장**: 도움이가 선택한 해석 혹은 직접 적은 올바른 의미, 대화 요약, 사용 카드를 화면에 제시합니다. 이번 대화에서 사용된 카드와 해석 정보는 피드백으로써 저장되고, 다음 대화에 추가 맥락으로써 사용되어 지속적으로 해석 정확도를 개선합니다.
<img width="80%" src="https://github.com/user-attachments/assets/17e350e9-d65b-4eb5-8266-7251dc0fee98"/>

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
chmod +x download_arasaac.sh
./download_arasaac.sh

# 데이터 처리 파이프라인 실행
cd data_processing
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

[![CC BY-NC-SA 4.0][cc-by-nc-sa-shield]][cc-by-nc-sa]

본 프로젝트는 [Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License][cc-by-nc-sa] 하에 배포됩니다.

[![CC BY-NC-SA 4.0][cc-by-nc-sa-image]][cc-by-nc-sa]

### 라이센스 조건

**저작자표시 (Attribution)**
본 저작물을 사용, 배포, 전시할 때에는 반드시 원저작자와 출처를 명시하여야 합니다.

**비영리 (NonCommercial)**
본 저작물은 비영리 목적으로만 사용할 수 있으며, 상업적 이용은 허용되지 않습니다.

**동일조건변경허락 (ShareAlike)**
본 저작물을 개작, 변형 또는 가공했을 경우 반드시 원저작물과 동일한 라이센스 조건으로 배포하여야 합니다.

### 포함된 제3자 저작물

본 소프트웨어는 다음의 제3자 저작물을 포함하고 있습니다:

**ARASAAC 픽토그램**
- 저작자: Sergio Palao
- 출처: [ARASAAC Portal Aragonés de la Comunicación Aumentativa y Alternativa](http://www.arasaac.org)
- 라이센스: Creative Commons BY-NC-SA
- 저작권자: Gobierno de Aragón (아라곤 자치정부, 스페인)

사용된 그림 기호는 Aragón 정부의 자산이며 Sergio Palao가 ARASAAC용으로 제작하였으며 Creative Commons 라이선스 BY-NC-SA에 따라 배포됩니다.

### 면책사항

본 소프트웨어는 "있는 그대로" 제공되며, 명시적이거나 묵시적인 어떠한 보증도 제공하지 않습니다. 본 소프트웨어의 사용으로 인해 발생하는 모든 손해에 대해 저작자는 어떠한 책임도 지지 않습니다.

### 추가 정보

라이센스에 대한 자세한 내용은 [Creative Commons 공식 웹사이트](https://creativecommons.org/licenses/by-nc-sa/4.0/deed.ko)에서 확인하실 수 있습니다.

[cc-by-nc-sa]: http://creativecommons.org/licenses/by-nc-sa/4.0/
[cc-by-nc-sa-image]: https://licensebuttons.net/l/by-nc-sa/4.0/88x31.png
[cc-by-nc-sa-shield]: https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey.svg

---

각 모듈의 상세한 설치 및 사용 방법은 해당 디렉토리의 README를 참조하세요:
- [Frontend 상세 문서](./frontend/README.md)
- [Backend 상세 문서](./backend/README.md)
- [Data Processing 상세 문서](./data_processing/README.md)
