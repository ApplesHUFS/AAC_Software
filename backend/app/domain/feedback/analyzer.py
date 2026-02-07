"""피드백 기반 컨텍스트 학습 분석기

Contextual Relevance Feedback 알고리즘을 구현합니다.
과거 피드백 데이터에서 상황-카드 연관 패턴을 학습하여
쿼리 확장에 활용합니다.

연구적 접근:
1. Context Similarity: 현재 상황과 과거 피드백의 유사도 계산
2. Pattern Mining: 성공적인 카드 선택 패턴 추출
3. Temporal Decay: 최근 피드백에 높은 가중치 부여
"""

import json
import logging
import math
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

logger = logging.getLogger(__name__)


@dataclass
class FeedbackPattern:
    """분석된 피드백 패턴

    Attributes:
        context: 원본 컨텍스트 (장소, 활동, 대화상대)
        cards: 선택된 카드 목록
        interpretation: 확정된 해석
        relevance_score: 현재 상황과의 유사도 (0~1)
        recency_weight: 시간 기반 가중치 (0~1)
    """

    context: Dict[str, str]
    cards: List[str]
    interpretation: Optional[str]
    relevance_score: float = 0.0
    recency_weight: float = 1.0

    @property
    def combined_score(self) -> float:
        """유사도와 시간 가중치를 결합한 최종 점수"""
        return self.relevance_score * self.recency_weight


@dataclass
class QueryExpansion:
    """피드백 기반 쿼리 확장 결과

    Attributes:
        original_context: 원본 컨텍스트
        relevant_cards: 과거 성공 패턴에서 추출된 관련 카드
        context_hints: 컨텍스트 힌트 (유사 상황의 키워드)
        confidence: 확장의 신뢰도 (충분한 데이터 기반 여부)
    """

    original_context: Dict[str, str]
    relevant_cards: List[str] = field(default_factory=list)
    context_hints: List[str] = field(default_factory=list)
    confidence: float = 0.0


class IFeedbackAnalyzer(ABC):
    """피드백 분석기 인터페이스"""

    @abstractmethod
    async def analyze_patterns(
        self,
        place: str,
        interaction_partner: str,
        current_activity: str,
        user_id: Optional[str] = None,
    ) -> QueryExpansion:
        """현재 상황과 유사한 과거 패턴 분석

        Args:
            place: 현재 장소
            interaction_partner: 현재 대화 상대
            current_activity: 현재 활동
            user_id: 사용자 ID (개인화 시 사용)

        Returns:
            피드백 기반 쿼리 확장 정보
        """
        pass

    @abstractmethod
    async def get_successful_cards(
        self,
        place: str,
        interaction_partner: str,
        current_activity: str,
        top_k: int = 5,
    ) -> List[Tuple[str, float]]:
        """현재 상황에서 성공적이었던 카드 목록 반환

        Args:
            place: 현재 장소
            interaction_partner: 현재 대화 상대
            current_activity: 현재 활동
            top_k: 반환할 최대 카드 수

        Returns:
            (카드명, 점수) 튜플 리스트
        """
        pass


class TFIDFFeedbackAnalyzer(IFeedbackAnalyzer):
    """TF-IDF 기반 피드백 분석기

    컨텍스트 텍스트의 TF-IDF 유사도를 사용하여
    과거 피드백과의 관련성을 계산합니다.
    """

    def __init__(
        self,
        feedback_file_path: Path,
        decay_days: int = 30,
        min_similarity: float = 0.3,
    ):
        self._feedback_path = feedback_file_path
        self._decay_days = decay_days
        self._min_similarity = min_similarity
        self._idf_cache: Dict[str, float] = {}

    def _load_feedbacks(self) -> List[Dict[str, Any]]:
        """저장된 피드백 데이터 로드"""
        try:
            if not self._feedback_path.exists():
                return []

            data = json.loads(self._feedback_path.read_text(encoding="utf-8"))
            return data.get("feedbacks", [])

        except (json.JSONDecodeError, FileNotFoundError) as e:
            logger.warning(f"피드백 데이터 로드 실패: {e}")
            return []

    def _tokenize(self, text: str) -> List[str]:
        """텍스트 토큰화 (한글 형태소 분석 간소화)"""
        if not text:
            return []

        # 공백 및 특수문자 기준 분리
        tokens = []
        current = ""

        for char in text:
            if char.isalnum() or char in "가-힣":
                current += char
            else:
                if current:
                    tokens.append(current.lower())
                    current = ""

        if current:
            tokens.append(current.lower())

        return tokens

    def _compute_tf(self, tokens: List[str]) -> Dict[str, float]:
        """Term Frequency 계산"""
        if not tokens:
            return {}

        tf: Dict[str, int] = {}
        for token in tokens:
            tf[token] = tf.get(token, 0) + 1

        max_freq = max(tf.values()) if tf else 1
        return {term: count / max_freq for term, count in tf.items()}

    def _compute_idf(self, feedbacks: List[Dict[str, Any]]) -> Dict[str, float]:
        """Inverse Document Frequency 계산 (캐싱)"""
        if self._idf_cache:
            return self._idf_cache

        n_docs = len(feedbacks) + 1  # +1 for smoothing
        doc_freq: Dict[str, int] = {}

        for fb in feedbacks:
            context = fb.get("context", {})
            text = " ".join([
                context.get("place", ""),
                context.get("currentActivity", ""),
            ])
            tokens = set(self._tokenize(text))

            for token in tokens:
                doc_freq[token] = doc_freq.get(token, 0) + 1

        self._idf_cache = {
            term: math.log(n_docs / (1 + freq))
            for term, freq in doc_freq.items()
        }

        return self._idf_cache

    def _compute_tfidf_similarity(
        self,
        query_tokens: List[str],
        doc_tokens: List[str],
        idf: Dict[str, float],
    ) -> float:
        """TF-IDF 코사인 유사도 계산"""
        if not query_tokens or not doc_tokens:
            return 0.0

        query_tf = self._compute_tf(query_tokens)
        doc_tf = self._compute_tf(doc_tokens)

        # TF-IDF 벡터 생성
        all_terms = set(query_tf.keys()) | set(doc_tf.keys())

        query_vec = []
        doc_vec = []

        for term in all_terms:
            term_idf = idf.get(term, 0.0)
            query_vec.append(query_tf.get(term, 0.0) * term_idf)
            doc_vec.append(doc_tf.get(term, 0.0) * term_idf)

        # 코사인 유사도
        dot_product = sum(q * d for q, d in zip(query_vec, doc_vec))
        query_norm = math.sqrt(sum(q * q for q in query_vec))
        doc_norm = math.sqrt(sum(d * d for d in doc_vec))

        if query_norm == 0 or doc_norm == 0:
            return 0.0

        return dot_product / (query_norm * doc_norm)

    def _compute_recency_weight(self, confirmed_at: str) -> float:
        """시간 기반 감쇠 가중치 계산

        최근 피드백에 높은 가중치 부여 (지수 감쇠)
        """
        try:
            # ISO 형식 파싱
            if "T" in confirmed_at:
                dt = datetime.fromisoformat(confirmed_at.replace("Z", "+00:00"))
            else:
                dt = datetime.fromisoformat(confirmed_at)

            days_ago = (datetime.now(dt.tzinfo) - dt).days

            # 지수 감쇠: e^(-days/decay_days)
            return math.exp(-days_ago / self._decay_days)

        except (ValueError, TypeError):
            return 0.5

    async def analyze_patterns(
        self,
        place: str,
        interaction_partner: str,
        current_activity: str,
        user_id: Optional[str] = None,
    ) -> QueryExpansion:
        """현재 상황과 유사한 과거 패턴 분석"""
        feedbacks = self._load_feedbacks()

        if not feedbacks:
            return QueryExpansion(
                original_context={
                    "place": place,
                    "interaction_partner": interaction_partner,
                    "current_activity": current_activity,
                },
                confidence=0.0,
            )

        # 현재 컨텍스트 토큰화
        query_text = f"{place} {current_activity}"
        query_tokens = self._tokenize(query_text)

        # IDF 계산
        idf = self._compute_idf(feedbacks)

        # 유사 패턴 검색
        patterns: List[FeedbackPattern] = []

        for fb in feedbacks:
            # 사용자 필터 (선택적)
            if user_id and fb.get("userId") != user_id:
                continue

            context = fb.get("context", {})
            doc_text = f"{context.get('place', '')} {context.get('currentActivity', '')}"
            doc_tokens = self._tokenize(doc_text)

            similarity = self._compute_tfidf_similarity(query_tokens, doc_tokens, idf)

            if similarity >= self._min_similarity:
                recency = self._compute_recency_weight(
                    fb.get("confirmedAt", "")
                )

                pattern = FeedbackPattern(
                    context=context,
                    cards=fb.get("cards", []),
                    interpretation=fb.get("selectedInterpretation"),
                    relevance_score=similarity,
                    recency_weight=recency,
                )
                patterns.append(pattern)

        # 점수순 정렬
        patterns.sort(key=lambda p: p.combined_score, reverse=True)

        # 상위 패턴에서 관련 카드 추출
        relevant_cards: List[str] = []
        context_hints: Set[str] = set()
        seen_cards: Set[str] = set()

        for pattern in patterns[:5]:
            for card in pattern.cards:
                if card not in seen_cards:
                    relevant_cards.append(card)
                    seen_cards.add(card)

            # 컨텍스트 힌트 추출
            if pattern.context.get("place"):
                context_hints.add(pattern.context["place"])
            if pattern.context.get("currentActivity"):
                context_hints.add(pattern.context["currentActivity"])

        # 신뢰도 계산 (충분한 유사 패턴 존재 여부)
        confidence = min(1.0, len(patterns) / 3.0)

        return QueryExpansion(
            original_context={
                "place": place,
                "interaction_partner": interaction_partner,
                "current_activity": current_activity,
            },
            relevant_cards=relevant_cards[:10],
            context_hints=list(context_hints)[:5],
            confidence=confidence,
        )

    async def get_successful_cards(
        self,
        place: str,
        interaction_partner: str,
        current_activity: str,
        top_k: int = 5,
    ) -> List[Tuple[str, float]]:
        """현재 상황에서 성공적이었던 카드 목록 반환"""
        expansion = await self.analyze_patterns(
            place, interaction_partner, current_activity
        )

        # 카드별 점수 집계
        card_scores: Dict[str, float] = {}

        feedbacks = self._load_feedbacks()
        query_text = f"{place} {current_activity}"
        query_tokens = self._tokenize(query_text)
        idf = self._compute_idf(feedbacks)

        for fb in feedbacks:
            context = fb.get("context", {})
            doc_text = f"{context.get('place', '')} {context.get('currentActivity', '')}"
            doc_tokens = self._tokenize(doc_text)

            similarity = self._compute_tfidf_similarity(query_tokens, doc_tokens, idf)
            recency = self._compute_recency_weight(fb.get("confirmedAt", ""))
            score = similarity * recency

            for card in fb.get("cards", []):
                card_scores[card] = card_scores.get(card, 0) + score

        # 상위 k개 반환
        sorted_cards = sorted(
            card_scores.items(),
            key=lambda x: x[1],
            reverse=True,
        )

        return sorted_cards[:top_k]


class NoOpFeedbackAnalyzer(IFeedbackAnalyzer):
    """피드백 분석 비활성화 시 사용하는 No-op 구현"""

    async def analyze_patterns(
        self,
        place: str,
        interaction_partner: str,
        current_activity: str,
        user_id: Optional[str] = None,
    ) -> QueryExpansion:
        """빈 확장 정보 반환"""
        return QueryExpansion(
            original_context={
                "place": place,
                "interaction_partner": interaction_partner,
                "current_activity": current_activity,
            },
            confidence=0.0,
        )

    async def get_successful_cards(
        self,
        place: str,
        interaction_partner: str,
        current_activity: str,
        top_k: int = 5,
    ) -> List[Tuple[str, float]]:
        """빈 리스트 반환"""
        return []
