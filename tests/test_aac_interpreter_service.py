import unittest
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from src.aac_interpreter_service import AACInterpreterService


class TestAACInterpreterService(unittest.TestCase):
    
    def setUp(self):
        """테스트 초기화"""
        # 임시 파일들 설정
        self.test_users_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        self.test_users_file.close()
        
        self.test_feedback_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        self.test_feedback_file.close()
        
        self.test_memory_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        self.test_memory_file.close()
        
        # 테스트 설정
        self.test_config = {
            'users_file_path': self.test_users_file.name,
            'feedback_file_path': self.test_feedback_file.name,
            'memory_file_path': self.test_memory_file.name,
            'openai_model': 'gpt-4o-2024-08-06',
            'openai_temperature': 0.8,
            'interpretation_max_tokens': 400
        }
        
        # 여러 컴포넌트를 모킹
        with patch('src.aac_interpreter_service.ConfigManager') as mock_config_manager, \
             patch('src.aac_interpreter_service.CardRecommender') as mock_card_recommender, \
             patch('src.aac_interpreter_service.CardInterpreter') as mock_card_interpreter, \
             patch('src.aac_interpreter_service.ConversationSummaryMemory') as mock_memory, \
             patch('src.aac_interpreter_service.NetworkUtils') as mock_network:
            
            # ConfigManager 모킹
            mock_config_instance = Mock()
            mock_config_instance.get_data_paths.return_value = {
                'users_file_path': self.test_users_file.name,
                'feedback_file_path': self.test_feedback_file.name,
                'memory_file_path': self.test_memory_file.name
            }
            mock_config_instance.get_cluster_config.return_value = {
                'cluster_tags_path': 'test_cluster_tags.json',
                'embeddings_path': 'test_embeddings.json',
                'clustering_results_path': 'test_clustering_results.json'
            }
            mock_config_manager.return_value = mock_config_instance
            
            self.service = AACInterpreterService(self.test_config)
    
    def tearDown(self):
        """테스트 정리"""
        for file_path in [self.test_users_file.name, self.test_feedback_file.name, self.test_memory_file.name]:
            if os.path.exists(file_path):
                os.unlink(file_path)
    
    def test_register_user(self):
        """사용자 등록 테스트"""
        persona = {
            'age': '25',
            'gender': 'male',
            'disability_type': '자폐스펙트럼 장애',
            'communication_characteristics': '단순한 문장 선호',
            'selection_complexity': 'simple',
            'interesting_topics': ['음식', '게임'],
            'password': 'test123'
        }
        
        result = self.service.register_user(persona)
        
        self.assertEqual(result['status'], 'success')
        self.assertIsInstance(result['user_id'], int)
        self.assertIn('생성', result['message'])
    
    def test_authenticate_user_success(self):
        """사용자 인증 성공 테스트"""
        # 먼저 사용자 생성
        persona = {
            'age': '25',
            'gender': 'male',
            'disability_type': '자폐스펙트럼 장애',
            'communication_characteristics': '단순한 문장 선호',
            'selection_complexity': 'simple',
            'interesting_topics': ['음식'],
            'password': 'test123'
        }
        
        register_result = self.service.register_user(persona)
        user_id = register_result['user_id']
        
        # 인증 테스트
        auth_result = self.service.authenticate_user(user_id, 'test123')
        
        self.assertEqual(auth_result['status'], 'success')
        self.assertTrue(auth_result['authenticated'])
        self.assertIsNotNone(auth_result['user_info'])
    
    def test_authenticate_user_failure(self):
        """사용자 인증 실패 테스트"""
        # 먼저 사용자 생성
        persona = {
            'age': '25',
            'gender': 'male',
            'disability_type': '자폐스펙트럼 장애',
            'communication_characteristics': '단순한 문장 선호',
            'selection_complexity': 'simple',
            'interesting_topics': ['음식'],
            'password': 'test123'
        }
        
        register_result = self.service.register_user(persona)
        user_id = register_result['user_id']
        
        # 잘못된 비밀번호로 인증 테스트
        auth_result = self.service.authenticate_user(user_id, 'wrong_password')
        
        self.assertEqual(auth_result['status'], 'error')
        self.assertFalse(auth_result['authenticated'])
        self.assertIsNone(auth_result['user_info'])
    
    def test_get_user_info(self):
        """사용자 정보 조회 테스트"""
        # 사용자 생성
        persona = {
            'age': '30',
            'gender': 'female',
            'disability_type': '지적 장애',
            'communication_characteristics': '그림 선호',
            'selection_complexity': 'moderate',
            'interesting_topics': ['동물', '자연'],
            'password': 'test456'
        }
        
        register_result = self.service.register_user(persona)
        user_id = register_result['user_id']
        
        # 정보 조회
        info_result = self.service.get_user_info(user_id)
        
        self.assertEqual(info_result['status'], 'success')
        self.assertEqual(info_result['user']['age'], '30')
        self.assertEqual(info_result['user']['gender'], 'female')
        # 비밀번호가 포함되지 않았는지 확인
        self.assertNotIn('password', info_result['user'])
    
    def test_recommend_cards(self):
        """카드 추천 테스트"""
        # 사용자 생성
        persona = {
            'age': '25',
            'gender': 'male',
            'disability_type': '자폐스펙트럼 장애',
            'communication_characteristics': '단순한 문장 선호',
            'selection_complexity': 'simple',
            'interesting_topics': ['음식'],
            'preferred_category_types': [1, 2, 3],
            'password': 'test123'
        }
        
        register_result = self.service.register_user(persona)
        user_id = register_result['user_id']
        
        # CardRecommender 모킹
        self.service.card_recommender.recommend_cards = Mock(return_value={
            'status': 'success',
            'cards': ['food1.png', 'food2.png', 'want.png', 'please.png'],
            'clusters_used': [1, 2],
            'message': '4개 카드 추천 완료'
        })
        
        # 카드 추천 테스트
        recommend_result = self.service.recommend_cards(user_id, 4)
        
        self.assertEqual(recommend_result['status'], 'success')
        self.assertEqual(len(recommend_result['recommended_cards']), 4)
        self.assertIn('food1.png', recommend_result['recommended_cards'])
    
    def test_interpret_cards(self):
        """카드 해석 테스트"""
        # 사용자 생성
        persona = {
            'age': '25',
            'gender': 'male',
            'disability_type': '자폐스펙트럼 장애',
            'communication_characteristics': '단순한 문장 선호',
            'selection_complexity': 'simple',
            'interesting_topics': ['음식'],
            'password': 'test123'
        }
        
        register_result = self.service.register_user(persona)
        user_id = register_result['user_id']
        
        # CardInterpreter 모킹
        self.service.card_interpreter.interpret_cards = Mock(return_value={
            'status': 'success',
            'interpretations': ['간식을 주세요', '배고파요', '먹고 싶어요'],
            'method': 'online',
            'message': 'OpenAI API 해석 완료'
        })
        
        # FeedbackManager 모킹
        self.service.feedback_manager.record_interpretation_attempt = Mock(return_value={
            'feedback_id': 1
        })
        
        # 카드 해석 테스트
        selected_cards = ['food.png', 'want.png']
        context = {
            'time': '오후 3시',
            'place': '집',
            'interaction_partner': '엄마',
            'current_activity': '간식 시간'
        }
        
        interpret_result = self.service.interpret_cards(user_id, selected_cards, context)
        
        self.assertEqual(interpret_result['status'], 'success')
        self.assertEqual(len(interpret_result['interpretations']), 3)
        self.assertEqual(interpret_result['method'], 'online')
        self.assertEqual(interpret_result['feedback_id'], 1)
    
    def test_submit_feedback(self):
        """피드백 제출 테스트"""
        # 피드백 매니저 모킹
        self.service.feedback_manager.record_user_feedback = Mock(return_value={
            'status': 'success',
            'message': '피드백이 기록되었습니다.'
        })
        
        # 가짜 해석 시도 데이터 설정
        self.service.feedback_manager._data = {
            'interpretations': [{
                'feedback_id': 1,
                'user_id': 1,
                'cards': ['food.png'],
                'context': {
                    'time': '오후 3시',
                    'place': '집',
                    'interaction_partner': '엄마',
                    'current_activity': '간식 시간'
                },
                'interpretations': ['간식 주세요', '배고파요', '먹고 싶어요']
            }]
        }
        
        # ConversationSummaryMemory 모킹
        self.service.conversation_memory.add_conversation_memory = Mock(return_value={
            'status': 'success',
            'message': '메모리 업데이트 완료'
        })
        
        # 피드백 제출 테스트
        feedback_result = self.service.submit_feedback(
            feedback_id=1,
            selected_interpretation_index=0
        )
        
        self.assertEqual(feedback_result['status'], 'success')
        self.assertIn('피드백이 기록되었으며', feedback_result['message'])
    
    def test_get_system_status(self):
        """시스템 상태 조회 테스트"""
        # NetworkUtils 모킹
        self.service.network_utils.get_network_info = Mock(return_value={
            'online_available': True,
            'connectivity': {'connected': True},
            'api_access': {'accessible': True}
        })
        
        # FeedbackManager 모킹
        self.service.feedback_manager.get_feedback_statistics = Mock(return_value={
            'total_attempts': 10,
            'completed_feedback': 8,
            'average_accuracy': 0.8
        })
        
        # UserManager 모킹
        self.service.user_manager.get_all_users = Mock(return_value={
            'count': 5
        })
        
        status_result = self.service.get_system_status()
        
        self.assertEqual(status_result['status'], 'success')
        self.assertEqual(status_result['total_users'], 5)
        self.assertEqual(status_result['system_health'], 'healthy')
        self.assertTrue(status_result['network_status']['online_available'])
    
    def test_get_user_history(self):
        """사용자 이력 조회 테스트"""
        user_id = 1
        
        # 각 매니저 모킹
        self.service.feedback_manager.get_user_feedback_history = Mock(return_value={
            'history': [{'feedback_id': 1, 'user_id': 1}],
            'total_count': 1
        })
        
        self.service.feedback_manager.get_user_interpretation_summary = Mock(return_value={
            'summary': '총 1회의 해석 시도'
        })
        
        self.service.conversation_memory.get_user_memory_summary = Mock(return_value={
            'summary': '음식 관련 카드 주로 사용',
            'conversation_count': 1
        })
        
        history_result = self.service.get_user_history(user_id)
        
        self.assertEqual(history_result['status'], 'success')
        self.assertEqual(history_result['total_attempts'], 1)
        self.assertEqual(history_result['conversation_count'], 1)
        self.assertIn('음식', history_result['memory_summary'])
    
    def test_update_user_context(self):
        """사용자 컨텍스트 업데이트 테스트"""
        # 사용자 생성
        persona = {
            'age': '25',
            'gender': 'male',
            'disability_type': '자폐스펙트럼 장애',
            'communication_characteristics': '단순한 문장 선호',
            'selection_complexity': 'simple',
            'interesting_topics': ['음식'],
            'password': 'test123'
        }
        
        register_result = self.service.register_user(persona)
        user_id = register_result['user_id']
        
        # ContextManager 모킹
        self.service.context_manager.validate_context = Mock(return_value={
            'valid': True,
            'errors': []
        })
        
        self.service.context_manager.create_context = Mock(return_value={
            'status': 'success',
            'context_id': 'ctx_123'
        })
        
        # 컨텍스트 업데이트 테스트
        context = {
            'time': '오후 3시',
            'place': '집',
            'interaction_partner': '엄마',
            'current_activity': '간식 시간'
        }
        
        update_result = self.service.update_user_context(user_id, context)
        
        self.assertEqual(update_result['status'], 'success')
        self.assertEqual(update_result['context_id'], 'ctx_123')
    
    def test_delete_user(self):
        """사용자 삭제 테스트"""
        # 사용자 생성
        persona = {
            'age': '25',
            'gender': 'male',
            'disability_type': '자폐스펙트럼 장애',
            'communication_characteristics': '단순한 문장 선호',
            'selection_complexity': 'simple',
            'interesting_topics': ['음식'],
            'password': 'test123'
        }
        
        register_result = self.service.register_user(persona)
        user_id = register_result['user_id']
        
        # 관련 매니저들 모킹
        self.service.feedback_manager.delete_user_feedback = Mock(return_value={
            'status': 'success'
        })
        
        self.service.conversation_memory.clear_user_memory = Mock(return_value={
            'status': 'success'
        })
        
        # 사용자 삭제 테스트
        delete_result = self.service.delete_user(user_id, 'test123')
        
        self.assertEqual(delete_result['status'], 'success')
        self.assertIn('모든 데이터가 성공적으로 삭제', delete_result['message'])
    
    def test_update_user_persona(self):
        """사용자 페르소나 업데이트 테스트"""
        # 사용자 생성
        persona = {
            'age': '25',
            'gender': 'male',
            'disability_type': '자폐스펙트럼 장애',
            'communication_characteristics': '단순한 문장 선호',
            'selection_complexity': 'simple',
            'interesting_topics': ['음식'],
            'password': 'test123'
        }
        
        register_result = self.service.register_user(persona)
        user_id = register_result['user_id']
        
        # 페르소나 업데이트
        updates = {
            'age': '26',
            'interesting_topics': ['음식', '게임']
        }
        
        update_result = self.service.update_user_persona(user_id, updates)
        
        self.assertEqual(update_result['status'], 'success')
        
        # 업데이트 확인
        user_info = self.service.get_user_info(user_id)
        self.assertEqual(user_info['user']['age'], '26')


if __name__ == '__main__':
    unittest.main()