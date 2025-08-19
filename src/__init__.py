"""
AAC 카드 해석 시스템 - 메인 모듈

모듈화된 구조:
- aac_interpreter_service: 메인 서비스 컨트롤러 (src 루트에 위치)
- public: 외부 API 및 사용자 인터페이스 모듈
- private: 내부 비즈니스 로직 및 데이터 처리 모듈
"""

# 메인 서비스 (src 루트)
from .aac_interpreter_service import AACInterpreterService

# Public 모듈들 (외부 접근 가능)
from .public import UserManager, ContextManager, FeedbackManager

# Private 모듈들 (내부 처리)
from .private import (
    ConfigManager,
    CardRecommender,
    CardSelector, 
    CardInterpreter,
    ConversationSummaryMemory
)

__all__ = [
    # 메인 서비스
    'AACInterpreterService',
    
    # Public 모듈
    'UserManager',
    'ContextManager', 
    'FeedbackManager',
    
    # Private 모듈
    'ConfigManager',
    'CardRecommender',
    'CardSelector',
    'CardInterpreter', 
    'ConversationSummaryMemory'
]