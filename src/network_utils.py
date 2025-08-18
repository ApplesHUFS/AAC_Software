import socket
import requests
from typing import Dict, Any, Optional


class NetworkUtils:
    """네트워크 상태 및 온라인 모드 확인을 위한 유틸리티 클래스"""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.timeout = self.config.get('network_timeout', 5)
        self.test_urls = self.config.get('test_urls', [
            'https://api.openai.com',
            'https://www.google.com',
            'https://httpbin.org/status/200'
        ])
    
    def is_online_mode_available(self) -> Dict[str, Any]:
        """
        온라인 모드 사용 가능 여부 확인
        
        Returns:
            Dict[str, Any]: {
                'available': bool,
                'reason': str,
                'network_status': Dict
            }
        """
        # 네트워크 연결 확인
        network_status = self.check_network_connectivity()
        
        if not network_status['connected']:
            return {
                'available': False,
                'reason': f"네트워크 연결 없음: {network_status['error']}",
                'network_status': network_status
            }
        
        # OpenAI API 접근 확인
        api_status = self.check_openai_api_access()
        
        if not api_status['accessible']:
            return {
                'available': False,
                'reason': f"OpenAI API 접근 불가: {api_status['error']}",
                'network_status': network_status
            }
        
        return {
            'available': True,
            'reason': '온라인 모드 사용 가능',
            'network_status': network_status
        }
    
    def check_network_connectivity(self) -> Dict[str, Any]:
        """
        기본 네트워크 연결성 확인
        
        Returns:
            Dict[str, Any]: {
                'connected': bool,
                'latency': float or None,
                'error': str or None
            }
        """
        try:
            # DNS 해결 및 연결 테스트
            socket.setdefaulttimeout(self.timeout)
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(("8.8.8.8", 53))
            
            # 응답 시간 측정
            import time
            start_time = time.time()
            response = requests.get(self.test_urls[1], timeout=self.timeout)
            latency = time.time() - start_time
            
            if response.status_code == 200:
                return {
                    'connected': True,
                    'latency': latency,
                    'error': None
                }
            else:
                return {
                    'connected': False,
                    'latency': None,
                    'error': f'HTTP {response.status_code}'
                }
                
        except socket.timeout:
            return {
                'connected': False,
                'latency': None,
                'error': '연결 타임아웃'
            }
        except socket.gaierror as e:
            return {
                'connected': False,
                'latency': None,
                'error': f'DNS 해결 실패: {str(e)}'
            }
        except Exception as e:
            return {
                'connected': False,
                'latency': None,
                'error': f'네트워크 오류: {str(e)}'
            }
    
    def check_openai_api_access(self) -> Dict[str, Any]:
        """
        OpenAI API 접근 가능성 확인
        
        Returns:
            Dict[str, Any]: {
                'accessible': bool,
                'response_time': float or None,
                'error': str or None
            }
        """
        try:
            import time
            start_time = time.time()
            
            # OpenAI API 엔드포인트 테스트
            response = requests.get(
                self.test_urls[0],
                timeout=self.timeout,
                headers={'User-Agent': 'AAC-Software/1.0'}
            )
            
            response_time = time.time() - start_time
            
            # 200이나 401(인증 오류)도 API가 작동한다는 의미
            if response.status_code in [200, 401, 429]:
                return {
                    'accessible': True,
                    'response_time': response_time,
                    'error': None
                }
            else:
                return {
                    'accessible': False,
                    'response_time': None,
                    'error': f'API HTTP {response.status_code}'
                }
                
        except requests.exceptions.Timeout:
            return {
                'accessible': False,
                'response_time': None,
                'error': 'API 타임아웃'
            }
        except requests.exceptions.ConnectionError:
            return {
                'accessible': False,
                'response_time': None,
                'error': 'API 연결 실패'
            }
        except Exception as e:
            return {
                'accessible': False,
                'response_time': None,
                'error': f'API 오류: {str(e)}'
            }
    
    def get_network_info(self) -> Dict[str, Any]:
        """
        전반적인 네트워크 정보 수집
        
        Returns:
            Dict[str, Any]: {
                'connectivity': Dict,
                'api_access': Dict,
                'online_available': bool
            }
        """
        connectivity = self.check_network_connectivity()
        api_access = self.check_openai_api_access()
        online_available = connectivity['connected'] and api_access['accessible']
        
        return {
            'connectivity': connectivity,
            'api_access': api_access,
            'online_available': online_available
        }