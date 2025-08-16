from typing import Dict, List, Optional, Any


class UserManager:
    """사용자 관리를 담당하는 추상화된 클래스"""
    
    def __init__(self, users_file_path: Optional[str] = None):
        pass
    
    def create_user(self, persona: Dict[str, Any]) -> Dict[str, Any]:
        """
        새 사용자 생성
        
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
    
    def get_user(self, user_id: int) -> Dict[str, Any]:
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
    
    def update_user_persona(self, user_id: int, persona: Dict[str, Any]) -> Dict[str, Any]:
        """
        사용자 페르소나 정보 업데이트
        
        Args:
            user_id: 사용자 ID
            persona: 업데이트할 페르소나 정보
            
        Returns:
            Dict[str, Any]: {
                'status': str,
                'message': str
            }
        """
        pass
    
    def get_all_users(self) -> Dict[str, Any]:
        """
        모든 사용자 조회
        
        Returns:
            Dict[str, Any]: {
                'status': str,
                'users': List[Dict],
                'count': int
            }
        """
        pass
    
    def delete_user(self, user_id: int) -> Dict[str, Any]:
        """
        사용자 삭제
        
        Args:
            user_id: 사용자 ID
            
        Returns:
            Dict[str, Any]: {
                'status': str,
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
                'message': str
            }
        """
        pass
    
    def update_user_password(self, user_id: int, old_password: str, new_password: str) -> Dict[str, Any]:
        """
        사용자 비밀번호 변경
        
        Args:
            user_id: 사용자 ID
            old_password: 기존 비밀번호
            new_password: 새 비밀번호
            
        Returns:
            Dict[str, Any]: {
                'status': str,
                'message': str
            }
        """
        pass