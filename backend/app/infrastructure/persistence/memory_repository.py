"""인메모리 저장소 구현"""

import asyncio
from typing import Dict, List, Optional, Set

from app.domain.context.entity import Context
from app.domain.context.repository import ContextRepository
from app.domain.card.entity import CardHistory
from app.domain.card.repository import CardHistoryRepository
from app.domain.feedback.entity import FeedbackRequest
from app.domain.feedback.repository import FeedbackRepository


class InMemoryContextRepository(ContextRepository):
    """인메모리 컨텍스트 저장소"""

    def __init__(self):
        self._storage: Dict[str, Context] = {}
        self.__lock: Optional[asyncio.Lock] = None

    @property
    def _lock(self) -> asyncio.Lock:
        """Lazy initialization of asyncio.Lock"""
        if self.__lock is None:
            self.__lock = asyncio.Lock()
        return self.__lock

    async def find_by_id(self, context_id: str) -> Optional[Context]:
        """컨텍스트 ID로 조회"""
        async with self._lock:
            return self._storage.get(context_id)

    async def save(self, context: Context) -> None:
        """컨텍스트 저장"""
        async with self._lock:
            self._storage[context.context_id] = context

    async def delete(self, context_id: str) -> None:
        """컨텍스트 삭제"""
        async with self._lock:
            self._storage.pop(context_id, None)


class InMemoryCardHistoryRepository(CardHistoryRepository):
    """인메모리 카드 히스토리 저장소"""

    def __init__(self):
        self._storage: Dict[str, List[CardHistory]] = {}
        self.__lock: Optional[asyncio.Lock] = None

    @property
    def _lock(self) -> asyncio.Lock:
        """Lazy initialization of asyncio.Lock"""
        if self.__lock is None:
            self.__lock = asyncio.Lock()
        return self.__lock

    async def save_history(self, history: CardHistory) -> None:
        """히스토리 저장"""
        async with self._lock:
            if history.context_id not in self._storage:
                self._storage[history.context_id] = []
            self._storage[history.context_id].append(history)

    async def get_history_by_context(self, context_id: str) -> List[CardHistory]:
        """컨텍스트별 히스토리 조회"""
        async with self._lock:
            return self._storage.get(context_id, [])

    async def get_history_page(
        self, context_id: str, page_number: int
    ) -> Optional[CardHistory]:
        """특정 페이지 히스토리 조회"""
        async with self._lock:
            histories = self._storage.get(context_id, [])
            for history in histories:
                if history.page_number == page_number:
                    return history
            return None

    async def get_all_recommended_cards(self, context_id: str) -> Set[str]:
        """해당 컨텍스트에서 추천된 모든 카드 파일명 조회"""
        async with self._lock:
            histories = self._storage.get(context_id, [])
            all_cards: Set[str] = set()
            for history in histories:
                for card in history.cards:
                    all_cards.add(card.filename)
            return all_cards

    async def get_total_pages(self, context_id: str) -> int:
        """총 페이지 수 반환"""
        async with self._lock:
            return len(self._storage.get(context_id, []))


class InMemoryFeedbackRequestRepository:
    """인메모리 피드백 요청 저장소"""

    def __init__(self):
        self._storage: Dict[str, FeedbackRequest] = {}
        self.__lock: Optional[asyncio.Lock] = None

    @property
    def _lock(self) -> asyncio.Lock:
        """Lazy initialization of asyncio.Lock"""
        if self.__lock is None:
            self.__lock = asyncio.Lock()
        return self.__lock

    async def save_request(self, request: FeedbackRequest) -> None:
        """피드백 요청 저장"""
        async with self._lock:
            self._storage[request.confirmation_id] = request

    async def find_request(self, confirmation_id: str) -> Optional[FeedbackRequest]:
        """피드백 요청 조회"""
        async with self._lock:
            return self._storage.get(confirmation_id)

    async def delete_request(self, confirmation_id: str) -> None:
        """피드백 요청 삭제"""
        async with self._lock:
            self._storage.pop(confirmation_id, None)
