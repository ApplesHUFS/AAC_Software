"""임베딩 모델 클라이언트"""

from typing import Dict, List, Optional, Tuple
import json

import numpy as np
import torch
from sentence_transformers import SentenceTransformer

from app.config.settings import Settings


class EmbeddingClient:
    """문장 임베딩 및 유사도 계산 클라이언트"""

    def __init__(self, settings: Settings):
        self._settings = settings
        self._model: Optional[SentenceTransformer] = None
        self._cluster_tags: Optional[Dict[str, str]] = None
        self._cluster_embeddings: Optional[Dict[int, np.ndarray]] = None

    def _get_device(self) -> str:
        """사용할 디바이스 결정"""
        if self._settings.device == "auto":
            return "cuda" if torch.cuda.is_available() else "cpu"
        return self._settings.device

    def _load_model(self) -> SentenceTransformer:
        """모델 지연 로딩"""
        if self._model is None:
            device = self._get_device()
            self._model = SentenceTransformer(
                self._settings.similarity_model,
                device=device,
            )
        return self._model

    def _load_cluster_tags(self) -> Dict[str, str]:
        """클러스터 태그 로드"""
        if self._cluster_tags is None:
            try:
                path = self._settings.cluster_tags_path
                self._cluster_tags = json.loads(path.read_text(encoding="utf-8"))
            except (FileNotFoundError, json.JSONDecodeError):
                self._cluster_tags = {}
        return self._cluster_tags

    def _get_cluster_embeddings(self) -> Dict[int, np.ndarray]:
        """클러스터 태그 임베딩 계산 (캐싱)"""
        if self._cluster_embeddings is None:
            model = self._load_model()
            cluster_tags = self._load_cluster_tags()
            self._cluster_embeddings = {}

            for cluster_id_str, tag in cluster_tags.items():
                try:
                    cluster_id = int(cluster_id_str)
                    embedding = model.encode(tag, convert_to_numpy=True)
                    self._cluster_embeddings[cluster_id] = embedding
                except (ValueError, Exception):
                    continue

        return self._cluster_embeddings

    def calculate_similarity(self, text1: str, text2: str) -> float:
        """두 텍스트 간 코사인 유사도 계산"""
        model = self._load_model()
        embeddings = model.encode([text1, text2], convert_to_numpy=True)

        similarity = np.dot(embeddings[0], embeddings[1]) / (
            np.linalg.norm(embeddings[0]) * np.linalg.norm(embeddings[1])
        )
        return float(similarity)

    def calculate_text_cluster_similarities(
        self, text: str
    ) -> List[Tuple[int, float]]:
        """텍스트와 모든 클러스터 태그 간 유사도 계산"""
        model = self._load_model()
        cluster_embeddings = self._get_cluster_embeddings()

        if not cluster_embeddings:
            return []

        text_embedding = model.encode(text, convert_to_numpy=True)
        similarities: List[Tuple[int, float]] = []

        for cluster_id, cluster_embedding in cluster_embeddings.items():
            similarity = np.dot(text_embedding, cluster_embedding) / (
                np.linalg.norm(text_embedding) * np.linalg.norm(cluster_embedding)
            )
            similarities.append((cluster_id, float(similarity)))

        # 유사도 높은 순으로 정렬
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities

    async def calculate_preferred_categories(
        self,
        topics: List[str],
        similarity_threshold: float,
        max_categories: int,
    ) -> List[int]:
        """관심 주제 기반 선호 카테고리 계산"""
        if not topics:
            return []

        # 모든 주제에 대해 클러스터 유사도 계산
        cluster_scores: Dict[int, float] = {}

        for topic in topics:
            similarities = self.calculate_text_cluster_similarities(topic)
            for cluster_id, score in similarities:
                if score >= similarity_threshold:
                    cluster_scores[cluster_id] = max(
                        cluster_scores.get(cluster_id, 0), score
                    )

        # 점수 높은 순으로 정렬하여 상위 N개 반환
        sorted_clusters = sorted(
            cluster_scores.items(), key=lambda x: x[1], reverse=True
        )
        return [cluster_id for cluster_id, _ in sorted_clusters[:max_categories]]

    def get_context_similar_clusters(
        self,
        place: str,
        interaction_partner: str,
        current_activity: str,
        threshold: float,
        max_clusters: int,
    ) -> List[int]:
        """컨텍스트 정보 기반 유사 클러스터 조회"""
        context_text = f"{place} {interaction_partner} {current_activity}".strip()
        if not context_text:
            return []

        similarities = self.calculate_text_cluster_similarities(context_text)

        # 임계값 이상인 클러스터만 필터링
        filtered = [
            (cluster_id, score)
            for cluster_id, score in similarities
            if score >= threshold
        ]

        return [cluster_id for cluster_id, _ in filtered[:max_clusters]]
