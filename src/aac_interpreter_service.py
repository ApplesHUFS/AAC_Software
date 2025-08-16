from typing import Dict, List, Optional, Any

from .user_manager import UserManager
from .card_recommender import CardRecommender
from .card_interpreter import CardInterpreter
from .feedback_manager import FeedbackManager
from .network_utils import NetworkUtils


class AACInterpreterService:
    """AAC 카드 해석 시스템의 메인 컨트롤러"""
    
    def __init__(self, config: Optional[Dict] = None):
        pass
    
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
        pass
    
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
        pass
    
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
        pass
    
    def recommend_cards(self, user_id: int, num_cards: int = 4) -> Dict[str, Any]:
        """
        사용자에게 카드 추천
        
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
        pass
    
    def interpret_cards(self, 
                       user_id: int,
                       selected_cards: List[str],
                       context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        선택된 카드들을 해석
        
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
        pass
    
    def submit_feedback(self,
                       feedback_id: int,
                       selected_interpretation_index: Optional[int] = None,
                       user_correction: Optional[str] = None) -> Dict[str, Any]:
        """
        사용자 피드백 제출
        
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
        pass
    
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
        pass
    
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