import unittest
import os
import json
import tempfile
from pathlib import Path
from src.user_manager import UserManager


class TestUserManager(unittest.TestCase):
    
    def setUp(self):
        """테스트 초기화"""
        # 임시 파일을 사용하여 테스트 격리
        self.test_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        self.test_file.close()
        self.user_manager = UserManager(self.test_file.name)
    
    def tearDown(self):
        """테스트 정리"""
        # 임시 파일 삭제
        if os.path.exists(self.test_file.name):
            os.unlink(self.test_file.name)
    
    def test_create_user_success(self):
        """사용자 생성 성공 테스트"""
        persona = {
            'age': '25',
            'gender': 'male',
            'disability_type': '자폐스펙트럼 장애',
            'communication_characteristics': '단순한 문장 선호',
            'selection_complexity': 'simple',
            'interesting_topics': ['음식', '게임'],
            'password': 'test123'
        }
        
        result = self.user_manager.create_user(persona)
        
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['user_id'], 1)
        self.assertIn('성공적으로 생성', result['message'])
    
    def test_create_multiple_users(self):
        """여러 사용자 생성 테스트"""
        persona1 = {
            'age': '20',
            'gender': 'female',
            'disability_type': '지적 장애',
            'communication_characteristics': '그림 선호',
            'selection_complexity': 'moderate',
            'interesting_topics': ['동물'],
            'password': 'pass1'
        }
        
        persona2 = {
            'age': '30',
            'gender': 'male',
            'disability_type': '의사소통 장애',
            'communication_characteristics': '복잡한 표현 가능',
            'selection_complexity': 'complex',
            'interesting_topics': ['스포츠', '음악'],
            'password': 'pass2'
        }
        
        result1 = self.user_manager.create_user(persona1)
        result2 = self.user_manager.create_user(persona2)
        
        self.assertEqual(result1['user_id'], 1)
        self.assertEqual(result2['user_id'], 2)
    
    def test_get_user_success(self):
        """사용자 조회 성공 테스트"""
        persona = {
            'age': '25',
            'gender': 'male',
            'disability_type': '자폐스펙트럼 장애',
            'communication_characteristics': '단순한 문장 선호',
            'selection_complexity': 'simple',
            'interesting_topics': ['음식'],
            'password': 'test123'
        }
        
        create_result = self.user_manager.create_user(persona)
        user_id = create_result['user_id']
        
        result = self.user_manager.get_user(user_id)
        
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['user']['age'], '25')
        self.assertEqual(result['user']['gender'], 'male')
        # 비밀번호가 반환되지 않는지 확인
        self.assertNotIn('password', result['user'])
    
    def test_get_user_not_found(self):
        """존재하지 않는 사용자 조회 테스트"""
        result = self.user_manager.get_user(999)
        
        self.assertEqual(result['status'], 'error')
        self.assertIsNone(result['user'])
        self.assertIn('조회할 수 없습니다', result['message'])
    
    def test_authenticate_user_success(self):
        """사용자 인증 성공 테스트"""
        persona = {
            'age': '25',
            'gender': 'male',
            'disability_type': '자폐스펙트럼 장애',
            'communication_characteristics': '단순한 문장 선호',
            'selection_complexity': 'simple',
            'interesting_topics': ['음식'],
            'password': 'test123'
        }
        
        create_result = self.user_manager.create_user(persona)
        user_id = create_result['user_id']
        
        result = self.user_manager.authenticate_user(user_id, 'test123')
        
        self.assertEqual(result['status'], 'success')
        self.assertTrue(result['authenticated'])
    
    def test_authenticate_user_wrong_password(self):
        """잘못된 비밀번호로 인증 실패 테스트"""
        persona = {
            'age': '25',
            'gender': 'male',
            'disability_type': '자폐스펙트럼 장애',
            'communication_characteristics': '단순한 문장 선호',
            'selection_complexity': 'simple',
            'interesting_topics': ['음식'],
            'password': 'test123'
        }
        
        create_result = self.user_manager.create_user(persona)
        user_id = create_result['user_id']
        
        result = self.user_manager.authenticate_user(user_id, 'wrong_password')
        
        self.assertEqual(result['status'], 'error')
        self.assertFalse(result['authenticated'])
    
    def test_update_user_persona(self):
        """사용자 페르소나 업데이트 테스트"""
        persona = {
            'age': '25',
            'gender': 'male',
            'disability_type': '자폐스펙트럼 장애',
            'communication_characteristics': '단순한 문장 선호',
            'selection_complexity': 'simple',
            'interesting_topics': ['음식'],
            'password': 'test123'
        }
        
        create_result = self.user_manager.create_user(persona)
        user_id = create_result['user_id']
        
        updates = {
            'age': '26',
            'interesting_topics': ['음식', '여행']
        }
        
        result = self.user_manager.update_user_persona(user_id, updates)
        self.assertEqual(result['status'], 'success')
        
        # 업데이트된 정보 확인
        user_info = self.user_manager.get_user(user_id)
        self.assertEqual(user_info['user']['age'], '26')
        self.assertEqual(user_info['user']['interesting_topics'], ['음식', '여행'])
    
    def test_delete_user(self):
        """사용자 삭제 테스트"""
        persona = {
            'age': '25',
            'gender': 'male',
            'disability_type': '자폐스펙트럼 장애',
            'communication_characteristics': '단순한 문장 선호',
            'selection_complexity': 'simple',
            'interesting_topics': ['음식'],
            'password': 'test123'
        }
        
        create_result = self.user_manager.create_user(persona)
        user_id = create_result['user_id']
        
        # 사용자 삭제
        delete_result = self.user_manager.delete_user(user_id)
        self.assertEqual(delete_result['status'], 'success')
        
        # 삭제된 사용자 조회 시 오류 확인
        get_result = self.user_manager.get_user(user_id)
        self.assertEqual(get_result['status'], 'error')
    
    def test_get_all_users(self):
        """모든 사용자 조회 테스트"""
        # 사용자들 생성
        personas = [
            {
                'age': '20',
                'gender': 'female',
                'disability_type': '지적 장애',
                'communication_characteristics': '그림 선호',
                'selection_complexity': 'moderate',
                'interesting_topics': ['동물'],
                'password': 'pass1'
            },
            {
                'age': '30',
                'gender': 'male',
                'disability_type': '의사소통 장애',
                'communication_characteristics': '복잡한 표현 가능',
                'selection_complexity': 'complex',
                'interesting_topics': ['스포츠'],
                'password': 'pass2'
            }
        ]
        
        for persona in personas:
            self.user_manager.create_user(persona)
        
        result = self.user_manager.get_all_users()
        
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['count'], 2)
        self.assertEqual(len(result['users']), 2)
        
        # 비밀번호가 포함되지 않았는지 확인
        for user in result['users']:
            self.assertNotIn('password', user)
    
    def test_update_user_password(self):
        """비밀번호 변경 테스트"""
        persona = {
            'age': '25',
            'gender': 'male',
            'disability_type': '자폐스펙트럼 장애',
            'communication_characteristics': '단순한 문장 선호',
            'selection_complexity': 'simple',
            'interesting_topics': ['음식'],
            'password': 'old_password'
        }
        
        create_result = self.user_manager.create_user(persona)
        user_id = create_result['user_id']
        
        # 비밀번호 변경
        result = self.user_manager.update_user_password(user_id, 'old_password', 'new_password')
        self.assertEqual(result['status'], 'success')
        
        # 새 비밀번호로 인증 테스트
        auth_result = self.user_manager.authenticate_user(user_id, 'new_password')
        self.assertTrue(auth_result['authenticated'])
        
        # 이전 비밀번호로 인증 실패 확인
        old_auth_result = self.user_manager.authenticate_user(user_id, 'old_password')
        self.assertFalse(old_auth_result['authenticated'])


if __name__ == '__main__':
    unittest.main()