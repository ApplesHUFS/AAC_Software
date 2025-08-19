import json
from typing import Dict, List, Optional, Any
import uuid
from datetime import datetime

class ContextManager:
    """상황 정보 관리 및 컨텍스트 기반 추천"""
    
    def __init__(self, config: Optional[Dict] = None):
        """간단한 컨텍스트 관리자 초기화"""
        self.contexts = {}
        self.config = config or {}
        self.user_context_history = {}  # user_id별 컨텍스트 히스토리


    def create_context(self, 
                      place: str,
                      interaction_partner: str,
                      current_activity: str,
                      user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        새로운 컨텍스트 생성
        
        Args:
            place: 장소 정보 (직접 입력, 필수)
            interaction_partner: 대화 상대 (직접 입력, 필수)
            current_activity: 현재 활동 (직접 입력, 필수)
            user_id: 유저 ID (선택사항)
            
        Returns:
            Dict[str, Any]: {
                'status': str,
                'context_id': str,
                'context': Dict
            }
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
        
        # current_activity 기본 검증 (빈 값만 체크, 옵션 제한 없음)
        if not current_activity or not current_activity.strip():
            return {
                'status': 'error',
                'context_id': '',
                'context': {},
                'message': '현재 활동(current_activity)는 필수 입력사항입니다.'
            }

        context_id = str(uuid.uuid4())
        
        # 의도: time 필드는 시스템에서 자동 생성 (워크플로우 3.1단계 - 정확한 현재 시간 보장)
        current_time = datetime.now()
        time_str = current_time.strftime("%H시 %M분")  # 한국어 표준 시간 형식
        
        context = {
            'time': time_str,  # 시스템에서 자동 생성
            'place': place.strip(),
            'interaction_partner': interaction_partner.strip(),
            'current_activity': current_activity.strip(),
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


    

    

