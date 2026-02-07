"""FeedbackService 유닛 테스트

피드백 요청, 제출, 조회 등 피드백 관련 비즈니스 로직을 테스트합니다.
AAA (Arrange-Act-Assert) 패턴을 준수합니다.
"""

from datetime import datetime
from typing import Optional
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.domain.feedback.entity import Feedback, FeedbackRequest
from app.domain.feedback.repository import FeedbackRepository
from app.domain.feedback.service import (
    FeedbackService,
    RequestFeedbackResult,
    SubmitFeedbackResult,
)


class MockFeedbackRepository(FeedbackRepository):
    """테스트용 피드백 저장소"""

    def __init__(self):
        self._requests: dict[str, FeedbackRequest] = {}
        self._feedbacks: dict[int, Feedback] = {}
        self._next_id = 1

    async def save_request(self, request: FeedbackRequest) -> None:
        self._requests[request.confirmation_id] = request

    async def find_request(self, confirmation_id: str) -> Optional[FeedbackRequest]:
        return self._requests.get(confirmation_id)

    async def save_feedback(self, feedback: Feedback) -> int:
        self._feedbacks[feedback.feedback_id] = feedback
        return feedback.feedback_id

    async def delete_request(self, confirmation_id: str) -> None:
        self._requests.pop(confirmation_id, None)

    async def get_next_feedback_id(self) -> int:
        next_id = self._next_id
        self._next_id += 1
        return next_id


@pytest.fixture
def mock_repo() -> MockFeedbackRepository:
    """Mock 피드백 저장소"""
    return MockFeedbackRepository()


@pytest.fixture
def feedback_service(mock_repo: MockFeedbackRepository) -> FeedbackService:
    """FeedbackService 인스턴스"""
    return FeedbackService(mock_repo)


@pytest.fixture
def sample_context() -> dict:
    """샘플 컨텍스트"""
    return {
        "time": "10시 30분",
        "place": "학교",
        "currentActivity": "점심 시간",
    }


@pytest.fixture
def sample_feedback_request(sample_context: dict) -> FeedbackRequest:
    """샘플 피드백 요청"""
    return FeedbackRequest(
        confirmation_id="test-confirmation-001",
        user_id="test-user-001",
        cards=["001_사과", "002_물"],
        context=sample_context,
        interpretations=["사과 주세요", "물 마시고 싶어요", "간식 먹고 싶어요"],
        partner_info="선생님",
    )


class TestFeedbackServiceRequestFeedback:
    """피드백 요청 생성 테스트"""

    @pytest.mark.asyncio
    async def test_request_feedback_success(
        self,
        feedback_service: FeedbackService,
        mock_repo: MockFeedbackRepository,
        sample_context: dict,
    ):
        """피드백 요청 생성 성공"""
        # Arrange
        user_id = "test-user-001"
        cards = ["001_사과", "002_물"]
        interpretations = ["사과 주세요", "물 마시고 싶어요", "간식 먹고 싶어요"]
        partner_info = "선생님"

        # Act
        result = await feedback_service.request_feedback(
            user_id=user_id,
            cards=cards,
            context=sample_context,
            interpretations=interpretations,
            partner_info=partner_info,
        )

        # Assert
        assert result.success is True
        assert result.confirmation_id is not None
        assert len(result.confirmation_id) == 36  # UUID 형식
        assert "생성" in result.message

        # 저장소에 요청이 저장되었는지 확인
        saved_request = await mock_repo.find_request(result.confirmation_id)
        assert saved_request is not None
        assert saved_request.user_id == user_id
        assert saved_request.cards == cards

    @pytest.mark.asyncio
    async def test_request_feedback_returns_confirmation_request(
        self, feedback_service: FeedbackService, sample_context: dict
    ):
        """피드백 요청 시 확인 요청 정보 반환"""
        # Arrange
        cards = ["001_사과"]
        interpretations = ["사과 주세요"]

        # Act
        result = await feedback_service.request_feedback(
            user_id="test-user",
            cards=cards,
            context=sample_context,
            interpretations=interpretations,
            partner_info="부모님",
        )

        # Assert
        assert "confirmationId" in result.confirmation_request
        assert "selectedCards" in result.confirmation_request
        assert "interpretationOptions" in result.confirmation_request
        assert "partner" in result.confirmation_request
        assert result.confirmation_request["selectedCards"] == cards
        assert result.confirmation_request["partner"] == "부모님"

    @pytest.mark.asyncio
    async def test_request_feedback_interpretation_options_format(
        self, feedback_service: FeedbackService, sample_context: dict
    ):
        """해석 옵션 형식 검증"""
        # Arrange
        interpretations = ["해석1", "해석2", "해석3"]

        # Act
        result = await feedback_service.request_feedback(
            user_id="test-user",
            cards=["001_사과"],
            context=sample_context,
            interpretations=interpretations,
            partner_info="선생님",
        )

        # Assert
        options = result.confirmation_request["interpretationOptions"]
        assert len(options) == 3
        for i, option in enumerate(options):
            assert option["index"] == i
            assert option["interpretation"] == interpretations[i]

    @pytest.mark.asyncio
    async def test_request_feedback_with_empty_cards(
        self, feedback_service: FeedbackService, sample_context: dict
    ):
        """빈 카드 목록으로 피드백 요청"""
        # Arrange & Act
        result = await feedback_service.request_feedback(
            user_id="test-user",
            cards=[],
            context=sample_context,
            interpretations=["해석"],
            partner_info="부모님",
        )

        # Assert (서비스는 빈 카드도 허용)
        assert result.success is True


class TestFeedbackServiceSubmitFeedback:
    """피드백 제출 테스트"""

    @pytest.mark.asyncio
    async def test_submit_feedback_with_selected_interpretation(
        self,
        feedback_service: FeedbackService,
        mock_repo: MockFeedbackRepository,
        sample_feedback_request: FeedbackRequest,
    ):
        """해석 선택으로 피드백 제출 성공"""
        # Arrange
        await mock_repo.save_request(sample_feedback_request)

        # Act
        result = await feedback_service.submit_feedback(
            confirmation_id=sample_feedback_request.confirmation_id,
            selected_index=1,
            direct_feedback=None,
        )

        # Assert
        assert result.success is True
        assert result.feedback is not None
        assert result.feedback.feedback_type == "interpretation_selected"
        assert result.feedback.selected_index == 1
        assert result.feedback.selected_interpretation == "물 마시고 싶어요"
        assert result.feedback.direct_feedback is None

    @pytest.mark.asyncio
    async def test_submit_feedback_with_direct_feedback(
        self,
        feedback_service: FeedbackService,
        mock_repo: MockFeedbackRepository,
        sample_feedback_request: FeedbackRequest,
    ):
        """직접 피드백으로 제출 성공"""
        # Arrange
        await mock_repo.save_request(sample_feedback_request)
        direct_message = "배가 고파요"

        # Act
        result = await feedback_service.submit_feedback(
            confirmation_id=sample_feedback_request.confirmation_id,
            selected_index=None,
            direct_feedback=direct_message,
        )

        # Assert
        assert result.success is True
        assert result.feedback is not None
        assert result.feedback.feedback_type == "direct_feedback"
        assert result.feedback.direct_feedback == direct_message
        assert result.feedback.selected_index is None
        assert result.feedback.selected_interpretation is None

    @pytest.mark.asyncio
    async def test_submit_feedback_deletes_request(
        self,
        feedback_service: FeedbackService,
        mock_repo: MockFeedbackRepository,
        sample_feedback_request: FeedbackRequest,
    ):
        """피드백 제출 후 요청 삭제"""
        # Arrange
        await mock_repo.save_request(sample_feedback_request)
        confirmation_id = sample_feedback_request.confirmation_id

        # Act
        await feedback_service.submit_feedback(
            confirmation_id=confirmation_id,
            selected_index=0,
            direct_feedback=None,
        )

        # Assert
        request = await mock_repo.find_request(confirmation_id)
        assert request is None

    @pytest.mark.asyncio
    async def test_submit_feedback_nonexistent_request_fails(
        self, feedback_service: FeedbackService
    ):
        """존재하지 않는 요청에 대한 피드백 제출 실패"""
        # Arrange & Act
        result = await feedback_service.submit_feedback(
            confirmation_id="nonexistent-confirmation-id",
            selected_index=0,
            direct_feedback=None,
        )

        # Assert
        assert result.success is False
        assert result.feedback is None
        assert "찾을 수 없" in result.message

    @pytest.mark.asyncio
    async def test_submit_feedback_no_selection_fails(
        self,
        feedback_service: FeedbackService,
        mock_repo: MockFeedbackRepository,
        sample_feedback_request: FeedbackRequest,
    ):
        """선택 없이 피드백 제출 실패"""
        # Arrange
        await mock_repo.save_request(sample_feedback_request)

        # Act
        result = await feedback_service.submit_feedback(
            confirmation_id=sample_feedback_request.confirmation_id,
            selected_index=None,
            direct_feedback=None,  # 둘 다 None
        )

        # Assert
        assert result.success is False
        assert result.feedback is None
        assert "선택" in result.message or "입력" in result.message

    @pytest.mark.asyncio
    async def test_submit_feedback_direct_feedback_takes_priority(
        self,
        feedback_service: FeedbackService,
        mock_repo: MockFeedbackRepository,
        sample_feedback_request: FeedbackRequest,
    ):
        """직접 피드백이 해석 선택보다 우선"""
        # Arrange
        await mock_repo.save_request(sample_feedback_request)

        # Act (둘 다 제공)
        result = await feedback_service.submit_feedback(
            confirmation_id=sample_feedback_request.confirmation_id,
            selected_index=0,
            direct_feedback="직접 입력한 피드백",
        )

        # Assert
        assert result.success is True
        assert result.feedback.feedback_type == "direct_feedback"
        assert result.feedback.direct_feedback == "직접 입력한 피드백"

    @pytest.mark.asyncio
    async def test_submit_feedback_saves_to_repository(
        self,
        feedback_service: FeedbackService,
        mock_repo: MockFeedbackRepository,
        sample_feedback_request: FeedbackRequest,
    ):
        """피드백이 저장소에 저장됨"""
        # Arrange
        await mock_repo.save_request(sample_feedback_request)

        # Act
        result = await feedback_service.submit_feedback(
            confirmation_id=sample_feedback_request.confirmation_id,
            selected_index=0,
            direct_feedback=None,
        )

        # Assert
        feedback_id = result.feedback.feedback_id
        saved_feedback = mock_repo._feedbacks.get(feedback_id)
        assert saved_feedback is not None
        assert saved_feedback.user_id == sample_feedback_request.user_id


class TestFeedbackServiceEdgeCases:
    """엣지 케이스 테스트"""

    @pytest.mark.asyncio
    async def test_submit_feedback_with_out_of_range_index(
        self,
        feedback_service: FeedbackService,
        mock_repo: MockFeedbackRepository,
        sample_feedback_request: FeedbackRequest,
    ):
        """범위 초과 인덱스로 피드백 제출"""
        # Arrange
        await mock_repo.save_request(sample_feedback_request)

        # Act (인덱스가 해석 목록 범위를 초과)
        result = await feedback_service.submit_feedback(
            confirmation_id=sample_feedback_request.confirmation_id,
            selected_index=100,  # 범위 초과
            direct_feedback=None,
        )

        # Assert
        assert result.success is True
        assert result.feedback.selected_interpretation is None  # 유효하지 않은 인덱스

    @pytest.mark.asyncio
    async def test_submit_feedback_with_negative_index(
        self,
        feedback_service: FeedbackService,
        mock_repo: MockFeedbackRepository,
        sample_feedback_request: FeedbackRequest,
    ):
        """음수 인덱스로 피드백 제출"""
        # Arrange
        await mock_repo.save_request(sample_feedback_request)

        # Act
        result = await feedback_service.submit_feedback(
            confirmation_id=sample_feedback_request.confirmation_id,
            selected_index=-1,
            direct_feedback=None,
        )

        # Assert
        assert result.success is True
        assert result.feedback.selected_interpretation is None  # 유효하지 않은 인덱스

    @pytest.mark.asyncio
    async def test_submit_feedback_preserves_original_data(
        self,
        feedback_service: FeedbackService,
        mock_repo: MockFeedbackRepository,
        sample_feedback_request: FeedbackRequest,
    ):
        """피드백 제출 시 원본 데이터 보존"""
        # Arrange
        await mock_repo.save_request(sample_feedback_request)

        # Act
        result = await feedback_service.submit_feedback(
            confirmation_id=sample_feedback_request.confirmation_id,
            selected_index=0,
            direct_feedback=None,
        )

        # Assert
        feedback = result.feedback
        assert feedback.user_id == sample_feedback_request.user_id
        assert feedback.cards == sample_feedback_request.cards
        assert feedback.context == sample_feedback_request.context
        assert feedback.interpretations == sample_feedback_request.interpretations
        assert feedback.partner_info == sample_feedback_request.partner_info

    @pytest.mark.asyncio
    async def test_submit_feedback_sets_confirmed_at(
        self,
        feedback_service: FeedbackService,
        mock_repo: MockFeedbackRepository,
        sample_feedback_request: FeedbackRequest,
    ):
        """피드백 제출 시 확인 시간 설정"""
        # Arrange
        await mock_repo.save_request(sample_feedback_request)
        before_submit = datetime.now()

        # Act
        result = await feedback_service.submit_feedback(
            confirmation_id=sample_feedback_request.confirmation_id,
            selected_index=0,
            direct_feedback=None,
        )

        # Assert
        after_submit = datetime.now()
        assert before_submit <= result.feedback.confirmed_at <= after_submit

    @pytest.mark.asyncio
    async def test_multiple_feedbacks_get_unique_ids(
        self,
        feedback_service: FeedbackService,
        mock_repo: MockFeedbackRepository,
        sample_context: dict,
    ):
        """여러 피드백이 고유 ID를 받음"""
        # Arrange
        feedback_ids = []

        # Act
        for i in range(3):
            # 각각 새로운 요청 생성
            result = await feedback_service.request_feedback(
                user_id=f"user-{i}",
                cards=["001_사과"],
                context=sample_context,
                interpretations=["해석"],
                partner_info="선생님",
            )

            submit_result = await feedback_service.submit_feedback(
                confirmation_id=result.confirmation_id,
                selected_index=0,
                direct_feedback=None,
            )
            feedback_ids.append(submit_result.feedback.feedback_id)

        # Assert
        assert len(set(feedback_ids)) == 3  # 모든 ID가 고유

    @pytest.mark.asyncio
    async def test_submit_feedback_with_empty_direct_feedback(
        self,
        feedback_service: FeedbackService,
        mock_repo: MockFeedbackRepository,
        sample_feedback_request: FeedbackRequest,
    ):
        """빈 문자열 직접 피드백으로 제출"""
        # Arrange
        await mock_repo.save_request(sample_feedback_request)

        # Act (빈 문자열은 falsy이므로 실패해야 함)
        result = await feedback_service.submit_feedback(
            confirmation_id=sample_feedback_request.confirmation_id,
            selected_index=None,
            direct_feedback="",  # 빈 문자열
        )

        # Assert
        # 빈 문자열은 falsy이므로 선택 없음으로 처리됨
        assert result.success is False

    @pytest.mark.asyncio
    async def test_feedback_to_dict_format(
        self,
        feedback_service: FeedbackService,
        mock_repo: MockFeedbackRepository,
        sample_feedback_request: FeedbackRequest,
    ):
        """피드백 딕셔너리 변환 형식 검증"""
        # Arrange
        await mock_repo.save_request(sample_feedback_request)

        # Act
        result = await feedback_service.submit_feedback(
            confirmation_id=sample_feedback_request.confirmation_id,
            selected_index=0,
            direct_feedback=None,
        )

        feedback_dict = result.feedback.to_dict()

        # Assert
        assert "feedbackId" in feedback_dict
        assert "feedbackType" in feedback_dict
        assert "selectedIndex" in feedback_dict
        assert "selectedInterpretation" in feedback_dict
        assert "directFeedback" in feedback_dict
        assert "confirmationId" in feedback_dict
        assert "userId" in feedback_dict
        assert "cards" in feedback_dict
        assert "context" in feedback_dict
        assert "interpretations" in feedback_dict
        assert "partnerInfo" in feedback_dict
        assert "confirmedAt" in feedback_dict


class TestFeedbackRequestEntity:
    """FeedbackRequest 엔티티 테스트"""

    def test_generate_id_returns_uuid(self):
        """ID 생성이 UUID 형식 반환"""
        # Act
        id1 = FeedbackRequest.generate_id()
        id2 = FeedbackRequest.generate_id()

        # Assert
        assert len(id1) == 36
        assert len(id2) == 36
        assert id1 != id2

    def test_to_confirmation_dict(self, sample_feedback_request: FeedbackRequest):
        """확인 딕셔너리 변환"""
        # Act
        result = sample_feedback_request.to_confirmation_dict()

        # Assert
        assert result["confirmationId"] == sample_feedback_request.confirmation_id
        assert result["selectedCards"] == sample_feedback_request.cards
        assert result["partner"] == sample_feedback_request.partner_info
        assert "userContext" in result
        assert "interpretationOptions" in result

    def test_confirmation_dict_user_context_format(
        self, sample_feedback_request: FeedbackRequest
    ):
        """확인 딕셔너리의 사용자 컨텍스트 형식"""
        # Act
        result = sample_feedback_request.to_confirmation_dict()
        user_context = result["userContext"]

        # Assert
        assert "time" in user_context
        assert "place" in user_context
        assert "currentActivity" in user_context


class TestFeedbackEntity:
    """Feedback 엔티티 테스트"""

    def test_feedback_to_dict(self):
        """피드백 딕셔너리 변환"""
        # Arrange
        feedback = Feedback(
            feedback_id=1,
            confirmation_id="conf-001",
            user_id="user-001",
            cards=["001_사과"],
            context={"time": "10시"},
            interpretations=["해석1"],
            partner_info="선생님",
            feedback_type="interpretation_selected",
            selected_index=0,
            selected_interpretation="해석1",
            confirmed_at=datetime(2024, 1, 15, 10, 30, 0),
        )

        # Act
        result = feedback.to_dict()

        # Assert
        assert result["feedbackId"] == 1
        assert result["confirmationId"] == "conf-001"
        assert result["userId"] == "user-001"
        assert result["feedbackType"] == "interpretation_selected"
        assert result["selectedIndex"] == 0
        assert result["selectedInterpretation"] == "해석1"
        assert result["confirmedAt"] == "2024-01-15T10:30:00"

    def test_feedback_to_dict_with_direct_feedback(self):
        """직접 피드백 딕셔너리 변환"""
        # Arrange
        feedback = Feedback(
            feedback_id=2,
            confirmation_id="conf-002",
            user_id="user-002",
            cards=["002_물"],
            context={"time": "11시"},
            interpretations=["해석1", "해석2"],
            partner_info="부모님",
            feedback_type="direct_feedback",
            direct_feedback="목이 말라요",
            confirmed_at=datetime.now(),
        )

        # Act
        result = feedback.to_dict()

        # Assert
        assert result["feedbackType"] == "direct_feedback"
        assert result["directFeedback"] == "목이 말라요"
        assert result["selectedIndex"] is None
        assert result["selectedInterpretation"] is None
