"""피드백 기반 컨텍스트 학습 분석기

CLIP 임베딩 기반 의미론적 유사도를 사용하여
과거 피드백 패턴을 분석하고 쿼리 확장에 활용합니다.

설계 원칙:
- CLIP 벡터 기반 의미론적 분석 (TF-IDF 제거)
- 랜덤 fallback 없이 명확한 결과 반환
- CLIPVisualPatternAnalyzer 재사용 (SSOT)
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Set, Tuple

if TYPE_CHECKING:
    from app.domain.feedback.visual_analyzer import IVisualPatternAnalyzer

logger = logging.getLogger(__name__)


@dataclass
class FeedbackPattern:
    """분석된 피드백 패턴

    Attributes:
        context: 원본 컨텍스트 (장소, 활동, 대화상대)
        cards: 선택된 카드 목록
        interpretation: 확정된 해석
        relevance_score: 현재 상황과의 유사도 (0~1)
        recency_weight: 시간 기반 가중치 (0~1)
    """

    context: Dict[str, str]
    cards: List[str]
    interpretation: Optional[str]
    relevance_score: float = 0.0
    recency_weight: float = 1.0

    @property
    def combined_score(self) -> float:
        """유사도와 시간 가중치를 결합한 최종 점수"""
        return self.relevance_score * self.recency_weight


@dataclass
class QueryExpansion:
    """피드백 기반 쿼리 확장 결과

    Attributes:
        original_context: 원본 컨텍스트
        relevant_cards: 과거 성공 패턴에서 추출된 관련 카드
        context_hints: 컨텍스트 힌트 (유사 상황의 키워드)
        confidence: 확장의 신뢰도 (충분한 데이터 기반 여부)
    """

    original_context: Dict[str, str]
    relevant_cards: List[str] = field(default_factory=list)
    context_hints: List[str] = field(default_factory=list)
    confidence: float = 0.0


class IFeedbackAnalyzer(ABC):
    """피드백 분석기 인터페이스"""

    @abstractmethod
    async def analyze_patterns(
        self,
        place: str,
        interaction_partner: str,
        current_activity: str,
        user_id: Optional[str] = None,
    ) -> QueryExpansion:
        """현재 상황과 유사한 과거 패턴 분석

        Args:
            place: 현재 장소
            interaction_partner: 현재 대화 상대
            current_activity: 현재 활동
            user_id: 사용자 ID (개인화 시 사용)

        Returns:
            피드백 기반 쿼리 확장 정보
        """
        pass

    @abstractmethod
    async def get_successful_cards(
        self,
        place: str,
        interaction_partner: str,
        current_activity: str,
        top_k: int = 5,
    ) -> List[Tuple[str, float]]:
        """현재 상황에서 성공적이었던 카드 목록 반환

        Args:
            place: 현재 장소
            interaction_partner: 현재 대화 상대
            current_activity: 현재 활동
            top_k: 반환할 최대 카드 수

        Returns:
            (카드명, 점수) 튜플 리스트
        """
        pass


class CLIPFeedbackAnalyzer(IFeedbackAnalyzer):
    """CLIP 임베딩 기반 피드백 분석기

    CLIPVisualPatternAnalyzer를 래핑하여 IFeedbackAnalyzer 인터페이스 구현.
    CLIP 벡터 유사도로 과거 피드백의 의미론적 관련성을 계산합니다.

    Attributes:
        _visual_analyzer: CLIP 기반 시각적 패턴 분석기
    """

    def __init__(self, visual_analyzer: "IVisualPatternAnalyzer"):
        self._visual_analyzer = visual_analyzer

    async def analyze_patterns(
        self,
        place: str,
        interaction_partner: str,
        current_activity: str,
        user_id: Optional[str] = None,
    ) -> QueryExpansion:
        """CLIP 기반 패턴 분석

        시각적 패턴 분석기를 활용하여 유사한 과거 피드백 검색.
        결과 없으면 빈 QueryExpansion 반환 (랜덤 fallback 없음).
        """
        # 시각적 분석기를 통해 유사 패턴 검색
        # 컨텍스트 기반 검색은 카드 파일명이 필요하므로
        # 이 메서드는 카드 없이 컨텍스트만으로 검색하는 경우 빈 결과 반환
        expansion = await self._visual_analyzer.find_similar_patterns(
            card_filenames=[],
            user_id=user_id,
            top_k=5,
        )

        # VisualQueryExpansion -> QueryExpansion 변환
        relevant_cards: List[str] = []
        context_hints: Set[str] = set()
        seen_cards: Set[str] = set()

        for pattern in expansion.similar_patterns:
            # 패턴의 카드 목록 추출
            pattern_cards = pattern.context.get("cards", [])
            if isinstance(pattern_cards, list):
                for card in pattern_cards:
                    if card not in seen_cards:
                        relevant_cards.append(card)
                        seen_cards.add(card)

            # 컨텍스트 힌트 추출
            if pattern.context.get("place"):
                context_hints.add(pattern.context["place"])
            if pattern.context.get("currentActivity"):
                context_hints.add(pattern.context["currentActivity"])

        return QueryExpansion(
            original_context={
                "place": place,
                "interaction_partner": interaction_partner,
                "current_activity": current_activity,
            },
            relevant_cards=relevant_cards[:10],
            context_hints=list(context_hints)[:5],
            confidence=expansion.visual_confidence,
        )

    async def analyze_patterns_with_cards(
        self,
        place: str,
        interaction_partner: str,
        current_activity: str,
        card_filenames: List[str],
        user_id: Optional[str] = None,
    ) -> QueryExpansion:
        """카드 기반 CLIP 패턴 분석

        선택된 카드의 시각적 서명으로 유사 패턴 검색.
        """
        if not card_filenames:
            return await self.analyze_patterns(
                place, interaction_partner, current_activity, user_id
            )

        expansion = await self._visual_analyzer.find_similar_patterns(
            card_filenames=card_filenames,
            user_id=user_id,
            top_k=5,
        )

        relevant_cards: List[str] = []
        context_hints: Set[str] = set()
        seen_cards: Set[str] = set(card_filenames)

        for pattern in expansion.similar_patterns:
            pattern_cards = pattern.context.get("cards", [])
            if isinstance(pattern_cards, list):
                for card in pattern_cards:
                    if card not in seen_cards:
                        relevant_cards.append(card)
                        seen_cards.add(card)

            if pattern.context.get("place"):
                context_hints.add(pattern.context["place"])
            if pattern.context.get("currentActivity"):
                context_hints.add(pattern.context["currentActivity"])

        return QueryExpansion(
            original_context={
                "place": place,
                "interaction_partner": interaction_partner,
                "current_activity": current_activity,
            },
            relevant_cards=relevant_cards[:10],
            context_hints=list(context_hints)[:5],
            confidence=expansion.visual_confidence,
        )

    async def get_successful_cards(
        self,
        place: str,
        interaction_partner: str,
        current_activity: str,
        top_k: int = 5,
    ) -> List[Tuple[str, float]]:
        """CLIP 기반 성공 카드 검색

        유사 패턴에서 관련 카드를 추출하여 점수와 함께 반환.
        결과 없으면 빈 리스트 반환 (랜덤 fallback 없음).
        """
        expansion = await self.analyze_patterns(
            place, interaction_partner, current_activity
        )

        if not expansion.relevant_cards:
            logger.info("유사한 과거 패턴 없음 - 빈 결과 반환")
            return []

        # 순위 기반 점수 할당
        return [
            (card, 1.0 - i * 0.1)
            for i, card in enumerate(expansion.relevant_cards[:top_k])
        ]


class NoOpFeedbackAnalyzer(IFeedbackAnalyzer):
    """피드백 분석 비활성화 시 사용하는 No-op 구현"""

    async def analyze_patterns(
        self,
        place: str,
        interaction_partner: str,
        current_activity: str,
        user_id: Optional[str] = None,
    ) -> QueryExpansion:
        """빈 확장 정보 반환"""
        return QueryExpansion(
            original_context={
                "place": place,
                "interaction_partner": interaction_partner,
                "current_activity": current_activity,
            },
            confidence=0.0,
        )

    async def get_successful_cards(
        self,
        place: str,
        interaction_partner: str,
        current_activity: str,
        top_k: int = 5,
    ) -> List[Tuple[str, float]]:
        """빈 리스트 반환"""
        return []
