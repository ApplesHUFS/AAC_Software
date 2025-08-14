# 1. 입력
"""
구현해야 할 것
1. 사용자의 나이, 성별, 장애 종류, 의사소통 특성 입력
2. 비밀번호 입력
3. 시간, 장소, 대화 상대, 현재 활동, 카드 조합 입력
4. 피드백 입력
"""
from .user_information import AACUserManager
from .user_context import AACUserContext
from .user_feedback import AACUserFeedback


# 2. 해석
"""
구현해야 할 것
1. 카드를 해석한 문장 생성?
"""
from .interpreting_card import CardInterpreter
