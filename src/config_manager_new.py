import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any


class ConfigManager:
    """시스템 설정 관리.
    
    AAC 시스템의 설정을 중앙에서 관리합니다.
    OpenAI API, 파일 경로, 모델 설정 등을 로드하여 제공합니다.
    
    Attributes:
        config_file_path: 설정 파일 경로
        config: 로드된 설정 딕셔너리
    """
    
    def __init__(self, config_file_path: Optional[str] = None):
        """ConfigManager 초기화.
        
        Args:
            config_file_path: 설정 파일 경로. None이면 기본값 사용.
        """
        if config_file_path:
            self.config_file_path = config_file_path
        else:
            self.config_file_path = 'config/service_config.py'
        self.config = {}

        if os.path.exists(self.config_file_path):
            result = self.load_config(self.config_file_path)
            if result['status'] == 'success':
                self.config = result['config']
            else:
                raise Exception(f"Failed to load config: {result['message']}")
        else:
            print(f"Warning: Config file {self.config_file_path} not found. Using defaults.")
            self.config = self._get_default_service_config()
    
    def load_config(self, config_path: Optional[str] = None) -> Dict[str, Any]:
        """설정 파일 로드.
        
        Args:
            config_path: 설정 파일 경로. None이면 인스턴스 기본값 사용.
            
        Returns:
            Dict containing:
                - status (str): 'success' 또는 'error'
                - config (Dict): 로드된 설정
                - message (str): 결과 메시지
        """
        if config_path is None:
            config_path = self.config_file_path
            
        try:
            # Python 모듈 형태의 설정 파일 로드
            import importlib.util
            spec = importlib.util.spec_from_file_location("config", config_path)
            config_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(config_module)
            
            # SERVICE_CONFIG 변수 추출
            if hasattr(config_module, 'SERVICE_CONFIG'):
                config = config_module.SERVICE_CONFIG
            else:
                raise Exception("SERVICE_CONFIG not found in config file")
            
            return {
                'status': 'success',
                'config': config,
                'message': 'Configuration loaded successfully'
            }
        except Exception as e:
            raise Exception(f"Failed to load config from {config_path}: {str(e)}")

    def get_setting(self, key: str, default: Any = None) -> Any:
        """특정 설정값 조회.
        
        Args:
            key: 설정 키
            default: 키가 없을 때 반환할 기본값
            
        Returns:
            설정값 또는 기본값
        """
        return self.config.get(key, default)

    def get_model_config(self) -> Dict[str, Any]:
        """AI 모델 관련 설정 조회.
        
        Returns:
            Dict containing OpenAI 모델 설정
        """
        return {
            'openai_model': self.get_setting('openai_model', 'gpt-4o-2024-08-06'),
            'temperature': self.get_setting('openai_temperature', 0.8),
            'max_tokens': self.get_setting('interpretation_max_tokens', 400),
            'timeout': self.get_setting('api_timeout', 15)
        }

    def get_cluster_config(self) -> Dict[str, Any]:
        """클러스터 관련 설정 조회.
        
        Returns:
            Dict containing 클러스터 파일 경로들
        """
        return {
            'cluster_tags_path': self.get_setting('cluster_tags_path', 'dataset/processed/cluster_tags.json'),
            'embeddings_path': self.get_setting('embeddings_path', 'dataset/processed/embeddings.json'),
            'clustering_results_path': self.get_setting('clustering_results_path', 'dataset/processed/clustering_results.json')
        }

    def get_data_paths(self) -> Dict[str, Any]:
        """데이터 파일 경로 설정 조회.
        
        Returns:
            Dict containing 데이터 파일 경로들
        """
        return {
            'users_file_path': self.get_setting('users_file_path', 'user_data/users.json'),
            'feedback_file_path': self.get_setting('feedback_file_path', 'user_data/feedback.json'),
            'memory_file_path': self.get_setting('memory_file_path', 'user_data/conversation_memory.json')
        }

    def validate_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """설정 유효성 검증.
        
        Args:
            config: 검증할 설정 딕셔너리
            
        Returns:
            Dict containing:
                - valid (bool): 유효성 여부
                - errors (List[str]): 오류 목록
        """
        errors = []
        
        # 필수 설정 키들 검증
        required_keys = [
            'openai_model', 'users_file_path', 'feedback_file_path',
            'memory_file_path', 'cluster_tags_path', 'embeddings_path'
        ]
        
        for key in required_keys:
            if key not in config:
                errors.append(f"Required setting '{key}' is missing")
        
        # OpenAI 모델명 검증
        if 'openai_model' in config:
            model = config['openai_model']
            if not isinstance(model, str) or not model.startswith('gpt'):
                errors.append("Invalid OpenAI model name")
        
        # 파일 경로 검증
        path_keys = ['users_file_path', 'feedback_file_path', 'memory_file_path']
        for key in path_keys:
            if key in config:
                path = config[key]
                if not isinstance(path, str):
                    errors.append(f"Invalid path for '{key}': must be string")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }

    def _get_default_service_config(self) -> Dict[str, Any]:
        """기본 서비스 설정 반환.
        
        Returns:
            Dict containing 기본 설정값들
        """
        return {
            # OpenAI API 설정
            'openai_model': 'gpt-4o-2024-08-06',
            'openai_temperature': 0.8,
            'interpretation_max_tokens': 400,
            'summary_max_tokens': 200,
            'api_timeout': 15,
            
            # 데이터 파일 경로
            'users_file_path': 'user_data/users.json',
            'feedback_file_path': 'user_data/feedback.json', 
            'memory_file_path': 'user_data/conversation_memory.json',
            
            # 클러스터 파일 경로
            'cluster_tags_path': 'dataset/processed/cluster_tags.json',
            'embeddings_path': 'dataset/processed/embeddings.json', 
            'clustering_results_path': 'dataset/processed/clustering_results.json',
            
            # 네트워크 및 성능 설정
            'network_timeout': 10,
            'max_retry_attempts': 3,
            'request_delay': 1,
            
            # 시스템 설정
            'max_conversation_history': 50,
            'similarity_threshold': 0.7,
        }
