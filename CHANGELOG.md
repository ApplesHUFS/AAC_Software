# 변경사항 (Changelog)

## [Unreleased]

### 예정
- 정식 릴리스 1.0.0 출시 준비
- 성능 최적화 및 안정성 개선
- 추가 기능 개발

## [0.9.0] - 2025-09-18 (Beta)

### 추가
- **소통,이룸 AAC Software 베타 버전 출시**
- **Frontend**: React 18.2 기반 웹 애플리케이션
  - 도움이/소통이 사용자 인증 및 프로필 관리
  - 개인화된 AAC 카드 선택 인터페이스
  - AI 해석 결과 표시 및 실시간 피드백 수집
  - 대화 메모리 기반 개인화 서비스
- **Backend**: Flask 3.0+ API 서버 (포트: 8000)
  - OpenAI GPT-4o 기반 카드 의미 해석
  - 개인화된 카드 추천 알고리즘
  - RESTful API 및 사용자 관리
  - 피드백 기반 해석 정확도 개선 시스템
- **Data Processing**: AI 기반 데이터 처리 파이프라인
  - CLIP 기반 멀티모달 임베딩 생성
  - 계층적 클러스터링 및 자동 태깅
  - OpenAI Vision API 활용 이미지 처리
  - ARASAAC 데이터셋 필터링 및 분류
- **데이터셋**: ARASAAC 픽토그램 통합
  - Sergio Palao 제작 ARASAAC 픽토그램 포함
  - Creative Commons BY-NC-SA 라이센스 준수

### 핵심 기능
- 개인화된 카드 추천 시스템
- AI 기반 카드 해석 및 의미 분석
- 실시간 피드백을 통한 지속적 학습
- 대화 패턴 학습을 통한 개인화 서비스

### 기술 스택
- **Frontend**: React 18.2, JavaScript ES6+, CSS3
- **Backend**: Flask 3.0+, OpenAI GPT-4o, LangChain, Sentence Transformers
- **Data Processing**: PyTorch, CLIP, scikit-learn, OpenAI Vision API
- **Data Storage**: JSON 파일, 파일 시스템

### 시스템 요구사항
- Python 3.8+
- Node.js 16.0+
- OpenAI API 키

### 알려진 제한사항
- 베타 버전으로 일부 기능이 제한적일 수 있음
- 상용 환경에서의 사용은 권장하지 않음

---

변경사항 형식:
- **추가**: 새로운 기능
- **변경**: 기존 기능 수정
- **수정**: 버그 수정
- **제거**: 기능 삭제
- **보안**: 보안 관련 수정
