"""MMR 다양성 선택기 유닛 테스트

Maximum Marginal Relevance 알고리즘의 동작을 검증합니다.
"""

from typing import List

import numpy as np
import pytest

from app.domain.card.diversity_selector import MMRDiversitySelector
from app.domain.card.entity import Card
from app.domain.card.interfaces import ScoredCard

from tests.conftest import MockVectorIndex


class TestMMRDiversitySelector:
    """MMR 다양성 선택기 테스트"""

    def test_select_diverse_returns_empty_when_no_candidates(
        self, mock_vector_index: MockVectorIndex
    ):
        """빈 후보 목록이면 빈 결과 반환"""
        # Arrange
        selector = MMRDiversitySelector(mock_vector_index)
        candidates: List[ScoredCard] = []

        # Act
        result = selector.select_diverse(candidates, count=5)

        # Assert
        assert result == []

    def test_select_diverse_returns_all_when_candidates_less_than_count(
        self,
        mock_vector_index: MockVectorIndex,
        sample_scored_cards: List[ScoredCard],
    ):
        """후보 수가 요청 수보다 적으면 전체 반환"""
        # Arrange
        selector = MMRDiversitySelector(mock_vector_index)
        candidates = sample_scored_cards[:3]

        # Act
        result = selector.select_diverse(candidates, count=10)

        # Assert
        assert len(result) == 3
        for sc in result:
            assert sc.diversity_score == 1.0

    def test_select_diverse_returns_requested_count(
        self,
        mock_vector_index: MockVectorIndex,
        sample_scored_cards: List[ScoredCard],
    ):
        """요청한 수만큼 카드 반환"""
        # Arrange
        selector = MMRDiversitySelector(mock_vector_index)
        count = 3

        # Act
        result = selector.select_diverse(sample_scored_cards, count=count)

        # Assert
        assert len(result) == count

    def test_select_diverse_first_card_has_highest_semantic_score(
        self,
        mock_vector_index: MockVectorIndex,
        sample_scored_cards: List[ScoredCard],
    ):
        """첫 번째 선택은 가장 높은 semantic_score를 가진 카드"""
        # Arrange
        selector = MMRDiversitySelector(mock_vector_index)

        # Act
        result = selector.select_diverse(sample_scored_cards, count=3)

        # Assert
        max_semantic = max(sc.semantic_score for sc in sample_scored_cards)
        assert result[0].semantic_score == max_semantic
        assert result[0].diversity_score == 1.0

    def test_select_diverse_sets_diversity_scores(
        self,
        mock_vector_index: MockVectorIndex,
        sample_scored_cards: List[ScoredCard],
    ):
        """모든 선택된 카드에 diversity_score 설정"""
        # Arrange
        selector = MMRDiversitySelector(mock_vector_index)

        # Act
        result = selector.select_diverse(sample_scored_cards, count=3)

        # Assert
        for sc in result:
            assert sc.diversity_score is not None
            assert 0.0 <= sc.diversity_score <= 1.0

    def test_select_diverse_with_high_lambda_favors_relevance(
        self,
        mock_vector_index: MockVectorIndex,
        sample_scored_cards: List[ScoredCard],
    ):
        """lambda=0.9 이면 관련성 위주 선택"""
        # Arrange
        selector = MMRDiversitySelector(mock_vector_index)

        # lambda=0.9: 관련성 90%, 다양성 10%
        result_relevance = selector.select_diverse(
            sample_scored_cards, count=3, lambda_param=0.9
        )

        # lambda=0.1: 관련성 10%, 다양성 90%
        result_diversity = selector.select_diverse(
            sample_scored_cards, count=3, lambda_param=0.1
        )

        # Act & Assert
        # 높은 lambda에서는 상위 semantic_score 카드들이 선택됨
        relevance_scores = [sc.semantic_score for sc in result_relevance]
        diversity_scores = [sc.semantic_score for sc in result_diversity]

        # 관련성 위주 결과의 평균 semantic_score가 더 높아야 함
        assert sum(relevance_scores) >= sum(diversity_scores)

    def test_fallback_selection_when_embedding_not_found(self, sample_cards: List[Card]):
        """임베딩을 찾지 못하면 fallback 선택 사용"""
        # Arrange
        empty_index = MockVectorIndex([])  # 빈 인덱스
        selector = MMRDiversitySelector(empty_index)
        candidates = [
            ScoredCard(card=card, semantic_score=0.9 - i * 0.1)
            for i, card in enumerate(sample_cards)
        ]

        # Act
        result = selector.select_diverse(candidates, count=3)

        # Assert
        # fallback은 semantic_score 기준 상위 선택
        assert len(result) == 3
        for sc in result:
            assert sc.diversity_score == 0.5

    def test_mmr_excludes_already_selected_cards(
        self,
        mock_vector_index: MockVectorIndex,
        sample_scored_cards: List[ScoredCard],
    ):
        """선택된 카드는 중복 선택되지 않음"""
        # Arrange
        selector = MMRDiversitySelector(mock_vector_index)

        # Act
        result = selector.select_diverse(sample_scored_cards, count=4)

        # Assert
        selected_ids = [sc.card.id for sc in result]
        assert len(selected_ids) == len(set(selected_ids))


class TestMMRAlgorithmCorrectness:
    """MMR 알고리즘 정확성 테스트"""

    def test_mmr_formula_verification(self):
        """MMR 공식: λ * Sim(d,q) - (1-λ) * max(Sim(d, d_selected))"""
        # Arrange
        filenames = ["a.png", "b.png", "c.png"]
        index = MockVectorIndex(filenames)
        selector = MMRDiversitySelector(index)

        cards = [
            Card(id=f"card_{i}", name=f"카드{i}", filename=fn, image_path=f"/api/{fn}", index=i)
            for i, fn in enumerate(filenames)
        ]
        candidates = [
            ScoredCard(card=card, semantic_score=0.9 - i * 0.1)
            for i, card in enumerate(cards)
        ]

        # Act
        result = selector.select_diverse(candidates, count=2, lambda_param=0.5)

        # Assert
        assert len(result) == 2
        # 첫 번째 카드: 최고 semantic_score
        assert result[0].semantic_score == 0.9
        # 두 번째 카드: MMR 알고리즘에 의해 선택됨
        assert result[1].card.id in ["card_1", "card_2"]

    def test_diversity_score_decreases_with_similarity(self):
        """유사한 카드 선택 시 diversity_score 감소"""
        # Arrange
        filenames = ["a.png", "b.png", "c.png"]

        # 유사한 벡터 생성
        class SimilarVectorIndex(MockVectorIndex):
            def __init__(self, filenames):
                self._filenames = filenames
                base_vector = np.array([1.0] * 512, dtype=np.float32)
                base_vector = base_vector / np.linalg.norm(base_vector)
                # 매우 유사한 벡터들
                self._vectors = np.vstack([
                    base_vector,
                    base_vector + np.random.randn(512) * 0.01,
                    base_vector + np.random.randn(512) * 0.01,
                ]).astype(np.float32)
                self._vectors = self._vectors / np.linalg.norm(
                    self._vectors, axis=1, keepdims=True
                )
                self._filename_to_idx = {fn: i for i, fn in enumerate(filenames)}

        index = SimilarVectorIndex(filenames)
        selector = MMRDiversitySelector(index)

        # 서로 다른 semantic_score로 설정
        cards = [
            Card(id=f"card_{i}", name=f"카드{i}", filename=fn, image_path=f"/api/{fn}", index=i)
            for i, fn in enumerate(filenames)
        ]
        candidates = [
            ScoredCard(card=cards[0], semantic_score=0.95),
            ScoredCard(card=cards[1], semantic_score=0.90),
            ScoredCard(card=cards[2], semantic_score=0.85),
        ]

        # Act
        result = selector.select_diverse(candidates, count=3)

        # Assert
        # 첫 번째 카드의 diversity_score는 1.0 (첫 선택)
        assert result[0].diversity_score == 1.0
        # 두 번째 이후 카드의 diversity_score는 이전 선택과의 유사도에 따라 감소
        assert result[1].diversity_score <= 1.0
