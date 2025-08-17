import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any


class ConfigManager:
    """시스템 설정 및 구성 관리"""
    
    def __init__(self, config_file_path: Optional[str] = None):
        self.config_file_path = config_file_path or 'config/dataset_config.py'
        self.config = {}

        if os.path.exists(self.config_file_path):
            result = self.load_config(self.config_file_path)
            if result['status'] == 'success':
                self.config = result['config']
            else:
                raise Exception(f"Failed to load config: {result['message']}")
    
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
        
        self.config = self.load_config()

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
        
        self.config = self.load_config()

        return {
            'openai_model': self.config.get('openai_model', 'gpt-4o-2024-08-06'),
            'local_model_path': self.config.get('local_model_path', ''), # 로컬 모델 경로를 모름
            'temperature': self.config.get('openai_temperature', 0.8),
            'max_tokens': self.config.get('interpretation_max_tokens', 400),
            'timeout': self.config.get('timeout', 60) # 임의로 60초로 설정함
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
        self.output_folder = Path(self.config['output_folder'])
        self.output_folder.mkdir(parents=True, exist_ok=True)

        self.config = self.load_config()
        cluster_tags_path = self.output_folder / self.config.get('cluster_tags_path', 'cluster_tags.json')
        embeddings_path = self.output_folder / self.config.get('embeddings_path', 'embeddings.json')
        clustering_results_path = self.output_folder / self.config.get('clustering_results_path', 'clustering_results.json')
        similarity_threshold = self.config.get('similarity_threshold', 0.5) #이건 클러스터링 선택일텐데

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
        
        self.config = self.load_config()

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
        
        path_settings = [
            'users_file_path',
            'feedback_file_path',
            'logs_directory',
            'backup_directory',
            'output_folder',
            'cluster_tags_path',
            'embeddings_path',
            'clustering_results_path'
        ]




        for setting in required_settings:
            if setting in config:
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
            default_config = {
                'openai_model': 'gpt-4o-2024-08-06',
                'openai_temperature': 0.8,
                'interpretation_max_tokens': 400,
                'timeout': 60,

                'local_model_path': '',
                'users_file_path': 'data/users.json',
                'feedback_file_path': 'data/feedback.json',
                'logs_directory': 'logs/',
                'backup_directory': 'backup/',

                'cluster_tags_path': 'dataset/cluster_tags.json',
                'embeddings_path': 'dataset/embeddings.json',
                'clustering_results_path': 'dataset/clustering_results.json',
                'similarity_threshold': 0.5,
                'output_folder': 'dataset/processed',
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
