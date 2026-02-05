"""컨텍스트 엔티티 정의"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
import uuid


@dataclass
class Context:
    """대화 상황 컨텍스트 엔티티"""

    context_id: str
    user_id: str
    time: str
    place: str
    interaction_partner: str
    current_activity: str = ""
    created_at: datetime = field(default_factory=datetime.now)

    @staticmethod
    def generate_id() -> str:
        """UUID 기반 컨텍스트 ID 생성"""
        return str(uuid.uuid4())

    @staticmethod
    def get_current_time() -> str:
        """현재 시간 문자열 반환 (HH시 MM분 형식)"""
        now = datetime.now()
        return f"{now.hour}시 {now.minute}분"

    def to_dict(self) -> dict:
        """딕셔너리 변환"""
        return {
            "contextId": self.context_id,
            "userId": self.user_id,
            "time": self.time,
            "place": self.place,
            "interactionPartner": self.interaction_partner,
            "currentActivity": self.current_activity,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
        }

    def to_summary_dict(self) -> dict:
        """요약 딕셔너리 (해석용)"""
        return {
            "time": self.time,
            "place": self.place,
            "interactionPartner": self.interaction_partner,
            "currentActivity": self.current_activity,
        }
