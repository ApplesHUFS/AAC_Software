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
    """피드백 결과 엔티티

    Attributes:
        feedback_id: 피드백 고유 ID
        confirmation_id: 확인 요청 ID
        user_id: 사용자 ID
        cards: 선택된 카드 파일명 목록
        context: 피드백 당시 상황 컨텍스트
        interpretations: AI가 생성한 해석 목록
        partner_info: 대화 상대 정보
        feedback_type: 피드백 유형 (해석 선택 또는 직접 입력)
        selected_index: 선택된 해석 인덱스
        selected_interpretation: 선택된 해석 텍스트
        direct_feedback: 직접 입력한 피드백
        confirmed_at: 확인 시간
        visual_signature: 카드 조합의 시각적 서명 (CLIP 임베딩)
    """

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
    visual_signature: Optional[List[float]] = None  # 768차원 CLIP 임베딩

    def to_dict(self) -> dict:
        """딕셔너리 변환"""
        result = {
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

        # 시각적 서명이 있으면 포함 (하위 호환성)
        if self.visual_signature is not None:
            result["visualSignature"] = self.visual_signature

        return result

    def get_confirmed_interpretation(self) -> Optional[str]:
        """확정된 해석 반환 (직접 입력 또는 선택된 해석)"""
        return self.direct_feedback or self.selected_interpretation
