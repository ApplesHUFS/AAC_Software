"""카드 추천 시스템 인터페이스 정의

SOLID 원칙 기반 추상화:
- SRP: 각 인터페이스는 단일 책임을 가짐
- OCP: 새로운 구현 추가 시 기존 코드 수정 불필요
- LSP: 구현체는 인터페이스 계약을 완전히 준수
- ISP: 클라이언트는 사용하지 않는 메서드에 의존하지 않음
- DIP: 고수준 모듈은 추상화에 의존

클러스터 없는 순수 CLIP 벡터 검색 아키텍처
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional, Set, Tuple

import numpy as np

from app.domain.card.entity import Card


@dataclass
class SearchContext:
    """추천 검색 컨텍스트

    사용자의 현재 상황과 선호도를 캡슐화하여
    추천 엔진에 전달하는 데이터 객체
    """
    place: str
    interaction_partner: str
    current_activity: str
    preferred_keywords: List[str] = field(default_factory=list)
    excluded_filenames: Set[str] = field(default_factory=set)

    def to_query_text(self) -> str:
        """컨텍스트를 검색 쿼리 텍스트로 변환"""
        parts = [self.place, self.interaction_partner, self.current_activity]
        return " ".join(p for p in parts if p and p.strip())

    def to_rich_query(self) -> str:
        """풍부한 자연어 쿼리 생성 (CLIP에 최적화)"""
        parts = []
        if self.place and self.place.strip():
            parts.append(self.place.strip())
        if self.interaction_partner and self.interaction_partner.strip():
            parts.append(f"{self.interaction_partner.strip()}와 함께")
        if self.current_activity and self.current_activity.strip():
            parts.append(self.current_activity.strip())

        if parts:
            return " ".join(parts) + " 상황에서 사용하는 의사소통 카드"
        return ""

    def has_valid_context(self) -> bool:
        """유효한 컨텍스트가 있는지 확인"""
        return bool(self.to_query_text().strip())


@dataclass
class ScoredCard:
    """점수가 부여된 카드

    추천 파이프라인의 각 단계에서 계산된 점수를 보유
    최종 순위 결정에 사용됨
    """
    card: Card
    semantic_score: float = 0.0   # CLIP 컨텍스트 유사도
    diversity_score: float = 0.0  # MMR 다양성 기여도
    persona_score: float = 0.0    # 선호 키워드 유사도
    final_score: float = 0.0      # 가중 합산 최종 점수

    @property
    def rank_key(self) -> Tuple[float, str]:
        """정렬 키 (내림차순 점수, 파일명)"""
        return (-self.final_score, self.card.filename)

    def compute_final_score(
        self,
        semantic_weight: float,
        diversity_weight: float,
        persona_weight: float,
    ) -> None:
        """가중치 기반 최종 점수 계산"""
        self.final_score = (
            semantic_weight * self.semantic_score
            + diversity_weight * self.diversity_score
            + persona_weight * self.persona_score
        )


class IEmbeddingProvider(ABC):
    """임베딩 생성 인터페이스 (ISP)

    텍스트를 벡터 공간으로 인코딩하는 책임만 담당
    구현체: CLIPEmbeddingClient
    """

    @abstractmethod
    def encode_text(self, text: str) -> np.ndarray:
        """단일 텍스트를 임베딩 벡터로 인코딩

        Args:
            text: 인코딩할 텍스트

        Returns:
            L2 정규화된 임베딩 벡터
        """
        pass

    @abstractmethod
    def encode_texts_batch(self, texts: List[str]) -> np.ndarray:
        """여러 텍스트를 배치로 인코딩

        Args:
            texts: 인코딩할 텍스트 목록

        Returns:
            (N, D) 형태의 임베딩 행렬
        """
        pass

    @abstractmethod
    def get_embedding_dimension(self) -> int:
        """임베딩 차원 반환"""
        pass


class IVectorIndex(ABC):
    """벡터 검색 인덱스 인터페이스 (DIP)

    사전 계산된 CLIP 임베딩에 대한 유사도 검색 담당
    구현체: NumpyVectorIndex
    """

    @abstractmethod
    def search(
        self,
        query_vector: np.ndarray,
        top_k: int,
        excluded_indices: Optional[Set[int]] = None,
    ) -> List[Tuple[int, float]]:
        """유사 벡터 검색

        Args:
            query_vector: 쿼리 벡터
            top_k: 반환할 결과 수
            excluded_indices: 제외할 인덱스 집합

        Returns:
            (인덱스, 유사도) 튜플 목록, 유사도 내림차순
        """
        pass

    @abstractmethod
    def get_vector(self, index: int) -> np.ndarray:
        """인덱스로 벡터 조회"""
        pass

    @abstractmethod
    def get_all_vectors(self) -> np.ndarray:
        """전체 벡터 행렬 반환"""
        pass

    @abstractmethod
    def get_filename(self, index: int) -> str:
        """인덱스에 해당하는 파일명 반환"""
        pass

    @abstractmethod
    def get_index(self, filename: str) -> Optional[int]:
        """파일명에 해당하는 인덱스 반환"""
        pass

    @property
    @abstractmethod
    def size(self) -> int:
        """인덱스에 저장된 벡터 수"""
        pass

    @property
    @abstractmethod
    def filenames(self) -> List[str]:
        """전체 파일명 목록"""
        pass


class IRecommendationStrategy(ABC):
    """추천 전략 인터페이스 (OCP)

    다양한 추천 알고리즘을 플러그인 방식으로 교체 가능
    구현체: CLIPCardRecommender, ContextAwareRecommender
    """

    @abstractmethod
    def recommend(
        self,
        context: SearchContext,
        count: int,
    ) -> List[ScoredCard]:
        """컨텍스트 기반 카드 추천

        Args:
            context: 검색 컨텍스트
            count: 추천할 카드 수

        Returns:
            점수가 부여된 추천 카드 목록
        """
        pass

    @abstractmethod
    def get_strategy_name(self) -> str:
        """전략 식별자 반환"""
        pass


class IDiversitySelector(ABC):
    """다양성 선택 인터페이스 (SRP)

    후보 집합에서 다양성을 보장하며 선택하는 책임 담당
    구현체: MMRDiversitySelector
    """

    @abstractmethod
    def select_diverse(
        self,
        candidates: List[ScoredCard],
        count: int,
        lambda_param: float = 0.5,
    ) -> List[ScoredCard]:
        """다양성을 고려한 부분집합 선택

        Args:
            candidates: 후보 카드 목록
            count: 선택할 카드 수
            lambda_param: 관련성(1.0) vs 다양성(0.0) 균형

        Returns:
            다양성 점수가 업데이트된 선택 카드 목록
        """
        pass


class ICardRepository(ABC):
    """카드 저장소 인터페이스 (DIP)

    카드 파일 접근을 추상화
    """

    @abstractmethod
    def get_all_filenames(self) -> List[str]:
        """전체 카드 파일명 목록 반환"""
        pass

    @abstractmethod
    def get_card_by_filename(self, filename: str) -> Optional[Card]:
        """파일명으로 카드 조회"""
        pass
