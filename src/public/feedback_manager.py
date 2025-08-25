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
        with open(self.feedback_file_path, "w", encoding="utf-8") as f:
            json.dump(self._data, f, ensure_ascii=False, indent=2)

    def _load_from_file(self):
        """파일에서 피드백 데이터 로드"""
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
                    'time': context.get('time'),
                    'place': context.get('place'),
                    'current_activity': context.get('current_activity')
                },
                'selected_cards': cards,
                'interpretation_options': [
                    {'index': i, 'interpretation': interp}
                    for i, interp in enumerate(interpretations)
                ],
                'partner': partner_info,
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
            "timestamp": datetime.now().isoformat()
        }

        self._data["interpretations"].append(attempt_record)
        self._save_to_file()

        return {
            "status": "success",
            "feedback_id": feedback_id,
            "message": "해석 시도가 기록되었습니다."
        }
