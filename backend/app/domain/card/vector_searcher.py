"""벡터 검색 인덱스

사전 계산된 CLIP 임베딩에 대한 효율적인 유사도 검색
- FaissVectorIndex: FAISS 기반 고성능 검색 (기본값)
- NumpyVectorIndex: NumPy 기반 브루트포스 검색 (fallback)
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

import faiss
import numpy as np

from app.config.settings import Settings
from app.domain.card.interfaces import IVectorIndex


class FaissVectorIndex(IVectorIndex):
    """FAISS 기반 벡터 검색 인덱스

    Inner Product (IP) 인덱스를 사용하여 정규화된 벡터에 대해
    코사인 유사도 검색 수행. IndexFlatIP는 정확한 검색을 보장.

    대규모 데이터셋의 경우 IndexIVFFlat이나 IndexHNSWFlat으로
    교체하여 근사 검색 가능 (현재 규모에서는 불필요)

    Attributes:
        _index: FAISS 인덱스
        _embeddings: 원본 임베딩 (get_vector 지원용)
        _filenames: 인덱스에 대응하는 파일명 목록
        _filename_to_index: 파일명 → 인덱스 역매핑
    """

    def __init__(self, settings: Settings):
        self._settings = settings
        self._index: Optional[faiss.Index] = None
        self._embeddings: Optional[np.ndarray] = None
        self._filenames: Optional[List[str]] = None
        self._filename_to_index: Optional[Dict[str, int]] = None

    def _load_embeddings(self) -> None:
        """임베딩 로드 및 FAISS 인덱스 구축"""
        if self._index is not None:
            return

        embeddings_path = self._settings.embeddings_path

        with open(embeddings_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self._filenames = data["filenames"]

        # 이미지 및 텍스트 임베딩 로드
        img_embeddings = np.array(data["image_embeddings"], dtype=np.float32)
        txt_embeddings = np.array(data["text_embeddings"], dtype=np.float32)

        # 임베딩 융합
        image_weight = self._settings.clip_image_weight
        self._embeddings = (
            image_weight * img_embeddings + (1 - image_weight) * txt_embeddings
        )

        # L2 정규화 (IP로 코사인 유사도 계산)
        faiss.normalize_L2(self._embeddings)

        # FAISS 인덱스 생성 (Inner Product = 코사인 유사도 for normalized vectors)
        dimension = self._embeddings.shape[1]
        self._index = faiss.IndexFlatIP(dimension)
        self._index.add(self._embeddings)

        # 역인덱스 구축
        self._filename_to_index = {fn: i for i, fn in enumerate(self._filenames)}

    def search(
        self,
        query_vector: np.ndarray,
        top_k: int,
        excluded_indices: Optional[Set[int]] = None,
    ) -> List[Tuple[int, float]]:
        """FAISS 기반 코사인 유사도 검색

        Args:
            query_vector: 쿼리 임베딩 (1D)
            top_k: 반환할 최대 결과 수
            excluded_indices: 결과에서 제외할 인덱스

        Returns:
            (인덱스, 유사도) 튜플 목록, 유사도 내림차순 정렬
        """
        self._load_embeddings()

        # 쿼리 정규화 및 reshape
        query = query_vector.astype(np.float32).reshape(1, -1)
        faiss.normalize_L2(query)

        # 제외 인덱스가 있으면 더 많이 검색 후 필터링
        search_k = top_k
        if excluded_indices:
            search_k = min(top_k + len(excluded_indices) * 2, self._index.ntotal)

        # FAISS 검색
        similarities, indices = self._index.search(query, search_k)

        # 결과 필터링 및 변환
        results: List[Tuple[int, float]] = []
        for idx, sim in zip(indices[0], similarities[0]):
            if idx < 0:  # FAISS returns -1 for invalid results
                continue
            if excluded_indices and int(idx) in excluded_indices:
                continue
            results.append((int(idx), float(sim)))
            if len(results) >= top_k:
                break

        return results

    def get_vector(self, index: int) -> np.ndarray:
        """인덱스로 벡터 조회"""
        self._load_embeddings()
        if 0 <= index < len(self._embeddings):
            return self._embeddings[index].copy()
        raise IndexError(f"Index {index} out of range")

    def get_all_vectors(self) -> np.ndarray:
        """전체 임베딩 행렬 반환"""
        self._load_embeddings()
        return self._embeddings

    def get_filename(self, index: int) -> str:
        """인덱스에 해당하는 파일명 반환"""
        self._load_embeddings()
        if 0 <= index < len(self._filenames):
            return self._filenames[index]
        raise IndexError(f"Index {index} out of range")

    def get_index(self, filename: str) -> Optional[int]:
        """파일명에 해당하는 인덱스 반환"""
        self._load_embeddings()
        return self._filename_to_index.get(filename)

    @property
    def size(self) -> int:
        """인덱스 크기"""
        self._load_embeddings()
        return self._index.ntotal

    @property
    def filenames(self) -> List[str]:
        """파일명 목록 접근"""
        self._load_embeddings()
        return self._filenames


class NumpyVectorIndex(IVectorIndex):
    """NumPy 기반 벡터 검색 인덱스 (fallback)

    FAISS를 사용할 수 없는 환경에서의 대체 구현
    """

    def __init__(self, settings: Settings):
        self._settings = settings
        self._embeddings: Optional[np.ndarray] = None
        self._filenames: Optional[List[str]] = None
        self._filename_to_index: Optional[Dict[str, int]] = None

    def _load_embeddings(self) -> None:
        """임베딩 지연 로딩"""
        if self._embeddings is not None:
            return

        embeddings_path = self._settings.embeddings_path

        with open(embeddings_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self._filenames = data["filenames"]

        img_embeddings = np.array(data["image_embeddings"], dtype=np.float32)
        txt_embeddings = np.array(data["text_embeddings"], dtype=np.float32)

        image_weight = self._settings.clip_image_weight
        self._embeddings = (
            image_weight * img_embeddings + (1 - image_weight) * txt_embeddings
        )

        # L2 정규화
        norms = np.linalg.norm(self._embeddings, axis=1, keepdims=True)
        self._embeddings = self._embeddings / np.maximum(norms, 1e-10)

        self._filename_to_index = {fn: i for i, fn in enumerate(self._filenames)}

    def search(
        self,
        query_vector: np.ndarray,
        top_k: int,
        excluded_indices: Optional[Set[int]] = None,
    ) -> List[Tuple[int, float]]:
        """코사인 유사도 기반 검색"""
        self._load_embeddings()

        query_norm = np.linalg.norm(query_vector)
        if query_norm > 0:
            query_normalized = query_vector / query_norm
        else:
            query_normalized = query_vector

        similarities = self._embeddings @ query_normalized

        if excluded_indices:
            mask = np.ones(len(similarities), dtype=bool)
            for idx in excluded_indices:
                if 0 <= idx < len(mask):
                    mask[idx] = False
            similarities = np.where(mask, similarities, -np.inf)

        num_valid = np.sum(similarities > -np.inf)
        k = min(top_k, num_valid)

        if k == 0:
            return []

        if k < len(similarities):
            top_indices = np.argpartition(similarities, -k)[-k:]
            top_indices = top_indices[np.argsort(similarities[top_indices])[::-1]]
        else:
            top_indices = np.argsort(similarities)[::-1]

        return [
            (int(idx), float(similarities[idx]))
            for idx in top_indices
            if similarities[idx] > -np.inf
        ]

    def get_vector(self, index: int) -> np.ndarray:
        """인덱스로 벡터 조회"""
        self._load_embeddings()
        if 0 <= index < len(self._embeddings):
            return self._embeddings[index].copy()
        raise IndexError(f"Index {index} out of range")

    def get_all_vectors(self) -> np.ndarray:
        """전체 임베딩 행렬 반환"""
        self._load_embeddings()
        return self._embeddings

    def get_filename(self, index: int) -> str:
        """인덱스에 해당하는 파일명 반환"""
        self._load_embeddings()
        if 0 <= index < len(self._filenames):
            return self._filenames[index]
        raise IndexError(f"Index {index} out of range")

    def get_index(self, filename: str) -> Optional[int]:
        """파일명에 해당하는 인덱스 반환"""
        self._load_embeddings()
        return self._filename_to_index.get(filename)

    @property
    def size(self) -> int:
        """인덱스 크기"""
        self._load_embeddings()
        return len(self._filenames)

    @property
    def filenames(self) -> List[str]:
        """파일명 목록 접근"""
        self._load_embeddings()
        return self._filenames


def create_vector_index(settings: Settings) -> IVectorIndex:
    """벡터 인덱스 팩토리

    FAISS 사용 가능 여부에 따라 적절한 인덱스 반환
    """
    try:
        return FaissVectorIndex(settings)
    except Exception:
        return NumpyVectorIndex(settings)
