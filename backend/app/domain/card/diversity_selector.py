"""다양성 기반 카드 선택

Maximum Marginal Relevance (MMR) 알고리즘을 사용하여
관련성과 다양성의 균형을 맞춘 카드 선택 수행
"""

from typing import List, Optional

import numpy as np

from app.domain.card.interfaces import IDiversitySelector, IVectorIndex, ScoredCard


class MMRDiversitySelector(IDiversitySelector):
    """MMR 기반 다양성 선택기

    Maximum Marginal Relevance 알고리즘:
    MMR = argmax[λ × Sim(d, q) - (1-λ) × max(Sim(d, d_selected))]

    - 첫 번째 항: 쿼리와의 관련성 (높을수록 좋음)
    - 두 번째 항: 이미 선택된 문서와의 최대 유사도 (낮을수록 좋음 = 다양함)
    - λ: 관련성과 다양성 간의 균형 파라미터

    Attributes:
        _vector_index: 벡터 검색 인덱스
    """

    def __init__(self, vector_index: IVectorIndex):
        self._vector_index = vector_index

    def select_diverse(
        self,
        candidates: List[ScoredCard],
        count: int,
        lambda_param: float = 0.6,
    ) -> List[ScoredCard]:
        """MMR 알고리즘으로 다양한 부분집합 선택

        Args:
            candidates: 후보 카드 목록 (semantic_score가 설정되어 있어야 함)
            count: 선택할 카드 수
            lambda_param: 관련성(1.0) vs 다양성(0.0) 균형 파라미터

        Returns:
            다양성 점수가 계산된 선택 카드 목록
        """
        if not candidates:
            return []

        if len(candidates) <= count:
            # 후보가 충분하지 않으면 모두 반환
            for sc in candidates:
                sc.diversity_score = 1.0
            return candidates

        # 후보 임베딩 수집
        candidate_embeddings = self._collect_embeddings(candidates)
        if candidate_embeddings is None:
            # 임베딩을 찾을 수 없으면 semantic_score 기준 선택
            return self._fallback_selection(candidates, count)

        # 후보 간 유사도 행렬 사전 계산
        similarity_matrix = candidate_embeddings @ candidate_embeddings.T

        # MMR 반복 선택
        selected_cards = self._mmr_select(
            candidates,
            similarity_matrix,
            count,
            lambda_param,
        )

        return selected_cards

    def _collect_embeddings(
        self, candidates: List[ScoredCard]
    ) -> Optional[np.ndarray]:
        """후보 카드들의 임베딩 수집"""
        embeddings = []

        for sc in candidates:
            idx = self._vector_index.get_index(sc.card.filename)
            if idx is not None:
                embeddings.append(self._vector_index.get_vector(idx))
            else:
                # 임베딩을 찾을 수 없는 경우
                return None

        return np.array(embeddings, dtype=np.float32)

    def _mmr_select(
        self,
        candidates: List[ScoredCard],
        similarity_matrix: np.ndarray,
        count: int,
        lambda_param: float,
    ) -> List[ScoredCard]:
        """MMR 반복 선택 수행"""
        n = len(candidates)
        selected: List[ScoredCard] = []
        selected_indices: List[int] = []
        remaining = set(range(n))

        # 첫 번째 선택: 가장 높은 semantic_score
        first_idx = max(remaining, key=lambda i: candidates[i].semantic_score)
        first_card = candidates[first_idx]
        first_card.diversity_score = 1.0  # 첫 번째는 최대 다양성
        selected.append(first_card)
        selected_indices.append(first_idx)
        remaining.remove(first_idx)

        # 나머지 반복 선택
        while len(selected) < count and remaining:
            best_mmr_score = -np.inf
            best_idx: Optional[int] = None
            best_max_sim = 0.0

            for idx in remaining:
                # 관련성 점수 (쿼리와의 유사도)
                relevance = candidates[idx].semantic_score

                # 이미 선택된 문서들과의 최대 유사도
                max_sim_to_selected = max(
                    similarity_matrix[idx, sel_idx] for sel_idx in selected_indices
                )

                # MMR 점수 계산
                mmr_score = lambda_param * relevance - (1 - lambda_param) * max_sim_to_selected

                if mmr_score > best_mmr_score:
                    best_mmr_score = mmr_score
                    best_idx = idx
                    best_max_sim = max_sim_to_selected

            if best_idx is not None:
                best_card = candidates[best_idx]
                # 다양성 점수: 기존 선택과 얼마나 다른가 (0~1), 부동소수점 오차 보정
                best_card.diversity_score = float(np.clip(1.0 - best_max_sim, 0.0, 1.0))
                selected.append(best_card)
                selected_indices.append(best_idx)
                remaining.remove(best_idx)

        return selected

    def _fallback_selection(
        self, candidates: List[ScoredCard], count: int
    ) -> List[ScoredCard]:
        """임베딩 없이 fallback 선택"""
        # semantic_score 기준 상위 선택
        sorted_candidates = sorted(
            candidates, key=lambda sc: sc.semantic_score, reverse=True
        )
        selected = sorted_candidates[:count]
        for sc in selected:
            sc.diversity_score = 0.5
        return selected
