from openai import OpenAI
import json
from typing import Dict, List, Optional, Any
import uuid
from .config_manager import ConfigManager
from sklearn.cluster import KMeans
from collections import Counter
import numpy as np
import pandas as pd

class ContextManager:
    """상황 정보 관리 및 컨텍스트 기반 추천"""
    
    def __init__(self, config: Optional[Dict] = None):
        self.contexts = {}
        self.config = config or {}
        self.user_context_history = {}
        self.config_manager = ConfigManager()
        
        # OpenAI 클라이언트 초기화
        try:
            self.openai_client = OpenAI()
        except Exception:
            self.openai_client = None


    def create_context(self, 
                      time: Optional[str] = None,
                      place: Optional[str] = None,
                      interaction_partner: Optional[str] = None,
                      current_activity: Optional[str] = None,
                      additional_info: Optional[Dict[str, Any]] = None, 
                      user_id: Optional[str] = None)-> Dict[str, Any]:
        """
        새로운 컨텍스트 생성
        
        Args:
            time: 시간 정보
            place: 장소 정보
            interaction_partner: 대화 상대
            current_activity: 현재 활동
            additional_info: 추가 정보
            user_id : 유저 정보(아이디)
            
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

        if user_id:
            if user_id not in self.user_context_history:
                self.user_context_history[user_id]=[]
            self.user_context_history[user_id].append(context_id)

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
        if not self.openai_client:
            return {
                'status': 'error',
                'card_suggestions': [],
                'activity_suggestions': [],
                'relevance_scores': [],
                'error_message': 'OpenAI client not initialized'
            }
            
        try:
            model_config = self.config_manager.get_model_config()

            response = self.openai_client.chat.completions.create(
                model=model_config['openai_model'],
                messages=[
                    {'role': 'system', 'content': '당신은 개인화 추천 전문가입니다.'},
                    {'role': 'user', 'content': prompt}
                ],
                max_tokens=model_config['max_tokens'],
                temperature=model_config['temperature']
            )
            ai_response = response.choices[0].message.content
            suggestions = self.parse_ai_response(ai_response)

            return {
                'status': 'success',
                'card_suggestions': suggestions.get('card_suggestions', []),
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
        try:
            if '{' in ai_response and '}' in ai_response:
                json_start = ai_response.find('{')
                json_end = ai_response.rfind('}') + 1
                json_str = ai_response[json_start:json_end]
                return json.loads(json_str)
            else:
                return {}
        except json.JSONDecodeError:
            return {}

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
        user_context_ids = self.user_context_history.get(user_id, [])

        if not user_context_ids:
            return {
                'status': 'error',
                'message': f'No contexts found for user {user_id}',
                'frequent_contexts': [],
                'time_patterns': {},
                'place_patterns': {},
                'activity_patterns': {}
            }

        contexts=[]
        for context_id in user_context_ids:
            contexts.append(self.contexts.get(context_id))

        if len(contexts) < 3:
            return self._fallback_frequency_analysis(contexts, 3)
        
        # K-means 분석
        vectors = self._contexts_to_onehot_vectors(contexts)
        
        n_clusters = min(3, len(contexts) // 2)
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        cluster_labels = kmeans.fit_predict(vectors)
        
        cluster_counts = Counter(cluster_labels)
        top_clusters = [cluster_id for cluster_id, _ in cluster_counts.most_common(3)]
        
        frequent_contexts = []
        time_patterns = {}
        place_patterns = {}
        activity_patterns = {}
        
        for cluster_id in top_clusters:
            cluster_contexts = [contexts[i] for i, label in enumerate(cluster_labels) if label == cluster_id]
            frequency = len(cluster_contexts)
            
            # 대표값 계산 (최빈값)
            representative = self._get_cluster_representative(cluster_contexts)

            frequent_contexts.append({
                'pattern': f'{representative['time']}-{representative['place']}-{representative['activity']}',
                'frequency': frequency,
                'contexts': cluster_contexts
            })
            
            # 개별 패턴별 집계
            time_patterns[representative['time']] = time_patterns.get(representative['time'], 0) + frequency
            place_patterns[representative['place']] = place_patterns.get(representative['place'], 0) + frequency
            activity_patterns[representative['activity']] = activity_patterns.get(representative['activity'], 0) + frequency

            time_patterns = dict(sorted(time_patterns.items(), key=lambda x: x[1], reverse=True)[:3])
            place_patterns = dict(sorted(place_patterns.items(), key=lambda x: x[1], reverse=True)[:3])
            activity_patterns = dict(sorted(activity_patterns.items(), key=lambda x: x[1], reverse=True)[:3])
            

        return {
            'status':'success',
            'frequent_contexts': frequent_contexts,
            'time_patterns': time_patterns,
            'place_patterns': place_patterns,
            'activity_patterns': activity_patterns
        }
    
    def _contexts_to_onehot_vectors(self, contexts: List[Dict[str, Any]]) -> np.ndarray:
        """컨텍스트를 One-Hot 벡터로 변환"""
        df = pd.DataFrame(contexts)
        
        relevant_columns = ['time', 'place', 'interaction_partner', 'current_activity']
        for col in relevant_columns:
            if col not in df.columns:
                df[col] = '알 수 없음'
            else:
                df[col] = df[col].fillna('알 수 없음')
        
        # One-Hot Encoding
        df_encoded = pd.get_dummies(df[relevant_columns], prefix=relevant_columns)

        return df_encoded.values
    
    def _get_cluster_representative(self, cluster_contexts: List[Dict[str, Any]]) -> Dict[str, str]:
        #클러스터의 대표값(최빈값) 계산
        times = [ctx.get('time', '알 수 없음') for ctx in cluster_contexts]
        places = [ctx.get('place', '알 수 없음') for ctx in cluster_contexts]
        activities = [ctx.get('current_activity', '알 수 없음') for ctx in cluster_contexts]
        
        most_common_time = Counter(times).most_common(1)[0][0] if times else '알 수 없음'
        most_common_place = Counter(places).most_common(1)[0][0] if places else '알 수 없음'
        most_common_activity = Counter(activities).most_common(1)[0][0] if activities else '알 수 없음'
        
        return {
            'time': most_common_time,
            'place': most_common_place,
            'activity': most_common_activity
        }
    
    def _fallback_frequency_analysis(self, contexts: List[Dict[str, Any]], top_n: int) -> Dict[str, Any]:
        """데이터가 적을 때 단순 빈도 분석"""
        def context_to_key(ctx):
            return f"{ctx.get('time', '알 수 없음')}-{ctx.get('place', '알 수 없음')}-{ctx.get('current_activity', '알 수 없음')}"
        
        keys = [context_to_key(ctx) for ctx in contexts]
        freq_counter = Counter(keys)
        
        frequent_contexts = []
        for pattern, freq in freq_counter.most_common(3):
            matching_contexts = [ctx for ctx in contexts if context_to_key(ctx) == pattern]
            frequent_contexts.append({
                'pattern': pattern,
                'frequency': freq,
                'contexts': matching_contexts
            })
        # 개별 패턴 집계
        time_counter = Counter([ctx.get('time', '알 수 없음') for ctx in contexts])
        place_counter = Counter([ctx.get('place', '알 수 없음') for ctx in contexts])
        activity_counter = Counter([ctx.get('current_activity', '알 수 없음') for ctx in contexts])
        
        return {
            'status': 'success',
            'frequent_contexts': frequent_contexts,
            'time_patterns': dict(time_counter.most_common(3)),
            'place_patterns': dict(place_counter.most_common(3)),
            'activity_patterns': dict(activity_counter.most_common(3))
        }
    

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