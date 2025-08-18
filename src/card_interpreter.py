from openai import OpenAI
from .network_utils import NetworkUtils
from data.dataset_generator import DatasetGenerator
import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Any

class CardInterpreter:
    """AAC 카드 해석 시스템 (온라인/오프라인 분기)"""

    def __init__(self, config: Optional[Dict] = None):
        # 환경 변수 및 설정값
        self.config = config or {}
        self.model = self.config.get('openai_model', 'gpt-4o-2024-08-06')
        self.temperature = self.config.get('openai_temperature', 0.8)
        self.max_tokens = self.config.get('interpretation_max_tokens', 400)
        self.api_timeout = self.config.get('api_timeout', 15)
        self.images_folder = self.config.get('images_folder', '')
        self.network_utils = NetworkUtils(self.config)
        self.feedback_counter = 100000

        # OpenAI API 클라이언트
        try:
            self.openai_client = OpenAI()
            self.openai_enabled = True
        except Exception:
            self.openai_client = None
            self.openai_enabled = False

        # dataset_generator 활용
        dataset_path = self.config.get("offline_db_path", "dummy.json")
        self.dataset_generator = None
        if self.images_folder:
            try:
                # 실제 파일 경로가 없다면 dummy 사용, 반드시 images_folder 필요
                self.dataset_generator = DatasetGenerator(dataset_path, self.images_folder, config=self.config)
            except Exception:
                self.dataset_generator = None

    def interpret_cards(self, 
        persona: Dict[str, Any],
        context: Dict[str, Any],
        cards: List[str],
        past_interpretation: str = ""
    ) -> Dict[str, Any]:
        timestamp = datetime.now().isoformat()
        validation = self.validate_interpretation_input(persona, context, cards)
        if not validation['valid']:
            return {
                'status': 'error',
                'interpretations': [],
                'method': 'none',
                'timestamp': timestamp,
                'message': f"입력 검증 실패: {', '.join(validation['errors'])}"
            }

        # 네트워크 상태 및 온라인 사용 가능 체크
        net_info = self.network_utils.is_online_mode_available()
        online_available = net_info['available']
        reason = net_info.get('reason', '')
        method = 'online' if online_available and self.openai_enabled else 'offline'

        # --- 온라인 해석 (DatasetGenerator의 _generate_interpretations 사용) ---
        if method == 'online' and self.dataset_generator is not None:
            try:
                interpretations = self.dataset_generator._generate_interpretations(persona, context, cards)
                if interpretations and isinstance(interpretations, list) and len(interpretations) == 3:
                    feedback_id = self.feedback_counter
                    self.feedback_counter += 1
                    return {
                        'status': 'success',
                        'interpretations': interpretations,
                        'method': 'online',
                        'timestamp': timestamp,
                        'message': f'OpenAI API 해석 완료. 피드백 ID: {feedback_id}'
                    }
                else:
                    raise Exception("API 응답 구조/개수 오류 또는 None")
            except Exception as e:
                # 오류 발생 시 오프라인 로직으로 강제 전환
                method = 'offline'
                reason = f"온라인 해석 실패: {str(e)}"

        # --- 오프라인 해석 (dataset_generator의 DB 활용, 예시 채우기) ---
        interpretations = []
        if self.dataset_generator and hasattr(self.dataset_generator, "dataset"):
            # 기존 DB에서 유사 카드를 기반으로 해석 최대 3개 추출
            candidates = []
            for item in self.dataset_generator.dataset:
                src_cards = item['input']['AAC_card_combination']
                src_ctx = item['input']['context']
                card_overlap = len(set(cards) & set(src_cards))
                ctx_match = sum([1 for k in ('time','place','interaction_partner','current_activity')
                                if context.get(k) and src_ctx.get(k) and context.get(k) == src_ctx.get(k)])
                if card_overlap > 0 or ctx_match > 0:
                    output_list = item.get('output', [])
                    if isinstance(output_list, list):
                        candidates.extend(output_list)
            for interp in candidates[:3]:
                interpretations.append(str(interp).strip())
        # 부족할 경우 기본 예시로 채우기(항상 3개)
        if len(interpretations) < 3:
            while len(interpretations) < 3:
                msg = (
                    f"{persona.get('age','?')}세 {persona.get('gender','?')} 사용자가 "
                    f"{context.get('place','?')}에서 {', '.join(cards)} 카드를 사용합니다."
                )
                interpretations.append(msg)
        feedback_id = self.feedback_counter
        self.feedback_counter += 1
        return {
            'status': 'warning' if method == 'offline' else 'success',
            'interpretations': interpretations[:3],
            'method': method,
            'timestamp': timestamp,
            'message': f"{reason or '오프라인 모드 처리'}. 피드백 ID: {feedback_id}"
        }

    def validate_interpretation_input(self, 
        persona: Dict[str, Any],
        context: Dict[str, Any],
        cards: List[str]
    ) -> Dict[str, Any]:
        errors = []
        fields_p = ['age', 'gender', 'disability_type', 'communication_characteristics']
        if not isinstance(persona, dict):
            errors.append("페르소나가 딕셔너리 형태가 아닙니다.")
        else:
            for f in fields_p:
                if f not in persona or not str(persona[f]).strip():
                    errors.append(f"페르소나 '{f}' 값 누락/비어있음")
        fields_c = ['time','place','interaction_partner','current_activity']
        if not isinstance(context, dict):
            errors.append("컨텍스트가 딕셔너리 형태가 아닙니다.")
        else:
            for f in fields_c:
                if f not in context or not str(context[f]).strip():
                    errors.append(f"컨텍스트 '{f}' 값 누락/비어있음")
                if context.get(f) in ['오류', 'error', None]:
                    errors.append(f"컨텍스트 '{f}' 오류값 포함")
        if not isinstance(cards, list):
            errors.append("카드가 리스트 형태가 아닙니다.")
        elif not (1 <= len(cards) <= 4):
            errors.append("카드는 1~4개여야 합니다.")
        else:
            for idx, card in enumerate(cards):
                if not isinstance(card, str):
                    errors.append(f"카드 {idx+1}이 문자열이 아님")
                elif not card.strip():
                    errors.append(f"카드 {idx+1}이 비어 있음")
                elif not card.endswith('.png'):
                    errors.append(f"카드 {idx+1}이 PNG 파일 아님")
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
