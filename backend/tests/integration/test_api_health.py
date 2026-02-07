"""헬스체크 API 통합 테스트

GET /api/health 엔드포인트를 테스트합니다.
"""

import pytest
from fastapi.testclient import TestClient


class TestHealthAPI:
    """헬스체크 API 테스트"""

    def test_health_check_returns_200(self, client: TestClient):
        """헬스체크 성공 응답"""
        # Act
        response = client.get("/api/health")

        # Assert
        assert response.status_code == 200

    def test_health_check_response_structure(self, client: TestClient):
        """헬스체크 응답 구조 검증"""
        # Act
        response = client.get("/api/health")
        data = response.json()

        # Assert
        assert data["success"] is True
        assert "data" in data
        assert "message" in data
        assert "timestamp" in data

    def test_health_check_data_content(self, client: TestClient):
        """헬스체크 데이터 내용 검증"""
        # Act
        response = client.get("/api/health")
        data = response.json()["data"]

        # Assert
        assert data["status"] == "healthy"
        assert data["service"] == "AAC Interpreter Service"
        assert data["version"] == "2.0.0"

    def test_health_check_message(self, client: TestClient):
        """헬스체크 메시지 검증"""
        # Act
        response = client.get("/api/health")
        message = response.json()["message"]

        # Assert
        assert "정상" in message or "서비스" in message


class TestRootHealthCheck:
    """루트 레벨 헬스체크 테스트"""

    def test_root_health_check_returns_200(self, client: TestClient):
        """루트 헬스체크 성공"""
        # Act
        response = client.get("/health")

        # Assert
        assert response.status_code == 200

    def test_root_health_check_data(self, client: TestClient):
        """루트 헬스체크 데이터"""
        # Act
        response = client.get("/health")
        data = response.json()

        # Assert
        assert data["success"] is True
        assert data["data"]["status"] == "healthy"


class TestRootEndpoint:
    """루트 엔드포인트 테스트"""

    def test_root_returns_200(self, client: TestClient):
        """루트 엔드포인트 성공"""
        # Act
        response = client.get("/")

        # Assert
        assert response.status_code == 200

    def test_root_contains_service_info(self, client: TestClient):
        """루트 응답에 서비스 정보 포함"""
        # Act
        response = client.get("/")
        data = response.json()

        # Assert
        assert data["success"] is True
        assert data["data"]["service"] == "AAC Interpreter Service"
        assert data["data"]["version"] == "2.0.0"
        assert "docs" in data["data"]
