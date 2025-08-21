"""
AAC 카드 해석 시스템 - 메인 모듈

모듈화된 구조:
- public: 외부 API 및 사용자 인터페이스 모듈
- private: 내부 비즈니스 로직 및 데이터 처리 모듈
- private.llm: OpenAI API 통합 관리 모듈
"""

# config
from . import service_config

# Public 모듈들 (외부 접근 가능)
from src.public import UserManager, ContextManager, FeedbackManager

# Private 모듈들 (내부 처리)
from src.private import (
    CardRecommender,
    CardInterpreter,
    ConversationSummaryMemory,
    LLMFactory
)

__all__ = [
    # config
    'service_config',

    # Public 모듈
    'UserManager',
    'ContextManager',
    'FeedbackManager',

    # Private 모듈
    'CardRecommender',
    'CardInterpreter',
    'ConversationSummaryMemory',
    'LLMFactory'
]
