from typing import Dict, Optional, Any
import requests
import time
import socket


class NetworkUtils:
    """네트워크 연결 상태 확인 및 관련 유틸리티"""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config if config else {}
        self.default_timeout = self.config.get('timeout', 10)
        self.test_urls = self.config.get('test_urls', ['https://www.google.com', 'https://www.cloudflare.com'])
        self.openai_api_url = self.config.get('openai_api_url', 'https://api.openai.com/v1/models')
        self.response_times = []
        self.success_count = 0
        self.total_requests = 0
    
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
        timeout = timeout or self.default_timeout
        start_time = time.time()
        
        try:
            response = requests.get(self.test_urls[0], timeout=timeout)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                self.total_requests += 1
                self.success_count += 1
                self.response_times.append(response_time)
                return {
                    'status': 'success',
                    'connected': True,
                    'response_time': response_time,
                    'message': '인터넷 연결이 정상입니다.'
                }
            else:
                self.total_requests += 1
                return {
                    'status': 'error',
                    'connected': False,
                    'response_time': response_time,
                    'message': f'연결 실패: HTTP {response.status_code}'
                }
        except requests.RequestException as e:
            self.total_requests += 1
            response_time = time.time() - start_time
            return {
                'status': 'error',
                'connected': False,
                'response_time': response_time,
                'message': f'연결 오류: {str(e)}'
            }
    
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
        timeout = timeout or self.default_timeout
        start_time = time.time()
        
        try:
            response = requests.get(self.openai_api_url, timeout=timeout)
            response_time = time.time() - start_time
            
            if response.status_code in [200, 401]:  # 200: OK, 401: API key required but service is available
                return {
                    'status': 'success',
                    'response_code': response.status_code,
                    'response_time': response_time,
                    'message': 'OpenAI API 서비스에 접근 가능합니다.'
                }
            else:
                return {
                    'status': 'error',
                    'response_code': response.status_code,
                    'response_time': response_time,
                    'message': f'OpenAI API 접근 실패: HTTP {response.status_code}'
                }
        except requests.RequestException as e:
            response_time = time.time() - start_time
            return {
                'status': 'error',
                'response_code': None,
                'response_time': response_time,
                'message': f'OpenAI API 연결 오류: {str(e)}'
            }
    
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
        timestamp = time.time()
        internet_check = self.check_internet_connection()
        openai_api_status = self.check_openai_api_connectivity()
        
        internet_connected = internet_check['connected']
        openai_available = openai_api_status['status'] == 'success'
        
        if internet_connected and openai_available:
            recommended_mode = 'online'
        else:
            recommended_mode = 'offline'
        
        return {
            'timestamp': timestamp,
            'internet_connected': internet_connected,
            'openai_api_status': openai_api_status,
            'recommended_mode': recommended_mode
        }
    
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
        network_status = self.get_network_status()
        internet_connected = network_status['internet_connected']
        openai_api_status = network_status['openai_api_status']
        
        if not internet_connected:
            return {
                'available': False,
                'reason': '인터넷 연결이 없습니다.',
                'quality': 'poor'
            }
        
        if openai_api_status['status'] != 'success':
            return {
                'available': False,
                'reason': 'OpenAI API에 접근할 수 없습니다.',
                'quality': 'poor'
            }
        
        # 연결 품질 평가
        quality_info = self.get_connection_quality()
        quality = quality_info['quality']
        
        if quality in ['excellent', 'good']:
            return {
                'available': True,
                'reason': '온라인 모드를 사용할 수 있습니다.',
                'quality': quality
            }
        elif quality == 'fair':
            return {
                'available': True,
                'reason': '온라인 모드를 사용할 수 있지만 연결이 불안정할 수 있습니다.',
                'quality': quality
            }
        else:
            return {
                'available': False,
                'reason': '연결 품질이 좋지 않습니다.',
                'quality': quality
            }
    
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
        start_time = time.time()
        attempts = 0
        
        while time.time() - start_time < max_wait_time:
            attempts += 1
            connection_check = self.check_internet_connection()
            
            if connection_check['connected']:
                wait_time = time.time() - start_time
                return {
                    'connected': True,
                    'wait_time': wait_time,
                    'attempts': attempts
                }
            
            time.sleep(check_interval)
        
        wait_time = time.time() - start_time
        return {
            'connected': False,
            'wait_time': wait_time,
            'attempts': attempts
        }
    
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
        if self.total_requests == 0:
            # 초기 연결 테스트 수행
            self.check_internet_connection()
        
        if self.total_requests == 0:
            return {
                'quality': 'disconnected',
                'average_response_time': None,
                'successful_requests': 0,
                'total_requests': 0,
                'success_rate': 0.0
            }
        
        success_rate = self.success_count / self.total_requests
        average_response_time = sum(self.response_times) / len(self.response_times) if self.response_times else None
        
        if success_rate == 0:
            quality = 'disconnected'
        elif success_rate < 0.5:
            quality = 'poor'
        elif success_rate < 0.8:
            quality = 'fair'
        elif average_response_time and average_response_time < 1.0:
            quality = 'excellent'
        else:
            quality = 'good'
        
        return {
            'quality': quality,
            'average_response_time': average_response_time,
            'successful_requests': self.success_count,
            'total_requests': self.total_requests,
            'success_rate': success_rate
        }