import os
from typing import Dict, Any

# 기본 서버 설정
SERVER_HOST = '127.0.0.1'
SERVER_PORT = 8000
DEBUG_MODE = True

# 사용자 데이터 관리 설정
USER_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'user_data')
USERS_FILE = os.path.join(USER_DATA_DIR, 'users.json')
SESSIONS_FILE = os.path.join(USER_DATA_DIR, 'sessions.json')
SECURITY_LOG_FILE = os.path.join(USER_DATA_DIR, 'security_events.json')
ENCRYPTION_KEYS_FILE = os.path.join(USER_DATA_DIR, 'encryption_keys.json')

# 보안 설정
SECURITY_CONFIG = {
    'session_duration': 3600,  # 1시간
    'max_login_attempts': 5,
    'rate_limit_window': 300,  # 5분
    'rate_limit_max_requests': 100,
    'user_data_dir': USER_DATA_DIR,
    'security_log_path': SECURITY_LOG_FILE
}

# 네트워크 설정
NETWORK_CONFIG = {
    'timeout': 10,
    'test_urls': ['https://www.google.com', 'https://www.cloudflare.com'],
    'openai_api_url': 'https://api.openai.com/v1/models'
}

# 데이터셋 설정
DATASET_CONFIG = {
    'dataset_dir': os.path.join(os.path.dirname(os.path.dirname(__file__)), 'dataset'),
    'images_dir': os.path.join(os.path.dirname(os.path.dirname(__file__)), 'dataset', 'images'),
    'filtered_images_dir': os.path.join(os.path.dirname(os.path.dirname(__file__)), 'dataset', 'filtered_images'),
    'processed_dir': os.path.join(os.path.dirname(os.path.dirname(__file__)), 'dataset', 'processed'),
    'persona_file': os.path.join(os.path.dirname(os.path.dirname(__file__)), 'dataset', 'persona.json')
}

# 로깅 설정
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file_path': os.path.join(USER_DATA_DIR, 'app.log')
}

# 전체 설정을 하나의 딕셔너리로 통합
CONFIG = {
    'server': {
        'host': SERVER_HOST,
        'port': SERVER_PORT,
        'debug': DEBUG_MODE
    },
    'security': SECURITY_CONFIG,
    'network': NETWORK_CONFIG,
    'dataset': DATASET_CONFIG,
    'logging': LOGGING_CONFIG,
    'paths': {
        'user_data_dir': USER_DATA_DIR,
        'users_file': USERS_FILE,
        'sessions_file': SESSIONS_FILE,
        'security_log_file': SECURITY_LOG_FILE,
        'encryption_keys_file': ENCRYPTION_KEYS_FILE
    }
}

def get_config() -> Dict[str, Any]:
    """
    전체 설정 반환
    
    Returns:
        Dict[str, Any]: 전체 설정 딕셔너리
    """
    return CONFIG

def get_security_config() -> Dict[str, Any]:
    """
    보안 설정 반환
    
    Returns:
        Dict[str, Any]: 보안 설정
    """
    return SECURITY_CONFIG

def get_network_config() -> Dict[str, Any]:
    """
    네트워크 설정 반환
    
    Returns:
        Dict[str, Any]: 네트워크 설정
    """
    return NETWORK_CONFIG

def get_dataset_config() -> Dict[str, Any]:
    """
    데이터셋 설정 반환
    
    Returns:
        Dict[str, Any]: 데이터셋 설정
    """
    return DATASET_CONFIG

def get_logging_config() -> Dict[str, Any]:
    """
    로깅 설정 반환
    
    Returns:
        Dict[str, Any]: 로깅 설정
    """
    return LOGGING_CONFIG
