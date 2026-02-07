"""LLM 기반 검색 쿼리 재작성 + 피드백 기반 확장

원본 컨텍스트를 여러 검색 쿼리로 확장하여
더 다양한 카드 후보를 확보합니다.

Graceful Degradation: LLM 실패 시 원본 쿼리만 사용

연구적 접근: Contextual Relevance Feedback
- 과거 피드백에서 유사 상황 패턴 학습
- 성공적인 카드 선택 패턴을 쿼리에 반영
"""

import logging
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, List, Optional

from app.core.exceptions import LLMRateLimitError, LLMServiceError, LLMTimeoutError

if TYPE_CHECKING:
    from app.domain.feedback.analyzer import IFeedbackAnalyzer
    from app.infrastructure.external.openai_client import OpenAIClient

logger = logging.getLogger(__name__)

# LLM 에러 타입 튜플 (Graceful Degradation 적용 대상)
LLM_ERRORS = (LLMServiceError, LLMTimeoutError, LLMRateLimitError)


class IQueryRewriter(ABC):
    """쿼리 재작성 인터페이스"""

    @abstractmethod
    async def rewrite(
        self,
        place: str,
        interaction_partner: str,
        current_activity: str,
    ) -> List[str]:
        """컨텍스트를 여러 검색 쿼리로 확장

        Args:
            place: 장소
            interaction_partner: 대화 상대
            current_activity: 현재 활동

        Returns:
            검색 쿼리 목록 (원본 + 확장)
        """
        pass


class LLMQueryRewriter(IQueryRewriter):
    """GPT-4.1-mini 기반 쿼리 재작성

    원본 컨텍스트를 LLM으로 분석하여
    동의어, 관련어, 확장 표현을 생성합니다.
    """

    def __init__(
        self,
        openai_client: "OpenAIClient",
        query_count: int = 3,
    ):
        self._openai = openai_client
        self._query_count = query_count

    async def rewrite(
        self,
        place: str,
        interaction_partner: str,
        current_activity: str,
    ) -> List[str]:
        """원본 컨텍스트를 다양한 검색 쿼리로 확장

        Graceful Degradation: LLM 실패 시 원본 쿼리만 반환

        Returns:
            [원본 쿼리, 확장 쿼리1, 확장 쿼리2, ...]
        """
        original_query = self._build_original_query(
            place, interaction_partner, current_activity
        )

        try:
            expanded_queries = await self._openai.rewrite_query(
                place=place,
                partner=interaction_partner,
                activity=current_activity,
                count=self._query_count,
            )

            if expanded_queries:
                logger.info(
                    f"쿼리 재작성: 원본 1개 + 확장 {len(expanded_queries)}개"
                )
                return [original_query] + expanded_queries

        except LLM_ERRORS as e:
            logger.warning(f"쿼리 재작성 실패, Graceful Degradation 적용: {e}")

        except Exception as e:
            logger.warning(f"쿼리 재작성 예상치 못한 오류, 원본만 사용: {e}")

        return [original_query]

    def _build_original_query(
        self,
        place: str,
        interaction_partner: str,
        current_activity: str,
    ) -> str:
        """원본 컨텍스트를 검색 쿼리로 변환"""
        parts = []

        if place and place.strip():
            parts.append(place.strip())

        if interaction_partner and interaction_partner.strip():
            parts.append(f"{interaction_partner.strip()}와 함께")

        if current_activity and current_activity.strip():
            parts.append(current_activity.strip())

        if parts:
            return " ".join(parts) + " 상황에서 사용하는 의사소통 카드"

        return "일상생활 의사소통 카드"


class NoOpQueryRewriter(IQueryRewriter):
    """쿼리 재작성 비활성화 시 사용하는 No-op 구현"""

    async def rewrite(
        self,
        place: str,
        interaction_partner: str,
        current_activity: str,
    ) -> List[str]:
        """원본 쿼리만 반환"""
        parts = []

        if place and place.strip():
            parts.append(place.strip())

        if interaction_partner and interaction_partner.strip():
            parts.append(f"{interaction_partner.strip()}와 함께")

        if current_activity and current_activity.strip():
            parts.append(current_activity.strip())

        if parts:
            return [" ".join(parts) + " 상황에서 사용하는 의사소통 카드"]

        return ["일상생활 의사소통 카드"]


class FeedbackAwareQueryRewriter(IQueryRewriter):
    """피드백 기반 컨텍스트 학습 쿼리 재작성기

    Contextual Relevance Feedback 알고리즘을 적용하여
    과거 성공적인 피드백 패턴을 쿼리에 반영합니다.

    연구적 노벨티:
    1. Historical Pattern Mining: 유사 상황의 과거 성공 패턴 활용
    2. Implicit Relevance Signals: 선택된 해석에서 의도 추론
    3. Hybrid Query Expansion: LLM 확장 + 피드백 기반 확장 결합
    """

    def __init__(
        self,
        openai_client: "OpenAIClient",
        feedback_analyzer: "IFeedbackAnalyzer",
        query_count: int = 3,
        feedback_weight: float = 0.4,
    ):
        self._openai = openai_client
        self._feedback_analyzer = feedback_analyzer
        self._query_count = query_count
        self._feedback_weight = feedback_weight

    async def rewrite(
        self,
        place: str,
        interaction_partner: str,
        current_activity: str,
    ) -> List[str]:
        """피드백 패턴을 반영한 쿼리 확장

        Returns:
            [원본 쿼리, LLM 확장 쿼리들, 피드백 기반 쿼리]
        """
        original_query = self._build_original_query(
            place, interaction_partner, current_activity
        )

        queries = [original_query]

        # 1. 피드백 패턴 분석
        expansion = await self._feedback_analyzer.analyze_patterns(
            place=place,
            interaction_partner=interaction_partner,
            current_activity=current_activity,
        )

        # 2. 피드백 기반 쿼리 생성 (신뢰도가 충분할 때)
        if expansion.confidence >= 0.3 and expansion.relevant_cards:
            feedback_query = self._build_feedback_query(expansion)
            if feedback_query:
                queries.append(feedback_query)
                logger.info(
                    f"피드백 기반 쿼리 생성: 신뢰도 {expansion.confidence:.2f}, "
                    f"관련 카드 {len(expansion.relevant_cards)}개"
                )

        # 3. LLM 기반 쿼리 확장 (Graceful Degradation 적용)
        try:
            expanded_queries = await self._openai.rewrite_query(
                place=place,
                partner=interaction_partner,
                activity=current_activity,
                count=self._query_count,
                context_hints=expansion.context_hints if expansion.confidence > 0 else None,
            )

            if expanded_queries:
                queries.extend(expanded_queries)
                logger.info(
                    f"쿼리 재작성: 원본 1개 + 피드백 {1 if expansion.confidence >= 0.3 else 0}개 "
                    f"+ LLM 확장 {len(expanded_queries)}개"
                )

        except LLM_ERRORS as e:
            logger.warning(f"LLM 쿼리 확장 실패, Graceful Degradation 적용: {e}")

        except Exception as e:
            logger.warning(f"LLM 쿼리 확장 예상치 못한 오류: {e}")

        return queries

    def _build_original_query(
        self,
        place: str,
        interaction_partner: str,
        current_activity: str,
    ) -> str:
        """원본 컨텍스트를 검색 쿼리로 변환"""
        parts = []

        if place and place.strip():
            parts.append(place.strip())

        if interaction_partner and interaction_partner.strip():
            parts.append(f"{interaction_partner.strip()}와 함께")

        if current_activity and current_activity.strip():
            parts.append(current_activity.strip())

        if parts:
            return " ".join(parts) + " 상황에서 사용하는 의사소통 카드"

        return "일상생활 의사소통 카드"

    def _build_feedback_query(self, expansion) -> Optional[str]:
        """피드백 패턴에서 쿼리 생성

        과거 성공 패턴의 카드명을 쿼리에 포함하여
        유사한 카드를 검색합니다.
        """
        if not expansion.relevant_cards:
            return None

        # 카드명에서 핵심 키워드 추출
        keywords = []
        for card in expansion.relevant_cards[:3]:
            # 카드명 정제 (숫자_이름.png 형식 처리)
            name = card.rsplit(".", 1)[0]  # 확장자 제거
            if "_" in name:
                name = name.split("_", 1)[1]  # 숫자 제거
            keywords.append(name)

        if keywords:
            return f"이전 상황에서 사용한 {', '.join(keywords)} 관련 의사소통 카드"

        return None
