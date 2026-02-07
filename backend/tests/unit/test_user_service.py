"""UserService 유닛 테스트

회원가입, 로그인, 프로필 조회/수정 등 사용자 관련 비즈니스 로직을 테스트합니다.
AAA (Arrange-Act-Assert) 패턴을 준수합니다.
"""

from datetime import datetime
from typing import Optional
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.config.settings import Settings
from app.domain.user.entity import User
from app.domain.user.repository import UserRepository
from app.domain.user.service import (
    UserService,
    RegisterResult,
    AuthResult,
    GetUserResult,
    UpdateResult,
)


class MockUserRepository(UserRepository):
    """테스트용 사용자 저장소"""

    def __init__(self):
        self._storage: dict[str, User] = {}

    async def find_by_id(self, user_id: str) -> Optional[User]:
        return self._storage.get(user_id)

    async def exists(self, user_id: str) -> bool:
        return user_id in self._storage

    async def save(self, user: User) -> None:
        self._storage[user.user_id] = user

    async def update(self, user: User) -> None:
        self._storage[user.user_id] = user


@pytest.fixture
def mock_repo() -> MockUserRepository:
    """Mock 사용자 저장소"""
    return MockUserRepository()


@pytest.fixture
def test_settings() -> Settings:
    """테스트용 설정"""
    return Settings(
        openai_api_key="test-api-key",
        debug=True,
        valid_genders=["남성", "여성"],
        valid_disability_types=["의사소통장애", "자폐스펙트럼장애", "지적장애"],
        min_age=1,
        max_age=100,
    )


@pytest.fixture
def user_service(mock_repo: MockUserRepository, test_settings: Settings) -> UserService:
    """UserService 인스턴스"""
    return UserService(mock_repo, test_settings)


@pytest.fixture
def existing_user() -> User:
    """기존 사용자"""
    return User(
        user_id="existing-user",
        name="기존 사용자",
        age=25,
        gender="남성",
        disability_type="자폐스펙트럼장애",
        communication_characteristics="간단한 문장 사용",
        interesting_topics=["음악", "게임"],
        password_hash=User.hash_password("Test1234!"),
    )


class TestUserServiceRegister:
    """회원가입 테스트"""

    @pytest.mark.asyncio
    async def test_register_user_success(
        self, user_service: UserService, mock_repo: MockUserRepository
    ):
        """회원가입 성공"""
        # Arrange
        user_id = "new-user-001"
        name = "새 사용자"
        age = 15
        gender = "남성"
        disability_type = "자폐스펙트럼장애"
        communication = "짧은 문장 사용"
        topics = ["동물", "음식"]
        password = "Test1234!"

        # Act
        result = await user_service.register_user(
            user_id=user_id,
            name=name,
            age=age,
            gender=gender,
            disability_type=disability_type,
            communication_characteristics=communication,
            interesting_topics=topics,
            password=password,
        )

        # Assert
        assert result.success is True
        assert result.user_id == user_id
        assert "성공" in result.message

        # 저장소에 사용자가 저장되었는지 확인
        saved_user = await mock_repo.find_by_id(user_id)
        assert saved_user is not None
        assert saved_user.name == name
        assert saved_user.age == age

    @pytest.mark.asyncio
    async def test_register_duplicate_user_id_fails(
        self, user_service: UserService, mock_repo: MockUserRepository, existing_user: User
    ):
        """중복 ID로 회원가입 실패"""
        # Arrange
        await mock_repo.save(existing_user)

        # Act
        result = await user_service.register_user(
            user_id=existing_user.user_id,
            name="다른 사용자",
            age=20,
            gender="여성",
            disability_type="지적장애",
            communication_characteristics="단어 사용",
            interesting_topics=["놀이"],
            password="Test1234!",
        )

        # Assert
        assert result.success is False
        assert "이미 존재" in result.message

    @pytest.mark.asyncio
    async def test_register_invalid_age_fails(self, user_service: UserService):
        """유효하지 않은 나이로 회원가입 실패"""
        # Arrange & Act
        result = await user_service.register_user(
            user_id="invalid-age-user",
            name="테스트",
            age=150,  # 최대 나이 초과
            gender="남성",
            disability_type="자폐스펙트럼장애",
            communication_characteristics="문장 사용",
            interesting_topics=["음악"],
            password="Test1234!",
        )

        # Assert
        assert result.success is False
        assert "나이" in result.message

    @pytest.mark.asyncio
    async def test_register_invalid_gender_fails(self, user_service: UserService):
        """유효하지 않은 성별로 회원가입 실패"""
        # Arrange & Act
        result = await user_service.register_user(
            user_id="invalid-gender-user",
            name="테스트",
            age=20,
            gender="기타",  # 유효하지 않은 성별
            disability_type="자폐스펙트럼장애",
            communication_characteristics="문장 사용",
            interesting_topics=["음악"],
            password="Test1234!",
        )

        # Assert
        assert result.success is False
        assert "성별" in result.message

    @pytest.mark.asyncio
    async def test_register_invalid_disability_type_fails(self, user_service: UserService):
        """유효하지 않은 장애 유형으로 회원가입 실패"""
        # Arrange & Act
        result = await user_service.register_user(
            user_id="invalid-disability-user",
            name="테스트",
            age=20,
            gender="남성",
            disability_type="알 수 없는 장애",  # 유효하지 않은 장애 유형
            communication_characteristics="문장 사용",
            interesting_topics=["음악"],
            password="Test1234!",
        )

        # Assert
        assert result.success is False
        assert "장애 유형" in result.message

    @pytest.mark.asyncio
    async def test_register_empty_topics_fails(self, user_service: UserService):
        """빈 관심 주제로 회원가입 실패"""
        # Arrange & Act
        result = await user_service.register_user(
            user_id="empty-topics-user",
            name="테스트",
            age=20,
            gender="남성",
            disability_type="자폐스펙트럼장애",
            communication_characteristics="문장 사용",
            interesting_topics=[],  # 빈 관심 주제
            password="Test1234!",
        )

        # Assert
        assert result.success is False
        assert "관심 주제" in result.message

    @pytest.mark.asyncio
    async def test_register_too_many_topics_fails(self, user_service: UserService):
        """너무 많은 관심 주제로 회원가입 실패"""
        # Arrange
        too_many_topics = [f"주제{i}" for i in range(15)]  # 10개 초과

        # Act
        result = await user_service.register_user(
            user_id="many-topics-user",
            name="테스트",
            age=20,
            gender="남성",
            disability_type="자폐스펙트럼장애",
            communication_characteristics="문장 사용",
            interesting_topics=too_many_topics,
            password="Test1234!",
        )

        # Assert
        assert result.success is False
        assert "관심 주제" in result.message


class TestUserServiceAuthenticate:
    """로그인/인증 테스트"""

    @pytest.mark.asyncio
    async def test_authenticate_success(
        self, user_service: UserService, mock_repo: MockUserRepository, existing_user: User
    ):
        """로그인 성공"""
        # Arrange
        await mock_repo.save(existing_user)

        # Act
        result = await user_service.authenticate_user(
            user_id=existing_user.user_id,
            password="Test1234!",
        )

        # Assert
        assert result.authenticated is True
        assert result.user_info is not None
        assert result.user_info["name"] == existing_user.name
        assert "성공" in result.message

    @pytest.mark.asyncio
    async def test_authenticate_wrong_password_fails(
        self, user_service: UserService, mock_repo: MockUserRepository, existing_user: User
    ):
        """잘못된 비밀번호로 로그인 실패"""
        # Arrange
        await mock_repo.save(existing_user)

        # Act
        result = await user_service.authenticate_user(
            user_id=existing_user.user_id,
            password="WrongPassword1!",
        )

        # Assert
        assert result.authenticated is False
        assert result.user_info is None
        assert "비밀번호" in result.message

    @pytest.mark.asyncio
    async def test_authenticate_nonexistent_user_fails(self, user_service: UserService):
        """존재하지 않는 사용자 로그인 실패"""
        # Arrange & Act
        result = await user_service.authenticate_user(
            user_id="nonexistent-user",
            password="Test1234!",
        )

        # Assert
        assert result.authenticated is False
        assert result.user_info is None
        assert "찾을 수 없" in result.message


class TestUserServiceGetUserInfo:
    """프로필 조회 테스트"""

    @pytest.mark.asyncio
    async def test_get_user_info_success(
        self, user_service: UserService, mock_repo: MockUserRepository, existing_user: User
    ):
        """프로필 조회 성공"""
        # Arrange
        await mock_repo.save(existing_user)

        # Act
        result = await user_service.get_user_info(existing_user.user_id)

        # Assert
        assert result.success is True
        assert result.user is not None
        assert result.user["name"] == existing_user.name
        assert result.user["age"] == existing_user.age
        # 비밀번호가 응답에 포함되지 않아야 함
        assert "password" not in result.user
        assert "password_hash" not in result.user

    @pytest.mark.asyncio
    async def test_get_user_info_not_found(self, user_service: UserService):
        """존재하지 않는 사용자 프로필 조회"""
        # Arrange & Act
        result = await user_service.get_user_info("nonexistent-user")

        # Assert
        assert result.success is False
        assert result.user is None
        assert "찾을 수 없" in result.message


class TestUserServiceCheckUserExists:
    """아이디 중복 확인 테스트"""

    @pytest.mark.asyncio
    async def test_check_existing_user_returns_true(
        self, user_service: UserService, mock_repo: MockUserRepository, existing_user: User
    ):
        """존재하는 사용자 ID 확인"""
        # Arrange
        await mock_repo.save(existing_user)

        # Act
        exists = await user_service.check_user_exists(existing_user.user_id)

        # Assert
        assert exists is True

    @pytest.mark.asyncio
    async def test_check_nonexistent_user_returns_false(self, user_service: UserService):
        """존재하지 않는 사용자 ID 확인"""
        # Arrange & Act
        exists = await user_service.check_user_exists("nonexistent-user")

        # Assert
        assert exists is False


class TestUserServiceUpdatePersona:
    """프로필 업데이트 테스트"""

    @pytest.mark.asyncio
    async def test_update_persona_success(
        self, user_service: UserService, mock_repo: MockUserRepository, existing_user: User
    ):
        """프로필 업데이트 성공"""
        # Arrange
        await mock_repo.save(existing_user)
        updates = {
            "name": "변경된 이름",
            "age": 30,
            "interestingTopics": ["새로운 주제"],
        }

        # Act
        result = await user_service.update_user_persona(existing_user.user_id, updates)

        # Assert
        assert result.success is True
        assert "name" in result.updated_fields
        assert "age" in result.updated_fields
        assert "interestingTopics" in result.updated_fields

        # 실제 업데이트 확인
        updated_user = await mock_repo.find_by_id(existing_user.user_id)
        assert updated_user.name == "변경된 이름"
        assert updated_user.age == 30
        assert updated_user.interesting_topics == ["새로운 주제"]

    @pytest.mark.asyncio
    async def test_update_persona_partial_update(
        self, user_service: UserService, mock_repo: MockUserRepository, existing_user: User
    ):
        """부분 업데이트 성공"""
        # Arrange
        await mock_repo.save(existing_user)
        original_age = existing_user.age
        updates = {"name": "부분 변경"}

        # Act
        result = await user_service.update_user_persona(existing_user.user_id, updates)

        # Assert
        assert result.success is True
        assert "name" in result.updated_fields
        assert "age" not in result.updated_fields

        updated_user = await mock_repo.find_by_id(existing_user.user_id)
        assert updated_user.name == "부분 변경"
        assert updated_user.age == original_age  # 변경되지 않음

    @pytest.mark.asyncio
    async def test_update_persona_nonexistent_user_fails(self, user_service: UserService):
        """존재하지 않는 사용자 프로필 업데이트 실패"""
        # Arrange
        updates = {"name": "새 이름"}

        # Act
        result = await user_service.update_user_persona("nonexistent-user", updates)

        # Assert
        assert result.success is False
        assert len(result.updated_fields) == 0
        assert "찾을 수 없" in result.message

    @pytest.mark.asyncio
    async def test_update_persona_with_camel_case_keys(
        self, user_service: UserService, mock_repo: MockUserRepository, existing_user: User
    ):
        """camelCase 키로 업데이트"""
        # Arrange
        await mock_repo.save(existing_user)
        updates = {
            "disabilityType": "지적장애",
            "communicationCharacteristics": "긴 문장 사용",
        }

        # Act
        result = await user_service.update_user_persona(existing_user.user_id, updates)

        # Assert
        assert result.success is True

        updated_user = await mock_repo.find_by_id(existing_user.user_id)
        assert updated_user.disability_type == "지적장애"
        assert updated_user.communication_characteristics == "긴 문장 사용"

    @pytest.mark.asyncio
    async def test_update_persona_with_snake_case_keys(
        self, user_service: UserService, mock_repo: MockUserRepository, existing_user: User
    ):
        """snake_case 키로 업데이트"""
        # Arrange
        await mock_repo.save(existing_user)
        updates = {
            "disability_type": "의사소통장애",
            "communication_characteristics": "제스처 사용",
        }

        # Act
        result = await user_service.update_user_persona(existing_user.user_id, updates)

        # Assert
        assert result.success is True

        updated_user = await mock_repo.find_by_id(existing_user.user_id)
        assert updated_user.disability_type == "의사소통장애"
        assert updated_user.communication_characteristics == "제스처 사용"

    @pytest.mark.asyncio
    async def test_update_persona_updates_timestamp(
        self, user_service: UserService, mock_repo: MockUserRepository, existing_user: User
    ):
        """업데이트 시 타임스탬프 갱신"""
        # Arrange
        await mock_repo.save(existing_user)
        original_updated_at = existing_user.updated_at
        updates = {"name": "타임스탬프 테스트"}

        # Act
        result = await user_service.update_user_persona(existing_user.user_id, updates)

        # Assert
        assert result.success is True
        updated_user = await mock_repo.find_by_id(existing_user.user_id)
        assert updated_user.updated_at >= original_updated_at


class TestUserServiceGetUser:
    """사용자 엔티티 조회 테스트"""

    @pytest.mark.asyncio
    async def test_get_user_returns_entity(
        self, user_service: UserService, mock_repo: MockUserRepository, existing_user: User
    ):
        """사용자 엔티티 반환"""
        # Arrange
        await mock_repo.save(existing_user)

        # Act
        user = await user_service.get_user(existing_user.user_id)

        # Assert
        assert user is not None
        assert isinstance(user, User)
        assert user.user_id == existing_user.user_id

    @pytest.mark.asyncio
    async def test_get_user_returns_none_for_nonexistent(self, user_service: UserService):
        """존재하지 않는 사용자는 None 반환"""
        # Arrange & Act
        user = await user_service.get_user("nonexistent-user")

        # Assert
        assert user is None


class TestUserServiceEdgeCases:
    """엣지 케이스 테스트"""

    @pytest.mark.asyncio
    async def test_register_with_boundary_age_min(self, user_service: UserService):
        """최소 나이 경계값 테스트"""
        # Arrange & Act
        result = await user_service.register_user(
            user_id="min-age-user",
            name="최소 나이",
            age=1,  # 최소 나이
            gender="남성",
            disability_type="자폐스펙트럼장애",
            communication_characteristics="비언어적",
            interesting_topics=["동물"],
            password="Test1234!",
        )

        # Assert
        assert result.success is True

    @pytest.mark.asyncio
    async def test_register_with_boundary_age_max(self, user_service: UserService):
        """최대 나이 경계값 테스트"""
        # Arrange & Act
        result = await user_service.register_user(
            user_id="max-age-user",
            name="최대 나이",
            age=100,  # 최대 나이
            gender="여성",
            disability_type="지적장애",
            communication_characteristics="문장 사용",
            interesting_topics=["음악"],
            password="Test1234!",
        )

        # Assert
        assert result.success is True

    @pytest.mark.asyncio
    async def test_register_with_zero_age_fails(self, user_service: UserService):
        """0세 나이 실패"""
        # Arrange & Act
        result = await user_service.register_user(
            user_id="zero-age-user",
            name="제로 나이",
            age=0,  # 최소 나이 미만
            gender="남성",
            disability_type="자폐스펙트럼장애",
            communication_characteristics="비언어적",
            interesting_topics=["동물"],
            password="Test1234!",
        )

        # Assert
        assert result.success is False

    @pytest.mark.asyncio
    async def test_password_verification_with_special_characters(
        self, user_service: UserService, mock_repo: MockUserRepository
    ):
        """특수문자 포함 비밀번호 검증"""
        # Arrange
        special_password = "Test!@#$%^&*()1234"
        await user_service.register_user(
            user_id="special-pass-user",
            name="특수문자 사용자",
            age=25,
            gender="남성",
            disability_type="의사소통장애",
            communication_characteristics="문장 사용",
            interesting_topics=["게임"],
            password=special_password,
        )

        # Act
        result = await user_service.authenticate_user(
            user_id="special-pass-user",
            password=special_password,
        )

        # Assert
        assert result.authenticated is True

    @pytest.mark.asyncio
    async def test_password_verification_with_unicode(
        self, user_service: UserService, mock_repo: MockUserRepository
    ):
        """유니코드 포함 비밀번호 검증"""
        # Arrange
        unicode_password = "Test한글1234!"
        await user_service.register_user(
            user_id="unicode-pass-user",
            name="유니코드 사용자",
            age=25,
            gender="여성",
            disability_type="지적장애",
            communication_characteristics="단어 사용",
            interesting_topics=["음악"],
            password=unicode_password,
        )

        # Act
        result = await user_service.authenticate_user(
            user_id="unicode-pass-user",
            password=unicode_password,
        )

        # Assert
        assert result.authenticated is True
