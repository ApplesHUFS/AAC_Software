"""복합 피드백 분석기

텍스트 기반 TF-IDF 분석과 시각적 패턴 분석을 통합하여
더 정확한 피드백 기반 추천을 제공합니다.
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
    """복합 쿼리 확장 결과

    텍스트 및 시각적 분석 결과를 통합한 쿼리 확장 정보

    Attributes:
        original_context: 원본 컨텍스트
        relevant_cards: 관련 카드 파일명 (텍스트 + 시각적 분석 통합)
        context_hints: 컨텍스트 힌트 (텍스트 분석)
        interpretation_hints: 해석 힌트 (시각적 분석)
        text_confidence: 텍스트 분석 신뢰도
        visual_confidence: 시각적 분석 신뢰도
        combined_confidence: 통합 신뢰도
    """

    original_context: Dict[str, str] = field(default_factory=dict)
    relevant_cards: List[str] = field(default_factory=list)
    context_hints: List[str] = field(default_factory=list)
    interpretation_hints: List[str] = field(default_factory=list)
    text_confidence: float = 0.0
    visual_confidence: float = 0.0
    combined_confidence: float = 0.0


class CompositeFeedbackAnalyzer(IFeedbackAnalyzer):
    """텍스트 + 시각적 분석 통합 분석기

    DIP: 추상화에 의존 (IFeedbackAnalyzer, IVisualPatternAnalyzer)
    SRP: 분석 통합 및 조율만 담당, 실제 분석은 위임
    OCP: 새로운 분석 전략 추가 시 기존 코드 수정 불필요

    Attributes:
        _text_analyzer: 텍스트 기반 분석기
        _visual_analyzer: 시각적 패턴 분석기
        _text_weight: 텍스트 분석 가중치
        _visual_weight: 시각적 분석 가중치
    """

    def __init__(
        self,
        text_analyzer: IFeedbackAnalyzer,
        visual_analyzer: Optional[IVisualPatternAnalyzer] = None,
        text_weight: float = 0.4,
        visual_weight: float = 0.6,
    ):
        self._text_analyzer = text_analyzer
        self._visual_analyzer = visual_analyzer
        self._text_weight = text_weight
        self._visual_weight = visual_weight

    async def analyze_patterns(
        self,
        place: str,
        interaction_partner: str,
        current_activity: str,
        user_id: Optional[str] = None,
    ) -> QueryExpansion:
        """기존 인터페이스 호환 분석 (텍스트만)

        IFeedbackAnalyzer 인터페이스 준수를 위한 메서드.
        시각적 분석을 포함하려면 analyze_patterns_with_cards 사용.
        """
        return await self._text_analyzer.analyze_patterns(
            place, interaction_partner, current_activity, user_id
        )

    async def analyze_patterns_with_cards(
        self,
        place: str,
        interaction_partner: str,
        current_activity: str,
        card_filenames: List[str],
        user_id: Optional[str] = None,
    ) -> CompositeQueryExpansion:
        """텍스트 + 시각적 복합 분석

        Args:
            place: 현재 장소
            interaction_partner: 대화 상대
            current_activity: 현재 활동
            card_filenames: 선택된 카드 파일명
            user_id: 사용자 ID

        Returns:
            통합된 쿼리 확장 결과
        """
        # 텍스트 분석 (기존 TF-IDF)
        text_expansion = await self._text_analyzer.analyze_patterns(
            place, interaction_partner, current_activity, user_id
        )

        # 시각적 분석 (새로운 CLIP 기반)
        visual_expansion: Optional[VisualQueryExpansion] = None
        if self._visual_analyzer and card_filenames:
            try:
                visual_expansion = await self._visual_analyzer.find_similar_patterns(
                    card_filenames, user_id
                )
            except Exception as e:
                logger.warning("시각적 패턴 분석 실패: %s", e)

        return self._merge_expansions(text_expansion, visual_expansion)

    def _merge_expansions(
        self,
        text_expansion: QueryExpansion,
        visual_expansion: Optional[VisualQueryExpansion],
    ) -> CompositeQueryExpansion:
        """텍스트와 시각적 분석 결과 통합

        가중치를 적용하여 카드 우선순위를 조정합니다.
        """
        # 카드 점수 맵 (파일명 -> 점수)
        card_scores: Dict[str, float] = {}

        # 텍스트 분석에서 추천된 카드 (순서대로 감소하는 점수)
        for i, card in enumerate(text_expansion.relevant_cards):
            score = self._text_weight * (1.0 - i * 0.1)
            card_scores[card] = card_scores.get(card, 0) + max(0, score)

        # 시각적 분석에서 추천된 카드
        interpretation_hints: List[str] = []
        visual_confidence = 0.0

        if visual_expansion:
            visual_confidence = visual_expansion.visual_confidence
            interpretation_hints = visual_expansion.interpretation_hints

            # 시각적 패턴에서 관련 카드 점수 추가
            for pattern in visual_expansion.similar_patterns:
                pattern_score = pattern.combined_score * self._visual_weight
                for card in pattern.context.get("cards", []):
                    if isinstance(card, str):
                        card_scores[card] = card_scores.get(card, 0) + pattern_score

        # 점수순 정렬
        sorted_cards = sorted(
            card_scores.items(),
            key=lambda x: x[1],
            reverse=True,
        )
        relevant_cards = [card for card, _ in sorted_cards[:15]]

        # 통합 신뢰도 계산
        combined_confidence = (
            self._text_weight * text_expansion.confidence
            + self._visual_weight * visual_confidence
        )

        return CompositeQueryExpansion(
            original_context=text_expansion.original_context,
            relevant_cards=relevant_cards,
            context_hints=text_expansion.context_hints,
            interpretation_hints=interpretation_hints,
            text_confidence=text_expansion.confidence,
            visual_confidence=visual_confidence,
            combined_confidence=combined_confidence,
        )

    async def get_successful_cards(
        self,
        place: str,
        interaction_partner: str,
        current_activity: str,
        top_k: int = 5,
    ) -> List[Tuple[str, float]]:
        """기존 인터페이스 호환 메서드"""
        return await self._text_analyzer.get_successful_cards(
            place, interaction_partner, current_activity, top_k
        )

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

        # 점수와 함께 반환
        result: List[Tuple[str, float]] = []
        for i, card in enumerate(expansion.relevant_cards[:top_k]):
            score = 1.0 - i * 0.1  # 순위 기반 점수
            result.append((card, max(0, score)))

        return result
