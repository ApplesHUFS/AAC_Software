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
    """

    def __init__(self, config: Optional[Dict] = None):
        """ContextManager 초기화.

        Args:
            config: 설정 딕셔너리.
        """
        self.config = config
        self.contexts = {}

    def create_context(self,
                      place: str,
                      interaction_partner: str,
                      user_id: str,
                      current_activity: Optional[str] = None
                      ) -> Dict[str, Any]:
        """새로운 대화 상황 컨텍스트 생성.

        Partner가 대화 상황 정보를 입력하여 컨텍스트를 생성합니다.
        
        Args:
            place: 장소 정보 (직접 입력, 필수)
            interaction_partner: 대화 상대 관계 (직접 입력, 필수)
            current_activity: 현재 활동 내용 (직접 입력, 선택사항)
            user_id: 사용자 ID

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
                'message': '장소 정보는 필수 입력사항입니다. 구체적인 장소를 입력해주세요.'
            }

        if not interaction_partner or not interaction_partner.strip():
            return {
                'status': 'error',
                'context_id': '',
                'context': {},
                'message': '대화 상대 정보는 필수 입력사항입니다. 대화 상대와의 관계를 입력해주세요.'
            }

        if not user_id or not user_id.strip():
            return {
                'status': 'error',
                'context_id': '',
                'context': {},
                'message': '사용자 ID가 누락되었습니다. 올바른 사용자 ID를 제공해주세요.'
            }

        try:
            # 현재 활동 정보 처리
            current_activity = current_activity.strip() if current_activity else ""

            # 고유 컨텍스트 ID 생성
            context_id = str(uuid.uuid4())

            # 현재 시간 생성
            current_time = datetime.now()
            time_str = current_time.strftime("%H시 %M분")

            # 컨텍스트 데이터 구성
            context = {
                'time': time_str,
                'place': place.strip(),
                'interaction_partner': interaction_partner.strip(),
                'current_activity': current_activity,
                'created_at': current_time.isoformat()
            }

            # 컨텍스트 저장 (조회를 위해)
            self.contexts[context_id] = context

            activity_info = f" (활동: {current_activity})" if current_activity else ""
            return {
                'status': 'success',
                'context_id': context_id,
                'context': context,
                'message': f'{time_str} {place}에서 {interaction_partner}와의 대화 상황이 설정되었습니다{activity_info}'
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'context_id': '',
                'context': {},
                'message': f'컨텍스트 생성 처리 중 시스템 오류가 발생했습니다: {str(e)}'
            }

    def get_context(self, context_id: str) -> Dict[str, Any]:
        """컨텍스트 ID로 컨텍스트 정보 조회.

        Args:
            context_id: 조회할 컨텍스트 ID

        Returns:
            Dict containing:
                - status (str): 'success' 또는 'error'
                - context (Dict): 컨텍스트 정보 or 빈 딕셔너리
                - message (str): 결과 메시지
        """
        # 컨텍스트 존재 여부 확인 (비즈니스 로직)
        if context_id not in self.contexts:
            return {
                'status': 'error',
                'context': {},
                'message': f'컨텍스트 ID {context_id}에 해당하는 대화 상황을 찾을 수 없습니다.'
            }

        try:
            # 컨텍스트 정보 복사
            context = self.contexts[context_id].copy()

            # 조회용 컨텍스트 정보 구성
            display_context = {
                'id': context_id,
                'time': context['time'],
                'place': context['place'],
                'interaction_partner': context['interaction_partner'],
                'current_activity': context['current_activity'],
                'created_at': context['created_at'],
                'status': 'active'
            }

            activity_info = f" (활동: {context['current_activity']})" if context['current_activity'] else ""
            return {
                'status': 'success',
                'context': display_context,
                'message': f'{context["time"]} {context["place"]}에서 {context["interaction_partner"]}와의 대화 상황을 조회했습니다{activity_info}'
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'context': {},
                'message': f'컨텍스트 조회 처리 중 시스템 오류가 발생했습니다: {str(e)}'
            }