"""LLM 필터 설정 (하위 호환성 유지)

DEPRECATED: settings.py로 통합됨
이 모듈은 하위 호환성을 위해 settings.py를 re-export합니다.
"""

from app.config.settings import (
    AgeAppropriatenessConfig,
    LLMConfig as LLMFilterConfig,
    get_settings,
)

__all__ = [
    "AgeAppropriatenessConfig",
    "LLMFilterConfig",
    "FilterSettings",
    "get_filter_settings",
]


class FilterSettings:
    """필터 설정 통합 (하위 호환성)"""

    def __init__(self):
        settings = get_settings()
        self.llm_config = settings.llm
        self.age_config = settings.age_appropriateness


def get_filter_settings() -> FilterSettings:
    """필터 설정 반환"""
    return FilterSettings()
