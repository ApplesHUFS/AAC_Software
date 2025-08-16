from typing import Dict, List, Optional, Any


class FeedbackManager:
    """사용자 피드백 및 해석 이력 관리"""
    
    def __init__(self, feedback_file_path: Optional[str] = None):
        pass
    
    def record_interpretation_attempt(self,
                                   user_id: int,
                                   cards: List[str],
                                   persona: Dict[str, Any],
                                   context: Dict[str, Any],
                                   interpretations: List[str],
                                   method: str = "online") -> Dict[str, Any]:
        """
        해석 시도 기록
        
        Args:
            user_id: 사용자 ID
            cards: 사용된 카드 리스트
            persona: 사용자 페르소나
            context: 상황 정보
            interpretations: 생성된 해석들 (3개)
            method: 해석 방법 ('online' or 'offline')
            
        Returns:
            Dict[str, Any]: {
                'status': str,
                'feedback_id': int,
                'message': str
            }
        """
        pass
    
    def record_user_feedback(self,
                           feedback_id: int,
                           selected_interpretation_index: Optional[int] = None,
                           user_correction: Optional[str] = None) -> Dict[str, Any]:
        """
        사용자 피드백 기록
        
        Args:
            feedback_id: 피드백 ID
            selected_interpretation_index: 선택된 해석의 인덱스 (0-2)
            user_correction: 사용자가 직접 입력한 올바른 해석
            
        Returns:
            Dict[str, Any]: {
                'status': str,
                'message': str
            }
        """
        pass
    
    def get_user_interpretation_summary(self, user_id: int) -> Dict[str, Any]:
        """
        사용자의 과거 해석 이력을 요약하여 반환
        
        Args:
            user_id: 사용자 ID
            
        Returns:
            Dict[str, Any]: {
                'status': str,
                'summary': str,
                'pattern_count': int
            }
        """
        pass
    
    def get_card_interpretation_patterns(self, cards: List[str]) -> Dict[str, Any]:
        """
        특정 카드 조합의 과거 해석 패턴 조회
        
        Args:
            cards: 카드 리스트
            
        Returns:
            Dict[str, Any]: {
                'status': str,
                'patterns': List[Dict],
                'relevance_scores': List[float]
            }
        """
        pass
    
    def get_feedback_statistics(self) -> Dict[str, Any]:
        """
        피드백 통계 정보 조회
        
        Returns:
            Dict[str, Any]: {
                'total_attempts': int,
                'completed_feedback': int,
                'completion_rate': float,
                'average_accuracy': float,
                'correction_rate': float
            }
        """
        pass
    
    def get_user_feedback_history(self, user_id: int, limit: int = 20) -> Dict[str, Any]:
        """
        특정 사용자의 피드백 이력 조회
        
        Args:
            user_id: 사용자 ID
            limit: 조회할 최대 개수
            
        Returns:
            Dict[str, Any]: {
                'status': str,
                'history': List[Dict],
                'total_count': int
            }
        """
        pass
    
    def delete_user_feedback(self, user_id: int) -> Dict[str, Any]:
        """
        특정 사용자의 모든 피드백 삭제
        
        Args:
            user_id: 사용자 ID
            
        Returns:
            Dict[str, Any]: {
                'status': str,
                'deleted_count': int,
                'message': str
            }
        """
        pass