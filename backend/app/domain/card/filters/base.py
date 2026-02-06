"""카드 필터 인터페이스 정의

SOLID 원칙 기반 추상화:
- SRP: 각 필터는 단일 책임 (적합성 평가 또는 재순위화)
- OCP: 새로운 필터 추가 시 기존 코드 수정 불필요
- DIP: 고수준 모듈은 추상화에 의존
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set

from app.domain.card.interfaces import ScoredCard
from app.domain.context.entity import Context
from app.domain.user.entity import User


@dataclass
class FilterContext:
    """필터에 전달되는 통합 컨텍스트

    사용자 정보와 현재 상황을 캡슐화하여
    LLM 필터에 필요한 모든 정보를 제공
    """

    user: User
    context: Context
    excluded_filenames: Set[str] = field(default_factory=set)

    def to_user_summary(self) -> str:
        """사용자 정보 요약"""
        return (
            f"{self.user.age}세 {self.user.gender}, "
            f"{self.user.disability_type}, "
            f"의사소통 특성: {self.user.communication_characteristics}"
        )

    def to_context_summary(self) -> str:
        """상황 정보 요약"""
        parts = []
        if self.context.place:
            parts.append(f"장소: {self.context.place}")
        if self.context.interaction_partner:
            parts.append(f"대화 상대: {self.context.interaction_partner}")
        if self.context.current_activity:
            parts.append(f"활동: {self.context.current_activity}")
        return ", ".join(parts) if parts else "정보 없음"


@dataclass
class FilterResult:
    """필터 결과

    필터링 후 적합/부적합 카드와 이유를 포함
    """

    appropriate_cards: List[ScoredCard]
    inappropriate_cards: List[Dict[str, str]] = field(default_factory=list)
    highly_relevant_cards: List[str] = field(default_factory=list)

    @property
    def filtered_count(self) -> int:
        """필터링된 카드 수"""
        return len(self.inappropriate_cards)

    @property
    def remaining_count(self) -> int:
        """남은 카드 수"""
        return len(self.appropriate_cards)


class ICardFilter(ABC):
    """카드 필터 인터페이스 (OCP)

    카드 적합성을 평가하고 부적절한 카드를 필터링
    구현체: LLMCardFilter
    """

    @abstractmethod
    async def filter_cards(
        self,
        candidates: List[ScoredCard],
        filter_ctx: FilterContext,
    ) -> FilterResult:
        """카드 필터링 실행

        Args:
            candidates: 필터링할 카드 목록
            filter_ctx: 사용자/컨텍스트 정보

        Returns:
            적합한 카드와 필터링 결과
        """
        pass

    @abstractmethod
    def get_filter_name(self) -> str:
        """필터 식별자"""
        pass


class ICardReranker(ABC):
    """카드 재순위화 인터페이스 (SRP)

    필터링된 카드들의 순위를 컨텍스트에 맞게 재조정
    구현체: LLMCardReranker
    """

    @abstractmethod
    async def rerank_cards(
        self,
        candidates: List[ScoredCard],
        filter_ctx: FilterContext,
    ) -> List[ScoredCard]:
        """카드 재순위화 실행

        Args:
            candidates: 재순위화할 카드 목록
            filter_ctx: 사용자/컨텍스트 정보

        Returns:
            재순위화된 카드 목록
        """
        pass

    @abstractmethod
    def get_reranker_name(self) -> str:
        """재순위화기 식별자"""
        pass
