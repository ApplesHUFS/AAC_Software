from typing import Dict, List, Optional, Any


class ExportManager:
    """데이터 내보내기 및 백업 관리"""
    
    def __init__(self, config: Optional[Dict] = None):
        pass
    
    def export_user_data(self, user_id: int, format: str = "json") -> Dict[str, Any]:
        """
        사용자 데이터 내보내기
        
        Args:
            user_id: 사용자 ID
            format: 내보내기 형식 ('json', 'csv', 'xml')
            
        Returns:
            Dict[str, Any]: {
                'status': str,
                'file_path': str,
                'file_size': int,
                'export_timestamp': str,
                'message': str
            }
        """
        pass
    
    def export_feedback_history(self, 
                               user_id: Optional[int] = None,
                               start_date: Optional[str] = None,
                               end_date: Optional[str] = None,
                               format: str = "json") -> Dict[str, Any]:
        """
        피드백 이력 내보내기
        
        Args:
            user_id: 특정 사용자 ID (None이면 전체)
            start_date: 시작 날짜
            end_date: 종료 날짜
            format: 내보내기 형식
            
        Returns:
            Dict[str, Any]: {
                'status': str,
                'file_path': str,
                'record_count': int,
                'export_timestamp': str,
                'message': str
            }
        """
        pass
    
    def export_interpretation_logs(self, 
                                  start_date: Optional[str] = None,
                                  end_date: Optional[str] = None,
                                  format: str = "json") -> Dict[str, Any]:
        """
        해석 로그 내보내기
        
        Args:
            start_date: 시작 날짜
            end_date: 종료 날짜
            format: 내보내기 형식
            
        Returns:
            Dict[str, Any]: {
                'status': str,
                'file_path': str,
                'log_count': int,
                'export_timestamp': str,
                'message': str
            }
        """
        pass
    
    def export_system_statistics(self, time_range: str = "30d", format: str = "json") -> Dict[str, Any]:
        """
        시스템 통계 내보내기
        
        Args:
            time_range: 시간 범위 ('1d', '7d', '30d', '1y')
            format: 내보내기 형식
            
        Returns:
            Dict[str, Any]: {
                'status': str,
                'file_path': str,
                'statistics': Dict,
                'export_timestamp': str,
                'message': str
            }
        """
        pass
    
    def create_backup(self, backup_type: str = "full") -> Dict[str, Any]:
        """
        시스템 백업 생성
        
        Args:
            backup_type: 백업 유형 ('full', 'incremental', 'users_only', 'feedback_only')
            
        Returns:
            Dict[str, Any]: {
                'status': str,
                'backup_id': str,
                'backup_path': str,
                'backup_size': int,
                'backup_timestamp': str,
                'included_data': List[str],
                'message': str
            }
        """
        pass
    
    def restore_backup(self, backup_id: str, restore_options: Dict[str, Any]) -> Dict[str, Any]:
        """
        백업에서 복원
        
        Args:
            backup_id: 백업 ID
            restore_options: 복원 옵션 {
                'restore_users': bool,
                'restore_feedback': bool,
                'restore_logs': bool,
                'overwrite_existing': bool
            }
            
        Returns:
            Dict[str, Any]: {
                'status': str,
                'restored_items': List[str],
                'skipped_items': List[str],
                'restore_timestamp': str,
                'message': str
            }
        """
        pass
    
    def list_backups(self) -> Dict[str, Any]:
        """
        백업 목록 조회
        
        Returns:
            Dict[str, Any]: {
                'status': str,
                'backups': List[Dict],  # {id, timestamp, size, type, status}
                'total_count': int,
                'total_size': int
            }
        """
        pass
    
    def delete_backup(self, backup_id: str) -> Dict[str, Any]:
        """
        백업 삭제
        
        Args:
            backup_id: 백업 ID
            
        Returns:
            Dict[str, Any]: {
                'status': str,
                'deleted_size': int,
                'message': str
            }
        """
        pass
    
    def schedule_automatic_backup(self, schedule: Dict[str, Any]) -> Dict[str, Any]:
        """
        자동 백업 스케줄 설정
        
        Args:
            schedule: 스케줄 설정 {
                'frequency': str,  # 'daily', 'weekly', 'monthly'
                'time': str,       # 'HH:MM'
                'backup_type': str,
                'retention_days': int
            }
            
        Returns:
            Dict[str, Any]: {
                'status': str,
                'schedule_id': str,
                'next_backup': str,
                'message': str
            }
        """
        pass
    
    def import_data(self, file_path: str, data_type: str, import_options: Dict[str, Any]) -> Dict[str, Any]:
        """
        데이터 가져오기
        
        Args:
            file_path: 가져올 파일 경로
            data_type: 데이터 유형 ('users', 'feedback', 'logs')
            import_options: 가져오기 옵션 {
                'merge_strategy': str,  # 'overwrite', 'merge', 'skip_existing'
                'validate_data': bool,
                'backup_before_import': bool
            }
            
        Returns:
            Dict[str, Any]: {
                'status': str,
                'imported_count': int,
                'skipped_count': int,
                'error_count': int,
                'import_timestamp': str,
                'errors': List[str],
                'message': str
            }
        """
        pass