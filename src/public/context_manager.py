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
            config: 설정 딕셔너리.
        """
        self.contexts = {}
        self.config = config
        self.user_context_history = {}  # user_id별 컨텍스트 이력

    def create_context(self,
                      place: str,
                      interaction_partner: str,
                      current_activity: Optional[str] = None,
                      user_id: Optional[str] = None) -> Dict[str, Any]:
        """새로운 대화 상황 컨텍스트 생성.

        Partner가 대화 상황 정보를 입력하여 컨텍스트를 생성합니다.
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
        # 검증
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

        current_time = datetime.now()
        time_str = current_time.strftime("%H시 %M분")  # 한국어 표준 시간 형식

        context = {
            'time': time_str,
            'place': place.strip(),
            'interaction_partner': interaction_partner.strip(),
            'current_activity': current_activity,
            'created_at': current_time.isoformat(),
            'user_id': user_id  # 추적을 위해 user_id 저장
        }

        self.contexts[context_id] = context

        # 사용자별 컨텍스트 히스토리 관리
        if user_id not in self.user_context_history:
            self.user_context_history[user_id] = []
        self.user_context_history[user_id].append(context_id)

        # 최대 50개까지만 보관 (메모리 관리)
        if len(self.user_context_history[user_id]) > 50:
            self.user_context_history[user_id] = self.user_context_history[user_id][-50:]

        return {
            'status': 'success',
            'context_id': context_id,
            'context': context,
            'message': f'컨텍스트 {context_id}가 성공적으로 생성되었습니다.'
        }

    def get_context(self, context_id: str) -> Dict[str, Any]:
        """컨텍스트 ID로 컨텍스트 정보 조회.

        Args:
            context_id: 조회할 컨텍스트 ID

        Returns:
            Dict containing:
                - status (str): 'success' 또는 'error'
                - context (Dict): 컨텍스트 정보 (성공시)
                - message (str): 결과 메시지
        """
        if context_id not in self.contexts:
            return {
                'status': 'error',
                'context': {},
                'message': f'컨텍스트 ID {context_id}를 찾을 수 없습니다.'
            }

        context = self.contexts[context_id].copy()

        # API 응답용으로 불필요한 내부 필드 제거
        display_context = {
            'id': context_id,
            'time': context['time'],
            'place': context['place'],
            'interaction_partner': context['interaction_partner'],
            'current_activity': context['current_activity'],
            'created_at': context['created_at'],
            'status': 'active'
        }

        return {
            'status': 'success',
            'context': display_context,
            'message': '컨텍스트를 성공적으로 조회했습니다.'
        }

    def get_user_contexts(self, user_id: str, limit: int = 10) -> Dict[str, Any]:
        """사용자의 최근 컨텍스트 이력 조회.

        Args:
            user_id: 사용자 ID
            limit: 조회할 최대 컨텍스트 수

        Returns:
            Dict containing:
                - status (str): 'success' 또는 'error'
                - contexts (List[Dict]): 컨텍스트 목록 (성공시)
                - total_count (int): 전체 컨텍스트 수
                - message (str): 결과 메시지
        """
        if user_id not in self.user_context_history:
            return {
                'status': 'error',
                'contexts': [],
                'total_count': 0,
                'message': f'사용자 {user_id}의 컨텍스트 이력이 없습니다.'
            }

        context_ids = self.user_context_history[user_id]
        total_count = len(context_ids)

        # 최근 limit개 조회 (역순)
        recent_context_ids = context_ids[-limit:] if limit > 0 else context_ids
        recent_context_ids.reverse()  # 최신순으로 정렬

        contexts = []
        for context_id in recent_context_ids:
            if context_id in self.contexts:
                context = self.contexts[context_id]
                contexts.append({
                    'id': context_id,
                    'time': context['time'],
                    'place': context['place'],
                    'interaction_partner': context['interaction_partner'],
                    'current_activity': context['current_activity'],
                    'created_at': context['created_at']
                })

        return {
            'status': 'success',
            'contexts': contexts,
            'total_count': total_count,
            'message': f'사용자 {user_id}의 컨텍스트 {len(contexts)}개를 조회했습니다.'
        }

    def update_context(self, context_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """기존 컨텍스트 정보 업데이트.

        Args:
            context_id: 업데이트할 컨텍스트 ID
            updates: 업데이트할 필드들 (place, interaction_partner, current_activity)

        Returns:
            Dict containing:
                - status (str): 'success' 또는 'error'
                - updated_fields (List[str]): 업데이트된 필드 목록
                - message (str): 결과 메시지
        """
        if context_id not in self.contexts:
            return {
                'status': 'error',
                'updated_fields': [],
                'message': f'컨텍스트 ID {context_id}를 찾을 수 없습니다.'
            }

        context = self.contexts[context_id]
        updated_fields = []

        # 업데이트 가능한 필드들
        updatable_fields = ['place', 'interaction_partner', 'current_activity']

        for field, new_value in updates.items():
            if field in updatable_fields:
                if field in ['place', 'interaction_partner']:
                    # 필수 필드는 빈 값 불허
                    if not new_value or not str(new_value).strip():
                        return {
                            'status': 'error',
                            'updated_fields': [],
                            'message': f'{field}는 필수 필드이므로 빈 값일 수 없습니다.'
                        }
                    context[field] = str(new_value).strip()
                else:
                    # current_activity는 빈 값 허용
                    context[field] = str(new_value).strip() if new_value else ""

                updated_fields.append(field)

        if updated_fields:
            context['updated_at'] = datetime.now().isoformat()

        return {
            'status': 'success',
            'updated_fields': updated_fields,
            'message': f'컨텍스트 {context_id}가 업데이트되었습니다. 업데이트된 필드: {", ".join(updated_fields)}'
        }

    def delete_context(self, context_id: str) -> Dict[str, Any]:
        """컨텍스트 삭제.

        Args:
            context_id: 삭제할 컨텍스트 ID

        Returns:
            Dict containing:
                - status (str): 'success' 또는 'error'
                - message (str): 결과 메시지
        """
        if context_id not in self.contexts:
            return {
                'status': 'error',
                'message': f'컨텍스트 ID {context_id}를 찾을 수 없습니다.'
            }

        context = self.contexts[context_id]
        user_id = context.get('user_id')

        # 컨텍스트 삭제
        del self.contexts[context_id]

        # 사용자 히스토리에서도 제거
        if user_id and user_id in self.user_context_history:
            if context_id in self.user_context_history[user_id]:
                self.user_context_history[user_id].remove(context_id)

        return {
            'status': 'success',
            'message': f'컨텍스트 {context_id}가 성공적으로 삭제되었습니다.'
        }

    def cleanup_old_contexts(self, max_age_days: int = 30) -> Dict[str, Any]:
        """오래된 컨텍스트들 정리.

        Args:
            max_age_days: 보관할 최대 일수

        Returns:
            Dict containing:
                - status (str): 'success'
                - cleaned_count (int): 정리된 컨텍스트 수
                - remaining_count (int): 남은 컨텍스트 수
                - message (str): 결과 메시지
        """
        from datetime import timedelta

        cutoff_time = datetime.now() - timedelta(days=max_age_days)
        cutoff_iso = cutoff_time.isoformat()

        initial_count = len(self.contexts)
        to_delete = []

        # 오래된 컨텍스트 찾기
        for context_id, context in self.contexts.items():
            if context.get('created_at', '') < cutoff_iso:
                to_delete.append(context_id)

        # 정리 실행
        for context_id in to_delete:
            self.delete_context(context_id)

        cleaned_count = len(to_delete)
        remaining_count = len(self.contexts)

        return {
            'status': 'success',
            'cleaned_count': cleaned_count,
            'remaining_count': remaining_count,
            'message': f'{cleaned_count}개의 오래된 컨텍스트가 정리되었습니다. 남은 컨텍스트: {remaining_count}개'
        }
