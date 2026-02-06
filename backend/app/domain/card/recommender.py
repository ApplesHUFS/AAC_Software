"""카드 추천 엔진

CLIP 기반 5단계 시맨틱 추천 시스템 (LLM 필터 포함)
컨텍스트 → 벡터 검색 → MMR 다양성 → LLM 필터 → LLM 재순위 → 키워드 부스트
"""

from typing import TYPE_CHECKING, List, Optional, Set

from app.config.settings import Settings
from app.domain.card.entity import Card
from app.domain.card.filters.base import ICardFilter, ICardReranker
from app.domain.card.interfaces import SearchContext, ScoredCard
from app.domain.context.entity import Context
from app.domain.user.entity import User

if TYPE_CHECKING:
    from app.domain.card.clip_recommender import CLIPCardRecommender
    from app.infrastructure.external.openai_client import OpenAIClient


class CardRecommender:
    """CLIP 기반 카드 추천기 (LLM 필터 포함)

    5단계 추천 파이프라인:
    1. CLIP 벡터 검색: 컨텍스트와 시맨틱 유사도가 높은 카드 검색
    2. MMR 다양성 선택: 중복 방지, 다양한 카드 포함
    3. LLM 적합성 필터: 부적절한 카드 필터링
    4. LLM 재순위화: 컨텍스트 맞춤 순위 조정
    5. 키워드 부스트: 사용자 선호 키워드 반영

    Attributes:
        _settings: 애플리케이션 설정
        _openai_client: OpenAI 클라이언트 (LLM 필터용)
        _clip_recommender: CLIP 기반 추천기 (지연 초기화)
    """

    def __init__(
        self,
        settings: Settings,
        openai_client: Optional["OpenAIClient"] = None,
    ):
        self._settings = settings
        self._openai_client = openai_client
        self._clip_recommender: Optional["CLIPCardRecommender"] = None
        self._llm_filter: Optional[ICardFilter] = None
        self._llm_reranker: Optional[ICardReranker] = None

    def _get_clip_recommender(self) -> "CLIPCardRecommender":
        """CLIP 추천기 지연 초기화

        첫 호출 시에만 CLIP 모델과 벡터 인덱스 로드
        LLM 필터와 재순위화기도 함께 초기화
        """
        if self._clip_recommender is None:
            # 지연 임포트 (순환 임포트 방지)
            from app.domain.card.clip_recommender import (
                CLIPCardRecommender,
                RecommendationConfig,
            )
            from app.domain.card.diversity_selector import MMRDiversitySelector
            from app.domain.card.filters.factory import FilterFactory
            from app.domain.card.vector_searcher import create_vector_index
            from app.infrastructure.external.clip_client import CLIPEmbeddingClient

            clip_client = CLIPEmbeddingClient(self._settings)
            vector_index = create_vector_index(self._settings)
            diversity_selector = MMRDiversitySelector(vector_index)

            config = RecommendationConfig(
                semantic_weight=self._settings.semantic_weight,
                diversity_weight=self._settings.diversity_weight,
                persona_weight=self._settings.persona_weight,
                mmr_lambda=self._settings.mmr_lambda,
            )

            # LLM 필터 초기화
            if self._openai_client and self._settings.enable_llm_filter:
                filter_factory = FilterFactory(
                    settings=self._settings,
                    openai_client=self._openai_client,
                )
                self._llm_filter, self._llm_reranker = filter_factory.create_all()

            self._clip_recommender = CLIPCardRecommender(
                settings=self._settings,
                embedding_provider=clip_client,
                vector_index=vector_index,
                diversity_selector=diversity_selector,
                config=config,
                llm_filter=self._llm_filter,
                llm_reranker=self._llm_reranker,
            )

        return self._clip_recommender

    def recommend_cards(
        self,
        preferred_keywords: List[str],
        place: str,
        interaction_partner: str,
        current_activity: str,
        excluded_cards: Set[str],
    ) -> List[Card]:
        """동기 카드 추천 (LLM 필터 없음)

        LLM 필터가 필요한 경우 recommend_cards_async 사용
        """
        context = SearchContext(
            place=place,
            interaction_partner=interaction_partner,
            current_activity=current_activity,
            preferred_keywords=preferred_keywords,
            excluded_filenames=excluded_cards,
        )

        recommender = self._get_clip_recommender()
        scored_cards = recommender.recommend(
            context,
            self._settings.display_cards_total,
        )

        cards: List[Card] = []
        for i, sc in enumerate(scored_cards):
            sc.card.index = i
            cards.append(sc.card)

        return cards

    async def recommend_cards_async(
        self,
        preferred_keywords: List[str],
        place: str,
        interaction_partner: str,
        current_activity: str,
        excluded_cards: Set[str],
        user: Optional[User] = None,
        context_entity: Optional[Context] = None,
    ) -> List[Card]:
        """비동기 카드 추천 (LLM 필터 포함)

        Args:
            preferred_keywords: 사용자 선호 키워드 목록
            place: 장소 컨텍스트
            interaction_partner: 대화 상대
            current_activity: 현재 활동
            excluded_cards: 제외할 카드 파일명 집합
            user: 사용자 정보 (LLM 필터에 사용)
            context_entity: 컨텍스트 엔티티 (LLM 필터에 사용)

        Returns:
            추천된 카드 목록 (총 display_cards_total 개)
        """
        context = SearchContext(
            place=place,
            interaction_partner=interaction_partner,
            current_activity=current_activity,
            preferred_keywords=preferred_keywords,
            excluded_filenames=excluded_cards,
        )

        recommender = self._get_clip_recommender()
        scored_cards = await recommender.recommend_async(
            context,
            self._settings.display_cards_total,
            user=user,
            context_entity=context_entity,
        )

        cards: List[Card] = []
        for i, sc in enumerate(scored_cards):
            sc.card.index = i
            cards.append(sc.card)

        return cards
