from typing import Dict, List, Optional, Any


class LoggingManager:
    """시스템 로깅 및 모니터링"""
    
    def __init__(self, log_file_path: Optional[str] = None, log_level: str = "INFO"):
        pass
    
    def log_user_action(self, user_id: int, action: str, details: Dict[str, Any]) -> Dict[str, Any]:
        """
        사용자 행동 로그
        
        Args:
            user_id: 사용자 ID
            action: 행동 유형
            details: 상세 정보
            
        Returns:
            Dict[str, Any]: {
                'status': str,
                'log_id': str,
                'timestamp': str
            }
        """
        pass
    
    def log_interpretation_request(self, user_id: int, cards: List[str], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        해석 요청 로그
        
        Args:
            user_id: 사용자 ID
            cards: 요청된 카드들
            context: 컨텍스트 정보
            
        Returns:
            Dict[str, Any]: {
                'status': str,
                'request_id': str,
                'timestamp': str
            }
        """
        pass
    
    def log_interpretation_result(self, request_id: str, interpretations: List[str], method: str) -> Dict[str, Any]:
        """
        해석 결과 로그
        
        Args:
            request_id: 요청 ID
            interpretations: 해석 결과들
            method: 해석 방법
            
        Returns:
            Dict[str, Any]: {
                'status': str,
                'result_id': str,
                'timestamp': str
            }
        """
        pass
    
    def log_system_event(self, event_type: str, details: Dict[str, Any], severity: str = "INFO") -> Dict[str, Any]:
        """
        시스템 이벤트 로그
        
        Args:
            event_type: 이벤트 유형
            details: 이벤트 상세
            severity: 심각도 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            
        Returns:
            Dict[str, Any]: {
                'status': str,
                'event_id': str,
                'timestamp': str
            }
        """
        pass
    
    def log_error(self, error_type: str, error_message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        오류 로그
        
        Args:
            error_type: 오류 유형
            error_message: 오류 메시지
            context: 오류 컨텍스트
            
        Returns:
            Dict[str, Any]: {
                'status': str,
                'error_id': str,
                'timestamp': str
            }
        """
        pass
    
    def get_logs(self, 
                start_time: Optional[str] = None,
                end_time: Optional[str] = None,
                log_level: Optional[str] = None,
                user_id: Optional[int] = None,
                limit: int = 100) -> Dict[str, Any]:
        """
        로그 조회
        
        Args:
            start_time: 시작 시간
            end_time: 종료 시간
            log_level: 로그 레벨 필터
            user_id: 사용자 ID 필터
            limit: 조회 제한
            
        Returns:
            Dict[str, Any]: {
                'status': str,
                'logs': List[Dict],
                'total_count': int,
                'filtered_count': int
            }
        """
        pass
    
    def get_error_summary(self, time_range: str = "24h") -> Dict[str, Any]:
        """
        오류 요약 조회
        
        Args:
            time_range: 시간 범위 (1h, 24h, 7d, 30d)
            
        Returns:
            Dict[str, Any]: {
                'status': str,
                'error_count': int,
                'error_types': Dict[str, int],
                'critical_errors': List[Dict],
                'trend': str
            }
        """
        pass
    
    def get_usage_statistics(self, time_range: str = "24h") -> Dict[str, Any]:
        """
        사용량 통계 조회
        
        Args:
            time_range: 시간 범위
            
        Returns:
            Dict[str, Any]: {
                'status': str,
                'total_requests': int,
                'unique_users': int,
                'avg_response_time': float,
                'success_rate': float,
                'popular_cards': List[str]
            }
        """
        pass
    
    def archive_old_logs(self, days_to_keep: int = 30) -> Dict[str, Any]:
        """
        오래된 로그 아카이브
        
        Args:
            days_to_keep: 보관할 일수
            
        Returns:
            Dict[str, Any]: {
                'status': str,
                'archived_count': int,
                'archive_path': str,
                'message': str
            }
        """
        pass