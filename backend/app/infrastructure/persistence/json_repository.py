"""JSON 파일 기반 저장소 구현"""

import json
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


class JsonUserRepository(UserRepository):
    """JSON 파일 기반 사용자 저장소"""

    def __init__(self, file_path: Path):
        self._file_path = file_path
        self._lock = threading.Lock()
        self._ensure_file_exists()

    def _ensure_file_exists(self) -> None:
        """파일 및 디렉토리 존재 확인"""
        self._file_path.parent.mkdir(parents=True, exist_ok=True)
        if not self._file_path.exists():
            self._file_path.write_text("{}", encoding="utf-8")

    def _load_data(self) -> Dict[str, Any]:
        """데이터 로드"""
        try:
            return json.loads(self._file_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, FileNotFoundError):
            return {}

    def _save_data(self, data: Dict[str, Any]) -> None:
        """데이터 저장"""
        self._file_path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    async def find_by_id(self, user_id: str) -> Optional[User]:
        """사용자 ID로 조회"""
        with self._lock:
            data = self._load_data()
            if user_id not in data:
                return None
            return User.from_dict(user_id, data[user_id])

    async def exists(self, user_id: str) -> bool:
        """사용자 존재 여부 확인"""
        with self._lock:
            data = self._load_data()
            return user_id in data

    async def save(self, user: User) -> None:
        """사용자 저장"""
        with self._lock:
            data = self._load_data()
            data[user.user_id] = user.to_dict()
            self._save_data(data)

    async def update(self, user: User) -> None:
        """사용자 업데이트"""
        await self.save(user)


class JsonCardRepository(CardRepository):
    """JSON 파일 기반 카드 저장소"""

    def __init__(self, settings):
        self._settings = settings
        self._cluster_tags: Optional[Dict[str, str]] = None
        self._clustering_results: Optional[Dict[str, int]] = None
        self._cards_by_cluster: Optional[Dict[int, List[Card]]] = None

    def _load_cluster_tags(self) -> Dict[str, str]:
        """클러스터 태그 로드"""
        if self._cluster_tags is None:
            try:
                path = self._settings.cluster_tags_path
                data = json.loads(path.read_text(encoding="utf-8"))
                self._cluster_tags = data
            except (FileNotFoundError, json.JSONDecodeError):
                self._cluster_tags = {}
        return self._cluster_tags

    def _load_clustering_results(self) -> Dict[str, int]:
        """클러스터링 결과 로드"""
        if self._clustering_results is None:
            try:
                path = self._settings.clustering_results_path
                data = json.loads(path.read_text(encoding="utf-8"))
                self._clustering_results = data
            except (FileNotFoundError, json.JSONDecodeError):
                self._clustering_results = {}
        return self._clustering_results

    def _build_cards_by_cluster(self) -> Dict[int, List[Card]]:
        """클러스터별 카드 목록 구축"""
        if self._cards_by_cluster is None:
            self._cards_by_cluster = {}
            clustering_results = self._load_clustering_results()

            for filename, cluster_id in clustering_results.items():
                if cluster_id not in self._cards_by_cluster:
                    self._cards_by_cluster[cluster_id] = []

                card = Card.from_filename(filename)
                card.cluster_id = cluster_id
                self._cards_by_cluster[cluster_id].append(card)

        return self._cards_by_cluster

    def get_all_cards(self) -> List[Card]:
        """모든 카드 조회"""
        cards_by_cluster = self._build_cards_by_cluster()
        all_cards = []
        for cards in cards_by_cluster.values():
            all_cards.extend(cards)
        return all_cards

    def get_cards_by_cluster(self, cluster_id: int) -> List[Card]:
        """클러스터별 카드 조회"""
        cards_by_cluster = self._build_cards_by_cluster()
        return cards_by_cluster.get(cluster_id, [])

    def get_cluster_tags(self) -> Dict[str, str]:
        """클러스터 태그 조회"""
        return self._load_cluster_tags()

    def get_clustering_results(self) -> Dict[str, int]:
        """클러스터링 결과 조회"""
        return self._load_clustering_results()


class JsonFeedbackRepository:
    """JSON 파일 기반 피드백 저장소 (저장 전용)"""

    def __init__(self, file_path: Path):
        self._file_path = file_path
        self._lock = threading.Lock()
        self._ensure_file_exists()

    def _ensure_file_exists(self) -> None:
        """파일 및 디렉토리 존재 확인"""
        self._file_path.parent.mkdir(parents=True, exist_ok=True)
        if not self._file_path.exists():
            self._file_path.write_text(
                json.dumps({"feedbacks": [], "next_id": 1}, ensure_ascii=False),
                encoding="utf-8",
            )

    def _load_data(self) -> Dict[str, Any]:
        """데이터 로드"""
        try:
            return json.loads(self._file_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, FileNotFoundError):
            return {"feedbacks": [], "next_id": 1}

    def _save_data(self, data: Dict[str, Any]) -> None:
        """데이터 저장"""
        self._file_path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    async def save_feedback(self, feedback: Feedback) -> int:
        """피드백 저장"""
        with self._lock:
            data = self._load_data()
            data["feedbacks"].append(feedback.to_dict())
            data["next_id"] = feedback.feedback_id + 1
            self._save_data(data)
            return feedback.feedback_id

    async def get_next_feedback_id(self) -> int:
        """다음 피드백 ID 반환"""
        with self._lock:
            data = self._load_data()
            return data.get("next_id", 1)
