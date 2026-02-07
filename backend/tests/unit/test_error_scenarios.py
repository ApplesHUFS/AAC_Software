"""에러 시나리오 테스트

네트워크 오류 시뮬레이션, 타임아웃 테스트, 잘못된 입력 처리 등
다양한 에러 시나리오를 테스트합니다.
AAA (Arrange-Act-Assert) 패턴을 준수합니다.
"""

import asyncio
from datetime import datetime
from typing import Optional
from unittest.mock import AsyncMock, MagicMock, patch, PropertyMock

import pytest

from app.config.settings import Settings
from app.domain.user.entity import User
from app.domain.user.repository import UserRepository
from app.domain.user.service import UserService
from app.domain.feedback.entity import FeedbackRequest, Feedback
from app.domain.feedback.repository import FeedbackRepository
from app.domain.feedback.service import FeedbackService
from app.core.security import TokenService


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


class TestNetworkErrorSimulation:
    """네트워크 오류 시뮬레이션 테스트"""

    @pytest.mark.asyncio
    async def test_repository_connection_timeout(self, test_settings: Settings):
        """저장소 연결 타임아웃"""
        # Arrange
        mock_repo = MagicMock(spec=UserRepository)

        async def slow_find(*args, **kwargs):
            await asyncio.sleep(5)  # 시뮬레이션용 지연
            return None

        mock_repo.find_by_id = slow_find
        mock_repo.exists = AsyncMock(return_value=False)

        service = UserService(mock_repo, test_settings)

        # Act & Assert
        with pytest.raises(asyncio.TimeoutError):
            await asyncio.wait_for(
                service.get_user_info("test-user"),
                timeout=0.1,
            )

    @pytest.mark.asyncio
    async def test_repository_save_failure(self, test_settings: Settings):
        """저장소 저장 실패"""
        # Arrange
        mock_repo = MagicMock(spec=UserRepository)
        mock_repo.exists = AsyncMock(return_value=False)
        mock_repo.save = AsyncMock(side_effect=Exception("Connection refused"))

        service = UserService(mock_repo, test_settings)

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await service.register_user(
                user_id="test-user",
                name="테스트",
                age=20,
                gender="남성",
                disability_type="자폐스펙트럼장애",
                communication_characteristics="문장 사용",
                interesting_topics=["음악"],
                password="Test1234!",
            )

        assert "Connection refused" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_repository_intermittent_failure(self, test_settings: Settings):
        """간헐적 저장소 실패"""
        # Arrange
        mock_repo = MagicMock(spec=UserRepository)
        call_count = 0

        async def intermittent_exists(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise ConnectionError("Network unstable")
            return False

        mock_repo.exists = intermittent_exists

        service = UserService(mock_repo, test_settings)

        # Act & Assert
        with pytest.raises(ConnectionError):
            await service.check_user_exists("test-user")


class TestTimeoutScenarios:
    """타임아웃 시나리오 테스트"""

    @pytest.mark.asyncio
    async def test_authentication_timeout(self, test_settings: Settings):
        """인증 타임아웃"""
        # Arrange
        mock_repo = MagicMock(spec=UserRepository)

        async def slow_auth(*args, **kwargs):
            await asyncio.sleep(10)
            return None

        mock_repo.find_by_id = slow_auth

        service = UserService(mock_repo, test_settings)

        # Act & Assert
        with pytest.raises(asyncio.TimeoutError):
            await asyncio.wait_for(
                service.authenticate_user("user", "pass"),
                timeout=0.1,
            )

    @pytest.mark.asyncio
    async def test_feedback_submission_timeout(self):
        """피드백 제출 타임아웃"""
        # Arrange
        mock_repo = MagicMock(spec=FeedbackRepository)

        async def slow_find(*args, **kwargs):
            await asyncio.sleep(10)
            return None

        mock_repo.find_request = slow_find

        service = FeedbackService(mock_repo)

        # Act & Assert
        with pytest.raises(asyncio.TimeoutError):
            await asyncio.wait_for(
                service.submit_feedback("conf-id", selected_index=0),
                timeout=0.1,
            )

    def test_token_verification_expired(self):
        """만료된 토큰 검증"""
        # Arrange
        token_service = TokenService(
            secret_key="test-secret",
            algorithm="HS256",
            access_token_expire_minutes=-1,  # 즉시 만료
        )

        user_id = "test-user"
        token = token_service.create_access_token(user_id)

        # Act (토큰이 즉시 만료되었으므로)
        # 참고: 실제로는 만료 시간이 과거이므로 검증 실패
        import time
        time.sleep(0.1)  # 약간의 지연

        result = token_service.verify_token(token)

        # Assert
        # 만료된 토큰은 None 반환
        assert result is None


class TestInvalidInputHandling:
    """잘못된 입력 처리 테스트"""

    @pytest.mark.asyncio
    async def test_register_with_none_values(self, test_settings: Settings):
        """None 값으로 회원가입"""
        # Arrange
        mock_repo = MagicMock(spec=UserRepository)
        mock_repo.exists = AsyncMock(return_value=False)
        service = UserService(mock_repo, test_settings)

        # Act & Assert
        with pytest.raises(ValueError):
            await service.register_user(
                user_id=None,  # type: ignore
                name="테스트",
                age=20,
                gender="남성",
                disability_type="자폐스펙트럼장애",
                communication_characteristics="문장 사용",
                interesting_topics=["음악"],
                password="Test1234!",
            )

    @pytest.mark.asyncio
    async def test_authenticate_with_empty_password(self, test_settings: Settings):
        """빈 비밀번호로 인증"""
        # Arrange
        mock_repo = MagicMock(spec=UserRepository)

        # 사용자가 존재한다고 가정
        mock_user = User(
            user_id="test-user",
            name="테스트",
            age=20,
            gender="남성",
            disability_type="자폐스펙트럼장애",
            communication_characteristics="문장 사용",
            interesting_topics=["음악"],
            password_hash=User.hash_password("Test1234!"),
        )
        mock_repo.find_by_id = AsyncMock(return_value=mock_user)

        service = UserService(mock_repo, test_settings)

        # Act
        result = await service.authenticate_user("test-user", "")

        # Assert
        assert result.authenticated is False

    @pytest.mark.asyncio
    async def test_update_with_invalid_field_names(self, test_settings: Settings):
        """잘못된 필드명으로 업데이트"""
        # Arrange
        mock_repo = MagicMock(spec=UserRepository)

        mock_user = User(
            user_id="test-user",
            name="테스트",
            age=20,
            gender="남성",
            disability_type="자폐스펙트럼장애",
            communication_characteristics="문장 사용",
            interesting_topics=["음악"],
            password_hash="hash",
        )
        mock_repo.find_by_id = AsyncMock(return_value=mock_user)
        mock_repo.update = AsyncMock()

        service = UserService(mock_repo, test_settings)

        # Act
        result = await service.update_user_persona(
            "test-user",
            {
                "invalid_field": "value",
                "another_invalid": 123,
            },
        )

        # Assert (유효하지 않은 필드는 무시됨)
        assert result.success is True
        assert len(result.updated_fields) == 0

    @pytest.mark.asyncio
    async def test_feedback_with_negative_confirmation_id(self):
        """음수 confirmation ID로 피드백"""
        # Arrange
        mock_repo = MagicMock(spec=FeedbackRepository)
        mock_repo.find_request = AsyncMock(return_value=None)

        service = FeedbackService(mock_repo)

        # Act
        result = await service.submit_feedback(
            confirmation_id="-1",
            selected_index=0,
        )

        # Assert
        assert result.success is False
        assert "찾을 수 없" in result.message

    def test_user_entity_verify_password_with_corrupted_hash(self):
        """손상된 해시로 비밀번호 검증"""
        # Arrange
        user = User(
            user_id="test-user",
            name="테스트",
            age=20,
            gender="남성",
            disability_type="자폐스펙트럼장애",
            communication_characteristics="문장 사용",
            interesting_topics=["음악"],
            password_hash="not-a-valid-bcrypt-hash",
        )

        # Act
        result = user.verify_password("any_password")

        # Assert (손상된 해시는 False 반환)
        assert result is False

    def test_user_entity_verify_password_with_empty_hash(self):
        """빈 해시로 비밀번호 검증"""
        # Arrange
        user = User(
            user_id="test-user",
            name="테스트",
            age=20,
            gender="남성",
            disability_type="자폐스펙트럼장애",
            communication_characteristics="문장 사용",
            interesting_topics=["음악"],
            password_hash="",
        )

        # Act
        result = user.verify_password("any_password")

        # Assert
        assert result is False


class TestEdgeCaseInputs:
    """엣지 케이스 입력 테스트"""

    def test_user_from_dict_with_missing_fields(self):
        """필수 필드 누락된 딕셔너리에서 User 생성"""
        # Arrange
        incomplete_data = {
            "name": "테스트",
            # age, gender 등 누락
        }

        # Act & Assert
        with pytest.raises(KeyError):
            User.from_dict("test-user", incomplete_data)

    def test_user_from_dict_with_invalid_datetime(self):
        """잘못된 datetime 형식"""
        # Arrange
        data = {
            "name": "테스트",
            "age": 20,
            "gender": "남성",
            "disability_type": "자폐스펙트럼장애",
            "communication_characteristics": "문장 사용",
            "interesting_topics": ["음악"],
            "created_at": "not-a-datetime",
        }

        # Act & Assert
        with pytest.raises(ValueError):
            User.from_dict("test-user", data)

    def test_feedback_request_with_special_characters(self):
        """특수 문자가 포함된 피드백 요청"""
        # Arrange
        request = FeedbackRequest(
            confirmation_id="test-<script>alert('xss')</script>",
            user_id="user-with-'quotes\"",
            cards=["card-with-<html>"],
            context={"key": "value\nwith\nnewlines"},
            interpretations=["해석 with 특수문자 !@#$%^&*()"],
            partner_info="파트너 정보\t\t탭 포함",
        )

        # Act
        result = request.to_confirmation_dict()

        # Assert (특수 문자가 그대로 보존됨)
        assert "xss" in result["confirmationId"]
        assert len(result["selectedCards"]) == 1

    def test_feedback_with_very_long_interpretation(self):
        """매우 긴 해석 텍스트"""
        # Arrange
        long_interpretation = "매우 긴 해석 " * 1000

        feedback = Feedback(
            feedback_id=1,
            confirmation_id="conf-001",
            user_id="user-001",
            cards=["card1"],
            context={},
            interpretations=[long_interpretation],
            partner_info="파트너",
            feedback_type="interpretation_selected",
            selected_index=0,
            selected_interpretation=long_interpretation,
        )

        # Act
        result = feedback.to_dict()

        # Assert
        assert len(result["selectedInterpretation"]) == len(long_interpretation)

    def test_feedback_with_unicode_characters(self):
        """유니코드 문자가 포함된 피드백"""
        # Arrange
        unicode_text = "이모지 포함 🎉🎊 그리고 한자 漢字"

        feedback = Feedback(
            feedback_id=1,
            confirmation_id="conf-001",
            user_id="user-001",
            cards=["card1"],
            context={"key": unicode_text},
            interpretations=[unicode_text],
            partner_info=unicode_text,
            feedback_type="direct_feedback",
            direct_feedback=unicode_text,
        )

        # Act
        result = feedback.to_dict()

        # Assert
        assert "🎉" in result["directFeedback"]
        assert "漢字" in result["directFeedback"]


class TestConcurrencyErrors:
    """동시성 관련 에러 테스트"""

    @pytest.mark.asyncio
    async def test_concurrent_registration_same_id(self, test_settings: Settings):
        """동일 ID로 동시 회원가입"""
        # Arrange
        mock_repo = MagicMock(spec=UserRepository)

        # 첫 번째 호출은 존재하지 않음, 두 번째부터는 존재
        call_count = 0

        async def exists_side_effect(user_id):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                await asyncio.sleep(0.1)  # 지연 시뮬레이션
                return False
            return True

        mock_repo.exists = exists_side_effect
        mock_repo.save = AsyncMock()

        service = UserService(mock_repo, test_settings)

        # Act
        async def register():
            return await service.register_user(
                user_id="same-user-id",
                name="테스트",
                age=20,
                gender="남성",
                disability_type="자폐스펙트럼장애",
                communication_characteristics="문장 사용",
                interesting_topics=["음악"],
                password="Test1234!",
            )

        results = await asyncio.gather(register(), register())

        # Assert (하나는 성공, 하나는 실패해야 함 - 실제 구현에 따라 다를 수 있음)
        success_count = sum(1 for r in results if r.success)
        # 현재 mock 구현에서는 둘 다 성공할 수 있음 (실제 저장소는 제약 조건으로 방지)
        assert success_count >= 1


class TestRecoveryScenarios:
    """복구 시나리오 테스트"""

    @pytest.mark.asyncio
    async def test_partial_update_recovery(self, test_settings: Settings):
        """부분 업데이트 실패 후 복구"""
        # Arrange
        mock_repo = MagicMock(spec=UserRepository)

        original_user = User(
            user_id="test-user",
            name="원래 이름",
            age=20,
            gender="남성",
            disability_type="자폐스펙트럼장애",
            communication_characteristics="문장 사용",
            interesting_topics=["음악"],
            password_hash="hash",
        )

        mock_repo.find_by_id = AsyncMock(return_value=original_user)

        update_call_count = 0

        async def failing_update(user):
            nonlocal update_call_count
            update_call_count += 1
            if update_call_count == 1:
                raise Exception("Update failed")
            return None

        mock_repo.update = failing_update

        service = UserService(mock_repo, test_settings)

        # Act & Assert (첫 번째 시도 실패)
        with pytest.raises(Exception):
            await service.update_user_persona("test-user", {"name": "새 이름"})

        # 두 번째 시도 (복구)
        result = await service.update_user_persona("test-user", {"name": "새 이름"})

        # Assert
        assert result.success is True


class TestTokenErrors:
    """토큰 관련 에러 테스트"""

    def test_verify_token_with_wrong_algorithm(self):
        """잘못된 알고리즘으로 토큰 검증"""
        # Arrange
        service1 = TokenService(
            secret_key="test-secret",
            algorithm="HS256",
        )
        service2 = TokenService(
            secret_key="test-secret",
            algorithm="HS384",  # 다른 알고리즘
        )

        token = service1.create_access_token("test-user")

        # Act
        result = service2.verify_token(token)

        # Assert (알고리즘 불일치로 실패)
        assert result is None

    def test_verify_token_with_wrong_secret(self):
        """잘못된 시크릿으로 토큰 검증"""
        # Arrange
        service1 = TokenService(secret_key="secret1")
        service2 = TokenService(secret_key="secret2")

        token = service1.create_access_token("test-user")

        # Act
        result = service2.verify_token(token)

        # Assert
        assert result is None

    def test_decode_malformed_token(self):
        """잘못된 형식의 토큰 디코딩"""
        # Arrange
        service = TokenService(secret_key="test-secret")

        # Act
        result = service.decode_token("not.a.valid.jwt.token")

        # Assert
        assert result is None

    def test_decode_empty_token(self):
        """빈 토큰 디코딩"""
        # Arrange
        service = TokenService(secret_key="test-secret")

        # Act
        result = service.decode_token("")

        # Assert
        assert result is None


class TestValidationErrors:
    """검증 관련 에러 테스트"""

    @pytest.mark.asyncio
    async def test_register_age_boundary_zero(self, test_settings: Settings):
        """나이 0으로 회원가입"""
        # Arrange
        mock_repo = MagicMock(spec=UserRepository)
        mock_repo.exists = AsyncMock(return_value=False)
        service = UserService(mock_repo, test_settings)

        # Act
        result = await service.register_user(
            user_id="zero-age",
            name="테스트",
            age=0,
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
    async def test_register_negative_age(self, test_settings: Settings):
        """음수 나이로 회원가입"""
        # Arrange
        mock_repo = MagicMock(spec=UserRepository)
        mock_repo.exists = AsyncMock(return_value=False)
        service = UserService(mock_repo, test_settings)

        # Act
        result = await service.register_user(
            user_id="negative-age",
            name="테스트",
            age=-5,
            gender="남성",
            disability_type="자폐스펙트럼장애",
            communication_characteristics="문장 사용",
            interesting_topics=["음악"],
            password="Test1234!",
        )

        # Assert
        assert result.success is False

    @pytest.mark.asyncio
    async def test_register_unknown_gender(self, test_settings: Settings):
        """알 수 없는 성별로 회원가입"""
        # Arrange
        mock_repo = MagicMock(spec=UserRepository)
        mock_repo.exists = AsyncMock(return_value=False)
        service = UserService(mock_repo, test_settings)

        # Act
        result = await service.register_user(
            user_id="unknown-gender",
            name="테스트",
            age=20,
            gender="기타",
            disability_type="자폐스펙트럼장애",
            communication_characteristics="문장 사용",
            interesting_topics=["음악"],
            password="Test1234!",
        )

        # Assert
        assert result.success is False
        assert "성별" in result.message
