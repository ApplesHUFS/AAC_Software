"""OpenAI 클라이언트 모듈

기능별로 분리된 클라이언트를 조합하여 제공:
- CardInterpreter: 카드 해석 및 대화 요약
- CardFilterReranker: 카드 필터링 및 재순위화
- QueryRewriter: 쿼리 재작성
- OpenAIClient: 통합 클라이언트 (하위 호환성)
"""

from typing import TYPE_CHECKING, Any, Dict, List, Optional
from pathlib import Path

from app.config.settings import Settings

from .base import OpenAIClientBase
from .interpreter import CardInterpreter
from .filter_reranker import CardFilterReranker
from .query_rewriter import QueryRewriter

if TYPE_CHECKING:
    from app.domain.feedback.visual_analyzer import IVisualPatternAnalyzer


class OpenAIClient(OpenAIClientBase):
    """OpenAI 통합 클라이언트 (하위 호환성 유지)

    기능별 클라이언트를 조합하여 기존 인터페이스 제공.
    시각적 패턴 분석기가 제공되면 해석 시 개인화된 힌트 활용.
    """

    def __init__(
        self,
        settings: Settings,
        visual_analyzer: Optional["IVisualPatternAnalyzer"] = None,
    ):
        super().__init__(settings)
        self._interpreter = CardInterpreter(settings, visual_analyzer)
        self._filter_reranker = CardFilterReranker(settings)
        self._query_rewriter = QueryRewriter(settings)

    # CardInterpreter 위임
    async def interpret_cards(
        self,
        card_images: List[Dict[str, Any]],
        user_persona: Dict[str, Any],
        context: Dict[str, Any],
        memory_summary: Optional[str] = None,
        max_retries: int = 3,
    ) -> List[str]:
        """카드 해석"""
        return await self._interpreter.interpret_cards(
            card_images, user_persona, context, memory_summary, max_retries
        )

    async def summarize_conversation(
        self,
        conversation_history: List[Dict[str, Any]],
    ) -> str:
        """대화 요약"""
        return await self._interpreter.summarize_conversation(conversation_history)

    # CardFilterReranker 위임
    async def filter_cards(
        self,
        prompt: str,
        max_retries: Optional[int] = None,
    ) -> Dict[str, Any]:
        """카드 필터링"""
        return await self._filter_reranker.filter_cards(prompt, max_retries)

    async def rerank_cards(
        self,
        prompt: str,
        max_retries: Optional[int] = None,
    ) -> Dict[str, Any]:
        """카드 재순위화"""
        return await self._filter_reranker.rerank_cards(prompt, max_retries)

    # QueryRewriter 위임
    async def rewrite_query(
        self,
        place: str,
        partner: str,
        activity: str,
        count: int = 3,
        context_hints: Optional[List[str]] = None,
    ) -> List[str]:
        """쿼리 재작성"""
        return await self._query_rewriter.rewrite_query(
            place, partner, activity, count, context_hints
        )


__all__ = [
    "OpenAIClient",
    "OpenAIClientBase",
    "CardInterpreter",
    "CardFilterReranker",
    "QueryRewriter",
]
