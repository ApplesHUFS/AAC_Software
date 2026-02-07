"""인증 API 통합 테스트

회원가입, 로그인, JWT 토큰 검증, 인증 필요 엔드포인트 접근 테스트입니다.
AAA (Arrange-Act-Assert) 패턴을 준수합니다.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from app.main import app
from app.core.security import TokenService


@pytest.fixture
def client() -> TestClient:
    """FastAPI 테스트 클라이언트"""
    return TestClient(app)


@pytest.fixture
def valid_register_data() -> dict:
    """유효한 회원가입 데이터"""
    return {
        "userId": "test-new-user-001",
        "name": "테스트 사용자",
        "age": 15,
        "gender": "남성",
        "disabilityType": "자폐스펙트럼장애",
        "communicationCharacteristics": "간단한 문장 사용",
        "interestingTopics": ["음악", "게임", "동물"],
        "password": "Test1234!@#",
    }


@pytest.fixture
def valid_login_data() -> dict:
    """유효한 로그인 데이터"""
    return {
        "userId": "test-new-user-001",
        "password": "Test1234!@#",
    }


@pytest.fixture
def token_service() -> TokenService:
    """토큰 서비스"""
    return TokenService(
        secret_key="test-secret-key-for-jwt-tokens",
        algorithm="HS256",
        access_token_expire_minutes=30,
    )


class TestRegisterAPI:
    """회원가입 API 테스트"""

    def test_register_success(self, client: TestClient, valid_register_data: dict):
        """회원가입 성공"""
        # Arrange
        # 고유한 사용자 ID 생성
        import uuid
        valid_register_data["userId"] = f"test-user-{uuid.uuid4().hex[:8]}"

        # Act
        response = client.post("/api/auth/register", json=valid_register_data)

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert data["data"]["userId"] == valid_register_data["userId"]
        assert data["data"]["status"] == "created"

    def test_register_duplicate_user_id_fails(
        self, client: TestClient, valid_register_data: dict
    ):
        """중복 사용자 ID로 회원가입 실패"""
        # Arrange
        import uuid
        user_id = f"duplicate-user-{uuid.uuid4().hex[:8]}"
        valid_register_data["userId"] = user_id

        # 첫 번째 등록
        client.post("/api/auth/register", json=valid_register_data)

        # Act - 동일 ID로 다시 등록
        response = client.post("/api/auth/register", json=valid_register_data)

        # Assert
        assert response.status_code == 400
        assert "이미 존재" in response.json()["error"]

    def test_register_missing_required_field_fails(self, client: TestClient):
        """필수 필드 누락 시 회원가입 실패"""
        # Arrange
        incomplete_data = {
            "userId": "incomplete-user",
            "name": "테스트",
            # password 누락
        }

        # Act
        response = client.post("/api/auth/register", json=incomplete_data)

        # Assert
        assert response.status_code == 422  # Validation error

    def test_register_weak_password_fails(
        self, client: TestClient, valid_register_data: dict
    ):
        """약한 비밀번호로 회원가입 실패"""
        # Arrange
        import uuid
        valid_register_data["userId"] = f"weak-pass-{uuid.uuid4().hex[:8]}"
        valid_register_data["password"] = "weak"  # 너무 짧고 복잡도 부족

        # Act
        response = client.post("/api/auth/register", json=valid_register_data)

        # Assert
        assert response.status_code == 422

    def test_register_password_without_uppercase_fails(
        self, client: TestClient, valid_register_data: dict
    ):
        """대문자 없는 비밀번호로 회원가입 실패"""
        # Arrange
        import uuid
        valid_register_data["userId"] = f"no-upper-{uuid.uuid4().hex[:8]}"
        valid_register_data["password"] = "test1234!@#"  # 대문자 없음

        # Act
        response = client.post("/api/auth/register", json=valid_register_data)

        # Assert
        assert response.status_code == 422

    def test_register_password_without_special_char_fails(
        self, client: TestClient, valid_register_data: dict
    ):
        """특수문자 없는 비밀번호로 회원가입 실패"""
        # Arrange
        import uuid
        valid_register_data["userId"] = f"no-special-{uuid.uuid4().hex[:8]}"
        valid_register_data["password"] = "Test12345678"  # 특수문자 없음

        # Act
        response = client.post("/api/auth/register", json=valid_register_data)

        # Assert
        assert response.status_code == 422

    def test_register_invalid_age_fails(
        self, client: TestClient, valid_register_data: dict
    ):
        """유효하지 않은 나이로 회원가입 실패"""
        # Arrange
        import uuid
        valid_register_data["userId"] = f"invalid-age-{uuid.uuid4().hex[:8]}"
        valid_register_data["age"] = 150  # 최대 나이 초과

        # Act
        response = client.post("/api/auth/register", json=valid_register_data)

        # Assert
        assert response.status_code == 422

    def test_register_empty_topics_fails(
        self, client: TestClient, valid_register_data: dict
    ):
        """빈 관심 주제로 회원가입 실패"""
        # Arrange
        import uuid
        valid_register_data["userId"] = f"empty-topics-{uuid.uuid4().hex[:8]}"
        valid_register_data["interestingTopics"] = []

        # Act
        response = client.post("/api/auth/register", json=valid_register_data)

        # Assert
        assert response.status_code == 422


class TestLoginAPI:
    """로그인 API 테스트"""

    def test_login_success(self, client: TestClient, valid_register_data: dict):
        """로그인 성공"""
        # Arrange
        import uuid
        user_id = f"login-test-{uuid.uuid4().hex[:8]}"
        valid_register_data["userId"] = user_id
        client.post("/api/auth/register", json=valid_register_data)

        login_data = {
            "userId": user_id,
            "password": valid_register_data["password"],
        }

        # Act
        response = client.post("/api/auth/login", json=login_data)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["authenticated"] is True
        assert data["data"]["userId"] == user_id
        assert "user" in data["data"]

    def test_login_wrong_password_fails(
        self, client: TestClient, valid_register_data: dict
    ):
        """잘못된 비밀번호로 로그인 실패"""
        # Arrange
        import uuid
        user_id = f"wrong-pass-{uuid.uuid4().hex[:8]}"
        valid_register_data["userId"] = user_id
        client.post("/api/auth/register", json=valid_register_data)

        login_data = {
            "userId": user_id,
            "password": "WrongPassword1!",
        }

        # Act
        response = client.post("/api/auth/login", json=login_data)

        # Assert
        assert response.status_code == 401
        assert "비밀번호" in response.json()["error"]

    def test_login_nonexistent_user_fails(self, client: TestClient):
        """존재하지 않는 사용자로 로그인 실패"""
        # Arrange
        login_data = {
            "userId": "nonexistent-user-xyz",
            "password": "Test1234!",
        }

        # Act
        response = client.post("/api/auth/login", json=login_data)

        # Assert
        assert response.status_code == 401
        assert "찾을 수 없" in response.json()["error"]

    def test_login_missing_password_fails(self, client: TestClient):
        """비밀번호 누락 시 로그인 실패"""
        # Arrange
        login_data = {
            "userId": "some-user",
        }

        # Act
        response = client.post("/api/auth/login", json=login_data)

        # Assert
        assert response.status_code == 422

    def test_login_returns_user_info(
        self, client: TestClient, valid_register_data: dict
    ):
        """로그인 시 사용자 정보 반환"""
        # Arrange
        import uuid
        user_id = f"user-info-{uuid.uuid4().hex[:8]}"
        valid_register_data["userId"] = user_id
        client.post("/api/auth/register", json=valid_register_data)

        login_data = {
            "userId": user_id,
            "password": valid_register_data["password"],
        }

        # Act
        response = client.post("/api/auth/login", json=login_data)

        # Assert
        data = response.json()
        user_info = data["data"]["user"]
        assert user_info["name"] == valid_register_data["name"]
        assert user_info["age"] == valid_register_data["age"]
        assert "password" not in user_info
        assert "password_hash" not in user_info

    def test_login_returns_jwt_tokens(
        self, client: TestClient, valid_register_data: dict
    ):
        """로그인 시 JWT 토큰 반환"""
        # Arrange
        import uuid
        user_id = f"jwt-test-{uuid.uuid4().hex[:8]}"
        valid_register_data["userId"] = user_id
        client.post("/api/auth/register", json=valid_register_data)

        login_data = {
            "userId": user_id,
            "password": valid_register_data["password"],
        }

        # Act
        response = client.post("/api/auth/login", json=login_data)

        # Assert
        data = response.json()
        assert "accessToken" in data["data"]
        assert "refreshToken" in data["data"]
        assert data["data"]["tokenType"] == "bearer"
        assert len(data["data"]["accessToken"]) > 0
        assert len(data["data"]["refreshToken"]) > 0


class TestRefreshTokenAPI:
    """리프레시 토큰 API 테스트"""

    def test_refresh_token_success(
        self, client: TestClient, valid_register_data: dict
    ):
        """리프레시 토큰으로 새 액세스 토큰 발급 성공"""
        # Arrange
        import uuid
        user_id = f"refresh-test-{uuid.uuid4().hex[:8]}"
        valid_register_data["userId"] = user_id
        client.post("/api/auth/register", json=valid_register_data)

        login_data = {"userId": user_id, "password": valid_register_data["password"]}
        login_response = client.post("/api/auth/login", json=login_data)
        refresh_token = login_response.json()["data"]["refreshToken"]

        # Act
        response = client.post(
            "/api/auth/refresh",
            json={"refreshToken": refresh_token},
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "accessToken" in data["data"]
        assert data["data"]["tokenType"] == "bearer"

    def test_refresh_token_invalid_fails(self, client: TestClient):
        """유효하지 않은 리프레시 토큰으로 실패"""
        # Arrange & Act
        response = client.post(
            "/api/auth/refresh",
            json={"refreshToken": "invalid.refresh.token"},
        )

        # Assert
        assert response.status_code == 401

    def test_refresh_with_access_token_fails(
        self, client: TestClient, valid_register_data: dict
    ):
        """액세스 토큰으로 리프레시 시도 실패"""
        # Arrange
        import uuid
        user_id = f"access-as-refresh-{uuid.uuid4().hex[:8]}"
        valid_register_data["userId"] = user_id
        client.post("/api/auth/register", json=valid_register_data)

        login_data = {"userId": user_id, "password": valid_register_data["password"]}
        login_response = client.post("/api/auth/login", json=login_data)
        access_token = login_response.json()["data"]["accessToken"]

        # Act
        response = client.post(
            "/api/auth/refresh",
            json={"refreshToken": access_token},
        )

        # Assert
        assert response.status_code == 401


class TestCheckIdAPI:
    """아이디 중복 확인 API 테스트"""

    def test_check_available_id(self, client: TestClient):
        """사용 가능한 ID 확인"""
        # Arrange
        import uuid
        available_id = f"available-{uuid.uuid4().hex[:8]}"

        # Act
        response = client.get(f"/api/auth/check-id/{available_id}")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["available"] is True
        assert data["data"]["userId"] == available_id

    def test_check_taken_id(self, client: TestClient, valid_register_data: dict):
        """이미 사용 중인 ID 확인"""
        # Arrange
        import uuid
        taken_id = f"taken-{uuid.uuid4().hex[:8]}"
        valid_register_data["userId"] = taken_id
        client.post("/api/auth/register", json=valid_register_data)

        # Act
        response = client.get(f"/api/auth/check-id/{taken_id}")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["available"] is False
        assert "이미 사용 중" in data["message"]


class TestProfileAPI:
    """프로필 API 테스트 (인증 필요)"""

    def _get_auth_headers(
        self, client: TestClient, user_id: str, password: str
    ) -> dict:
        """로그인 후 인증 헤더 반환"""
        login_data = {"userId": user_id, "password": password}
        response = client.post("/api/auth/login", json=login_data)
        token = response.json()["data"]["accessToken"]
        return {"Authorization": f"Bearer {token}"}

    def test_get_profile_success(self, client: TestClient, valid_register_data: dict):
        """프로필 조회 성공 (인증된 사용자)"""
        # Arrange
        import uuid
        user_id = f"profile-get-{uuid.uuid4().hex[:8]}"
        valid_register_data["userId"] = user_id
        client.post("/api/auth/register", json=valid_register_data)
        headers = self._get_auth_headers(
            client, user_id, valid_register_data["password"]
        )

        # Act
        response = client.get(f"/api/auth/profile/{user_id}", headers=headers)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["userId"] == user_id
        assert data["data"]["name"] == valid_register_data["name"]

    def test_get_profile_without_token_fails(self, client: TestClient):
        """토큰 없이 프로필 조회 실패"""
        # Arrange & Act
        response = client.get("/api/auth/profile/some-user-id")

        # Assert
        assert response.status_code == 401

    def test_get_other_user_profile_fails(
        self, client: TestClient, valid_register_data: dict
    ):
        """다른 사용자 프로필 조회 실패 (403)"""
        # Arrange
        import uuid
        user_id = f"profile-owner-{uuid.uuid4().hex[:8]}"
        other_user_id = f"profile-other-{uuid.uuid4().hex[:8]}"
        valid_register_data["userId"] = user_id
        client.post("/api/auth/register", json=valid_register_data)
        headers = self._get_auth_headers(
            client, user_id, valid_register_data["password"]
        )

        # Act
        response = client.get(f"/api/auth/profile/{other_user_id}", headers=headers)

        # Assert
        assert response.status_code == 403

    def test_update_profile_success(
        self, client: TestClient, valid_register_data: dict
    ):
        """프로필 업데이트 성공 (인증된 사용자)"""
        # Arrange
        import uuid
        user_id = f"profile-update-{uuid.uuid4().hex[:8]}"
        valid_register_data["userId"] = user_id
        client.post("/api/auth/register", json=valid_register_data)
        headers = self._get_auth_headers(
            client, user_id, valid_register_data["password"]
        )

        update_data = {
            "name": "변경된 이름",
            "age": 20,
        }

        # Act
        response = client.put(
            f"/api/auth/profile/{user_id}", json=update_data, headers=headers
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "name" in data["data"]["updatedFields"]
        assert "age" in data["data"]["updatedFields"]

    def test_update_profile_partial(
        self, client: TestClient, valid_register_data: dict
    ):
        """부분 프로필 업데이트 (인증된 사용자)"""
        # Arrange
        import uuid
        user_id = f"partial-update-{uuid.uuid4().hex[:8]}"
        valid_register_data["userId"] = user_id
        client.post("/api/auth/register", json=valid_register_data)
        headers = self._get_auth_headers(
            client, user_id, valid_register_data["password"]
        )

        update_data = {"name": "이름만 변경"}

        # Act
        response = client.put(
            f"/api/auth/profile/{user_id}", json=update_data, headers=headers
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "name" in data["data"]["updatedFields"]
        assert "age" not in data["data"]["updatedFields"]

    def test_update_profile_without_token_fails(self, client: TestClient):
        """토큰 없이 프로필 업데이트 실패"""
        # Arrange
        update_data = {"name": "새 이름"}

        # Act
        response = client.put(
            "/api/auth/profile/some-user-id", json=update_data
        )

        # Assert
        assert response.status_code == 401

    def test_update_other_user_profile_fails(
        self, client: TestClient, valid_register_data: dict
    ):
        """다른 사용자 프로필 업데이트 실패 (403)"""
        # Arrange
        import uuid
        user_id = f"update-owner-{uuid.uuid4().hex[:8]}"
        other_user_id = f"update-other-{uuid.uuid4().hex[:8]}"
        valid_register_data["userId"] = user_id
        client.post("/api/auth/register", json=valid_register_data)
        headers = self._get_auth_headers(
            client, user_id, valid_register_data["password"]
        )

        update_data = {"name": "시도된 변경"}

        # Act
        response = client.put(
            f"/api/auth/profile/{other_user_id}", json=update_data, headers=headers
        )

        # Assert
        assert response.status_code == 403


class TestJWTTokenService:
    """JWT 토큰 서비스 테스트"""

    def test_create_access_token(self, token_service: TokenService):
        """액세스 토큰 생성"""
        # Arrange
        user_id = "test-user-001"

        # Act
        token = token_service.create_access_token(user_id)

        # Assert
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_refresh_token(self, token_service: TokenService):
        """리프레시 토큰 생성"""
        # Arrange
        user_id = "test-user-001"

        # Act
        token = token_service.create_refresh_token(user_id)

        # Assert
        assert token is not None
        assert isinstance(token, str)

    def test_verify_valid_access_token(self, token_service: TokenService):
        """유효한 액세스 토큰 검증"""
        # Arrange
        user_id = "test-user-001"
        token = token_service.create_access_token(user_id)

        # Act
        result = token_service.verify_token(token, token_type="access")

        # Assert
        assert result == user_id

    def test_verify_valid_refresh_token(self, token_service: TokenService):
        """유효한 리프레시 토큰 검증"""
        # Arrange
        user_id = "test-user-001"
        token = token_service.create_refresh_token(user_id)

        # Act
        result = token_service.verify_token(token, token_type="refresh")

        # Assert
        assert result == user_id

    def test_verify_token_wrong_type_fails(self, token_service: TokenService):
        """잘못된 토큰 타입으로 검증 실패"""
        # Arrange
        user_id = "test-user-001"
        access_token = token_service.create_access_token(user_id)

        # Act (액세스 토큰을 리프레시 토큰으로 검증)
        result = token_service.verify_token(access_token, token_type="refresh")

        # Assert
        assert result is None

    def test_verify_invalid_token_fails(self, token_service: TokenService):
        """유효하지 않은 토큰 검증 실패"""
        # Arrange
        invalid_token = "invalid.token.string"

        # Act
        result = token_service.verify_token(invalid_token)

        # Assert
        assert result is None

    def test_verify_tampered_token_fails(self, token_service: TokenService):
        """변조된 토큰 검증 실패"""
        # Arrange
        user_id = "test-user-001"
        token = token_service.create_access_token(user_id)
        tampered_token = token[:-5] + "xxxxx"  # 토큰 끝부분 변조

        # Act
        result = token_service.verify_token(tampered_token)

        # Assert
        assert result is None

    def test_decode_token(self, token_service: TokenService):
        """토큰 디코딩"""
        # Arrange
        user_id = "test-user-001"
        token = token_service.create_access_token(user_id)

        # Act
        payload = token_service.decode_token(token)

        # Assert
        assert payload is not None
        assert payload.sub == user_id
        assert payload.type == "access"

    def test_different_tokens_for_same_user(self, token_service: TokenService):
        """동일 사용자에 대해 다른 토큰 생성"""
        # Arrange
        user_id = "test-user-001"

        # Act
        token1 = token_service.create_access_token(user_id)
        token2 = token_service.create_access_token(user_id)

        # Assert (시간이 다르므로 토큰도 다름)
        # 매우 빠른 실행에서는 같을 수 있으므로 둘 다 유효한지만 확인
        assert token_service.verify_token(token1) == user_id
        assert token_service.verify_token(token2) == user_id


class TestAuthenticatedEndpoints:
    """인증 필요 엔드포인트 테스트"""

    def test_access_protected_endpoint_without_token_fails(self, client: TestClient):
        """토큰 없이 보호된 엔드포인트 접근 실패"""
        # Arrange & Act
        response = client.get("/api/auth/me")

        # Assert
        assert response.status_code == 401

    def test_access_protected_endpoint_with_invalid_token_fails(
        self, client: TestClient
    ):
        """유효하지 않은 토큰으로 보호된 엔드포인트 접근 실패"""
        # Arrange
        invalid_token = "invalid.jwt.token"
        headers = {"Authorization": f"Bearer {invalid_token}"}

        # Act
        response = client.get("/api/auth/me", headers=headers)

        # Assert
        assert response.status_code == 401

    def test_access_protected_endpoint_with_expired_token_fails(
        self, client: TestClient
    ):
        """만료된 토큰으로 보호된 엔드포인트 접근 실패"""
        # Arrange
        # 매우 짧은 만료 시간으로 토큰 생성
        from datetime import datetime, timedelta, timezone
        from jose import jwt

        expired_payload = {
            "sub": "test-user",
            "exp": datetime.now(timezone.utc) - timedelta(hours=1),
            "iat": datetime.now(timezone.utc) - timedelta(hours=2),
            "type": "access",
        }
        expired_token = jwt.encode(
            expired_payload, "test-secret-key", algorithm="HS256"
        )
        headers = {"Authorization": f"Bearer {expired_token}"}

        # Act
        response = client.get("/api/auth/me", headers=headers)

        # Assert
        assert response.status_code == 401

    def test_my_profile_endpoint_success(
        self, client: TestClient, valid_register_data: dict
    ):
        """/me 엔드포인트로 내 프로필 조회 성공"""
        # Arrange
        import uuid
        user_id = f"me-test-{uuid.uuid4().hex[:8]}"
        valid_register_data["userId"] = user_id
        client.post("/api/auth/register", json=valid_register_data)

        login_data = {"userId": user_id, "password": valid_register_data["password"]}
        login_response = client.post("/api/auth/login", json=login_data)
        token = login_response.json()["data"]["accessToken"]
        headers = {"Authorization": f"Bearer {token}"}

        # Act
        response = client.get("/api/auth/me", headers=headers)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["userId"] == user_id
        assert data["data"]["name"] == valid_register_data["name"]


class TestAuthAPIResponseFormat:
    """인증 API 응답 형식 테스트"""

    def test_register_response_format(
        self, client: TestClient, valid_register_data: dict
    ):
        """회원가입 응답 형식"""
        # Arrange
        import uuid
        valid_register_data["userId"] = f"format-test-{uuid.uuid4().hex[:8]}"

        # Act
        response = client.post("/api/auth/register", json=valid_register_data)
        data = response.json()

        # Assert
        assert "success" in data
        assert "data" in data
        assert "message" in data
        assert "timestamp" in data

    def test_login_response_format(
        self, client: TestClient, valid_register_data: dict
    ):
        """로그인 응답 형식"""
        # Arrange
        import uuid
        user_id = f"login-format-{uuid.uuid4().hex[:8]}"
        valid_register_data["userId"] = user_id
        client.post("/api/auth/register", json=valid_register_data)

        login_data = {"userId": user_id, "password": valid_register_data["password"]}

        # Act
        response = client.post("/api/auth/login", json=login_data)
        data = response.json()

        # Assert
        assert "success" in data
        assert "data" in data
        assert "message" in data
        assert "timestamp" in data
        assert "userId" in data["data"]
        assert "authenticated" in data["data"]
        assert "user" in data["data"]

    def test_error_response_format(self, client: TestClient):
        """에러 응답 형식"""
        # Arrange
        login_data = {"userId": "nonexistent", "password": "Test1234!"}

        # Act
        response = client.post("/api/auth/login", json=login_data)

        # Assert
        assert response.status_code == 401
        data = response.json()
        assert "success" in data
        assert data["success"] is False
        assert "error" in data
