import openai
import json
from typing import Dict, List, Optional, Any
import uuid
import ConfigManager


class ContextManager:
    """상황 정보 관리 및 컨텍스트 기반 추천"""
    
    def __init__(self, config: Optional[Dict] = None):
        self.contexts = {}
        self.config = config or {}
    
    def create_context(self, 
                      time: Optional[str] = None,
                      place: Optional[str] = None,
                      interaction_partner: Optional[str] = None,
                      current_activity: Optional[str] = None,
                      additional_info: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        새로운 컨텍스트 생성
        
        Args:
            time: 시간 정보
            place: 장소 정보
            interaction_partner: 대화 상대
            current_activity: 현재 활동
            additional_info: 추가 정보
            
        Returns:
            Dict[str, Any]: {
                'status': str,
                'context_id': str,
                'context': Dict,
                'suggestions': List[str] 
            }
        """

        context_id = str(uuid.uuid4())
        context = {
            'time': time,
            'place': place,
            'interaction_partner': interaction_partner,
            'current_activity': current_activity,
            'additional_info': additional_info or {}
        }

        self.contexts[context_id] = context

        return {
            'status': 'success',
            'context_id': context_id,
            'context': context,
            'suggestions': []  
        }


    def update_context(self, context_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        기존 컨텍스트 업데이트
        
        Args:
            context_id: 컨텍스트 ID
            updates: 업데이트할 정보
            
        Returns:
            Dict[str, Any]: {
                'status': str,
                'updated_context': Dict,
                'message': str
            }
        """
        
        context = self.contexts.get(context_id)

        if not context:
            return {
                'status': 'error',
                'updated_context': None,
                'message': f'Context with ID {context_id} not found.'
            }

        for key, value in updates.items():
            if key in context:
                context[key] = value
        
        return {
            'status': 'success',
            'updated_context': context,
            'message': f'Context {context_id} updated successfully.'
        }
    

    def get_context_suggestions(self, context: Dict[str, Any], persona: Dict[str, Any]) -> Dict[str, Any]:
        """
        컨텍스트와 페르소나를 기반으로 한 제안
        
        Args:
            context: 현재 컨텍스트
            persona: 사용자 페르소나
            
        Returns:
            Dict[str, Any]: {
                'status': str,
                'card_suggestions': List[str],
                'activity_suggestions': List[str],
                'relevance_scores': List[float]
            }
        """

        prompt=f'''
            당신은 사용자의 상황과 성향을 분석하여 AAC 카드에 대한 개인화된 제안을 하는 전문가입니다.

            현재 상황:
            - 시간: {context.get('time', '알 수 없음')}
            - 장소: {context.get('place', '알 수 없음')}
            - 대화 상대: {context.get('interaction_partner', '알 수 없음')}
            - 현재 활동: {context.get('current_activity', '알 수 없음')}

            사용자 페르소나:
            - 나이: {persona.get('age', '알 수 없음')}
            - 성별: {persona.get('gender', '알 수 없음')}
            - 장애유형: {persona.get('disability_type', '알 수 없음')}
            - 대화 특징: 
                '선택하는 카드 개수': {persona.get('communication_characteristics', '알 수 없음').get('selection_complexity', '알 수 없음')},
                '선호 카테고리': {persona.get('communication_characteristics', '알 수 없음').get('preferred_category_type', '알 수 없음')},
                '관심 주제: {persona.get('communication_characteristics','알 수 없음').get('interesting_topic', '알 수 없음')}

                
            이 정보를 바탕으로 적합한 추천 카드 조합과 활동을 3개씩, 관련도 점수와 함께 JSON 형식으로 제안해주세요.

            [형식 예시]
            {{
            "card_suggestions": ["카드1", "카드2", "카드3"],
            "activity_suggestions": ["활동1", "활동2", "활동3"],
            "relevance_scores": [0.9, 0.8, 0.7]
            }}
            '''
        try:
            model_config = self.config_manager.get_model_config()


            response = openai.ChatCompletion.create(
                model = model_config['openai_model'],
                messages = [
                    {'role':'system', 'content': '당신은 개인화 추천 전문가입니다.'},
                    {'role':'user', 'content': prompt}
                ],
                max_tokens=model_config['max_token'],
                temperature=model_config['temperature']
            )
            ai_response = response['choices'][0]['message']['content']
            suggestions = self.parse_ai_response(ai_response)

            return {
                'status' : 'success',
                'card_suggestions' : suggestions.get('card_suggestions', []),
                'activity_suggestions': suggestions.get('activity_suggestions', []),
                'relevance_scores': suggestions.get('relevance_scores', [])
                }
        except Exception as e:
            return {
                'status': 'error',
                'card_suggestions': [],
                'activity_suggestions': [],
                'relevance_scores': [],
                'error_message': str(e)
            }
    
    def parse_ai_response(self, ai_response: str) -> Dict[str, Any]:
        if '{' in ai_response and '}' in ai_response:
            json_start = ai_response.find('{')
            json_end = ai_response.rfind('}') + 1
            json_str = ai_response[json_start:json_end]
            return json.loads(json_str)

    def analyze_context_patterns(self, user_id: int) -> Dict[str, Any]:
        """
        사용자의 컨텍스트 패턴 분석
        
        Args:
            user_id: 사용자 ID
            
        Returns:
            Dict[str, Any]: {
                'status': str,
                'frequent_contexts': List[Dict],
                'time_patterns': Dict,
                'place_patterns': Dict,
                'activity_patterns': Dict
            }
        """
        pass

    
    def validate_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        컨텍스트 정보 유효성 검사
        
        Args:
            context: 검사할 컨텍스트
            
        Returns:
            Dict[str, Any]: {
                'valid': bool,
                'errors': List[str],
                'warnings': List[str]
            }
        """
        required_context = [
            'time',
            'place',
            'interaction_partner',
            'current_activity'
        ]

        errors = []
        warnings = []

        for key in required_context:
            if key not in context or context[key] is None:
                errors.append(f"Required context field missing or empty: {key}") 
        
        if context.get('time'):
            time = context.get('time')
            if int(time)<0 or int(time)>24:
                warnings.append("Time value must be between 0 and 24")


        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }