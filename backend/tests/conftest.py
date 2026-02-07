"""테스트 설정 및 pytest fixtures"""

from datetime import datetime
from typing import List, Optional, Set, Tuple
from unittest.mock import AsyncMock, MagicMock

import numpy as np
import pytest
from fastapi.testclient import TestClient

from app.config.settings import Settings
from app.domain.card.entity import Card
from app.domain.card.interfaces import IEmbeddingProvider, IVectorIndex, ScoredCard
from app.domain.context.entity import Context
from app.domain.context.repository import ContextRepository
from app.domain.user.entity import User
from app.main import app


@pytest.fixture
def test_settings() -> Settings:
    """테스트용 설정"""
    return Settings(
        openai_api_key="test-api-key",
        debug=True,
        display_cards_total=20,
        min_card_selection=1,
        max_card_selection=4,
        interpretation_count=3,
    )


@pytest.fixture
def sample_user() -> User:
    """샘플 사용자"""
    return User(
        user_id="test-user-001",
        name="테스트 사용자",
        age=10,
        gender="남성",
        disability_type="자폐스펙트럼장애",
        communication_characteristics="간단한 문장 사용",
        interesting_topics=["놀이", "음식", "동물"],
        password_hash=User.hash_password("test1234"),
    )


@pytest.fixture
def sample_context() -> Context:
    """샘플 컨텍스트"""
    return Context(
        context_id="ctx-test-001",
        user_id="test-user-001",
        time="10시 30분",
        place="학교",
        interaction_partner="선생님",
        current_activity="수업 중",
    )


@pytest.fixture
def sample_card() -> Card:
    """샘플 카드"""
    return Card(
        id="001_사과",
        name="사과",
        filename="001_사과.png",
        image_path="/api/images/001_사과.png",
        index=0,
    )


@pytest.fixture
def sample_cards() -> List[Card]:
    """여러 샘플 카드"""
    card_data = [
        ("001_사과", "사과"),
        ("002_바나나", "바나나"),
        ("003_물", "물"),
        ("004_우유", "우유"),
        ("005_밥", "밥"),
    ]
    return [
        Card(
            id=card_id,
            name=name,
            filename=f"{card_id}.png",
            image_path=f"/api/images/{card_id}.png",
            index=i,
        )
        for i, (card_id, name) in enumerate(card_data)
    ]


@pytest.fixture
def sample_scored_cards(sample_cards: List[Card]) -> List[ScoredCard]:
    """점수가 부여된 샘플 카드"""
    scores = [0.9, 0.85, 0.8, 0.75, 0.7]
    return [
        ScoredCard(card=card, semantic_score=score)
        for card, score in zip(sample_cards, scores)
    ]


class MockEmbeddingProvider(IEmbeddingProvider):
    """테스트용 임베딩 제공자"""

    def __init__(self, dimension: int = 512):
        self._dimension = dimension

    def encode_text(self, text: str) -> np.ndarray:
        """텍스트를 일관된 랜덤 벡터로 인코딩"""
        np.random.seed(hash(text) % (2**32))
        vec = np.random.randn(self._dimension).astype(np.float32)
        return vec / np.linalg.norm(vec)

    def encode_texts_batch(self, texts: List[str]) -> np.ndarray:
        """배치 인코딩"""
        return np.array([self.encode_text(t) for t in texts])

    def get_embedding_dimension(self) -> int:
        return self._dimension


class MockVectorIndex(IVectorIndex):
    """테스트용 벡터 인덱스"""

    def __init__(self, filenames: List[str]):
        self._filenames = filenames
        self._vectors = np.random.randn(len(filenames), 512).astype(np.float32)
        self._vectors = self._vectors / np.linalg.norm(
            self._vectors, axis=1, keepdims=True
        )
        self._filename_to_idx = {fn: i for i, fn in enumerate(filenames)}

    def search(
        self,
        query_vector: np.ndarray,
        top_k: int,
        excluded_indices: Optional[Set[int]] = None,
    ) -> List[Tuple[int, float]]:
        excluded = excluded_indices or set()
        similarities = self._vectors @ query_vector
        results = []
        for i, sim in enumerate(similarities):
            if i not in excluded:
                results.append((i, float(sim)))
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]

    def get_vector(self, index: int) -> np.ndarray:
        return self._vectors[index]

    def get_all_vectors(self) -> np.ndarray:
        return self._vectors

    def get_filename(self, index: int) -> str:
        return self._filenames[index]

    def get_index(self, filename: str) -> Optional[int]:
        return self._filename_to_idx.get(filename)

    @property
    def size(self) -> int:
        return len(self._filenames)

    @property
    def filenames(self) -> List[str]:
        return self._filenames


@pytest.fixture
def mock_vector_index(sample_cards: List[Card]) -> MockVectorIndex:
    """테스트용 벡터 인덱스"""
    filenames = [card.filename for card in sample_cards]
    return MockVectorIndex(filenames)


@pytest.fixture
def mock_embedding_provider() -> MockEmbeddingProvider:
    """테스트용 임베딩 제공자"""
    return MockEmbeddingProvider()


class MockContextRepository(ContextRepository):
    """테스트용 컨텍스트 저장소"""

    def __init__(self):
        self._storage = {}

    async def save(self, context: Context) -> None:
        self._storage[context.context_id] = context

    async def find_by_id(self, context_id: str) -> Optional[Context]:
        return self._storage.get(context_id)

    async def delete(self, context_id: str) -> None:
        self._storage.pop(context_id, None)


@pytest.fixture
def mock_context_repository() -> MockContextRepository:
    """테스트용 컨텍스트 저장소"""
    return MockContextRepository()


@pytest.fixture
def mock_openai_client() -> MagicMock:
    """Mock OpenAI 클라이언트"""
    client = MagicMock()
    client.rewrite_query = AsyncMock(return_value=["확장 쿼리1", "확장 쿼리2"])
    client.interpret_cards = AsyncMock(return_value=["해석1", "해석2", "해석3"])
    client.encode_image_to_base64 = MagicMock(return_value="base64encodedimage")
    client.get_image_media_type = MagicMock(return_value="image/png")
    return client


@pytest.fixture(autouse=True)
def reset_rate_limiter():
    """각 테스트 전에 rate limiter 상태 초기화"""
    from app.core.rate_limit import limiter

    limiter.reset()
    yield


@pytest.fixture
def client() -> TestClient:
    """FastAPI 테스트 클라이언트"""
    return TestClient(app)
