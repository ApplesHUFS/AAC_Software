# API 문서

AAC Software Backend API 엔드포인트 가이드입니다.

## 기본 정보

- **Base URL**: `http://localhost:8000`
- **Content-Type**: `application/json`

## 인증 API

### 회원가입
```http
POST /api/auth/register
Content-Type: application/json

{
  "username": "helper_name",
  "password": "password123",
  "helper_name": "도움이 이름"
}
```

### 로그인
```http
POST /api/auth/login
Content-Type: application/json

{
  "username": "helper_name",
  "password": "password123"
}
```

### 프로필 조회
```http
GET /api/auth/profile/{userId}
```

## 카드 시스템 API

### 카드 추천
```http
POST /api/cards/recommend
Content-Type: application/json

{
  "user_id": "user123",
  "context_id": "context456",
  "situation": "놀이시간에 친구와 함께 놀고 싶어함"
}
```

**응답 예시:**
```json
{
  "recommended_cards": [
    {
      "filename": "play_001.jpg",
      "cluster_id": 5,
      "similarity_score": 0.85
    }
  ],
  "context_id": "context456"
}
```

### 카드 해석
```http
POST /api/cards/interpret
Content-Type: application/json

{
  "context_id": "context456",
  "selected_cards": ["play_001.jpg", "friend_002.jpg"],
  "situation": "놀이시간"
}
```

**응답 예시:**
```json
{
  "interpretation": "소통이가 친구와 함께 놀고 싶어합니다.",
  "feedback_id": "feedback789"
}
```

### 추천 히스토리
```http
GET /api/cards/history/{contextId}
GET /api/cards/history/{contextId}/page/{pageNumber}
```

## 피드백 API

### 피드백 제출
```http
POST /api/feedback/submit
Content-Type: application/json

{
  "feedback_id": "feedback789",
  "accuracy": 4,
  "comments": "정확한 해석이었습니다"
}
```

## 상황 관리 API

### 상황 생성
```http
POST /api/context
Content-Type: application/json

{
  "user_id": "user123",
  "situation": "놀이시간",
  "additional_info": "친구들과 함께"
}
```

## 에러 코드
- `400`: 잘못된 요청 데이터
- `401`: 인증 실패
- `404`: 리소스를 찾을 수 없음
- `500`: 서버 내부 오류

## 사용 예시

```javascript
// 카드 추천 요청
const response = await fetch('http://localhost:8000/api/cards/recommend', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    user_id: 'user123',
    context_id: 'context456',
    situation: '놀이시간에 친구와 함께 놀고 싶어함'
  })
});

const data = await response.json();
console.log(data.recommended_cards);
```
