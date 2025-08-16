from typing import Dict, List, Optional, Any


class ConfigManager:
    """시스템 설정 및 구성 관리"""
    
    def __init__(self, config_file_path: Optional[str] = None):
        pass
    
    def load_config(self, config_path: Optional[str] = None) -> Dict[str, Any]:
        """
        설정 파일 로드
        
        Args:
            config_path: 설정 파일 경로
            
        Returns:
            Dict[str, Any]: {
                'status': str,
                'config': Dict,
                'message': str
            }
        """
        pass
    
    def save_config(self, config: Dict[str, Any], config_path: Optional[str] = None) -> Dict[str, Any]:
        """
        설정 파일 저장
        
        Args:
            config: 저장할 설정
            config_path: 저장 경로
            
        Returns:
            Dict[str, Any]: {
                'status': str,
                'message': str
            }
        """
        pass
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """
        특정 설정값 조회
        
        Args:
            key: 설정 키
            default: 기본값
            
        Returns:
            설정값 또는 기본값
        """
        pass
    
    def update_setting(self, key: str, value: Any) -> Dict[str, Any]:
        """
        특정 설정값 업데이트
        
        Args:
            key: 설정 키
            value: 새 값
            
        Returns:
            Dict[str, Any]: {
                'status': str,
                'old_value': Any,
                'new_value': Any,
                'message': str
            }
        """
        pass
    
    def get_model_config(self) -> Dict[str, Any]:
        """
        모델 관련 설정 조회
        
        Returns:
            Dict[str, Any]: {
                'openai_model': str,
                'local_model_path': str,
                'temperature': float,
                'max_tokens': int,
                'timeout': int
            }
        """
        pass
    
    def get_cluster_config(self) -> Dict[str, Any]:
        """
        클러스터링 관련 설정 조회
        
        Returns:
            Dict[str, Any]: {
                'cluster_tags_path': str,
                'embeddings_path': str,
                'clustering_results_path': str,
                'similarity_threshold': float
            }
        """
        pass
    
    def get_data_paths(self) -> Dict[str, Any]:
        """
        데이터 파일 경로 설정 조회
        
        Returns:
            Dict[str, Any]: {
                'users_file_path': str,
                'feedback_file_path': str,
                'logs_directory': str,
                'backup_directory': str
            }
        """
        pass
    
    def validate_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        설정 유효성 검사
        
        Args:
            config: 검사할 설정
            
        Returns:
            Dict[str, Any]: {
                'valid': bool,
                'errors': List[str],
                'warnings': List[str]
            }
        """
        pass
    
    def reset_to_defaults(self) -> Dict[str, Any]:
        """
        설정을 기본값으로 초기화
        
        Returns:
            Dict[str, Any]: {
                'status': str,
                'message': str
            }
        """
        pass