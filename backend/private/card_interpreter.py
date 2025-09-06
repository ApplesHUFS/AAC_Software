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
        self.feedback_counter = 100000

        try:
            # LLM 팩토리 설정 구성
            llm_config = {
                'openai_model': self.config.get('openai_model'),
                'openai_temperature': self.config.get('openai_temperature'),
                'interpretation_max_tokens': self.config.get('interpretation_max_tokens'),
                'summary_max_tokens': self.config.get('summary_max_tokens'),
                'api_timeout': self.config.get('api_timeout'),
                'images_folder': self.config.get('images_folder')
            }
            
            # LLM 팩토리 초기화
            self.llm_factory = LLMFactory(llm_config)
            
        except Exception as e:
            print(f"LLM 팩토리 초기화 실패: {e}")
            self.llm_factory = None

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
                - method (str): 'online' 또는 'none'
                - timestamp (str): 해석 생성 시간
                - message (str): 결과 메시지
        """
        timestamp = datetime.now().isoformat()

        # 입력 검증
        if not persona or not isinstance(persona, dict):
            return {
                'status': 'error',
                'interpretations': [],
                'method': 'none',
                'timestamp': timestamp,
                'message': '페르소나 정보가 제공되지 않았습니다. 사용자 페르소나 데이터가 필요합니다.'
            }

        if not context or not isinstance(context, dict):
            return {
                'status': 'error',
                'interpretations': [],
                'method': 'none',
                'timestamp': timestamp,
                'message': '컨텍스트 정보가 제공되지 않았습니다. 대화 상황 정보가 필요합니다.'
            }

        if not cards or len(cards) == 0:
            return {
                'status': 'error',
                'interpretations': [],
                'method': 'none',
                'timestamp': timestamp,
                'message': '해석할 카드가 선택되지 않았습니다. 최소 1개 이상의 카드를 선택해주세요.'
            }

        max_cards = self.config.get('max_card_selection', 4)
        if len(cards) > max_cards:
            return {
                'status': 'error',
                'interpretations': [],
                'method': 'none',
                'timestamp': timestamp,
                'message': f'선택된 카드가 너무 많습니다. 최대 {max_cards}개까지만 선택 가능합니다. (현재: {len(cards)}개)'
            }

        # LLM 팩토리 사용 가능 여부 확인
        if self.llm_factory is None:
            return {
                'status': 'error',
                'interpretations': [],
                'method': 'none',
                'timestamp': timestamp,
                'message': 'AI 해석 시스템을 사용할 수 없습니다. OpenAI API 설정을 확인해주세요.'
            }

        try:
            # 사용자 정보 확인
            user_name = persona.get('name', '사용자')
            disability_type = persona.get('disability_type', '알 수 없음')
            place = context.get('place', '알 수 없는 장소')
            
            # LLM 팩토리를 통한 카드 해석 생성
            interpretations = self.llm_factory.generate_card_interpretations(
                persona, context, cards, past_interpretation
            )

            # 피드백 ID 생성
            feedback_id = self.feedback_counter
            self.feedback_counter += 1

            card_names = [card.replace('.png', '').replace('_', ' ') for card in cards]
            memory_info = " (과거 해석 패턴 반영)" if past_interpretation else ""

            return {
                'status': 'success',
                'interpretations': interpretations,
                'method': 'online',
                'timestamp': timestamp,
                'message': f'{place}에서 {user_name}({disability_type})의 {len(cards)}개 카드 조합이 해석되었습니다{memory_info}'
            }

        except ValueError as e:
            # 해석 개수 오류 등 예상 가능한 오류
            return {
                'status': 'error',
                'interpretations': [],
                'method': 'none',
                'timestamp': timestamp,
                'message': f'카드 해석 생성 중 오류가 발생했습니다: {str(e)}'
            }

        except Exception as e:
            # 예상치 못한 시스템 오류
            return {
                'status': 'error',
                'interpretations': [],
                'method': 'none',
                'timestamp': timestamp,
                'message': f'카드 해석 처리 중 시스템 오류가 발생했습니다: {str(e)}'
            }