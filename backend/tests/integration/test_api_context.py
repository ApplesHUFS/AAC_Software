"""컨텍스트 API 통합 테스트

POST /api/context 및 GET /api/context/{id} 엔드포인트를 테스트합니다.
"""

import pytest
from fastapi.testclient import TestClient


class TestCreateContextAPI:
    """컨텍스트 생성 API 테스트"""

    def test_create_context_success(self, client: TestClient):
        """컨텍스트 생성 성공"""
        # Arrange
        request_data = {
            "userId": "test-user-001",
            "place": "학교",
            "interactionPartner": "선생님",
            "currentActivity": "수업 중",
        }

        # Act
        response = client.post("/api/context", json=request_data)

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True

    def test_create_context_returns_context_id(self, client: TestClient):
        """생성된 컨텍스트에 ID 포함"""
        # Arrange
        request_data = {
            "userId": "test-user-001",
            "place": "병원",
            "interactionPartner": "의사",
        }

        # Act
        response = client.post("/api/context", json=request_data)
        data = response.json()["data"]

        # Assert
        assert "contextId" in data
        assert len(data["contextId"]) > 0

    def test_create_context_returns_time(self, client: TestClient):
        """생성된 컨텍스트에 시간 포함"""
        # Arrange
        request_data = {
            "userId": "test-user-001",
            "place": "집",
            "interactionPartner": "엄마",
        }

        # Act
        response = client.post("/api/context", json=request_data)
        data = response.json()["data"]

        # Assert
        assert "time" in data
        assert "시" in data["time"]
        assert "분" in data["time"]

    def test_create_context_without_activity(self, client: TestClient):
        """현재 활동 없이 컨텍스트 생성"""
        # Arrange
        request_data = {
            "userId": "test-user-001",
            "place": "공원",
            "interactionPartner": "친구",
        }

        # Act
        response = client.post("/api/context", json=request_data)

        # Assert
        assert response.status_code == 201
        data = response.json()["data"]
        assert data["currentActivity"] == ""

    def test_create_context_missing_place(self, client: TestClient):
        """장소 누락 시 에러"""
        # Arrange
        request_data = {
            "userId": "test-user-001",
            "interactionPartner": "선생님",
        }

        # Act
        response = client.post("/api/context", json=request_data)

        # Assert
        assert response.status_code == 422

    def test_create_context_missing_partner(self, client: TestClient):
        """대화 상대 누락 시 에러"""
        # Arrange
        request_data = {
            "userId": "test-user-001",
            "place": "학교",
        }

        # Act
        response = client.post("/api/context", json=request_data)

        # Assert
        assert response.status_code == 422

    def test_create_context_empty_place(self, client: TestClient):
        """빈 장소 시 에러"""
        # Arrange
        request_data = {
            "userId": "test-user-001",
            "place": "",
            "interactionPartner": "선생님",
        }

        # Act
        response = client.post("/api/context", json=request_data)

        # Assert
        assert response.status_code == 422


class TestGetContextAPI:
    """컨텍스트 조회 API 테스트"""

    def test_get_context_success(self, client: TestClient):
        """컨텍스트 조회 성공"""
        # Arrange: 먼저 컨텍스트 생성
        create_response = client.post(
            "/api/context",
            json={
                "userId": "test-user-001",
                "place": "학교",
                "interactionPartner": "선생님",
                "currentActivity": "수업",
            },
        )
        context_id = create_response.json()["data"]["contextId"]

        # Act
        response = client.get(f"/api/context/{context_id}")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["contextId"] == context_id

    def test_get_context_returns_all_fields(self, client: TestClient):
        """조회된 컨텍스트에 모든 필드 포함"""
        # Arrange
        create_response = client.post(
            "/api/context",
            json={
                "userId": "user-abc",
                "place": "카페",
                "interactionPartner": "친구",
                "currentActivity": "대화",
            },
        )
        context_id = create_response.json()["data"]["contextId"]

        # Act
        response = client.get(f"/api/context/{context_id}")
        data = response.json()["data"]

        # Assert
        assert data["userId"] == "user-abc"
        assert data["place"] == "카페"
        assert data["interactionPartner"] == "친구"
        assert data["currentActivity"] == "대화"
        assert "time" in data
        assert "createdAt" in data

    def test_get_context_not_found(self, client: TestClient):
        """존재하지 않는 컨텍스트 조회"""
        # Act
        response = client.get("/api/context/non-existent-id")

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert data["success"] is False

    def test_get_context_invalid_id_format(self, client: TestClient):
        """잘못된 형식의 컨텍스트 ID"""
        # Act
        response = client.get("/api/context/")

        # Assert
        # 빈 ID는 라우팅되지 않음 (405: 해당 경로에 GET 없음)
        assert response.status_code in [404, 307, 405]


class TestContextDataIntegrity:
    """컨텍스트 데이터 무결성 테스트"""

    def test_context_data_preserved(self, client: TestClient):
        """생성 시 입력한 데이터가 조회 시 유지됨"""
        # Arrange
        original_data = {
            "userId": "integrity-test-user",
            "place": "도서관",
            "interactionPartner": "사서",
            "currentActivity": "책 빌리기",
        }
        create_response = client.post("/api/context", json=original_data)
        context_id = create_response.json()["data"]["contextId"]

        # Act
        response = client.get(f"/api/context/{context_id}")
        retrieved = response.json()["data"]

        # Assert
        assert retrieved["userId"] == original_data["userId"]
        assert retrieved["place"] == original_data["place"]
        assert retrieved["interactionPartner"] == original_data["interactionPartner"]
        assert retrieved["currentActivity"] == original_data["currentActivity"]

    def test_multiple_contexts_isolated(self, client: TestClient):
        """여러 컨텍스트가 서로 독립적"""
        # Arrange
        context1 = client.post(
            "/api/context",
            json={
                "userId": "user-1",
                "place": "장소1",
                "interactionPartner": "상대1",
            },
        ).json()["data"]

        context2 = client.post(
            "/api/context",
            json={
                "userId": "user-2",
                "place": "장소2",
                "interactionPartner": "상대2",
            },
        ).json()["data"]

        # Act
        retrieved1 = client.get(f"/api/context/{context1['contextId']}").json()["data"]
        retrieved2 = client.get(f"/api/context/{context2['contextId']}").json()["data"]

        # Assert
        assert retrieved1["place"] == "장소1"
        assert retrieved2["place"] == "장소2"
        assert retrieved1["contextId"] != retrieved2["contextId"]
