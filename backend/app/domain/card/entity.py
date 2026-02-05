"""카드 엔티티 정의"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


@dataclass
class Card:
    """AAC 카드 엔티티"""

    id: str
    name: str
    filename: str
    image_path: str
    index: int = 0
    selected: bool = False

    def to_dict(self) -> dict:
        """딕셔너리 변환"""
        return {
            "id": self.id,
            "name": self.name,
            "filename": self.filename,
            "imagePath": self.image_path,
            "index": self.index,
            "selected": self.selected,
        }

    @classmethod
    def from_filename(cls, filename: str, index: int = 0) -> "Card":
        """파일명에서 카드 생성"""
        name = filename.rsplit(".", 1)[0] if "." in filename else filename
        card_id = name.replace(" ", "_").lower()

        return cls(
            id=card_id,
            name=name,
            filename=filename,
            image_path=f"/api/images/{filename}",
            index=index,
        )


@dataclass
class CardHistory:
    """카드 추천 히스토리"""

    context_id: str
    page_number: int
    cards: List[Card]
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        """딕셔너리 변환"""
        return {
            "contextId": self.context_id,
            "pageNumber": self.page_number,
            "cards": [card.to_dict() for card in self.cards],
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class Interpretation:
    """카드 해석"""

    index: int
    text: str
    selected: bool = False

    def to_dict(self) -> dict:
        """딕셔너리 변환"""
        return {
            "index": self.index,
            "text": self.text,
            "selected": self.selected,
        }
