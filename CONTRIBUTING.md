# 기여 가이드라인

AAC Software 프로젝트에 기여해 주셔서 감사합니다.

## 기여 방법

1. **이슈 신고**: 버그나 기능 요청은 [Issues](../../issues)를 통해 신고
2. **코드 기여**: Fork → 브랜치 생성 → 수정 → Pull Request
3. **문서 개선**: 오타, 설명 개선 등 모든 문서 개선 환영

## 개발 환경 설정

```bash
git clone https://github.com/YOUR_USERNAME/AAC_Software.git
cd AAC_Software

# 백엔드
cd backend && pip install -r requirements.txt
echo "OPENAI_API_KEY=your_key" > .env

# 프론트엔드
cd ../frontend && npm install

# 데이터 처리
cd ../data_processing && pip install -r requirements.txt
```

## 코드 스타일

- **Python**: PEP 8 준수, docstring 작성
- **JavaScript**: ES6+, camelCase 사용
- **커밋**: `feat:`, `fix:`, `docs:` 등 타입 명시

## Pull Request

1. 최신 main 브랜치와 동기화
2. 명확한 제목과 설명 작성
3. 관련 이슈 번호 연결 (`Closes #123`)

기여해 주셔서 감사합니다! 🎉