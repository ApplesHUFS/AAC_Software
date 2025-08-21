from datetime import datetime
from typing import Dict, List, Optional, Any
from .llm import LLMFactory


class CardInterpreter:
    """AAC 카드 해석 엔진.

    사용자가 선택한 카드 조합을 페르소나, 컨텍스트, 대화 메모리를 기반으로
    해석하여 Top-3 가능한 의미를 생성합니다. LLMFactory를 활용합니다.

    Attributes:
        config: 설정 딕셔너리
        llm_factory: OpenAI API 통합 관리 팩토리
        feedback_counter: 피드백 ID 카운터
    """

    def __init__(self, config: Optional[Dict] = None):
        """CardInterpreter 초기화.

        Args:
            config: 설정 딕셔너리. None이면 기본 설정 사용.
        """
        self.config = config or {}

        # LLMFactory 초기화 - config에서 필요한 설정들을 추출
        llm_config = {
            'openai_model': self.config.get('openai_model', 'gpt-4o-2024-08-06'),
            'openai_temperature': self.config.get('openai_temperature', 0.8),
            'interpretation_max_tokens': self.config.get('interpretation_max_tokens', 400),
            'summary_max_tokens': self.config.get('summary_max_tokens', 200),
            'api_timeout': self.config.get('api_timeout', 15),
            'images_folder': self.config.get('images_folder', 'dataset/images')
        }
        self.llm_factory = LLMFactory(llm_config)

        self.feedback_counter = 100000

    def interpret_cards(self,
        persona: Dict[str, Any],
        context: Dict[str, Any],
        cards: List[str],
        past_interpretation: str = ""
    ) -> Dict[str, Any]:
        """선택된 AAC 카드 조합 해석.

        페르소나, 컨텍스트, 과거 해석 이력을 종합하여
        카드 조합의 의미를 3가지 해석으로 생성합니다.

        Args:
            persona: 사용자 페르소나 정보
            context: 현재 상황 정보 (time, place, interaction_partner, current_activity)
            cards: 선택된 카드 파일명 리스트 (1-4개)
            past_interpretation: 과거 해석 이력 요약

        Returns:
            Dict containing:
                - status (str): 'success' 또는 'error'
                - interpretations (List[str]): 3개의 해석 결과
                - method (str): 'online'
                - timestamp (str): 해석 생성 시간
                - message (str): 결과 메시지
        """
        timestamp = datetime.now().isoformat()

        # 입력 검증
        validation = self._validate_input(persona, context, cards)
        if not validation['valid']:
            return {
                'status': 'error',
                'interpretations': [],
                'method': 'none',
                'timestamp': timestamp,
                'message': f"입력 검증 실패: {', '.join(validation['errors'])}"
            }

        # LLMFactory를 통한 해석 생성
        try:
            interpretations = self.llm_factory.generate_card_interpretations(
                persona, context, cards, past_interpretation
            )

            feedback_id = self.feedback_counter
            self.feedback_counter += 1

            return {
                'status': 'success',
                'interpretations': interpretations,
                'method': 'online',
                'timestamp': timestamp,
                'message': f'카드 해석 완료. 피드백 ID: {feedback_id}'
            }

        except Exception as e:
            return {
                'status': 'error',
                'interpretations': [],
                'method': 'none',
                'timestamp': timestamp,
                'message': f'카드 해석 실패: {str(e)}'
            }

    def _validate_input(self,
        persona: Dict[str, Any],
        context: Dict[str, Any],
        cards: List[str]
    ) -> Dict[str, Any]:
        """해석 입력 유효성 검증.

        Args:
            persona: 페르소나 정보
            context: 컨텍스트 정보
            cards: 카드 리스트

        Returns:
            Dict containing:
                - valid (bool): 유효성 여부
                - errors (List[str]): 오류 목록
        """
        errors = []

        # 페르소나 검증
        required_persona_fields = ['age', 'gender', 'disability_type', 'communication_characteristics']
        if not isinstance(persona, dict):
            errors.append("페르소나가 딕셔너리 형태가 아닙니다.")
        else:
            for field in required_persona_fields:
                if field not in persona or not str(persona[field]).strip():
                    errors.append(f"페르소나 '{field}' 값이 누락되었습니다.")

        # 컨텍스트 검증
        required_context_fields = ['time', 'place', 'interaction_partner', 'current_activity']
        if not isinstance(context, dict):
            errors.append("컨텍스트가 딕셔너리 형태가 아닙니다.")
        else:
            for field in required_context_fields:
                if field not in context:
                    errors.append(f"컨텍스트 '{field}' 값이 누락되었습니다.")

        # 카드 검증
        min_cards = self.config.get('min_card_selection', 1)
        max_cards = self.config.get('max_card_selection', 4)

        if not isinstance(cards, list):
            errors.append("카드가 리스트 형태가 아닙니다.")
        elif not (min_cards <= len(cards) <= max_cards):
            errors.append(f"카드는 {min_cards}~{max_cards}개여야 합니다.")
        else:
            for idx, card in enumerate(cards):
                if not isinstance(card, str) or not card.strip():
                    errors.append(f"카드 {idx+1}이 유효하지 않습니다.")
                elif not card.endswith('.png'):
                    errors.append(f"카드 {idx+1}이 PNG 파일이 아닙니다.")

        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
