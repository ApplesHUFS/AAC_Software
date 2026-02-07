"""필터 팩토리 (DIP)

설정에 따라 적절한 필터 인스턴스를 생성합니다.
의존성 역전 원칙을 준수하여 고수준 모듈이
저수준 구현에 직접 의존하지 않도록 합니다.
"""

from typing import Optional, Tuple

from app.config.settings import Settings
from app.domain.card.filters.base import ICardFilter, ICardReranker
from app.domain.card.filters.llm_filter import LLMCardFilter
from app.domain.card.filters.llm_reranker import LLMCardReranker
from app.infrastructure.external.openai_client import OpenAIClient


class FilterFactory:
    """필터 팩토리

    설정에 따라 LLM 필터와 재순위화기를 생성합니다.
    """

    def __init__(
        self,
        settings: Settings,
        openai_client: OpenAIClient,
    ):
        self._settings = settings
        self._openai_client = openai_client

    def create_filter(self) -> Optional[ICardFilter]:
        """카드 필터 생성

        settings.enable_llm_filter가 True이면 LLMCardFilter 반환
        False이면 None 반환 (필터링 비활성화)
        """
        if not self._settings.enable_llm_filter:
            return None

        return LLMCardFilter(
            openai_client=self._openai_client,
            batch_size=self._settings.filter_batch_size,
            fallback_config=self._settings.age_appropriateness,
        )

    def create_reranker(self) -> Optional[ICardReranker]:
        """카드 재순위화기 생성

        settings.enable_llm_reranker가 True이면 LLMCardReranker 반환
        False이면 None 반환 (재순위화 비활성화)
        """
        if not self._settings.enable_llm_reranker:
            return None

        return LLMCardReranker(
            openai_client=self._openai_client,
            batch_size=self._settings.rerank_batch_size,
        )

    def create_all(self) -> Tuple[Optional[ICardFilter], Optional[ICardReranker]]:
        """필터와 재순위화기 모두 생성"""
        return self.create_filter(), self.create_reranker()
