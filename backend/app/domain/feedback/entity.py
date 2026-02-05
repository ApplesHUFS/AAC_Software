"""피드백 엔티티 정의"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
import uuid


@dataclass
class FeedbackRequest:
    """피드백 요청 엔티티"""

    confirmation_id: str
    user_id: str
    cards: List[str]
    context: Dict[str, Any]
    interpretations: List[str]
    partner_info: str
    created_at: datetime = field(default_factory=datetime.now)

    @staticmethod
    def generate_id() -> str:
        """확인 ID 생성"""
        return str(uuid.uuid4())

    def to_confirmation_dict(self) -> dict:
        """확인 요청 딕셔너리 변환"""
        return {
            "confirmationId": self.confirmation_id,
            "userContext": {
                "time": self.context.get("time", ""),
                "place": self.context.get("place", ""),
                "currentActivity": self.context.get("currentActivity", ""),
            },
            "selectedCards": self.cards,
            "interpretationOptions": [
                {"index": i, "interpretation": interp}
                for i, interp in enumerate(self.interpretations)
            ],
            "partner": self.partner_info,
        }


@dataclass
class Feedback:
    """피드백 결과 엔티티"""

    feedback_id: int
    confirmation_id: str
    user_id: str
    cards: List[str]
    context: Dict[str, Any]
    interpretations: List[str]
    partner_info: str
    feedback_type: str  # "interpretation_selected" or "direct_feedback"
    selected_index: Optional[int] = None
    selected_interpretation: Optional[str] = None
    direct_feedback: Optional[str] = None
    confirmed_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        """딕셔너리 변환"""
        return {
            "feedbackId": self.feedback_id,
            "feedbackType": self.feedback_type,
            "selectedIndex": self.selected_index,
            "selectedInterpretation": self.selected_interpretation,
            "directFeedback": self.direct_feedback,
            "confirmationId": self.confirmation_id,
            "userId": self.user_id,
            "cards": self.cards,
            "context": self.context,
            "interpretations": self.interpretations,
            "partnerInfo": self.partner_info,
            "confirmedAt": self.confirmed_at.isoformat(),
        }
