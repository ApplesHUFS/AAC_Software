import json
import os
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import uuid


class FeedbackManager:
    """통합 피드백 관리 시스템

    - Partner 피드백 워크플로우 관리
    - 사용자 해석 이력 및 피드백 저장
    - 통계 및 분석 기능 제공

    Attributes:
        feedback_file_path: 피드백 데이터 저장 파일 경로
        _data: 피드백 파일 데이터
        _feedback_id_counter: 피드백 ID 생성 카운터 (1부터 시작)
        confirmation_counter: 확인 요청 ID 생성 카운터 (1000000부터 시작)
        pending_confirmation: 대기 중인 파트너 확인 요청을 저장하는 딕셔너리

    """

    def __init__(self, feedback_file_path: Optional[str] = None):
        self.feedback_file_path = feedback_file_path
        self._data = {
            "interpretations": [],
            "feedbacks": []
        }
        self._feedback_id_counter = 1

        # Partner 피드백 관련 데이터
        self.pending_confirmations = {}  # confirmation_id별 대기 중인 확인 요청들
        self.confirmation_counter = 1000000

        self._load_from_file()

    def _save_to_file(self):
        """피드백 데이터를 파일에 저장"""
        if self.feedback_file_path:
            with open(self.feedback_file_path, "w", encoding="utf-8") as f:
                json.dump(self._data, f, ensure_ascii=False, indent=2)

    def _load_from_file(self):
        """파일에서 피드백 데이터 로드"""
        if self.feedback_file_path and os.path.exists(self.feedback_file_path):
            with open(self.feedback_file_path, "r", encoding="utf-8") as f:
                self._data = json.load(f)
            if self._data.get("feedbacks"):
                self._feedback_id_counter = max([f["feedback_id"] for f in self._data["feedbacks"]]) + 1

    # ===== Partner 피드백 워크플로우 =====

    def request_interpretation_confirmation(self,
                                         user_id: int,
                                         cards: List[str],
                                         context: Dict[str, Any],
                                         interpretations: List[str],
                                         partner_info: Dict[str, Any]) -> Dict[str, Any]:
        """Partner에게 Top-3 해석 중 올바른 해석 확인 요청

        Args:
            user_id: 사용자 ID
            cards: 선택된 AAC 카드들
            context: 상황 정보 (time, place, interaction_partner, current_activity)
            interpretations: 생성된 3개 해석
            partner_info: Partner 정보 (name, relationship 등)

        Returns:
            Dict containing:
                - status (str): 'success' 또는 'error'
                - confirmation_id (str): 생성된 확인 요청 id
                - confirmation_request (dict): 생성된 확인 요청 데이터
                - message (str): 결과 메시지
        """
        if not isinstance(interpretations, list) or len(interpretations) != 3:
            return {
                'status': 'error',
                'confirmation_id': '',
                'confirmation_request': {},
                'message': '정확히 3개의 해석이 필요합니다.'
            }

        confirmation_id = str(self.confirmation_counter)
        self.confirmation_counter += 1

        # 확인 요청 데이터 생성
        confirmation_request = {
            'confirmation_id': confirmation_id,
            'user_id': user_id,
            'cards': cards,
            'context': context,
            'interpretations': interpretations,
            'partner_info': partner_info,
            'created_at': datetime.now().isoformat(),
            'status': 'pending'  # pending, confirmed, direct_feedback
        }

        self.pending_confirmations[confirmation_id] = confirmation_request

        return {
            'status': 'success',
            'confirmation_id': confirmation_id,
            'confirmation_request': {
                'confirmation_id': confirmation_id,
                'user_context': {
                    'time': context.get('time', '알 수 없음'),
                    'place': context.get('place', '알 수 없음'),
                    'current_activity': context.get('current_activity', '')
                },
                'selected_cards': cards,
                'interpretation_options': [
                    {'index': i, 'interpretation': interp}
                    for i, interp in enumerate(interpretations)
                ],
                'partner_name': partner_info.get('name', '대화상대'),
                'partner_relationship': partner_info.get('relationship', context.get('interaction_partner', '알 수 없음'))
            },
            'message': f'Partner 해석 확인 요청이 생성되었습니다. (ID: {confirmation_id})'
        }

    def submit_partner_confirmation(self,
                                  confirmation_id: str,
                                  selected_interpretation_index: Optional[int] = None,
                                  direct_feedback: Optional[str] = None) -> Dict[str, Any]:
        """Partner의 해석 확인 또는 직접 피드백 제출

        Args:
            confirmation_id: 확인 요청 ID
            selected_interpretation_index: 선택된 해석의 인덱스 (0-2)
            direct_feedback: 직접 입력한 올바른 해석

        Returns:
            Dict containing:
                - status (str): 'success' 또는 'error'
                - feedback_result (dict): 생성된 피드백 데이터
                - message (str): 결과 메시지
        """
        if confirmation_id not in self.pending_confirmations:
            return {
                'status': 'error',
                'feedback_result': {},
                'message': f'확인 요청 ID {confirmation_id}를 찾을 수 없습니다.'
            }

        confirmation_request = self.pending_confirmations[confirmation_id]

        # 이미 처리된 요청인지 확인
        if confirmation_request['status'] != 'pending':
            return {
                'status': 'error',
                'feedback_result': {},
                'message': f'확인 요청 {confirmation_id}는 이미 처리되었습니다.'
            }

        # 피드백 유형 결정 및 검증
        if selected_interpretation_index is not None:
            # 해석 선택 피드백
            if not (0 <= selected_interpretation_index <= 2):
                return {
                    'status': 'error',
                    'feedback_result': {},
                    'message': '해석 인덱스는 0, 1, 2 중 하나여야 합니다.'
                }

            feedback_result = {
                'feedback_type': 'interpretation_selected',
                'selected_index': selected_interpretation_index,
                'selected_interpretation': confirmation_request['interpretations'][selected_interpretation_index],
                'direct_feedback': None
            }
            confirmation_request['status'] = 'confirmed'

        elif direct_feedback and direct_feedback.strip():
            # 직접 피드백
            feedback_result = {
                'feedback_type': 'direct_feedback',
                'selected_index': None,
                'selected_interpretation': None,
                'direct_feedback': direct_feedback.strip()
            }
            confirmation_request['status'] = 'direct_feedback'

        else:
            return {
                'status': 'error',
                'feedback_result': {},
                'message': '해석 선택 또는 직접 피드백 중 하나는 필수입니다.'
            }

        # 피드백 결과 저장
        feedback_result.update({
            'confirmation_id': confirmation_id,
            'user_id': confirmation_request['user_id'],
            'cards': confirmation_request['cards'],
            'context': confirmation_request['context'],
            'interpretations': confirmation_request['interpretations'],
            'partner_info': confirmation_request['partner_info'],
            'confirmed_at': datetime.now().isoformat()
        })

        confirmation_request['feedback_result'] = feedback_result

        return {
            'status': 'success',
            'feedback_result': feedback_result,
            'message': f'Partner 피드백이 처리되었습니다. (유형: {feedback_result["feedback_type"]})'
        }

    def get_pending_confirmations(self, partner_filter: Optional[str] = None) -> Dict[str, Any]:
        """대기 중인 확인 요청들 조회

        Args:
            partner_filter: 특정 Partner로 필터링 (선택사항)

        Returns:
            Dict containing:
                - status (str): 'success'
                - pending_requests (List): 대기 중인 확인 요청들
                - total_count (int): 대기 중인 요청 수
        """
        pending_requests = []

        for confirmation_id, request in self.pending_confirmations.items():
            if request['status'] == 'pending':
                if partner_filter is None or request['partner_info'].get('name', '') == partner_filter:
                    pending_requests.append({
                        'confirmation_id': confirmation_id,
                        'user_id': request['user_id'],
                        'cards': request['cards'],
                        'context_summary': {
                            'place': request['context'].get('place', '알 수 없음'),
                            'activity': request['context'].get('current_activity', ''),
                            'time': request['context'].get('time', '알 수 없음')
                        },
                        'interpretations': request['interpretations'],
                        'partner_name': request['partner_info'].get('name', '알 수 없음'),
                        'created_at': request['created_at']
                    })

        # 생성 시간순으로 정렬 (최신순)
        pending_requests.sort(key=lambda x: x['created_at'], reverse=True)

        return {
            'status': 'success',
            'pending_requests': pending_requests,
            'total_count': len(pending_requests)
        }

    def cleanup_old_requests(self, max_age_days: int = 7) -> Dict[str, Any]:
        """오래된 확인 요청들 정리

        Args:
            max_age_days: 보관할 최대 일수

        Returns:
            Dict containing:
                - status (str): 'success'
                - cleaned_count (int): 삭제된 요청 수
                - remaining_count (int): 삭제 후 남아 있는 요청 수
                - message (str): 결과 메시지
        """
        cutoff_time = datetime.now() - timedelta(days=max_age_days)
        cutoff_iso = cutoff_time.isoformat()

        # 오래된 요청들 제거
        to_remove = []
        for confirmation_id, request in self.pending_confirmations.items():
            if request['created_at'] < cutoff_iso:
                to_remove.append(confirmation_id)

        for confirmation_id in to_remove:
            del self.pending_confirmations[confirmation_id]

        cleaned_count = len(to_remove)
        remaining_count = len(self.pending_confirmations)

        return {
            'status': 'success',
            'cleaned_count': cleaned_count,
            'remaining_count': remaining_count,
            'message': f'{cleaned_count}개의 오래된 확인 요청이 정리되었습니다.'
        }

    # ===== 해석 이력 및 피드백 관리 =====

    def record_interpretation_attempt(
        self,
        user_id: int,
        cards: List[str],
        persona: Dict[str, Any],
        context: Dict[str, Any],
        interpretations: List[str],
        method: str = "online"
    ) -> Dict[str, Any]:
        """해석 시도 기록 저장

        Args:
            user_id: 사용자 ID
            cards: 선택된 AAC 카드들
            persona: 사용자 페르소나 정보
            context: 상황 정보
            interpretations: 생성된 해석들
            method: 해석 방법 (online/offline)

        Returns:
            Dict containing:
                - status (str): 'success'
                - feedback_id (int): 해석 시도 기록 저장 시 생성된 피드백 id
                - message (str): '해석 시도가 기록되었습니다.'
        """
        feedback_id = self._feedback_id_counter
        self._feedback_id_counter += 1

        attempt_record = {
            "feedback_id": feedback_id,
            "user_id": user_id,
            "cards": cards,
            "persona": persona,
            "context": context,
            "interpretations": interpretations,
            "method": method,
            "timestamp": datetime.now().isoformat()
        }

        self._data["interpretations"].append(attempt_record)
        # AAC 사용자는 직접 피드백을 제공하지 않으므로 feedbacks 배열에 빈 엔트리 추가하지 않음
        self._save_to_file()

        return {
            "status": "success",
            "feedback_id": feedback_id,
            "message": "해석 시도가 기록되었습니다."
        }

    def get_interpretation_attempt(self, feedback_id: int) -> Dict[str, Any]:
        """피드백 ID로 해석 시도 정보 조회

        Args:
            feedback_id: 피드백 ID

        Returns:
            Dict containing:
                - status (str): 'success' 또는 'error'
                - interpretation_attempt (dict or None): 해석 시도 정보 또는 None
                - message (str): 결과 메시지
        """
        for attempt in self._data["interpretations"]:
            if attempt["feedback_id"] == feedback_id:
                return {
                    "status": "success",
                    "interpretation_attempt": attempt
                }

        return {
            "status": "error",
            "interpretation_attempt": None,
            "message": f"피드백 ID {feedback_id}에 해당하는 해석 시도를 찾을 수 없습니다."
        }

    def get_confirmation_history(self,
                               user_id: Optional[int] = None,
                               limit: int = 20) -> Dict[str, Any]:
        """Partner 확인 요청 이력 조회 (대화 메모리 용도)

        Args:
            user_id: 특정 사용자로 필터링 (선택사항)
            limit: 조회할 기록 수 제한

        Returns:
            Dict containing:
                - status (str): 'success'
                - history (List): 조회된 확인 요청 기록들
                - total_processed (int): 확인된 총 요청 기록 수
        """
        history = []

        for confirmation_id, request in self.pending_confirmations.items():
            if request['status'] in ['confirmed', 'direct_feedback']:
                if user_id is None or request['user_id'] == user_id:
                    feedback_result = request.get('feedback_result', {})
                    history.append({
                        'confirmation_id': confirmation_id,
                        'user_id': request['user_id'],
                        'cards': request['cards'],
                        'context': request['context'],
                        'interpretations': request['interpretations'],
                        'feedback_type': feedback_result.get('feedback_type', '알 수 없음'),
                        'final_interpretation': (
                            feedback_result.get('selected_interpretation') or
                            feedback_result.get('direct_feedback')
                        ),
                        'partner_name': request['partner_info'].get('name', '알 수 없음'),
                        'created_at': request['created_at'],
                        'confirmed_at': feedback_result.get('confirmed_at', '')
                    })

        # 확인 시간순으로 정렬 (최신순)
        history.sort(key=lambda x: x.get('confirmed_at', ''), reverse=True)

        return {
            'status': 'success',
            'history': history[:limit],
            'total_processed': len(history)
        }
