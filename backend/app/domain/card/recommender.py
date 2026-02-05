"""카드 추천 엔진"""

import random
from typing import Dict, List, Set

from app.config.settings import Settings
from app.domain.card.entity import Card
from app.infrastructure.external.embedding_client import EmbeddingClient
from app.infrastructure.persistence.json_repository import JsonCardRepository


class CardRecommender:
    """카드 추천 비즈니스 로직"""

    def __init__(
        self,
        settings: Settings,
        embedding_client: EmbeddingClient,
        card_repository: JsonCardRepository,
    ):
        self._settings = settings
        self._embedding = embedding_client
        self._card_repo = card_repository

    def recommend_cards(
        self,
        user_preferred_clusters: List[int],
        place: str,
        interaction_partner: str,
        current_activity: str,
        excluded_cards: Set[str],
    ) -> List[Card]:
        """
        페르소나와 컨텍스트 기반 카드 추천

        Args:
            user_preferred_clusters: 사용자 선호 클러스터 ID 목록
            place: 장소
            interaction_partner: 대화 상대
            current_activity: 현재 활동
            excluded_cards: 제외할 카드 파일명 집합

        Returns:
            추천된 카드 목록 (총 display_cards_total 개)
        """
        total_cards = self._settings.display_cards_total
        context_ratio = self._settings.context_persona_ratio

        # 컨텍스트 기반 카드 수
        context_card_count = int(total_cards * context_ratio)
        persona_card_count = total_cards - context_card_count

        # 컨텍스트 기반 추천
        context_clusters = self._embedding.get_context_similar_clusters(
            place=place,
            interaction_partner=interaction_partner,
            current_activity=current_activity,
            threshold=self._settings.context_similarity_threshold,
            max_clusters=self._settings.context_max_clusters,
        )

        context_cards = self._get_cards_from_clusters(
            context_clusters, context_card_count, excluded_cards
        )

        # 페르소나 기반 추천
        persona_cards = self._get_cards_from_clusters(
            user_preferred_clusters,
            persona_card_count,
            excluded_cards | {c.filename for c in context_cards},
        )

        # 결과 병합 및 섞기
        all_cards = context_cards + persona_cards
        random.shuffle(all_cards)

        # 인덱스 할당
        for i, card in enumerate(all_cards):
            card.index = i

        return all_cards

    def _get_cards_from_clusters(
        self,
        cluster_ids: List[int],
        count: int,
        excluded: Set[str],
    ) -> List[Card]:
        """지정된 클러스터들에서 카드 선택"""
        if not cluster_ids or count <= 0:
            return []

        candidates: List[Card] = []

        for cluster_id in cluster_ids:
            cluster_cards = self._card_repo.get_cards_by_cluster(cluster_id)
            for card in cluster_cards:
                if card.filename not in excluded:
                    candidates.append(card)

        # 부족하면 전체 카드에서 보충
        if len(candidates) < count:
            all_cards = self._card_repo.get_all_cards()
            for card in all_cards:
                if card.filename not in excluded and card not in candidates:
                    candidates.append(card)
                    if len(candidates) >= count * 2:
                        break

        # 랜덤 선택
        if len(candidates) <= count:
            return candidates

        return random.sample(candidates, count)
