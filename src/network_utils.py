from typing import Dict, Optional, Any


class NetworkUtils:
    """네트워크 연결 상태 확인 및 관련 유틸리티"""
    
    def __init__(self, config: Optional[Dict] = None):
        pass
    
    def check_internet_connection(self, timeout: Optional[int] = None) -> Dict[str, Any]:
        """
        인터넷 연결 상태 확인
        
        Args:
            timeout: 연결 시도 시간 제한 (초)
            
        Returns:
            Dict[str, Any]: {
                'status': str,
                'connected': bool,
                'response_time': float,
                'message': str
            }
        """
        pass
    
    def check_openai_api_connectivity(self, timeout: Optional[int] = None) -> Dict[str, Any]:
        """
        OpenAI API 연결 상태 확인
        
        Args:
            timeout: 연결 시도 시간 제한 (초)
            
        Returns:
            Dict[str, Any]: {
                'status': str,
                'response_code': int or None,
                'response_time': float,
                'message': str
            }
        """
        pass
    
    def get_network_status(self) -> Dict[str, Any]:
        """
        종합적인 네트워크 상태 정보 반환
        
        Returns:
            Dict[str, Any]: {
                'timestamp': float,
                'internet_connected': bool,
                'openai_api_status': Dict,
                'recommended_mode': str  # 'online' or 'offline'
            }
        """
        pass
    
    def is_online_mode_available(self) -> Dict[str, Any]:
        """
        온라인 모드 사용 가능 여부 확인
        
        Returns:
            Dict[str, Any]: {
                'available': bool,
                'reason': str,
                'quality': str  # 'excellent', 'good', 'fair', 'poor'
            }
        """
        pass
    
    def wait_for_connection(self, max_wait_time: int = 30, check_interval: int = 2) -> Dict[str, Any]:
        """
        네트워크 연결이 복구될 때까지 대기
        
        Args:
            max_wait_time: 최대 대기 시간 (초)
            check_interval: 연결 확인 간격 (초)
            
        Returns:
            Dict[str, Any]: {
                'connected': bool,
                'wait_time': float,
                'attempts': int
            }
        """
        pass
    
    def get_connection_quality(self) -> Dict[str, Any]:
        """
        연결 품질 측정
        
        Returns:
            Dict[str, Any]: {
                'quality': str,  # 'excellent', 'good', 'fair', 'poor', 'disconnected'
                'average_response_time': float or None,
                'successful_requests': int,
                'total_requests': int,
                'success_rate': float
            }
        """
        pass