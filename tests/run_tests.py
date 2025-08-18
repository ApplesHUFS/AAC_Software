#!/usr/bin/env python3
"""
AAC Software 단위 테스트 실행 스크립트
"""

import unittest
import sys
import os
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 테스트 모듈들
TEST_MODULES = [
    'tests.test_user_manager',
    'tests.test_conversation_memory', 
    'tests.test_aac_interpreter_service',
    'tests.test_card_recommender',
    'tests.test_network_utils'
]

def run_all_tests():
    """모든 테스트 실행"""
    print("=" * 60)
    print("AAC Software 단위 테스트 실행")
    print("=" * 60)
    
    # 테스트 로더 생성
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 각 테스트 모듈 로드
    for module_name in TEST_MODULES:
        try:
            tests = loader.loadTestsFromName(module_name)
            suite.addTest(tests)
            print(f"✓ {module_name} 로드됨")
        except Exception as e:
            print(f"✗ {module_name} 로드 실패: {e}")
    
    print("-" * 60)
    
    # 테스트 실행
    runner = unittest.TextTestRunner(
        verbosity=2,
        stream=sys.stdout,
        descriptions=True,
        failfast=False
    )
    
    result = runner.run(suite)
    
    # 결과 요약
    print("=" * 60)
    print("테스트 결과 요약")
    print("=" * 60)
    print(f"실행된 테스트: {result.testsRun}")
    print(f"실패: {len(result.failures)}")
    print(f"오류: {len(result.errors)}")
    
    if result.failures:
        print("\n실패한 테스트:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback.split(chr(10))[-2] if chr(10) in traceback else traceback}")
    
    if result.errors:
        print("\n오류가 발생한 테스트:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback.split(chr(10))[-2] if chr(10) in traceback else traceback}")
    
    success_rate = ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100) if result.testsRun > 0 else 0
    print(f"\n성공률: {success_rate:.1f}%")
    
    return result.wasSuccessful()

def run_specific_test(test_name):
    """특정 테스트만 실행"""
    print(f"단일 테스트 실행: {test_name}")
    print("-" * 60)
    
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromName(test_name)
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()

if __name__ == '__main__':
    if len(sys.argv) > 1:
        # 특정 테스트 실행
        test_name = sys.argv[1]
        success = run_specific_test(test_name)
    else:
        # 모든 테스트 실행
        success = run_all_tests()
    
    # 종료 코드 설정
    sys.exit(0 if success else 1)