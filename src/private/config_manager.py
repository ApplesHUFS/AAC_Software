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
        self._load_config()
    
    def _load_config(self):
        """설정 파일 로드."""
        if os.path.exists(self.config_file_path):
            result = self._load_from_file(self.config_file_path)
            if result['status'] == 'success':
                self.config = result['config']
            else:
                raise Exception(f"설정 로드 실패: {result['message']}")
        else:
            print(f"Warning: 설정 파일 {self.config_file_path}을 찾을 수 없습니다. 기본값을 사용합니다.")
            self.config = self._get_default_config()
    
    def _load_from_file(self, config_path: str) -> Dict[str, Any]:
        """설정 파일에서 로드.
        
        Args:
            config_path: 설정 파일 경로
            
        Returns:
            Dict containing:
                - status (str): 'success' 또는 'error'
                - config (Dict): 로드된 설정
                - message (str): 결과 메시지
        """
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
                raise Exception("SERVICE_CONFIG를 찾을 수 없습니다.")
            
            return {
                'status': 'success',
                'config': config,
                'message': '설정 로드 완료'
            }
        except Exception as e:
            return {
                'status': 'error',
                'config': {},
                'message': f"설정 로드 실패: {str(e)}"
            }

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
            'openai_temperature': self.get_setting('openai_temperature', 0.8),
            'interpretation_max_tokens': self.get_setting('interpretation_max_tokens', 400),
            'summary_max_tokens': self.get_setting('summary_max_tokens', 200),
            'api_timeout': self.get_setting('api_timeout', 15),
            'images_folder': self.get_setting('images_folder', 'dataset/images')
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

    def _get_default_config(self) -> Dict[str, Any]:
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
            
            # 이미지 폴더 경로
            'images_folder': 'dataset/images',
            
            # 데이터 파일 경로
            'users_file_path': 'user_data/users.json',
            'feedback_file_path': 'user_data/feedback.json', 
            'memory_file_path': 'user_data/conversation_memory.json',
            
            # 클러스터 파일 경로 (전처리된 데이터)
            'cluster_tags_path': 'dataset/processed/cluster_tags.json',
            'embeddings_path': 'dataset/processed/embeddings.json', 
            'clustering_results_path': 'dataset/processed/clustering_results.json',
            
            # 카드 추천 설정
            'display_cards_total': 20,
            'recommendation_ratio': 0.7,
            'cluster_count': 6,
            
            # 카드 선택 설정
            'min_card_selection': 1,
            'max_card_selection': 4,
            
            # 해석 설정
            'interpretation_count': 3,
            
            # 시스템 설정
            'max_conversation_history': 50,
            'memory_pattern_limit': 5,
            
            # 사용자 페르소나 검증
            'valid_genders': ['male', 'female'],
            'valid_disability_types': ['의사소통 장애', '자폐스펙트럼 장애', '지적 장애'],
            'min_age': 1,
            'max_age': 100,
            'required_cluster_count': 6,
        }