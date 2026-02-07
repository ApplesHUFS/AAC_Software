"""CLIP 기반 멀티모달 카드 추천 엔진

클러스터 없는 순수 CLIP 벡터 검색 + LLM 필터링 기반 추천:
1. 시맨틱 검색: CLIP 공간에서 컨텍스트-이미지 직접 유사도 검색
2. 다양성 선택: MMR 알고리즘으로 중복 방지
3. LLM 적합성 필터: GPT-4o 기반 부적절 카드 필터링
4. LLM 재순위화: GPT-4o 기반 컨텍스트 맞춤 재순위
5. 페르소나 부스트: 선호 키워드와의 유사도로 가산점
"""

import logging
import random
from dataclasses import dataclass
from typing import List, Optional, Set

import numpy as np

from app.config.settings import Settings
from app.domain.card.entity import Card
from app.domain.card.filters.base import FilterContext, ICardFilter, ICardReranker
from app.domain.card.interfaces import (
    IDiversitySelector,
    IEmbeddingProvider,
    IRecommendationStrategy,
    IVectorIndex,
    SearchContext,
    ScoredCard,
)
from app.domain.card.query_rewriter import IQueryRewriter
from app.domain.context.entity import Context
from app.domain.user.entity import User

logger = logging.getLogger(__name__)


@dataclass
class RecommendationConfig:
    """추천 알고리즘 설정"""
    semantic_weight: float = 0.6    # CLIP 컨텍스트 유사도 가중치
    diversity_weight: float = 0.2   # MMR 다양성 가중치
    persona_weight: float = 0.2     # 선호 키워드 유사도 가중치
    mmr_lambda: float = 0.7         # MMR 관련성-다양성 균형 (높을수록 관련성)
    candidate_multiplier: int = 10  # Stage 1 초기 검색 배수
    diversity_multiplier: int = 4   # Stage 2 MMR 선택 배수


class CLIPCardRecommender(IRecommendationStrategy):
    """CLIP 기반 순수 벡터 검색 + LLM 필터링 추천기

    클러스터 없이 직접 CLIP 임베딩 유사도로 카드 추천
    LLM(GPT-4o)을 활용한 적합성 필터링 및 재순위화

    Pipeline:
        1. 컨텍스트 → CLIP 인코딩 → 5,901개 이미지와 직접 유사도 검색
        2. MMR로 다양성 확보 (비슷한 이미지 중복 방지)
        3. [NEW] LLM 적합성 필터 (부적절 카드 제거)
        4. [NEW] LLM 재순위화 (컨텍스트 맞춤 순위)
        5. 선호 키워드 유사도로 개인화 부스트
    """

    def __init__(
        self,
        settings: Settings,
        embedding_provider: IEmbeddingProvider,
        vector_index: IVectorIndex,
        diversity_selector: IDiversitySelector,
        config: Optional[RecommendationConfig] = None,
        llm_filter: Optional[ICardFilter] = None,
        llm_reranker: Optional[ICardReranker] = None,
        query_rewriter: Optional[IQueryRewriter] = None,
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
            candidate_multiplier=settings.initial_search_multiplier,
            diversity_multiplier=settings.diversity_selection_multiplier,
        )

        # LLM 필터 및 재순위화기
        self._llm_filter = llm_filter
        self._llm_reranker = llm_reranker

        # 쿼리 재작성기
        self._query_rewriter = query_rewriter

        # 선호 키워드 임베딩 캐시
        self._keyword_embedding_cache: dict = {}

    def get_strategy_name(self) -> str:
        return "CLIPDirectSearchRecommender"

    def recommend(
        self,
        context: SearchContext,
        count: int,
    ) -> List[ScoredCard]:
        """동기 추천 파이프라인 (LLM 필터 없음)

        LLM 필터가 필요한 경우 recommend_async 사용
        """
        candidates = self._stage1_semantic_search(context, count)

        if not candidates:
            return self._fallback_random_selection(context, count)

        diverse_candidates = self._stage2_diversity_selection(candidates, count)
        final_cards = self._stage5_persona_boost(diverse_candidates, context)

        return final_cards

    async def recommend_async(
        self,
        context: SearchContext,
        count: int,
        user: Optional[User] = None,
        context_entity: Optional[Context] = None,
    ) -> List[ScoredCard]:
        """비동기 추천 파이프라인 (LLM 필터 포함, 카드 수 보장)

        Args:
            context: 검색 컨텍스트 (장소, 상대, 활동, 선호 키워드)
            count: 최종 추천 카드 수
            user: 사용자 정보 (LLM 필터에 사용)
            context_entity: 컨텍스트 엔티티 (LLM 필터에 사용)

        Returns:
            점수가 계산된 추천 카드 목록 (count개 보장)
        """
        # Stage 1: 다중 쿼리 시맨틱 검색 (CLIP + Query Rewriting)
        candidates = await self._stage1_semantic_search_async(context, count)

        if not candidates:
            return self._fallback_random_selection(context, count)

        # Stage 2: 다양성 선택 (MMR)
        diverse_candidates = self._stage2_diversity_selection(candidates, count)

        # Stage 3: LLM 적합성 필터 (GPT-4o) + Backfill
        filtered_candidates = await self._stage3_llm_filter_with_backfill(
            diverse_candidates=diverse_candidates,
            all_candidates=candidates,
            user=user,
            context_entity=context_entity,
            target_count=count,
        )

        # Stage 4: LLM 재순위화 (GPT-4o)
        reranked_candidates = await self._stage4_llm_rerank(
            filtered_candidates, user, context_entity
        )

        # Stage 5: 페르소나 부스트
        final_cards = self._stage5_persona_boost(reranked_candidates, context)

        return final_cards

    async def _stage3_llm_filter(
        self,
        candidates: List[ScoredCard],
        user: Optional[User],
        context_entity: Optional[Context],
    ) -> List[ScoredCard]:
        """Stage 3: LLM 적합성 필터 (단순 버전, 카드 수 보장 없음)

        GPT-4o를 사용하여 사용자 나이, 장애유형, 상황에
        부적절한 카드를 필터링합니다.
        """
        if not self._llm_filter or not user or not context_entity:
            return candidates

        try:
            filter_ctx = FilterContext(
                user=user,
                context=context_entity,
                excluded_filenames=set(),
            )

            result = await self._llm_filter.filter_cards(candidates, filter_ctx)

            if result.appropriate_cards:
                logger.info(
                    f"LLM 필터: {result.remaining_count}개 적합, "
                    f"{result.filtered_count}개 필터링됨"
                )
                return result.appropriate_cards

        except Exception as e:
            logger.warning(f"LLM 필터 오류, 원본 반환: {e}")

        return candidates

    async def _stage3_llm_filter_with_backfill(
        self,
        diverse_candidates: List[ScoredCard],
        all_candidates: List[ScoredCard],
        user: Optional[User],
        context_entity: Optional[Context],
        target_count: int,
    ) -> List[ScoredCard]:
        """Stage 3: LLM 적합성 필터 + Backfill Strategy

        LLM 필터링 후 카드 수가 목표 미만이면 예비 후보에서 보충합니다.
        이 방식은 필터링 품질을 유지하면서 카드 수를 보장합니다.

        Args:
            diverse_candidates: MMR로 선택된 다양성 후보
            all_candidates: Stage 1에서 검색된 전체 후보
            user: 사용자 정보
            context_entity: 컨텍스트 엔티티
            target_count: 목표 카드 수

        Returns:
            target_count개의 적합 카드 (가능한 한)
        """
        if not self._llm_filter or not user or not context_entity:
            return diverse_candidates

        # 필터링에 이미 사용된 파일명 추적
        processed_filenames: Set[str] = {
            sc.card.filename for sc in diverse_candidates
        }

        # 백필용 예비 후보 준비 (MMR 선택에서 제외된 카드들)
        reserve_candidates = [
            sc for sc in all_candidates
            if sc.card.filename not in processed_filenames
        ]

        try:
            filter_ctx = FilterContext(
                user=user,
                context=context_entity,
                excluded_filenames=set(),
            )

            # 1차 필터링
            result = await self._llm_filter.filter_cards(
                diverse_candidates, filter_ctx
            )
            appropriate_cards = result.appropriate_cards or []

            # 카드 수가 충분하면 바로 반환
            if len(appropriate_cards) >= target_count:
                logger.info(
                    f"LLM 필터: {len(appropriate_cards)}개 적합 (목표 달성)"
                )
                return appropriate_cards

            # Backfill 필요: 예비 후보에서 추가 카드 확보
            deficit = target_count - len(appropriate_cards)
            logger.info(
                f"LLM 필터: {len(appropriate_cards)}개 적합, "
                f"{deficit}개 부족 → Backfill 시작"
            )

            # 이미 적합 판정된 파일명
            appropriate_filenames = {sc.card.filename for sc in appropriate_cards}

            # 예비 후보를 배치로 필터링
            backfill_batch_size = min(deficit * 3, len(reserve_candidates))

            if backfill_batch_size > 0 and reserve_candidates:
                backfill_batch = reserve_candidates[:backfill_batch_size]

                backfill_result = await self._llm_filter.filter_cards(
                    backfill_batch, filter_ctx
                )

                if backfill_result.appropriate_cards:
                    for sc in backfill_result.appropriate_cards:
                        if sc.card.filename not in appropriate_filenames:
                            appropriate_cards.append(sc)
                            appropriate_filenames.add(sc.card.filename)

                            if len(appropriate_cards) >= target_count:
                                break

            logger.info(
                f"Backfill 완료: 최종 {len(appropriate_cards)}개 카드"
            )

            # 여전히 부족하면 필터링 없이 예비 후보 추가 (최후의 수단)
            if len(appropriate_cards) < target_count:
                remaining_reserve = [
                    sc for sc in reserve_candidates
                    if sc.card.filename not in appropriate_filenames
                ]

                for sc in remaining_reserve:
                    appropriate_cards.append(sc)
                    if len(appropriate_cards) >= target_count:
                        break

                logger.warning(
                    f"Backfill 후에도 부족, 비필터 카드 추가: "
                    f"최종 {len(appropriate_cards)}개"
                )

            return appropriate_cards

        except Exception as e:
            logger.warning(f"LLM 필터 + Backfill 오류, 원본 반환: {e}")
            return diverse_candidates

    async def _stage4_llm_rerank(
        self,
        candidates: List[ScoredCard],
        user: Optional[User],
        context_entity: Optional[Context],
    ) -> List[ScoredCard]:
        """Stage 4: LLM 재순위화

        GPT-4o를 사용하여 현재 상황에 맞게
        카드 순위를 최적화합니다.
        """
        if not self._llm_reranker or not user or not context_entity:
            return candidates

        try:
            filter_ctx = FilterContext(
                user=user,
                context=context_entity,
                excluded_filenames=set(),
            )

            reranked = await self._llm_reranker.rerank_cards(candidates, filter_ctx)

            if reranked:
                logger.info(f"LLM 재순위화: {len(reranked)}개 카드 순위 조정됨")
                return reranked

        except Exception as e:
            logger.warning(f"LLM 재순위화 오류, 원본 반환: {e}")

        return candidates

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

    async def _stage1_semantic_search_async(
        self,
        context: SearchContext,
        count: int,
    ) -> List[ScoredCard]:
        """Stage 1: 다중 쿼리 CLIP 시맨틱 검색

        쿼리 재작성이 활성화된 경우 여러 쿼리로 검색하여
        더 다양한 후보를 확보합니다.
        """
        # 쿼리 생성 (재작성 또는 원본)
        if self._query_rewriter:
            queries = await self._query_rewriter.rewrite(
                context.place or "",
                context.interaction_partner or "",
                context.current_activity or "",
            )
        else:
            queries = [self._build_rich_query(context)]

        if not queries or not any(q.strip() for q in queries):
            return []

        # 제외할 인덱스 계산
        excluded_indices: Set[int] = set()
        for fn in context.excluded_filenames:
            idx = self._vector_index.get_index(fn)
            if idx is not None:
                excluded_indices.add(idx)

        # 후보 수 계산
        candidate_count = count * self._config.candidate_multiplier

        # 다중 쿼리로 검색 (중복 제거)
        seen_filenames: Set[str] = set()
        all_candidates: List[ScoredCard] = []

        for query in queries:
            if not query.strip():
                continue

            query_embedding = self._embedding.encode_text(query)

            search_results = self._vector_index.search(
                query_embedding,
                candidate_count,
                excluded_indices,
            )

            for idx, similarity in search_results:
                filename = self._vector_index.get_filename(idx)

                if filename in seen_filenames:
                    continue

                seen_filenames.add(filename)
                card = Card.from_filename(filename)

                all_candidates.append(
                    ScoredCard(
                        card=card,
                        semantic_score=float(similarity),
                        diversity_score=0.0,
                        persona_score=0.0,
                        final_score=float(similarity),
                    )
                )

        # 점수순 정렬 후 상위 N개 반환
        all_candidates.sort(key=lambda sc: sc.semantic_score, reverse=True)

        logger.info(
            f"Stage 1: {len(queries)}개 쿼리로 {len(all_candidates)}개 후보 검색"
        )

        return all_candidates[:candidate_count]

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
        selection_count = min(
            count * self._config.diversity_multiplier,
            len(candidates),
        )

        diverse_cards = self._diversity.select_diverse(
            candidates,
            selection_count,
            lambda_param=self._config.mmr_lambda,
        )

        logger.info(f"Stage 2: {len(diverse_cards)}개 다양성 선택 완료")

        return diverse_cards

    def _stage5_persona_boost(
        self,
        candidates: List[ScoredCard],
        context: SearchContext,
    ) -> List[ScoredCard]:
        """Stage 5: 선호 키워드 기반 개인화 부스트

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
