"""카드 API 통합 테스트

POST /api/cards/validate 엔드포인트를 테스트합니다.
카드 추천(recommend)은 외부 서비스 의존성이 있어 Mock을 사용합니다.
"""

import pytest
from fastapi.testclient import TestClient


class TestCardValidateAPI:
    """카드 선택 검증 API 테스트"""

    def test_validate_selection_success(self, client: TestClient):
        """유효한 카드 선택 검증"""
        # Arrange
        request_data = {
            "selectedCards": ["001_사과.png", "002_바나나.png"],
            "allRecommendedCards": [
                "001_사과.png",
                "002_바나나.png",
                "003_물.png",
                "004_우유.png",
            ],
        }

        # Act
        response = client.post("/api/cards/validate", json=request_data)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["valid"] is True
        assert data["data"]["selectedCount"] == 2

    def test_validate_selection_single_card(self, client: TestClient):
        """단일 카드 선택"""
        # Arrange
        request_data = {
            "selectedCards": ["001_사과.png"],
            "allRecommendedCards": ["001_사과.png", "002_바나나.png"],
        }

        # Act
        response = client.post("/api/cards/validate", json=request_data)

        # Assert
        assert response.status_code == 200
        assert response.json()["data"]["valid"] is True
        assert response.json()["data"]["selectedCount"] == 1

    def test_validate_selection_max_cards(self, client: TestClient):
        """최대 4개 카드 선택"""
        # Arrange
        request_data = {
            "selectedCards": [
                "001_사과.png",
                "002_바나나.png",
                "003_물.png",
                "004_우유.png",
            ],
            "allRecommendedCards": [
                "001_사과.png",
                "002_바나나.png",
                "003_물.png",
                "004_우유.png",
                "005_밥.png",
            ],
        }

        # Act
        response = client.post("/api/cards/validate", json=request_data)

        # Assert
        assert response.status_code == 200
        assert response.json()["data"]["valid"] is True
        assert response.json()["data"]["selectedCount"] == 4

    def test_validate_selection_too_many_cards(self, client: TestClient):
        """5개 이상 카드 선택 시 에러"""
        # Arrange
        request_data = {
            "selectedCards": [
                "001_사과.png",
                "002_바나나.png",
                "003_물.png",
                "004_우유.png",
                "005_밥.png",
            ],
            "allRecommendedCards": [
                "001_사과.png",
                "002_바나나.png",
                "003_물.png",
                "004_우유.png",
                "005_밥.png",
                "006_빵.png",
            ],
        }

        # Act
        response = client.post("/api/cards/validate", json=request_data)

        # Assert
        assert response.status_code == 400
        data = response.json()
        assert data["success"] is False

    def test_validate_selection_no_cards(self, client: TestClient):
        """카드 미선택 시 에러"""
        # Arrange
        request_data = {
            "selectedCards": [],
            "allRecommendedCards": ["001_사과.png", "002_바나나.png"],
        }

        # Act
        response = client.post("/api/cards/validate", json=request_data)

        # Assert
        assert response.status_code == 400
        data = response.json()
        assert data["success"] is False

    def test_validate_selection_invalid_card(self, client: TestClient):
        """추천되지 않은 카드 선택 시 에러"""
        # Arrange
        request_data = {
            "selectedCards": ["invalid_card.png"],
            "allRecommendedCards": ["001_사과.png", "002_바나나.png"],
        }

        # Act
        response = client.post("/api/cards/validate", json=request_data)

        # Assert
        assert response.status_code == 400
        data = response.json()
        assert data["success"] is False

    def test_validate_selection_message_content(self, client: TestClient):
        """검증 성공 메시지 내용"""
        # Arrange
        request_data = {
            "selectedCards": ["001_사과.png"],
            "allRecommendedCards": ["001_사과.png"],
        }

        # Act
        response = client.post("/api/cards/validate", json=request_data)

        # Assert
        message = response.json()["message"]
        assert "유효" in message or "성공" in message


class TestCardValidateEdgeCases:
    """카드 검증 엣지 케이스 테스트"""

    def test_validate_with_empty_recommended_list(self, client: TestClient):
        """추천 목록이 비어있을 때"""
        # Arrange
        request_data = {
            "selectedCards": ["001_사과.png"],
            "allRecommendedCards": [],
        }

        # Act
        response = client.post("/api/cards/validate", json=request_data)

        # Assert
        assert response.status_code == 400

    def test_validate_with_duplicate_selections(self, client: TestClient):
        """중복 선택 처리"""
        # Arrange
        request_data = {
            "selectedCards": ["001_사과.png", "001_사과.png"],
            "allRecommendedCards": ["001_사과.png", "002_바나나.png"],
        }

        # Act
        response = client.post("/api/cards/validate", json=request_data)

        # Assert
        assert response.status_code == 200
        assert response.json()["data"]["selectedCount"] == 2

    def test_validate_missing_selected_cards_field(self, client: TestClient):
        """selectedCards 필드 누락"""
        # Arrange
        request_data = {
            "allRecommendedCards": ["001_사과.png"],
        }

        # Act
        response = client.post("/api/cards/validate", json=request_data)

        # Assert
        assert response.status_code == 422

    def test_validate_missing_recommended_cards_field(self, client: TestClient):
        """allRecommendedCards 필드 누락"""
        # Arrange
        request_data = {
            "selectedCards": ["001_사과.png"],
        }

        # Act
        response = client.post("/api/cards/validate", json=request_data)

        # Assert
        assert response.status_code == 422


class TestCardRecommendAPI:
    """카드 추천 API 테스트 (외부 의존성 필요)

    실제 카드 추천은 CLIP 모델, 벡터 인덱스 등
    외부 서비스에 의존하므로 기본적인 요청 구조만 테스트합니다.
    """

    def test_recommend_missing_user_id(self, client: TestClient):
        """userId 누락 시 에러"""
        # Arrange
        request_data = {
            "contextId": "ctx-123",
        }

        # Act
        response = client.post("/api/cards/recommend", json=request_data)

        # Assert
        assert response.status_code == 422

    def test_recommend_missing_context_id(self, client: TestClient):
        """contextId 누락 시 에러"""
        # Arrange
        request_data = {
            "userId": "user-123",
        }

        # Act
        response = client.post("/api/cards/recommend", json=request_data)

        # Assert
        assert response.status_code == 422

    def test_recommend_invalid_user(self, client: TestClient):
        """존재하지 않는 사용자"""
        # Arrange
        # 먼저 컨텍스트 생성
        ctx_response = client.post(
            "/api/context",
            json={
                "userId": "non-existent-user",
                "place": "학교",
                "interactionPartner": "선생님",
            },
        )
        context_id = ctx_response.json()["data"]["contextId"]

        request_data = {
            "userId": "non-existent-user",
            "contextId": context_id,
        }

        # Act
        response = client.post("/api/cards/recommend", json=request_data)

        # Assert
        assert response.status_code == 404

    def test_recommend_invalid_context(self, client: TestClient):
        """존재하지 않는 컨텍스트"""
        # Arrange
        request_data = {
            "userId": "user-123",
            "contextId": "non-existent-context",
        }

        # Act
        response = client.post("/api/cards/recommend", json=request_data)

        # Assert
        assert response.status_code == 404
