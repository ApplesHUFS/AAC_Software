"""카드 저장소 인터페이스"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Optional, Set

from app.domain.card.entity import Card, CardHistory


class CardRepository(ABC):
    """카드 저장소 추상 클래스"""

    @abstractmethod
    def get_all_cards(self) -> List[Card]:
        """모든 카드 조회"""
        pass

    @abstractmethod
    def get_cards_by_cluster(self, cluster_id: int) -> List[Card]:
        """클러스터별 카드 조회"""
        pass

    @abstractmethod
    def get_cluster_tags(self) -> Dict[str, str]:
        """클러스터 태그 조회"""
        pass

    @abstractmethod
    def get_clustering_results(self) -> Dict[str, int]:
        """클러스터링 결과 조회 (파일명 -> 클러스터 ID)"""
        pass


class CardHistoryRepository(ABC):
    """카드 히스토리 저장소 추상 클래스"""

    @abstractmethod
    async def save_history(self, history: CardHistory) -> None:
        """히스토리 저장"""
        pass

    @abstractmethod
    async def get_history_by_context(self, context_id: str) -> List[CardHistory]:
        """컨텍스트별 히스토리 조회"""
        pass

    @abstractmethod
    async def get_history_page(
        self, context_id: str, page_number: int
    ) -> Optional[CardHistory]:
        """특정 페이지 히스토리 조회"""
        pass

    @abstractmethod
    async def get_all_recommended_cards(self, context_id: str) -> Set[str]:
        """해당 컨텍스트에서 추천된 모든 카드 파일명 조회"""
        pass
