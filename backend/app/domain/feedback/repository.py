"""피드백 저장소 인터페이스"""

from abc import ABC, abstractmethod
from typing import Optional

from app.domain.feedback.entity import Feedback, FeedbackRequest


class FeedbackRepository(ABC):
    """피드백 저장소 추상 클래스"""

    @abstractmethod
    async def save_request(self, request: FeedbackRequest) -> None:
        """피드백 요청 저장"""
        pass

    @abstractmethod
    async def find_request(self, confirmation_id: str) -> Optional[FeedbackRequest]:
        """피드백 요청 조회"""
        pass

    @abstractmethod
    async def save_feedback(self, feedback: Feedback) -> int:
        """피드백 저장 및 ID 반환"""
        pass

    @abstractmethod
    async def delete_request(self, confirmation_id: str) -> None:
        """피드백 요청 삭제"""
        pass

    @abstractmethod
    async def get_next_feedback_id(self) -> int:
        """다음 피드백 ID 반환"""
        pass
