"""JSON 파일 기반 저장소 구현

메모리 캐싱으로 파일 I/O 최소화
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
import threading

from app.domain.user.entity import User
from app.domain.user.repository import UserRepository
from app.domain.card.entity import Card
from app.domain.card.repository import CardRepository
from app.domain.feedback.entity import Feedback
from app.domain.feedback.repository import FeedbackRepository


class CachedJsonStore:
    """메모리 캐싱을 지원하는 JSON 파일 저장소 기반 클래스

    - 읽기: 메모리 캐시 우선 사용
    - 쓰기: 캐시 갱신 + 파일 저장
    - TTL 기반 캐시 무효화 지원
    """

    def __init__(self, file_path: Path, default_data: Any = None, ttl_seconds: int = 0):
        self._file_path = file_path
        self._default_data = default_data if default_data is not None else {}
        self._ttl_seconds = ttl_seconds  # 0 = 무제한
        self._lock = threading.Lock()
        self._cache: Optional[Dict[str, Any]] = None
        self._cache_time: float = 0
        self._ensure_file_exists()

    def _ensure_file_exists(self) -> None:
        """파일 및 디렉토리 존재 확인"""
        self._file_path.parent.mkdir(parents=True, exist_ok=True)
        if not self._file_path.exists():
            self._file_path.write_text(
                json.dumps(self._default_data, ensure_ascii=False),
                encoding="utf-8",
            )

    def _is_cache_valid(self) -> bool:
        """캐시 유효성 검사"""
        if self._cache is None:
            return False
        if self._ttl_seconds <= 0:
            return True
        return (time.time() - self._cache_time) < self._ttl_seconds

    def _load_from_file(self) -> Dict[str, Any]:
        """파일에서 데이터 로드"""
        try:
            return json.loads(self._file_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, FileNotFoundError):
            return self._default_data.copy() if isinstance(self._default_data, dict) else self._default_data

    def load(self) -> Dict[str, Any]:
        """캐시 우선 데이터 로드"""
        with self._lock:
            if self._is_cache_valid():
                return self._cache
            self._cache = self._load_from_file()
            self._cache_time = time.time()
            return self._cache

    def save(self, data: Dict[str, Any]) -> None:
        """데이터 저장 (캐시 + 파일)"""
        with self._lock:
            self._cache = data
            self._cache_time = time.time()
            self._file_path.write_text(
                json.dumps(data, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

    def invalidate_cache(self) -> None:
        """캐시 무효화"""
        with self._lock:
            self._cache = None


class JsonUserRepository(UserRepository):
    """JSON 파일 기반 사용자 저장소 (메모리 캐싱)"""

    def __init__(self, file_path: Path):
        self._store = CachedJsonStore(file_path, default_data={})

    async def find_by_id(self, user_id: str) -> Optional[User]:
        """사용자 ID로 조회"""
        data = self._store.load()
        if user_id not in data:
            return None
        return User.from_dict(user_id, data[user_id])

    async def exists(self, user_id: str) -> bool:
        """사용자 존재 여부 확인"""
        data = self._store.load()
        return user_id in data

    async def save(self, user: User) -> None:
        """사용자 저장"""
        data = self._store.load()
        data[user.user_id] = user.to_dict()
        self._store.save(data)

    async def update(self, user: User) -> None:
        """사용자 업데이트"""
        await self.save(user)


class JsonCardRepository(CardRepository):
    """이미지 파일 기반 카드 저장소"""

    def __init__(self, settings):
        self._settings = settings
        self._cards_cache: Optional[List[Card]] = None

    def _load_cards(self) -> List[Card]:
        """이미지 폴더에서 카드 목록 로드"""
        if self._cards_cache is None:
            self._cards_cache = []
            images_folder = self._settings.images_folder

            if images_folder.exists():
                for image_file in images_folder.glob("*.png"):
                    card = Card.from_filename(image_file.name)
                    self._cards_cache.append(card)

        return self._cards_cache

    def get_all_cards(self) -> List[Card]:
        """모든 카드 조회"""
        return self._load_cards()

    def get_all_filenames(self) -> List[str]:
        """모든 카드 파일명 조회"""
        return [card.filename for card in self._load_cards()]

    def get_card_by_filename(self, filename: str) -> Optional[Card]:
        """파일명으로 카드 조회"""
        for card in self._load_cards():
            if card.filename == filename:
                return card
        return None


class JsonFeedbackRepository:
    """JSON 파일 기반 피드백 저장소 (메모리 캐싱)"""

    def __init__(self, file_path: Path):
        self._store = CachedJsonStore(
            file_path,
            default_data={"feedbacks": [], "next_id": 1},
        )

    async def save_feedback(self, feedback: Feedback) -> int:
        """피드백 저장"""
        data = self._store.load()
        data["feedbacks"].append(feedback.to_dict())
        data["next_id"] = feedback.feedback_id + 1
        self._store.save(data)
        return feedback.feedback_id

    async def get_next_feedback_id(self) -> int:
        """다음 피드백 ID 반환"""
        data = self._store.load()
        return data.get("next_id", 1)
