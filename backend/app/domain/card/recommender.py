"""카드 추천 엔진

CLIP 기반 3단계 시맨틱 추천 시스템
컨텍스트 → 벡터 검색 → MMR 다양성 → 키워드 부스트
"""

from typing import List, Optional, Set

from app.config.settings import Settings
from app.domain.card.entity import Card
from app.domain.card.interfaces import SearchContext, ScoredCard
from app.domain.card.clip_recommender import CLIPCardRecommender, RecommendationConfig
from app.domain.card.vector_searcher import create_vector_index
from app.domain.card.diversity_selector import MMRDiversitySelector
from app.infrastructure.external.clip_client import CLIPEmbeddingClient


class CardRecommender:
    """CLIP 기반 카드 추천기

    3단계 추천 파이프라인:
    1. CLIP 벡터 검색: 컨텍스트와 시맨틱 유사도가 높은 카드 검색
    2. MMR 다양성 선택: 중복 방지, 다양한 카드 포함
    3. 키워드 부스트: 사용자 선호 키워드 반영

    Attributes:
        _settings: 애플리케이션 설정
        _clip_recommender: CLIP 기반 추천기 (지연 초기화)
    """

    def __init__(self, settings: Settings):
        self._settings = settings
        self._clip_recommender: Optional[CLIPCardRecommender] = None

    def _get_clip_recommender(self) -> CLIPCardRecommender:
        """CLIP 추천기 지연 초기화

        첫 호출 시에만 CLIP 모델과 벡터 인덱스 로드
        """
        if self._clip_recommender is None:
            clip_client = CLIPEmbeddingClient(self._settings)
            vector_index = create_vector_index(self._settings)
            diversity_selector = MMRDiversitySelector(vector_index)

            config = RecommendationConfig(
                semantic_weight=self._settings.semantic_weight,
                diversity_weight=self._settings.diversity_weight,
                persona_weight=self._settings.persona_weight,
                mmr_lambda=self._settings.mmr_lambda,
            )

            self._clip_recommender = CLIPCardRecommender(
                settings=self._settings,
                embedding_provider=clip_client,
                vector_index=vector_index,
                diversity_selector=diversity_selector,
                config=config,
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
        """카드 추천 실행

        Args:
            preferred_keywords: 사용자 선호 키워드 목록
            place: 장소 컨텍스트
            interaction_partner: 대화 상대
            current_activity: 현재 활동
            excluded_cards: 제외할 카드 파일명 집합

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
        scored_cards = recommender.recommend(
            context,
            self._settings.display_cards_total,
        )

        # ScoredCard에서 Card 추출 및 인덱스 할당
        cards: List[Card] = []
        for i, sc in enumerate(scored_cards):
            sc.card.index = i
            cards.append(sc.card)

        return cards
