"""시각적 패턴 분석기

CLIP 임베딩 기반 시각적 특징-의미 연결 시스템.
카드 조합의 시각적 서명을 계산하고, 유사한 과거 패턴을 검색하여
해석 힌트를 제공합니다.
"""

import json
import logging
import math
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np

from app.domain.card.interfaces import IVectorIndex

logger = logging.getLogger(__name__)


@dataclass
class VisualPattern:
    """피드백에서 추출된 시각적 패턴

    Attributes:
        feedback_id: 원본 피드백 ID
        visual_signature: 카드 조합의 CLIP 임베딩 (768차원)
        interpretation: 사용자가 확정한 해석
        context: 피드백 당시 상황
        similarity_score: 현재 쿼리와의 시각적 유사도
        recency_weight: 시간 기반 가중치 (최근일수록 높음)
    """

    feedback_id: int
    visual_signature: np.ndarray
    interpretation: Optional[str]
    context: Dict[str, str]
    similarity_score: float = 0.0
    recency_weight: float = 1.0

    @property
    def combined_score(self) -> float:
        """유사도와 시간 가중치를 결합한 최종 점수"""
        return self.similarity_score * self.recency_weight


@dataclass
class VisualQueryExpansion:
    """시각적 패턴 기반 쿼리 확장 결과

    Attributes:
        similar_patterns: 유사한 시각적 패턴 목록
        interpretation_hints: 해석 힌트 문자열 목록
        visual_confidence: 시각적 패턴 매칭 신뢰도
    """

    similar_patterns: List[VisualPattern] = field(default_factory=list)
    interpretation_hints: List[str] = field(default_factory=list)
    visual_confidence: float = 0.0


class IVisualPatternAnalyzer(ABC):
    """시각적 패턴 분석 인터페이스

    ISP: 시각적 분석 기능만 정의
    DIP: 고수준 모듈(해석기, 피드백 서비스)이 이 추상화에 의존
    """

    @abstractmethod
    async def compute_visual_signature(
        self, card_filenames: List[str]
    ) -> np.ndarray:
        """카드 조합의 시각적 서명 계산

        Args:
            card_filenames: 카드 파일명 목록

        Returns:
            L2 정규화된 768차원 시각적 서명 벡터
        """
        pass

    @abstractmethod
    async def find_similar_patterns(
        self,
        card_filenames: List[str],
        user_id: Optional[str] = None,
        top_k: int = 5,
    ) -> VisualQueryExpansion:
        """유사한 시각적 패턴 검색

        Args:
            card_filenames: 현재 선택된 카드 파일명
            user_id: 사용자 ID (개인화 시 사용)
            top_k: 반환할 최대 패턴 수

        Returns:
            시각적 쿼리 확장 결과
        """
        pass

    @abstractmethod
    async def get_interpretation_hints(
        self,
        card_filenames: List[str],
        context: Dict[str, Any],
        user_id: Optional[str] = None,
    ) -> List[str]:
        """해석 힌트 생성

        Args:
            card_filenames: 카드 파일명 목록
            context: 현재 상황 컨텍스트
            user_id: 사용자 ID

        Returns:
            해석 힌트 문자열 목록
        """
        pass


class CLIPVisualPatternAnalyzer(IVisualPatternAnalyzer):
    """CLIP 기반 시각적 패턴 분석기

    SRP: 시각적 패턴 분석 및 유사도 검색만 담당
    DIP: IVectorIndex 추상화에 의존 (SSOT)

    Attributes:
        _vector_index: CLIP 임베딩 접근용 벡터 인덱스
        _feedback_path: 피드백 데이터 파일 경로
        _signature_method: 임베딩 집계 방법
        _similarity_threshold: 유사 패턴 판정 임계값
        _decay_days: 시간 감쇠 기준 일수
    """

    EMBEDDING_DIM = 768

    def __init__(
        self,
        vector_index: IVectorIndex,
        feedback_file_path: Path,
        signature_method: str = "mean",
        similarity_threshold: float = 0.7,
        decay_days: int = 30,
    ):
        self._vector_index = vector_index
        self._feedback_path = feedback_file_path
        self._signature_method = signature_method
        self._similarity_threshold = similarity_threshold
        self._decay_days = decay_days

        # 시각적 서명 캐시 (feedback_id -> signature)
        self._signature_cache: Dict[int, np.ndarray] = {}

    def _load_feedbacks(self) -> List[Dict[str, Any]]:
        """피드백 데이터 로드"""
        try:
            if not self._feedback_path.exists():
                return []

            data = json.loads(self._feedback_path.read_text(encoding="utf-8"))
            return data.get("feedbacks", [])

        except (json.JSONDecodeError, FileNotFoundError) as e:
            logger.warning("피드백 데이터 로드 실패: %s", e)
            return []

    def _aggregate_embeddings(
        self, embeddings: List[np.ndarray]
    ) -> np.ndarray:
        """임베딩 집계 전략

        Args:
            embeddings: 카드별 CLIP 임베딩 목록

        Returns:
            집계된 시각적 서명
        """
        if not embeddings:
            return np.zeros(self.EMBEDDING_DIM, dtype=np.float32)

        embeddings_array = np.array(embeddings)

        if self._signature_method == "mean":
            # 평균: 전체 테마 캡처
            signature = np.mean(embeddings_array, axis=0)

        elif self._signature_method == "max":
            # 요소별 최대값: 가장 강한 특징 캡처
            signature = np.max(embeddings_array, axis=0)

        elif self._signature_method == "attention":
            # 순서 가중 평균: 첫 카드에 더 높은 가중치
            n = len(embeddings)
            weights = np.array([1.0 / (i + 1) for i in range(n)])
            weights /= weights.sum()
            signature = np.average(embeddings_array, axis=0, weights=weights)

        else:
            # 기본값: mean
            signature = np.mean(embeddings_array, axis=0)

        # L2 정규화
        norm = np.linalg.norm(signature)
        if norm > 1e-10:
            signature = signature / norm

        return signature.astype(np.float32)

    def _compute_recency_weight(self, confirmed_at: str) -> float:
        """시간 기반 감쇠 가중치 계산

        최근 피드백에 높은 가중치 부여 (지수 감쇠)
        """
        try:
            if "T" in confirmed_at:
                dt = datetime.fromisoformat(confirmed_at.replace("Z", "+00:00"))
            else:
                dt = datetime.fromisoformat(confirmed_at)

            # timezone-aware vs naive 처리
            now = datetime.now(dt.tzinfo) if dt.tzinfo else datetime.now()
            days_ago = (now - dt).days

            # 지수 감쇠: e^(-days/decay_days)
            return math.exp(-days_ago / self._decay_days)

        except (ValueError, TypeError):
            return 0.5

    def _compute_similarity(
        self, sig1: np.ndarray, sig2: np.ndarray
    ) -> float:
        """코사인 유사도 계산"""
        norm1 = np.linalg.norm(sig1)
        norm2 = np.linalg.norm(sig2)

        if norm1 < 1e-10 or norm2 < 1e-10:
            return 0.0

        return float(np.dot(sig1, sig2) / (norm1 * norm2))

    async def compute_visual_signature(
        self, card_filenames: List[str]
    ) -> np.ndarray:
        """카드 조합의 시각적 서명 계산"""
        embeddings = []

        for filename in card_filenames:
            idx = self._vector_index.get_index(filename)
            if idx is not None:
                embedding = self._vector_index.get_vector(idx)
                embeddings.append(embedding)
            else:
                logger.warning("카드 임베딩 없음: %s", filename)

        return self._aggregate_embeddings(embeddings)

    async def find_similar_patterns(
        self,
        card_filenames: List[str],
        user_id: Optional[str] = None,
        top_k: int = 5,
    ) -> VisualQueryExpansion:
        """유사한 시각적 패턴 검색"""
        if not card_filenames:
            return VisualQueryExpansion()

        # 현재 카드 조합의 시각적 서명 계산
        query_signature = await self.compute_visual_signature(card_filenames)

        feedbacks = self._load_feedbacks()
        if not feedbacks:
            return VisualQueryExpansion()

        patterns: List[VisualPattern] = []

        for fb in feedbacks:
            # 사용자 필터 (선택적)
            if user_id and fb.get("userId") != user_id:
                continue

            fb_id = fb.get("feedbackId", 0)
            fb_cards = fb.get("cards", [])

            if not fb_cards:
                continue

            # 시각적 서명 계산 또는 캐시에서 로드
            if fb_id in self._signature_cache:
                fb_signature = self._signature_cache[fb_id]
            elif fb.get("visualSignature"):
                # 저장된 시각적 서명 사용
                fb_signature = np.array(fb["visualSignature"], dtype=np.float32)
                self._signature_cache[fb_id] = fb_signature
            else:
                # 시각적 서명 계산
                fb_signature = await self.compute_visual_signature(fb_cards)
                self._signature_cache[fb_id] = fb_signature

            # 유사도 계산
            similarity = self._compute_similarity(query_signature, fb_signature)

            if similarity >= self._similarity_threshold:
                # 최종 해석 추출
                interpretation = fb.get("selectedInterpretation") or fb.get("directFeedback")

                recency = self._compute_recency_weight(fb.get("confirmedAt", ""))

                pattern = VisualPattern(
                    feedback_id=fb_id,
                    visual_signature=fb_signature,
                    interpretation=interpretation,
                    context=fb.get("context", {}),
                    similarity_score=similarity,
                    recency_weight=recency,
                )
                patterns.append(pattern)

        # 점수순 정렬 후 상위 k개 선택
        patterns.sort(key=lambda p: p.combined_score, reverse=True)
        top_patterns = patterns[:top_k]

        # 해석 힌트 추출
        hints = []
        for p in top_patterns:
            if p.interpretation:
                hints.append(p.interpretation)

        # 신뢰도 계산
        confidence = min(1.0, len(top_patterns) / 3.0) if top_patterns else 0.0

        return VisualQueryExpansion(
            similar_patterns=top_patterns,
            interpretation_hints=hints,
            visual_confidence=confidence,
        )

    async def get_interpretation_hints(
        self,
        card_filenames: List[str],
        context: Dict[str, Any],
        user_id: Optional[str] = None,
    ) -> List[str]:
        """해석 힌트 생성

        시각적 유사도가 높은 과거 피드백에서 해석 힌트 추출
        """
        expansion = await self.find_similar_patterns(
            card_filenames, user_id, top_k=5
        )

        return expansion.interpretation_hints


class NoOpVisualPatternAnalyzer(IVisualPatternAnalyzer):
    """시각적 분석 비활성화 시 사용하는 No-op 구현"""

    async def compute_visual_signature(
        self, card_filenames: List[str]
    ) -> np.ndarray:
        """빈 시각적 서명 반환"""
        return np.zeros(768, dtype=np.float32)

    async def find_similar_patterns(
        self,
        card_filenames: List[str],
        user_id: Optional[str] = None,
        top_k: int = 5,
    ) -> VisualQueryExpansion:
        """빈 확장 정보 반환"""
        return VisualQueryExpansion()

    async def get_interpretation_hints(
        self,
        card_filenames: List[str],
        context: Dict[str, Any],
        user_id: Optional[str] = None,
    ) -> List[str]:
        """빈 힌트 반환"""
        return []
