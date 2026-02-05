"""피드백 서비스"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.domain.feedback.entity import Feedback, FeedbackRequest
from app.domain.feedback.repository import FeedbackRepository


@dataclass
class RequestFeedbackResult:
    """피드백 요청 결과"""

    success: bool
    confirmation_id: str
    confirmation_request: Dict[str, Any]
    message: str


@dataclass
class SubmitFeedbackResult:
    """피드백 제출 결과"""

    success: bool
    feedback: Optional[Feedback]
    message: str


class FeedbackService:
    """피드백 관련 비즈니스 로직"""

    def __init__(self, repository: FeedbackRepository):
        self._repo = repository

    async def request_feedback(
        self,
        user_id: str,
        cards: List[str],
        context: Dict[str, Any],
        interpretations: List[str],
        partner_info: str,
    ) -> RequestFeedbackResult:
        """피드백 요청 생성"""
        confirmation_id = FeedbackRequest.generate_id()

        request = FeedbackRequest(
            confirmation_id=confirmation_id,
            user_id=user_id,
            cards=cards,
            context=context,
            interpretations=interpretations,
            partner_info=partner_info,
        )

        await self._repo.save_request(request)

        return RequestFeedbackResult(
            success=True,
            confirmation_id=confirmation_id,
            confirmation_request=request.to_confirmation_dict(),
            message="피드백 요청이 생성되었습니다.",
        )

    async def submit_feedback(
        self,
        confirmation_id: str,
        selected_index: Optional[int] = None,
        direct_feedback: Optional[str] = None,
    ) -> SubmitFeedbackResult:
        """피드백 제출"""
        request = await self._repo.find_request(confirmation_id)

        if not request:
            return SubmitFeedbackResult(
                success=False,
                feedback=None,
                message="피드백 요청을 찾을 수 없습니다.",
            )

        # 피드백 타입 및 내용 결정
        if direct_feedback:
            feedback_type = "direct_feedback"
            selected_interpretation = None
        elif selected_index is not None:
            feedback_type = "interpretation_selected"
            selected_interpretation = (
                request.interpretations[selected_index]
                if 0 <= selected_index < len(request.interpretations)
                else None
            )
        else:
            return SubmitFeedbackResult(
                success=False,
                feedback=None,
                message="해석 선택 또는 직접 피드백 중 하나를 입력해주세요.",
            )

        feedback_id = await self._repo.get_next_feedback_id()

        feedback = Feedback(
            feedback_id=feedback_id,
            confirmation_id=confirmation_id,
            user_id=request.user_id,
            cards=request.cards,
            context=request.context,
            interpretations=request.interpretations,
            partner_info=request.partner_info,
            feedback_type=feedback_type,
            selected_index=selected_index,
            selected_interpretation=selected_interpretation,
            direct_feedback=direct_feedback,
            confirmed_at=datetime.now(),
        )

        await self._repo.save_feedback(feedback)
        await self._repo.delete_request(confirmation_id)

        return SubmitFeedbackResult(
            success=True,
            feedback=feedback,
            message="피드백이 성공적으로 저장되었습니다.",
        )
