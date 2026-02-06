"""LLM 필터 설정 (SSOT)

모든 LLM 기반 필터링 관련 설정을 중앙 관리
DRY 원칙: 설정값을 한 곳에서만 정의
"""

from dataclasses import dataclass, field
from typing import FrozenSet


@dataclass(frozen=True)
class LLMFilterConfig:
    """LLM 기반 필터 설정"""

    # 필터 활성화
    enable_llm_filter: bool = True
    enable_llm_reranker: bool = True

    # 배치 크기 (API 호출당 처리할 카드 수)
    filter_batch_size: int = 40
    rerank_batch_size: int = 30

    # 온도 설정 (낮을수록 일관된 결과)
    filter_temperature: float = 0.3
    rerank_temperature: float = 0.2

    # 토큰 제한
    filter_max_tokens: int = 1000
    rerank_max_tokens: int = 600

    # 재시도 설정
    max_retries: int = 3
    retry_delay_base: float = 2.0


@dataclass(frozen=True)
class AgeAppropriatenessConfig:
    """나이별 부적절 키워드 설정 (폴백용)

    LLM 필터 실패 시 사용되는 키워드 기반 폴백
    """

    # 아동 (6-12세) 부적절 키워드
    child_inappropriate: FrozenSet[str] = field(
        default_factory=lambda: frozenset(
            {
                "사랑에 빠지다",
                "연애하다",
                "키스하다",
                "결혼",
                "신혼부부",
                "결혼한 커플",
                "기저귀를 갈다",
                "기저귀를 입은",
                "잠자는 숲속의 미녀",
                "생리대",
                "임신",
                "출산",
                "성관계",
            }
        )
    )

    # 청소년 (13-17세) 부적절 키워드
    teen_inappropriate: FrozenSet[str] = field(
        default_factory=lambda: frozenset(
            {
                "기저귀를 갈다",
                "기저귀를 입은",
            }
        )
    )

    # 기본 (모든 나이) 부적절 키워드
    universal_inappropriate: FrozenSet[str] = field(
        default_factory=lambda: frozenset(
            {
                "강간",
                "성매매",
                "자살",
                "살인",
                "학대",
                "마약",
            }
        )
    )


@dataclass(frozen=True)
class FilterSettings:
    """필터 설정 통합"""

    llm_config: LLMFilterConfig = field(default_factory=LLMFilterConfig)
    age_config: AgeAppropriatenessConfig = field(
        default_factory=AgeAppropriatenessConfig
    )


def get_filter_settings() -> FilterSettings:
    """필터 설정 반환"""
    return FilterSettings()
