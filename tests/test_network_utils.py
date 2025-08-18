import unittest
from unittest.mock import Mock, patch, MagicMock
from src.network_utils import NetworkUtils


class TestNetworkUtils(unittest.TestCase):
    
    def setUp(self):
        """테스트 초기화"""
        self.config = {
            'network_timeout': 5,
            'test_urls': [
                'https://api.openai.com',
                'https://www.google.com',
                'https://httpbin.org/status/200'
            ]
        }
        self.network_utils = NetworkUtils(self.config)
    
    @patch('src.network_utils.socket')
    @patch('src.network_utils.requests')
    def test_check_network_connectivity_success(self, mock_requests, mock_socket):
        """네트워크 연결성 확인 성공 테스트"""
        # socket 연결 성공 모킹
        mock_socket_instance = Mock()
        mock_socket.socket.return_value = mock_socket_instance
        mock_socket_instance.connect.return_value = None
        
        # requests GET 성공 모킹
        mock_response = Mock()
        mock_response.status_code = 200
        mock_requests.get.return_value = mock_response
        
        result = self.network_utils.check_network_connectivity()
        
        self.assertTrue(result['connected'])
        self.assertIsNotNone(result['latency'])
        self.assertIsNone(result['error'])
        self.assertIsInstance(result['latency'], float)
    
    @patch('src.network_utils.socket')
    def test_check_network_connectivity_timeout(self, mock_socket):
        """네트워크 연결 타임아웃 테스트"""
        # socket 타임아웃 모킹
        mock_socket_instance = Mock()
        mock_socket.socket.return_value = mock_socket_instance
        mock_socket_instance.connect.side_effect = mock_socket.timeout()
        
        result = self.network_utils.check_network_connectivity()
        
        self.assertFalse(result['connected'])
        self.assertIsNone(result['latency'])
        self.assertEqual(result['error'], '연결 타임아웃')
    
    @patch('src.network_utils.socket')
    def test_check_network_connectivity_dns_failure(self, mock_socket):
        """DNS 해결 실패 테스트"""
        # DNS 오류 모킹
        mock_socket_instance = Mock()
        mock_socket.socket.return_value = mock_socket_instance
        mock_socket_instance.connect.side_effect = mock_socket.gaierror('Name resolution failed')
        
        result = self.network_utils.check_network_connectivity()
        
        self.assertFalse(result['connected'])
        self.assertIsNone(result['latency'])
        self.assertIn('DNS 해결 실패', result['error'])
    
    @patch('src.network_utils.requests')
    def test_check_openai_api_access_success(self, mock_requests):
        """OpenAI API 접근 성공 테스트"""
        # API 접근 성공 모킹 (200 응답)
        mock_response = Mock()
        mock_response.status_code = 200
        mock_requests.get.return_value = mock_response
        
        result = self.network_utils.check_openai_api_access()
        
        self.assertTrue(result['accessible'])
        self.assertIsNotNone(result['response_time'])
        self.assertIsNone(result['error'])
        self.assertIsInstance(result['response_time'], float)
    
    @patch('src.network_utils.requests')
    def test_check_openai_api_access_auth_error(self, mock_requests):
        """OpenAI API 인증 오류 테스트 (401은 API 작동 의미)"""
        # API 인증 오류 모킹 (401 응답 - API는 작동함)
        mock_response = Mock()
        mock_response.status_code = 401
        mock_requests.get.return_value = mock_response
        
        result = self.network_utils.check_openai_api_access()
        
        self.assertTrue(result['accessible'])  # 401도 API 작동을 의미
        self.assertIsNotNone(result['response_time'])
        self.assertIsNone(result['error'])
    
    @patch('src.network_utils.requests')
    def test_check_openai_api_access_rate_limit(self, mock_requests):
        """OpenAI API 속도 제한 테스트 (429는 API 작동 의미)"""
        # API 속도 제한 모킹 (429 응답 - API는 작동함)
        mock_response = Mock()
        mock_response.status_code = 429
        mock_requests.get.return_value = mock_response
        
        result = self.network_utils.check_openai_api_access()
        
        self.assertTrue(result['accessible'])  # 429도 API 작동을 의미
        self.assertIsNotNone(result['response_time'])
        self.assertIsNone(result['error'])
    
    @patch('src.network_utils.requests')
    def test_check_openai_api_access_server_error(self, mock_requests):
        """OpenAI API 서버 오류 테스트"""
        # API 서버 오류 모킹 (500 응답)
        mock_response = Mock()
        mock_response.status_code = 500
        mock_requests.get.return_value = mock_response
        
        result = self.network_utils.check_openai_api_access()
        
        self.assertFalse(result['accessible'])
        self.assertIsNone(result['response_time'])
        self.assertEqual(result['error'], 'API HTTP 500')
    
    @patch('src.network_utils.requests')
    def test_check_openai_api_access_timeout(self, mock_requests):
        """OpenAI API 타임아웃 테스트"""
        # API 타임아웃 모킹
        mock_requests.get.side_effect = mock_requests.exceptions.Timeout()
        
        result = self.network_utils.check_openai_api_access()
        
        self.assertFalse(result['accessible'])
        self.assertIsNone(result['response_time'])
        self.assertEqual(result['error'], 'API 타임아웃')
    
    @patch('src.network_utils.requests')
    def test_check_openai_api_access_connection_error(self, mock_requests):
        """OpenAI API 연결 오류 테스트"""
        # API 연결 오류 모킹
        mock_requests.get.side_effect = mock_requests.exceptions.ConnectionError()
        
        result = self.network_utils.check_openai_api_access()
        
        self.assertFalse(result['accessible'])
        self.assertIsNone(result['response_time'])
        self.assertEqual(result['error'], 'API 연결 실패')
    
    def test_is_online_mode_available_success(self):
        """온라인 모드 사용 가능 성공 테스트"""
        # 네트워크와 API 모두 성공하도록 모킹
        self.network_utils.check_network_connectivity = Mock(return_value={
            'connected': True,
            'latency': 0.1,
            'error': None
        })
        
        self.network_utils.check_openai_api_access = Mock(return_value={
            'accessible': True,
            'response_time': 0.5,
            'error': None
        })
        
        result = self.network_utils.is_online_mode_available()
        
        self.assertTrue(result['available'])
        self.assertEqual(result['reason'], '온라인 모드 사용 가능')
        self.assertTrue(result['network_status']['connected'])
    
    def test_is_online_mode_available_network_failure(self):
        """네트워크 실패로 온라인 모드 불가 테스트"""
        # 네트워크 실패 모킹
        self.network_utils.check_network_connectivity = Mock(return_value={
            'connected': False,
            'latency': None,
            'error': '연결 타임아웃'
        })
        
        result = self.network_utils.is_online_mode_available()
        
        self.assertFalse(result['available'])
        self.assertIn('네트워크 연결 없음', result['reason'])
        self.assertFalse(result['network_status']['connected'])
    
    def test_is_online_mode_available_api_failure(self):
        """API 실패로 온라인 모드 불가 테스트"""
        # 네트워크는 성공, API는 실패 모킹
        self.network_utils.check_network_connectivity = Mock(return_value={
            'connected': True,
            'latency': 0.1,
            'error': None
        })
        
        self.network_utils.check_openai_api_access = Mock(return_value={
            'accessible': False,
            'response_time': None,
            'error': 'API 연결 실패'
        })
        
        result = self.network_utils.is_online_mode_available()
        
        self.assertFalse(result['available'])
        self.assertIn('OpenAI API 접근 불가', result['reason'])
        self.assertTrue(result['network_status']['connected'])
    
    def test_get_network_info(self):
        """전반적인 네트워크 정보 수집 테스트"""
        # 각 메서드 모킹
        connectivity_result = {
            'connected': True,
            'latency': 0.1,
            'error': None
        }
        
        api_access_result = {
            'accessible': True,
            'response_time': 0.5,
            'error': None
        }
        
        self.network_utils.check_network_connectivity = Mock(return_value=connectivity_result)
        self.network_utils.check_openai_api_access = Mock(return_value=api_access_result)
        
        result = self.network_utils.get_network_info()
        
        self.assertEqual(result['connectivity'], connectivity_result)
        self.assertEqual(result['api_access'], api_access_result)
        self.assertTrue(result['online_available'])
    
    def test_get_network_info_partial_failure(self):
        """부분적 실패 상황의 네트워크 정보 테스트"""
        # 네트워크 성공, API 실패
        connectivity_result = {
            'connected': True,
            'latency': 0.1,
            'error': None
        }
        
        api_access_result = {
            'accessible': False,
            'response_time': None,
            'error': 'API 타임아웃'
        }
        
        self.network_utils.check_network_connectivity = Mock(return_value=connectivity_result)
        self.network_utils.check_openai_api_access = Mock(return_value=api_access_result)
        
        result = self.network_utils.get_network_info()
        
        self.assertEqual(result['connectivity'], connectivity_result)
        self.assertEqual(result['api_access'], api_access_result)
        self.assertFalse(result['online_available'])
    
    def test_configuration_with_custom_timeout(self):
        """사용자 정의 타임아웃 설정 테스트"""
        custom_config = {
            'network_timeout': 10,
            'test_urls': ['https://custom.api.com']
        }
        
        custom_network_utils = NetworkUtils(custom_config)
        
        self.assertEqual(custom_network_utils.timeout, 10)
        self.assertEqual(custom_network_utils.test_urls, ['https://custom.api.com'])
    
    def test_configuration_with_defaults(self):
        """기본 설정 테스트"""
        default_network_utils = NetworkUtils()
        
        self.assertEqual(default_network_utils.timeout, 5)
        self.assertIn('https://api.openai.com', default_network_utils.test_urls)
        self.assertIn('https://www.google.com', default_network_utils.test_urls)
        self.assertIn('https://httpbin.org/status/200', default_network_utils.test_urls)


if __name__ == '__main__':
    unittest.main()