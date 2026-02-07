"""복합 피드백 분석기

CLIP 임베딩 기반 시각적 패턴 분석으로 피드백 기반 추천 제공.
TF-IDF 기반 텍스트 분석 제거됨 - 시각적 분석으로 통일.
"""

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple

from app.domain.feedback.analyzer import (
    IFeedbackAnalyzer,
    QueryExpansion,
)
from app.domain.feedback.visual_analyzer import (
    IVisualPatternAnalyzer,
    VisualQueryExpansion,
)

logger = logging.getLogger(__name__)


@dataclass
class CompositeQueryExpansion:
    """쿼리 확장 결과

    시각적 분석 결과를 담은 쿼리 확장 정보

    Attributes:
        original_context: 원본 컨텍스트
        relevant_cards: 관련 카드 파일명
        context_hints: 컨텍스트 힌트
        interpretation_hints: 해석 힌트 (시각적 분석)
        visual_confidence: 시각적 분석 신뢰도
    """

    original_context: Dict[str, str] = field(default_factory=dict)
    relevant_cards: List[str] = field(default_factory=list)
    context_hints: List[str] = field(default_factory=list)
    interpretation_hints: List[str] = field(default_factory=list)
    visual_confidence: float = 0.0


class CompositeFeedbackAnalyzer(IFeedbackAnalyzer):
    """CLIP 기반 시각적 패턴 분석기

    시각적 패턴 분석만 사용 (TF-IDF 제거됨).

    Attributes:
        _visual_analyzer: CLIP 기반 시각적 패턴 분석기
    """

    def __init__(self, visual_analyzer: IVisualPatternAnalyzer):
        self._visual_analyzer = visual_analyzer

    async def analyze_patterns(
        self,
        place: str,
        interaction_partner: str,
        current_activity: str,
        user_id: Optional[str] = None,
    ) -> QueryExpansion:
        """기존 인터페이스 호환 분석

        IFeedbackAnalyzer 인터페이스 준수를 위한 메서드.
        시각적 분석을 포함하려면 analyze_patterns_with_cards 사용.
        """
        # 카드 없이는 시각적 분석 불가 - 빈 결과 반환
        return QueryExpansion(
            original_context={
                "place": place,
                "interaction_partner": interaction_partner,
                "current_activity": current_activity,
            },
            relevant_cards=[],
            context_hints=[],
            confidence=0.0,
        )

    async def analyze_patterns_with_cards(
        self,
        place: str,
        interaction_partner: str,
        current_activity: str,
        card_filenames: List[str],
        user_id: Optional[str] = None,
    ) -> CompositeQueryExpansion:
        """시각적 패턴 분석

        Args:
            place: 현재 장소
            interaction_partner: 대화 상대
            current_activity: 현재 활동
            card_filenames: 선택된 카드 파일명
            user_id: 사용자 ID

        Returns:
            시각적 분석 기반 쿼리 확장 결과
        """
        original_context = {
            "place": place,
            "interaction_partner": interaction_partner,
            "current_activity": current_activity,
        }

        if not card_filenames:
            return CompositeQueryExpansion(
                original_context=original_context,
                visual_confidence=0.0,
            )

        try:
            visual_expansion = await self._visual_analyzer.find_similar_patterns(
                card_filenames, user_id
            )
        except Exception as e:
            logger.warning("시각적 패턴 분석 실패: %s", e)
            return CompositeQueryExpansion(
                original_context=original_context,
                visual_confidence=0.0,
            )

        # 시각적 분석 결과에서 카드 및 힌트 추출
        card_scores: Dict[str, float] = {}
        context_hints: Set[str] = set()

        for pattern in visual_expansion.similar_patterns:
            pattern_score = pattern.combined_score
            pattern_cards = pattern.context.get("cards", [])

            if isinstance(pattern_cards, list):
                for card in pattern_cards:
                    if isinstance(card, str):
                        card_scores[card] = card_scores.get(card, 0) + pattern_score

            # 컨텍스트 힌트 추출
            if pattern.context.get("place"):
                context_hints.add(pattern.context["place"])
            if pattern.context.get("currentActivity"):
                context_hints.add(pattern.context["currentActivity"])

        # 점수순 정렬
        sorted_cards = sorted(
            card_scores.items(),
            key=lambda x: x[1],
            reverse=True,
        )
        relevant_cards = [card for card, _ in sorted_cards[:15]]

        return CompositeQueryExpansion(
            original_context=original_context,
            relevant_cards=relevant_cards,
            context_hints=list(context_hints)[:5],
            interpretation_hints=visual_expansion.interpretation_hints,
            visual_confidence=visual_expansion.visual_confidence,
        )

    async def get_successful_cards(
        self,
        place: str,
        interaction_partner: str,
        current_activity: str,
        top_k: int = 5,
    ) -> List[Tuple[str, float]]:
        """기존 인터페이스 호환 메서드

        카드 없이는 시각적 분석 불가 - 빈 결과 반환.
        """
        return []

    async def get_successful_cards_with_visual(
        self,
        place: str,
        interaction_partner: str,
        current_activity: str,
        card_filenames: List[str],
        user_id: Optional[str] = None,
        top_k: int = 5,
    ) -> List[Tuple[str, float]]:
        """시각적 분석을 포함한 성공 카드 검색

        Args:
            place: 현재 장소
            interaction_partner: 대화 상대
            current_activity: 현재 활동
            card_filenames: 현재 선택된 카드
            user_id: 사용자 ID
            top_k: 반환할 카드 수

        Returns:
            (카드명, 점수) 튜플 리스트
        """
        expansion = await self.analyze_patterns_with_cards(
            place, interaction_partner, current_activity, card_filenames, user_id
        )

        result: List[Tuple[str, float]] = []
        for i, card in enumerate(expansion.relevant_cards[:top_k]):
            score = 1.0 - i * 0.1
            result.append((card, max(0, score)))

        return result
