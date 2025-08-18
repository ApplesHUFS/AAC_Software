from typing import Dict, List, Optional, Any

from .user_manager import UserManager
from .card_recommender import CardRecommender
from .card_interpreter import CardInterpreter
from .feedback_manager import FeedbackManager
from .network_utils import NetworkUtils
from .context_manager import ContextManager
from .conversation_memory import ConversationSummaryMemory
from .config_manager import ConfigManager


class AACInterpreterService:
    """AAC 카드 해석 시스템의 메인 컨트롤러"""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.config_manager = ConfigManager()
        
        # 각 컴포넌트 초기화
        data_paths = self.config_manager.get_data_paths()
        cluster_config = self.config_manager.get_cluster_config()
        
        self.user_manager = UserManager(data_paths['users_file_path'])
        self.feedback_manager = FeedbackManager(data_paths['feedback_file_path'])
        self.context_manager = ContextManager(config)
        self.conversation_memory = ConversationSummaryMemory(
            memory_file_path=data_paths.get('memory_file_path', 'user_data/conversation_memory.json'),
            config=config
        )
        
        # 카드 추천 및 해석 시스템
        self.card_recommender = CardRecommender(
            cluster_tags_path=str(cluster_config['cluster_tags_path']),
            embeddings_path=str(cluster_config['embeddings_path']),
            clustering_results_path=str(cluster_config['clustering_results_path'])
        )
        self.card_interpreter = CardInterpreter(config)
        
        self.network_utils = NetworkUtils(config)
    
    def register_user(self, persona: Dict[str, Any]) -> Dict[str, Any]:
        """
        새 사용자 등록
        
        Args:
            persona: 사용자 페르소나 정보 {
                'age': str,
                'gender': str,
                'disability_type': str,
                'communication_characteristics': str,
                'selection_complexity': str,
                'interesting_topics': List[str],
                'password': str
            }
            
        Returns:
            Dict[str, Any]: {
                'status': str,
                'user_id': int,
                'message': str
            }
        """
        return self.user_manager.create_user(persona)
    
    def authenticate_user(self, user_id: int, password: str) -> Dict[str, Any]:
        """
        사용자 인증
        
        Args:
            user_id: 사용자 ID
            password: 비밀번호
            
        Returns:
            Dict[str, Any]: {
                'status': str,
                'authenticated': bool,
                'user_info': Dict or None,
                'message': str
            }
        """
        auth_result = self.user_manager.authenticate_user(user_id, password)
        
        if auth_result['authenticated']:
            user_info = self.user_manager.get_user(user_id)
            return {
                'status': 'success',
                'authenticated': True,
                'user_info': user_info.get('user'),
                'message': '인증 성공'
            }
        else:
            return {
                'status': 'error',
                'authenticated': False,
                'user_info': None,
                'message': auth_result['message']
            }
    
    def get_user_info(self, user_id: int) -> Dict[str, Any]:
        """
        사용자 정보 조회
        
        Args:
            user_id: 사용자 ID
            
        Returns:
            Dict[str, Any]: {
                'status': str,
                'user': Dict or None,
                'message': str
            }
        """
        return self.user_manager.get_user(user_id)
    
    def recommend_cards(self, user_id: int, num_cards: int = 4) -> Dict[str, Any]:
        """
        사용자에게 카드 추천 (제시된 흐름의 3.2단계)
        
        Args:
            user_id: 사용자 ID
            num_cards: 추천할 카드 수 (1-4)
            
        Returns:
            Dict[str, Any]: {
                'status': str,
                'recommended_cards': List[str],
                'clusters_used': List[int],
                'message': str
            }
        """
        # 사용자 정보 조회
        user_info = self.user_manager.get_user(user_id)
        if user_info['status'] != 'success':
            return {
                'status': 'error',
                'recommended_cards': [],
                'clusters_used': [],
                'message': '사용자 정보를 찾을 수 없습니다.'
            }
        
        # 페르소나 기반 카드 추천
        persona = {
            'interesting_topics': user_info['user'].get('interesting_topics', []),
            'preferred_category_types': user_info['user'].get('preferred_category_types', []),
            'selection_complexity': user_info['user'].get('selection_complexity', 'moderate')
        }
        
        recommendation = self.card_recommender.recommend_cards(persona, num_cards)
        
        if recommendation['status'] == 'success':
            return {
                'status': 'success',
                'recommended_cards': recommendation['cards'],
                'clusters_used': recommendation['clusters_used'],
                'message': recommendation['message']
            }
        else:
            return recommendation
    
    def interpret_cards(self, 
                       user_id: int,
                       selected_cards: List[str],
                       context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        선택된 카드들을 해석 (제시된 흐름의 3.4단계)
        
        Args:
            user_id: 사용자 ID
            selected_cards: 선택된 카드 리스트 (1-4개)
            context: 상황 정보 {
                'time': str,
                'place': str,
                'interaction_partner': str,
                'current_activity': str
            }
            
        Returns:
            Dict[str, Any]: {
                'status': str,
                'interpretations': List[str],  # 3개
                'feedback_id': int,
                'method': str,  # 'online' or 'offline'
                'message': str
            }
        """
        # 사용자 정보 조회
        user_info = self.user_manager.get_user(user_id)
        if user_info['status'] != 'success':
            return {
                'status': 'error',
                'interpretations': [],
                'feedback_id': -1,
                'method': 'none',
                'message': '사용자 정보를 찾을 수 없습니다.'
            }
        
        # 컨텍스트 기본값 설정
        if context is None:
            context = {
                'time': '현재',
                'place': '알 수 없음',
                'interaction_partner': '알 수 없음',
                'current_activity': '대화'
            }
        
        # 페르소나 정보 준비
        user_data = user_info['user']
        persona = {
            'age': user_data.get('age', ''),
            'gender': user_data.get('gender', ''),
            'disability_type': user_data.get('disability_type', ''),
            'communication_characteristics': user_data.get('communication_characteristics', ''),
            'interesting_topics': user_data.get('interesting_topics', [])
        }
        
        # 과거 해석 패턴 조회 (대화 메모리에서)
        memory_patterns = self.conversation_memory.get_card_usage_patterns(user_id, selected_cards)
        past_interpretation = ""
        if memory_patterns['patterns']:
            past_interpretation = f"과거 유사한 상황에서의 해석: {', '.join(memory_patterns['patterns'][-2:])}"
        
        # 카드 해석 수행
        interpretation_result = self.card_interpreter.interpret_cards(
            persona=persona,
            context=context,
            cards=selected_cards,
            past_interpretation=past_interpretation
        )
        
        if interpretation_result['status'] in ['success', 'warning']:
            # 피드백 추적을 위해 해석 시도 기록
            feedback_result = self.feedback_manager.record_interpretation_attempt(
                user_id=user_id,
                cards=selected_cards,
                persona=persona,
                context=context,
                interpretations=interpretation_result['interpretations'],
                method=interpretation_result['method']
            )
            
            return {
                'status': interpretation_result['status'],
                'interpretations': interpretation_result['interpretations'],
                'feedback_id': feedback_result['feedback_id'],
                'method': interpretation_result['method'],
                'message': interpretation_result['message']
            }
        else:
            return {
                'status': 'error',
                'interpretations': [],
                'feedback_id': -1,
                'method': 'none',
                'message': interpretation_result['message']
            }
    
    def submit_feedback(self,
                       feedback_id: int,
                       selected_interpretation_index: Optional[int] = None,
                       user_correction: Optional[str] = None) -> Dict[str, Any]:
        """
        사용자 피드백 제출 (제시된 흐름의 3.5, 3.6단계)
        
        Args:
            feedback_id: 피드백 ID
            selected_interpretation_index: 선택된 해석 인덱스 (0-2)
            user_correction: 사용자 수정 내용
            
        Returns:
            Dict[str, Any]: {
                'status': str,
                'message': str
            }
        """
        # 피드백 기록
        feedback_result = self.feedback_manager.record_user_feedback(
            feedback_id=feedback_id,
            selected_interpretation_index=selected_interpretation_index,
            user_correction=user_correction
        )
        
        if feedback_result['status'] != 'success':
            return feedback_result
        
        # 해석 시도 정보 조회 (ConversationSummaryMemory에 저장하기 위해)
        try:
            # feedback_id를 통해 해석 시도 정보 찾기
            interpretation_attempt = None
            for attempt in self.feedback_manager._data["interpretations"]:
                if attempt["feedback_id"] == feedback_id:
                    interpretation_attempt = attempt
                    break
            
            if interpretation_attempt:
                user_id = interpretation_attempt["user_id"]
                cards = interpretation_attempt["cards"]
                context = interpretation_attempt["context"]
                interpretations = interpretation_attempt["interpretations"]
                
                # 최종 선택된 해석 결정
                final_interpretation = None
                if user_correction:
                    final_interpretation = user_correction
                elif selected_interpretation_index is not None and 0 <= selected_interpretation_index < len(interpretations):
                    final_interpretation = interpretations[selected_interpretation_index]
                
                # ConversationSummaryMemory에 대화 기억 추가 (제시된 흐름의 3.6단계)
                if final_interpretation:
                    memory_result = self.conversation_memory.add_conversation_memory(
                        user_id=user_id,
                        cards=cards,
                        context=context,
                        interpretations=interpretations,
                        selected_interpretation=final_interpretation if not user_correction else None,
                        user_correction=user_correction
                    )
                    
                    return {
                        'status': 'success',
                        'message': f"피드백이 기록되었으며, 대화 메모리가 업데이트되었습니다. {memory_result.get('message', '')}"
                    }
            
            return {
                'status': 'success',
                'message': '피드백이 기록되었습니다.'
            }
            
        except Exception as e:
            return {
                'status': 'warning',
                'message': f'피드백은 기록되었으나 메모리 업데이트 중 오류 발생: {str(e)}'
            }
    
    def get_system_status(self) -> Dict[str, Any]:
        """
        시스템 상태 조회
        
        Returns:
            Dict[str, Any]: {
                'status': str,
                'network_status': Dict,
                'feedback_statistics': Dict,
                'total_users': int,
                'system_health': str
            }
        """
        pass
    
    def get_user_history(self, user_id: int, limit: int = 10) -> Dict[str, Any]:
        """
        사용자 이력 조회
        
        Args:
            user_id: 사용자 ID
            limit: 조회할 최대 개수
            
        Returns:
            Dict[str, Any]: {
                'status': str,
                'feedback_history': List[Dict],
                'interpretation_summary': str,
                'total_attempts': int
            }
        """
        try:
            # 피드백 이력 조회
            feedback_history = self.feedback_manager.get_user_feedback_history(user_id, limit)
            
            # 해석 요약 조회
            interpretation_summary = self.feedback_manager.get_user_interpretation_summary(user_id)
            
            # ConversationSummaryMemory에서 메모리 요약 가져오기
            memory_summary = self.conversation_memory.get_user_memory_summary(user_id)
            
            return {
                'status': 'success',
                'feedback_history': feedback_history.get('history', []),
                'interpretation_summary': interpretation_summary.get('summary', ''),
                'memory_summary': memory_summary.get('summary', ''),
                'total_attempts': feedback_history.get('total_count', 0),
                'conversation_count': memory_summary.get('conversation_count', 0)
            }
        except Exception as e:
            return {
                'status': 'error',
                'feedback_history': [],
                'interpretation_summary': '',
                'memory_summary': '',
                'total_attempts': 0,
                'conversation_count': 0,
                'message': str(e)
            }
    
    def update_user_context(self, user_id: int, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        사용자 컨텍스트 업데이트
        
        Args:
            user_id: 사용자 ID
            context: 업데이트할 컨텍스트 정보
            
        Returns:
            Dict[str, Any]: {
                'status': str,
                'message': str
            }
        """
        pass
    
    def get_cluster_information(self) -> Dict[str, Any]:
        """
        클러스터 정보 조회
        
        Returns:
            Dict[str, Any]: {
                'status': str,
                'clusters': List[Dict],
                'total_clusters': int
            }
        """
        pass
    
    def update_user_persona(self, user_id: int, persona_updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        사용자 페르소나 업데이트
        
        Args:
            user_id: 사용자 ID
            persona_updates: 업데이트할 페르소나 정보
            
        Returns:
            Dict[str, Any]: {
                'status': str,
                'message': str
            }
        """
        pass
    
    def delete_user(self, user_id: int, password: str) -> Dict[str, Any]:
        """
        사용자 삭제
        
        Args:
            user_id: 사용자 ID
            password: 비밀번호 확인
            
        Returns:
            Dict[str, Any]: {
                'status': str,
                'message': str
            }
        """
        pass