"""
AAC 카드 해석 시스템 - 메인 모듈

모듈화된 구조:
- public: 외부 API 및 사용자 인터페이스 모듈
- private: 내부 비즈니스 로직 및 데이터 처리 모듈
- private.llm: OpenAI API 통합 관리 모듈
- service_config: 서비스 설정 및 구성 모듈
- aac_interpreter: AAC 카드 해석 제어 모듈
"""

# config
from . import service_config

# Public 모듈들
from backend.public import UserManager, ContextManager, FeedbackManager

# Private 모듈들
from backend.private import (
    CardRecommender,
    CardInterpreter,
    ConversationSummaryMemory,
    LLMFactory
)

from aac_interpreter_service import AACInterpreterService

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
    'LLMFactory',

    # 제어 모듈
    'AACInterpreterService'
]
