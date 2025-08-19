import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any


class ConfigManager:
    """시스템 설정 및 구성 관리"""
    
    def __init__(self, config_file_path: Optional[str] = None):
        """
        ConfigManager 초기화 (src/에서는 service_config.py만 사용)
        
        Args:
            config_file_path: 설정 파일 경로 (선택사항, 기본값: service_config.py)
        """
        if config_file_path:
            self.config_file_path = config_file_path
        else:
            self.config_file_path = 'config/service_config.py'  # src/에서는 항상 service_config만 사용
        
        self.config_type = 'service'  # 고정값
        self.config = {}

        if os.path.exists(self.config_file_path):
            result = self.load_config(self.config_file_path)
            if result['status'] == 'success':
                self.config = result['config']
            else:
                raise Exception(f"Failed to load config: {result['message']}")
        else:
            # 설정 파일이 없으면 기본값으로 초기화
            print(f"Warning: Config file {self.config_file_path} not found. Using defaults.")
            self.config = self._get_default_config('service')
    
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
        if config_path is None:
            config_path = self.config_file_path
            
        try:
            if config_path.endswith('.py'):
                # Python 파일인 경우 동적 임포트
                import importlib.util
                import sys
                
                spec = importlib.util.spec_from_file_location("config_module", config_path)
                config_module = importlib.util.module_from_spec(spec)
                sys.modules["config_module"] = config_module
                spec.loader.exec_module(config_module)
                
                # CONFIG 변수 찾기 (DATASET_CONFIG 또는 SERVICE_CONFIG)
                if self.config_type == 'dataset':
                    config = getattr(config_module, 'DATASET_CONFIG', {})
                else:
                    config = getattr(config_module, 'SERVICE_CONFIG', {})
            else:
                # JSON 파일인 경우
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            
            if config:
                status = 'success'
                message = 'Configuration loaded successfully.'
            else:
                raise Exception("Configuration file is empty or invalid.")
            
            return {
                'status': status,
                'config': config,
                'message': message
            }
        except Exception as e:
            raise Exception(f"Failed to load config from {config_path}: {str(e)}")


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
        Path(config_path).parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, 'w') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
    
        if os.path.exists(config_path):
            status = 'success'
            message = 'Configuration saved successfully.'
        else:
            raise Exception("Failed to save configuration file.")
        
        return {
            'status': status,
            'message': message
        }


    def get_setting(self, key: str, default: Any = None) -> Any:
        """
        특정 설정값 조회
        
        Args:
            key: 설정 키
            default: 기본값
            
        Returns:
            설정값 또는 기본값
        """
        return self.config.get(key, default)
    

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
        old_value = self.get_setting(key)
        self.config[key] = value
        self.save_config(self.config)

        return {
            'status': 'success',
            'old_value': old_value,
            'new_value': value,
            'message': f'Setting {key} updated successfully.'
        }
    

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
        return {
            'openai_model': self.config.get('openai_model', 'gpt-4o-2024-08-06'),
            'local_model_path': self.config.get('local_model_path', ''),
            'temperature': self.config.get('openai_temperature', 0.8),
            'max_tokens': self.config.get('interpretation_max_tokens', 400),
            'timeout': self.config.get('request_delay', 1)
        }
    
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
        # 의도: src/에서는 service 설정만 사용 (완성된 클러스터 파일들에 대한 절대 경로)
        cluster_tags_path = Path(self.config.get('cluster_tags_path', 'dataset/processed/cluster_tags.json'))
        embeddings_path = Path(self.config.get('embeddings_path', 'dataset/processed/embeddings.json'))
        clustering_results_path = Path(self.config.get('clustering_results_path', 'dataset/processed/clustering_results.json'))
        
        similarity_threshold = self.config.get('similarity_threshold', 0.7)

        return {
            'cluster_tags_path': cluster_tags_path,
            'embeddings_path': embeddings_path,
            'clustering_results_path': clustering_results_path,
            'similarity_threshold': similarity_threshold
        }
    
    
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
        return {
            'users_file_path': self.config.get('users_file_path', 'data/users.json'),
            'feedback_file_path': self.config.get('feedback_file_path', 'data/feedback.json'),
            'logs_directory': self.config.get('logs_directory', 'logs/'),
            'backup_directory': self.config.get('backup_directory', 'backup/')
        }
    

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
        error = []
        warning = []

        required_settings = [
            'openai_model',
            'openai_temperature',
            'interpretation_max_tokens',
            'similarity_threshold',
            'timeout',
        ]
        
        # 의도: service 설정에서 검증이 필요한 경로들 (output_folder 제외)
        path_settings = [
            'users_file_path',
            'feedback_file_path',
            'logs_directory',
            'backup_directory',
            'cluster_tags_path',
            'embeddings_path',
            'clustering_results_path'
        ]




        for setting in required_settings:
            if setting not in config:
                error.append(f"Missing required setting: {setting}")

        if 'openai_temperature' in config:
            temp = config['openai_temperature']
            if not isinstance(temp, (int, float)) or temp < 0.0 or temp > 1.0:
                error.append(f"Invalid value for openai_temperature: {temp}. Must be between 0.0 and 1.0.")
        
        if 'interpretation_max_tokens' in config:
            max_tokens = config['interpretation_max_tokens']
            if not isinstance(max_tokens, int) or max_tokens < 1 or max_tokens > 512:
                error.append(f"Invalid value for interpretation_max_tokens: {max_tokens}. Must be between 1 and 512.")

        if 'timeout' in config:
            timeout = config['timeout']
            if not isinstance(timeout, int) or timeout < 1 or timeout > 180:
                error.append(f"Invalid value for timeout: {timeout}. Must be between 1 and 180 seconds.")

        if 'similarity_threshold' in config:
            threshold = config['similarity_threshold']
            if not isinstance(threshold, (int, float)) or threshold < 0.0 or threshold > 1.0:
                error.append('similarity_threshold must be between 0.0 and 1.0')        

        if 'openai_model' in config:
            model = config['openai_model']
            valid_models = ['gpt-4o-2024-08-06', 'gpt-3.5-turbo', 'gpt-4']
            if not isinstance(model, str) or model not in valid_models:
                warning.append(f"Invalid OpenAI model: {model}. Valid options are {valid_models}.")
        

        for path_setting in path_settings:
            if path_setting in config:
                path = config[path_setting]
                if not isinstance(path, str):
                    error.append(f'{path_setting} must be a string')
                elif path_setting.endswith('_directory') or path_setting == 'output_folder':
                    # 디렉토리 경로 확인
                    if not os.path.exists(path):
                        warning.append(f'Directory does not exist: {path_setting} = {path}')
                else:
                    # 파일 경로 확인 (디렉토리만)
                    directory = os.path.dirname(path) or '.'
                    if not os.path.exists(directory):
                        warning.append(f'Parent directory does not exist for {path_setting}: {directory}')

        # 5. local_model_path 특별 검증
        if 'local_model_path' in config:
            local_path = config['local_model_path']
            if local_path and not os.path.exists(local_path):
                warning.append(f'Local model file does not exist: {local_path}')

        return {
            'valid': len(error) == 0,
            'errors': error,
            'warnings': warning
        }



    def reset_to_defaults(self) -> Dict[str, Any]:
        """
        설정을 기본값으로 초기화
        
        Returns:
            Dict[str, Any]: {
                'status': str,
                'message': str
            }
        """
        try:
            # 의도: src/용 service 설정 기본값 (데이터셋 생성 관련 설정 제외)
            default_config = {
                # OpenAI API 설정
                'openai_model': 'gpt-4o-2024-08-06',
                'openai_temperature': 0.8,
                'interpretation_max_tokens': 400,
                'timeout': 60,

                # 파일 경로 설정
                'users_file_path': 'data/users.json',
                'feedback_file_path': 'data/feedback.json',
                'logs_directory': 'logs/',
                'backup_directory': 'backup/',

                # 클러스터 파일 경로 (완성된 파일들)
                'cluster_tags_path': 'dataset/processed/cluster_tags.json',
                'embeddings_path': 'dataset/processed/embeddings.json',
                'clustering_results_path': 'dataset/processed/clustering_results.json',
                'similarity_threshold': 0.5,
            }

            self.config = default_config
            save_result = self.save_config(default_config)

            if save_result['status'] == 'success':
                return {
                    'status': 'success',
                    'message': 'Configuration reset to defaults successfully.'
                }
            else:
                raise Exception(f"Failed to save default config: {save_result['message']}")
            
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def _get_default_config(self, config_type: str) -> Dict[str, Any]:
        """기본 설정 반환"""
        if config_type == 'service':
            return {
                'openai_model': 'gpt-4o-2024-08-06',
                'openai_temperature': 0.8,
                'interpretation_max_tokens': 400,
                'summary_max_tokens': 200,
                'api_timeout': 15,
                'users_file_path': 'user_data/users.json',
                'feedback_file_path': 'user_data/feedback.json', 
                'memory_file_path': 'user_data/conversation_memory.json',
                'logs_directory': 'logs/',
                'backup_directory': 'backup/',
                'cluster_tags_path': 'dataset/processed/cluster_tags.json',
                'embeddings_path': 'dataset/processed/embeddings.json', 
                'clustering_results_path': 'dataset/processed/clustering_results.json',
                'network_timeout': 10,
                'max_retry_attempts': 3,
                'request_delay': 1,
                'similarity_threshold': 0.7,
                'offline_db_path': 'user_data/offline_interpretations.json'
            }
        else:  # dataset
            return {
                'images_folder': 'dataset/images',
                'output_folder': 'dataset/processed',
                'samples_per_persona': 200,
                'n_clusters': 64,
                'openai_model': 'gpt-4o-2024-08-06',
                'openai_temperature': 0.8,
                'context_max_tokens': 300,
                'interpretation_max_tokens': 400,
                'similarity_threshold': 0.5
            }
