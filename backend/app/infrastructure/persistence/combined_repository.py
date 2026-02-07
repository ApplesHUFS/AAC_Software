"""복합 저장소 구현

여러 저장소를 조합하여 사용하는 래퍼 클래스
"""

from typing import Optional, Any

from app.infrastructure.persistence.json_repository import JsonFeedbackRepository
from app.infrastructure.persistence.memory_repository import InMemoryFeedbackRequestRepository


class CombinedFeedbackRepository:
    """피드백 저장소와 요청 저장소를 조합한 복합 저장소

    FeedbackService에서 필요한 인터페이스를 단일 객체로 제공
    """

    def __init__(
        self,
        feedback_repo: JsonFeedbackRepository,
        request_repo: InMemoryFeedbackRequestRepository,
    ):
        self._feedback = feedback_repo
        self._request = request_repo

    async def save_request(self, request: Any) -> None:
        """피드백 요청 저장"""
        await self._request.save_request(request)

    async def find_request(self, confirmation_id: str) -> Optional[Any]:
        """피드백 요청 조회"""
        return await self._request.find_request(confirmation_id)

    async def save_feedback(self, feedback: Any) -> Any:
        """피드백 저장"""
        return await self._feedback.save_feedback(feedback)

    async def delete_request(self, confirmation_id: str) -> None:
        """피드백 요청 삭제"""
        await self._request.delete_request(confirmation_id)

    async def get_next_feedback_id(self) -> int:
        """다음 피드백 ID 반환"""
        return await self._feedback.get_next_feedback_id()
