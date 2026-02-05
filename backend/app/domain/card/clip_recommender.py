"""CLIP 기반 멀티모달 카드 추천 엔진

클러스터 없는 순수 CLIP 벡터 검색 기반 추천:
1. 시맨틱 검색: CLIP 공간에서 컨텍스트-이미지 직접 유사도 검색
2. 다양성 선택: MMR 알고리즘으로 중복 방지
3. 페르소나 부스트: 선호 키워드와의 유사도로 가산점
"""

import random
from dataclasses import dataclass
from typing import List, Optional, Set

import numpy as np

from app.config.settings import Settings
from app.domain.card.entity import Card
from app.domain.card.interfaces import (
    IDiversitySelector,
    IEmbeddingProvider,
    IRecommendationStrategy,
    IVectorIndex,
    SearchContext,
    ScoredCard,
)


@dataclass
class RecommendationConfig:
    """추천 알고리즘 설정"""
    semantic_weight: float = 0.6    # CLIP 컨텍스트 유사도 가중치
    diversity_weight: float = 0.2   # MMR 다양성 가중치
    persona_weight: float = 0.2     # 선호 키워드 유사도 가중치
    mmr_lambda: float = 0.7         # MMR 관련성-다양성 균형 (높을수록 관련성)
    candidate_multiplier: int = 5   # 초기 검색 배수


class CLIPCardRecommender(IRecommendationStrategy):
    """CLIP 기반 순수 벡터 검색 추천기

    클러스터 없이 직접 CLIP 임베딩 유사도로 카드 추천
    모든 매칭이 시맨틱 공간에서 직접 이루어짐

    Pipeline:
        1. 컨텍스트 → CLIP 인코딩 → 5,901개 이미지와 직접 유사도 검색
        2. MMR로 다양성 확보 (비슷한 이미지 중복 방지)
        3. 선호 키워드 유사도로 개인화 부스트
    """

    def __init__(
        self,
        settings: Settings,
        embedding_provider: IEmbeddingProvider,
        vector_index: IVectorIndex,
        diversity_selector: IDiversitySelector,
        config: Optional[RecommendationConfig] = None,
    ):
        self._settings = settings
        self._embedding = embedding_provider
        self._vector_index = vector_index
        self._diversity = diversity_selector
        self._config = config or RecommendationConfig(
            semantic_weight=settings.semantic_weight,
            diversity_weight=settings.diversity_weight,
            persona_weight=settings.persona_weight,
            mmr_lambda=settings.mmr_lambda,
        )

        # 선호 키워드 임베딩 캐시
        self._keyword_embedding_cache: dict = {}

    def get_strategy_name(self) -> str:
        return "CLIPDirectSearchRecommender"

    def recommend(
        self,
        context: SearchContext,
        count: int,
    ) -> List[ScoredCard]:
        """추천 파이프라인 실행

        Args:
            context: 검색 컨텍스트 (장소, 상대, 활동, 선호 키워드)
            count: 최종 추천 카드 수

        Returns:
            점수가 계산된 추천 카드 목록
        """
        # Stage 1: 시맨틱 검색
        candidates = self._stage1_semantic_search(context, count)

        if not candidates:
            return self._fallback_random_selection(context, count)

        # Stage 2: 다양성 선택
        diverse_candidates = self._stage2_diversity_selection(candidates, count)

        # Stage 3: 페르소나 부스트
        final_cards = self._stage3_persona_boost(diverse_candidates, context)

        return final_cards

    def _stage1_semantic_search(
        self,
        context: SearchContext,
        count: int,
    ) -> List[ScoredCard]:
        """Stage 1: CLIP 직접 시맨틱 검색

        컨텍스트를 자연어 문장으로 변환하여 CLIP 인코딩
        전체 이미지와 직접 유사도 검색
        """
        # 컨텍스트를 풍부한 쿼리로 변환
        query_text = self._build_rich_query(context)
        if not query_text.strip():
            return []

        # CLIP 텍스트 인코딩
        query_embedding = self._embedding.encode_text(query_text)

        # 제외할 인덱스 계산
        excluded_indices: Set[int] = set()
        for fn in context.excluded_filenames:
            idx = self._vector_index.get_index(fn)
            if idx is not None:
                excluded_indices.add(idx)

        # 후보 수 계산 (MMR을 위해 여유있게)
        candidate_count = count * self._config.candidate_multiplier

        # 벡터 검색 실행
        search_results = self._vector_index.search(
            query_embedding,
            candidate_count,
            excluded_indices,
        )

        # ScoredCard 객체로 변환
        scored_cards: List[ScoredCard] = []
        for idx, similarity in search_results:
            filename = self._vector_index.get_filename(idx)
            card = Card.from_filename(filename)

            scored_cards.append(
                ScoredCard(
                    card=card,
                    semantic_score=float(similarity),
                    diversity_score=0.0,
                    persona_score=0.0,
                    final_score=float(similarity),
                )
            )

        return scored_cards

    def _build_rich_query(self, context: SearchContext) -> str:
        """컨텍스트를 풍부한 자연어 쿼리로 변환

        단순 키워드 나열보다 문장 형태가 CLIP에 더 효과적
        """
        parts = []

        if context.place and context.place.strip():
            parts.append(context.place.strip())

        if context.interaction_partner and context.interaction_partner.strip():
            parts.append(f"{context.interaction_partner.strip()}와 함께")

        if context.current_activity and context.current_activity.strip():
            parts.append(context.current_activity.strip())

        if parts:
            return " ".join(parts) + " 상황에서 사용하는 의사소통 카드"

        return ""

    def _stage2_diversity_selection(
        self,
        candidates: List[ScoredCard],
        count: int,
    ) -> List[ScoredCard]:
        """Stage 2: MMR 기반 다양성 선택

        시맨틱 유사도가 높은 카드 중에서도
        서로 다른 의미의 카드들이 포함되도록 선택
        """
        selection_count = min(count * 2, len(candidates))

        diverse_cards = self._diversity.select_diverse(
            candidates,
            selection_count,
            lambda_param=self._config.mmr_lambda,
        )

        return diverse_cards

    def _stage3_persona_boost(
        self,
        candidates: List[ScoredCard],
        context: SearchContext,
    ) -> List[ScoredCard]:
        """Stage 3: 선호 키워드 기반 개인화 부스트

        사용자의 선호 키워드와 각 카드의 유사도를 계산하여 가산점
        """
        count = self._settings.display_cards_total

        # 선호 키워드가 있으면 부스트 적용
        if context.preferred_keywords:
            self._apply_keyword_boost(candidates, context.preferred_keywords)

        # 최종 점수 계산
        for sc in candidates:
            sc.compute_final_score(
                semantic_weight=self._config.semantic_weight,
                diversity_weight=self._config.diversity_weight,
                persona_weight=self._config.persona_weight,
            )

        # 최종 점수 기준 정렬
        candidates.sort(key=lambda sc: sc.rank_key)

        return candidates[:count]

    def _apply_keyword_boost(
        self,
        candidates: List[ScoredCard],
        keywords: List[str],
    ) -> None:
        """선호 키워드와의 유사도로 persona_score 계산"""
        if not keywords:
            return

        # 키워드 임베딩 (캐싱)
        keyword_embeddings = []
        for kw in keywords:
            if kw not in self._keyword_embedding_cache:
                self._keyword_embedding_cache[kw] = self._embedding.encode_text(kw)
            keyword_embeddings.append(self._keyword_embedding_cache[kw])

        keyword_embeddings = np.array(keyword_embeddings)

        # 각 카드에 대해 키워드 유사도 계산
        for sc in candidates:
            idx = self._vector_index.get_index(sc.card.filename)
            if idx is None:
                sc.persona_score = 0.0
                continue

            card_embedding = self._vector_index.get_vector(idx)

            # 모든 키워드와의 유사도 중 최대값
            similarities = keyword_embeddings @ card_embedding
            sc.persona_score = float(np.max(similarities))

    def _fallback_random_selection(
        self,
        context: SearchContext,
        count: int,
    ) -> List[ScoredCard]:
        """Fallback: 시맨틱 검색 실패 시 랜덤 선택"""
        all_filenames = self._vector_index.filenames

        available = [
            fn for fn in all_filenames
            if fn not in context.excluded_filenames
        ]

        if not available:
            return []

        selected = random.sample(available, min(count, len(available)))

        return [
            ScoredCard(
                card=Card.from_filename(fn),
                semantic_score=0.5,
                diversity_score=0.5,
                persona_score=0.5,
                final_score=0.5,
            )
            for fn in selected
        ]


class ContextAwareRecommender(IRecommendationStrategy):
    """컨텍스트 품질 인식 추천기

    컨텍스트 정보의 풍부함에 따라 추천 전략 조정
    """

    def __init__(
        self,
        clip_recommender: CLIPCardRecommender,
        min_context_quality: float = 0.3,
    ):
        self._clip = clip_recommender
        self._min_quality = min_context_quality

    def get_strategy_name(self) -> str:
        return "ContextAwareRecommender"

    def recommend(
        self,
        context: SearchContext,
        count: int,
    ) -> List[ScoredCard]:
        """컨텍스트 품질에 따른 추천"""
        quality = self._evaluate_context_quality(context)

        if quality >= self._min_quality:
            return self._clip.recommend(context, count)
        else:
            # 컨텍스트 부족 시 키워드 기반 fallback
            return self._keyword_based_recommendation(context, count)

    def _evaluate_context_quality(self, context: SearchContext) -> float:
        """컨텍스트 품질 점수 (0~1)"""
        score = 0.0

        if context.place and len(context.place.strip()) >= 2:
            score += 1.0
        if context.interaction_partner and len(context.interaction_partner.strip()) >= 2:
            score += 1.0
        if context.current_activity and len(context.current_activity.strip()) >= 2:
            score += 1.0

        return score / 3.0

    def _keyword_based_recommendation(
        self,
        context: SearchContext,
        count: int,
    ) -> List[ScoredCard]:
        """선호 키워드 기반 추천 (컨텍스트 부족 시)"""
        if context.preferred_keywords:
            # 키워드를 쿼리로 사용
            keyword_query = " ".join(context.preferred_keywords[:3])
            modified_context = SearchContext(
                place=keyword_query,
                interaction_partner="",
                current_activity="",
                preferred_keywords=context.preferred_keywords,
                excluded_filenames=context.excluded_filenames,
            )
            return self._clip.recommend(modified_context, count)
        else:
            return self._clip._fallback_random_selection(context, count)
