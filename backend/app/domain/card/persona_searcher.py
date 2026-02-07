"""페르소나 기반 카드 검색

사용자의 관심 주제(interesting_topics)를 기반으로
CLIP 벡터 검색을 수행하여 개인화된 카드 후보를 제공합니다.
"""

import logging
from typing import List, Optional, Set

from app.domain.card.entity import Card
from app.domain.card.interfaces import (
    IEmbeddingProvider,
    IVectorIndex,
    ScoredCard,
)

logger = logging.getLogger(__name__)


class PersonaSearcher:
    """사용자 관심 주제 기반 CLIP 검색

    interesting_topics 키워드를 쿼리로 변환하여
    사용자의 관심사와 관련된 카드를 검색합니다.
    """

    # 최대 쿼리 생성 개수
    MAX_KEYWORD_QUERIES = 5

    def __init__(
        self,
        embedding_provider: IEmbeddingProvider,
        vector_index: IVectorIndex,
    ):
        self._embedding = embedding_provider
        self._vector_index = vector_index

    def search(
        self,
        keywords: List[str],
        count: int,
        excluded_indices: Optional[Set[int]] = None,
    ) -> List[ScoredCard]:
        """관심 주제 기반 카드 검색

        Args:
            keywords: 사용자 관심 주제 목록
            count: 검색할 카드 수
            excluded_indices: 제외할 벡터 인덱스

        Returns:
            페르소나 관련 카드 목록 (persona_score=1.0 설정됨)
        """
        if not keywords:
            return []

        if excluded_indices is None:
            excluded_indices = set()

        queries = self._build_persona_queries(keywords)
        if not queries:
            return []

        seen_filenames: Set[str] = set()
        all_candidates: List[ScoredCard] = []

        for query in queries:
            if not query.strip():
                continue

            query_embedding = self._embedding.encode_text(query)

            search_results = self._vector_index.search(
                query_embedding,
                count,
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
                        persona_score=1.0,  # 페르소나 검색 출처 표시
                        final_score=float(similarity),
                    )
                )

        # 유사도 내림차순 정렬 후 상위 N개 반환
        all_candidates.sort(key=lambda sc: -sc.semantic_score)

        logger.debug(
            "페르소나 검색: %d개 쿼리로 %d개 후보 검색",
            len(queries), len(all_candidates)
        )

        return all_candidates[:count]

    def _build_persona_queries(self, keywords: List[str]) -> List[str]:
        """관심 주제를 검색 쿼리로 변환

        Args:
            keywords: 사용자 관심 주제 목록

        Returns:
            CLIP 검색용 쿼리 목록
        """
        queries: List[str] = []

        # 개별 키워드 쿼리 (최대 MAX_KEYWORD_QUERIES개)
        for kw in keywords[:self.MAX_KEYWORD_QUERIES]:
            kw = kw.strip()
            if kw:
                queries.append(f"{kw} 관련 의사소통 카드")

        # 복합 쿼리 (상위 키워드 조합)
        if len(keywords) >= 2:
            combined = " ".join(kw.strip() for kw in keywords[:3] if kw.strip())
            if combined:
                queries.append(f"{combined} 관련 의사소통 카드")

        return queries
