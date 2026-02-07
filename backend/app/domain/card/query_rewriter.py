"""LLM 기반 검색 쿼리 재작성

원본 컨텍스트를 여러 검색 쿼리로 확장하여
더 다양한 카드 후보를 확보합니다.
"""

import logging
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from app.infrastructure.external.openai_client import OpenAIClient

logger = logging.getLogger(__name__)


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

        except Exception as e:
            logger.warning(f"쿼리 재작성 실패, 원본만 사용: {e}")

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
