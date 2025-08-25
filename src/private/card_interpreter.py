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
            config: 설정 딕셔너리.
        """
        self.config = config

        # LLMFactory 초기화
        llm_config = {
            'openai_model': self.config.get('openai_model'),
            'openai_temperature': self.config.get('openai_temperature'),
            'interpretation_max_tokens': self.config.get('interpretation_max_tokens'),
            'summary_max_tokens': self.config.get('summary_max_tokens'),
            'api_timeout': self.config.get('api_timeout'),
            'images_folder': self.config.get('images_folder')
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
