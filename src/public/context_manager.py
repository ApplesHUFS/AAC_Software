import json
from typing import Dict, List, Optional, Any
import uuid
from datetime import datetime


class ContextManager:
    """상황 정보 관리 시스템.

    Partner가 입력하는 대화 상황 정보를 관리합니다.
    time(시스템 자동), place(직접 입력), interaction_partner(직접 입력),
    current_activity(선택사항) 정보를 수집하여 카드 해석에 활용합니다.

    Attributes:
        contexts: 컨텍스트 ID별 정보 저장
        config: 설정 딕셔너리
        user_context_history: 사용자별 컨텍스트 이력
    """

    def __init__(self, config: Optional[Dict] = None):
        """ContextManager 초기화.

        Args:
            config: 설정 딕셔너리. None이면 기본값 사용.
        """
        self.contexts = {}
        self.config = config or {}
        self.user_context_history = {}  # user_id별 컨텍스트 이력

    def create_context(self,
                      place: str,
                      interaction_partner: str,
                      current_activity: Optional[str] = None,
                      user_id: Optional[str] = None) -> Dict[str, Any]:
        """새로운 대화 상황 컨텍스트 생성.

        Partner가 대화 상황 정보를 입력하여 컨텍스트를 생성합니다.
        시간은 시스템에서 자동으로 설정됩니다.

        Args:
            place: 장소 정보 (직접 입력, 필수)
            interaction_partner: 대화 상대 관계 (직접 입력, 필수)
            current_activity: 현재 활동 내용 (직접 입력, 선택사항)
            user_id: 사용자 ID (선택사항)

        Returns:
            Dict containing:
                - status (str): 'success' 또는 'error'
                - context_id (str): 생성된 컨텍스트 ID
                - context (Dict): 컨텍스트 정보
                - message (str): 결과 메시지
        """
        # 필수 필드 검증
        if not place or not place.strip():
            return {
                'status': 'error',
                'context_id': '',
                'context': {},
                'message': '장소(place)는 필수 입력사항입니다.'
            }

        if not interaction_partner or not interaction_partner.strip():
            return {
                'status': 'error',
                'context_id': '',
                'context': {},
                'message': '대화상대(interaction_partner)는 필수 입력사항입니다.'
            }

        # current_activity는 옵션 필드 (흐름 명세서에 따라)
        current_activity = current_activity.strip() if current_activity else ""

        context_id = str(uuid.uuid4())

        # time 필드는 시스템에서 자동 생성
        current_time = datetime.now()
        time_str = current_time.strftime("%H시 %M분")  # 한국어 표준 시간 형식

        context = {
            'time': time_str,  # 시스템에서 자동 생성
            'place': place.strip(),
            'interaction_partner': interaction_partner.strip(),
            'current_activity': current_activity,  # 옵션 필드, 빈 값 허용
            'created_at': current_time.isoformat()
        }

        self.contexts[context_id] = context

        # 사용자별 컨텍스트 히스토리 관리
        if user_id:
            if user_id not in self.user_context_history:
                self.user_context_history[user_id] = []
            self.user_context_history[user_id].append(context_id)

            # 최대 50개까지만 보관 (메모리 관리)
            if len(self.user_context_history[user_id]) > 50:
                self.user_context_history[user_id] = self.user_context_history[user_id][-50:]

        return {
            'status': 'success',
            'context_id': context_id,
            'context': context
        }
