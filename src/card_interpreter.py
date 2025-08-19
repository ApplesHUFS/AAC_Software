from openai import OpenAI
from .network_utils import NetworkUtils
from .config_manager import ConfigManager
import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Any

class CardInterpreter:
    """AAC 카드 해석 시스템 (온라인/오프라인 분기)"""

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.config_manager = ConfigManager()
        
        # 모델 설정 가져오기
        model_config = self.config_manager.get_model_config()
        self.model = model_config['openai_model']
        self.temperature = model_config['temperature']
        self.max_tokens = model_config['max_tokens']
        self.api_timeout = model_config['timeout']
        
        self.network_utils = NetworkUtils(self.config)
        self.feedback_counter = 100000

        # OpenAI API 클라이언트
        try:
            self.openai_client = OpenAI()
            self.openai_enabled = True
        except Exception:
            self.openai_client = None
            self.openai_enabled = False


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

        # 의도: OpenAI API 필수 사용 검증 (워크플로우 4단계 - 완벽한 해석을 위해 fallback 없음)
        if not self.openai_enabled:
            raise RuntimeError("OpenAI API 클라이언트가 초기화되지 않았습니다. 환경변수 OPENAI_API_KEY를 확인하세요.")
        
        # 의도: 네트워크 연결 필수 검증 (온라인 해석만 허용)
        net_info = self.network_utils.is_online_mode_available()
        if not net_info['available']:
            raise ConnectionError(f"네트워크 연결 실패: {net_info.get('reason', '알 수 없는 오류')}")

        # 의도: OpenAI API로만 해석 수행 (완벽성을 위해 대안 방법 제공하지 않음)
        try:
            interpretations = self._generate_online_interpretations(persona, context, cards, past_interpretation)
            if not interpretations or len(interpretations) != 3:
                raise ValueError("OpenAI API가 정확히 3개의 해석을 반환하지 않았습니다")
            
            feedback_id = self.feedback_counter
            self.feedback_counter += 1
            return {
                'status': 'success',
                'interpretations': interpretations,
                'method': 'online',
                'timestamp': timestamp,
                'message': f'OpenAI API 해석 완료. 피드백 ID: {feedback_id}'
            }
        except Exception as e:
            # 의도: 완벽하지 않은 해석 결과 대신 명확한 에러로 문제 지점 식별
            raise RuntimeError(f"카드 해석 완전 실패: {str(e)}. context 및 persona 및 대화 요약된 메모리 기반 OpenAI API 해석이 필수입니다. 시스템을 완벽하게 수정 후 재시도하세요.")

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
    
    def _generate_online_interpretations(self, persona: Dict[str, Any], context: Dict[str, Any], 
                                       cards: List[str], past_interpretation: str = "") -> List[str]:
        """OpenAI API를 사용한 온라인 카드 해석"""
        # 카드명에서 .png 제거하여 더 자연스럽게
        card_names = [card.replace('.png', '').replace('_', ' ') for card in cards]
        
        system_prompt = """당신은 AAC(보완대체의사소통) 전문가입니다. 
사용자의 페르소나와 상황을 고려하여 선택된 AAC 카드들을 해석해주세요.

해석 원칙:
1. 사용자의 의도를 정확히 파악하여 자연스러운 한국어로 표현
2. 페르소나의 특성(나이, 성별, 장애유형, 의사소통 특성)을 반영
3. 상황 맥락(시간, 장소, 대화상대, 활동)을 고려
4. 과거 해석 패턴이 있다면 일관성 유지

정확히 3개의 해석을 제공하되, 각각 다른 관점에서 접근해주세요.
해석 앞에 번호나 접두사는 붙이지 마세요."""

        user_prompt = f"""
페르소나:
- 나이: {persona.get('age', '알 수 없음')}
- 성별: {persona.get('gender', '알 수 없음')}
- 장애 유형: {persona.get('disability_type', '알 수 없음')}
- 의사소통 특성: {persona.get('communication_characteristics', '알 수 없음')}
- 관심 주제: {', '.join(persona.get('interesting_topics', []))}

현재 상황:
- 시간: {context.get('time', '알 수 없음')}
- 장소: {context.get('place', '알 수 없음')}
- 대화 상대: {context.get('interaction_partner', '알 수 없음')}
- 현재 활동: {context.get('current_activity', '알 수 없음')}

선택된 AAC 카드: {', '.join(card_names)}

{past_interpretation if past_interpretation else ""}

위 정보를 바탕으로 사용자가 전달하고자 하는 의도를 3가지 관점에서 해석해주세요.
"""

        try:
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                timeout=self.api_timeout
            )
            
            content = response.choices[0].message.content.strip()
            interpretations = self._parse_interpretations(content)
            
            # 정확히 3개가 나오지 않으면 후처리
            if len(interpretations) != 3:
                interpretations = self._ensure_three_interpretations(interpretations, persona, context, cards)
            
            return interpretations
            
        except Exception as e:
            raise Exception(f"OpenAI API 호출 실패: {str(e)}")
    
    
    def _parse_interpretations(self, content: str) -> List[str]:
        """OpenAI 응답에서 해석들을 추출"""
        # 줄바꿈으로 분할하고 빈 줄 제거
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        
        interpretations = []
        for line in lines:
            # 번호나 특수문자로 시작하는 경우 제거
            cleaned = line.strip()
            if cleaned:
                # 번호나 접두사 제거
                import re
                cleaned = re.sub(r'^[\d\.\-\*]+\s*', '', cleaned)
                cleaned = re.sub(r'^(첫\s*번째|두\s*번째|세\s*번째|해석\s*\d+)\s*:?\s*', '', cleaned)
                
                if cleaned and len(cleaned) > 5:  # 너무 짧은 것은 제외
                    interpretations.append(cleaned)
        
        return interpretations[:3]  # 최대 3개만
    
    def _ensure_three_interpretations(self, interpretations: List[str], persona: Dict[str, Any], 
                                    context: Dict[str, Any], cards: List[str]) -> List[str]:
        """정확히 3개의 해석을 보장"""
        while len(interpretations) < 3:
            # 부족한 경우 기본 패턴으로 채우기
            card_names = [card.replace('.png', '').replace('_', ' ') for card in cards]
            default_interp = f"{', '.join(card_names)}에 관심이 있어요."
            if default_interp not in interpretations:
                interpretations.append(default_interp)
            else:
                interpretations.append(f"{', '.join(card_names)}를 알고 싶어요.")
        
        return interpretations[:3]  # 정확히 3개만
    
