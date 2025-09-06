import os
import sys
import json
from typing import Dict, List, Any
from pprint import pprint

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.aac_interpreter_service import AACInterpreterService


class AACServiceTester:
    """AAC Interpreter Service 통합 테스트 클래스.
    
    모든 주요 기능들을 순차적으로 테스트하여 시스템의 정상 동작을 확인합니다.
    """

    def __init__(self):
        """테스터 초기화 및 서비스 인스턴스 생성."""
        print("=== AAC Interpreter Service 테스트 시작 ===")
        try:
            self.service = AACInterpreterService()
            print("✓ 서비스 초기화 성공")
        except Exception as e:
            print(f"✗ 서비스 초기화 실패: {e}")
            raise
        
        # 테스트 결과 저장
        self.test_results = {}
        self.test_data = {}

    def _print_test_result(self, test_name: str, result: Dict[str, Any], expected_status: str = 'success'):
        """테스트 결과를 포맷팅하여 출력."""
        status = result.get('status', 'unknown')
        message = result.get('message', 'No message')
        
        if status == expected_status:
            print(f"✓ {test_name} 성공")
            print(f"  메시지: {message}")
        else:
            print(f"✗ {test_name} 실패")
            print(f"  상태: {status}")
            print(f"  메시지: {message}")
        
        self.test_results[test_name] = status == expected_status
        print(f"  전체 응답:")
        pprint(result, indent=4)
        print()

    def test_user_registration(self):
        """새 사용자 등록 및 페르소나 생성 테스트."""
        print("=== 1. 새 사용자 등록 및 페르소나 생성 ===")
        
        persona = {
            "name": "홍길동",
            "age": 22,
            "gender": "남성",
            "disability_type": "지적장애",
            "communication_characteristics": "단순한 단어나 짧은 구문을 선호",
            "interesting_topics": ["게임", "친구", "소방차"],
            "password": "test123"
        }
        
        try:
            result = self.service.register_user("test_user", persona)
            self._print_test_result("사용자 등록", result)
            
            # 성공시 사용자 ID 저장
            if result.get('status') == 'success':
                self.test_data['user_id'] = result.get('user_id', 'test_user')
                
        except Exception as e:
            print(f"✗ 사용자 등록 중 예외 발생: {e}")
            self.test_results["사용자 등록"] = False

    def test_user_authentication(self):
        """사용자 인증 및 세션 정보 반환 테스트."""
        print("=== 2. 사용자 인증 및 세션 정보 반환 ===")
        
        try:
            result = self.service.authenticate_user("test_user", "test123")
            self._print_test_result("사용자 인증", result)
            
            # 인증 성공시 사용자 정보 저장
            if result.get('authenticated') and result.get('user_info'):
                self.test_data['user_info'] = result['user_info']
                
        except Exception as e:
            print(f"✗ 사용자 인증 중 예외 발생: {e}")
            self.test_results["사용자 인증"] = False

    def test_get_user_info(self):
        """사용자 정보 조회 테스트."""
        print("=== 3. 사용자 정보 조회 ===")
        
        try:
            result = self.service.get_user_info("test_user")
            self._print_test_result("사용자 정보 조회", result)
            
        except Exception as e:
            print(f"✗ 사용자 정보 조회 중 예외 발생: {e}")
            self.test_results["사용자 정보 조회"] = False

    def test_update_user_persona(self):
        """사용자 페르소나 업데이트 및 선호 카테고리 재계산 테스트."""
        print("=== 4. 사용자 페르소나 업데이트 및 필요시 선호 카테고리 재계산 ===")
        
        try:
            result = self.service.update_user_persona("test_user", {
                "interesting_topics": ["흙", "가위", "머리카락"]
            })
            self._print_test_result("페르소나 업데이트", result)
            
        except Exception as e:
            print(f"✗ 페르소나 업데이트 중 예외 발생: {e}")
            self.test_results["페르소나 업데이트"] = False

    def test_create_context(self):
        """사용자 컨텍스트 생성 테스트."""
        print("=== 5. 사용자 컨텍스트 업데이트 ===")
        
        try:
            result = self.service.update_user_context(
                user_id="test_user",
                place="집",
                interaction_partner="가족",
                current_activity="식사"
            )
            self._print_test_result("컨텍스트 생성", result)
            
            # 성공시 컨텍스트 ID 저장
            if result.get('status') == 'success':
                self.test_data['context_id'] = result.get('context_id', 'test_context')
                self.test_data['context'] = {
                    "time": "12시 30분",
                    "place": "집",
                    "interaction_partner": "가족", 
                    "current_activity": "식사"
                }
                
        except Exception as e:
            print(f"✗ 컨텍스트 생성 중 예외 발생: {e}")
            self.test_results["컨텍스트 생성"] = False

    def test_get_card_selection_interface(self):
        """카드 선택 인터페이스 생성 테스트."""
        print("=== 6. 카드 선택 인터페이스 생성 ===")
        
        # 이전 테스트에서 생성된 데이터 사용
        context = self.test_data.get('context', {
            "time": "12시 30분",
            "place": "집", 
            "interaction_partner": "가족",
            "current_activity": "식사"
        })
        context_id = self.test_data.get('context_id', 'test_context')
        
        try:
            result = self.service.get_card_selection_interface("test_user", context, context_id)
            self._print_test_result("카드 선택 인터페이스 생성", result)
            
            # 성공시 카드 목록 저장
            if result.get('status') == 'success':
                interface_data = result.get('interface_data', {})
                all_selection_cards = interface_data.get('selection_options', [])
                self.test_data['all_cards'] = all_selection_cards
                self.test_data['selected_cards'] = all_selection_cards[:2] if len(all_selection_cards) >= 2 else all_selection_cards
                
        except Exception as e:
            print(f"✗ 카드 선택 인터페이스 생성 중 예외 발생: {e}")
            self.test_results["카드 선택 인터페이스 생성"] = False

    def test_validate_card_selection(self):
        """사용자 카드 선택 검증 테스트."""
        print("=== 7. 사용자 카드 선택 검증 ===")
        
        # 이전 테스트에서 생성된 카드 데이터 사용
        selected_cards = self.test_data.get('selected_cards', [])
        all_cards = self.test_data.get('all_cards', [])
        
        if not selected_cards or not all_cards:
            print("✗ 검증할 카드 데이터가 없습니다. 이전 테스트가 실패했을 가능성이 있습니다.")
            self.test_results["카드 선택 검증"] = False
            return
        
        try:
            result = self.service.validate_card_selection(selected_cards, all_cards)
            self._print_test_result("카드 선택 검증", result)
            
        except Exception as e:
            print(f"✗ 카드 선택 검증 중 예외 발생: {e}")
            self.test_results["카드 선택 검증"] = False

    def test_interpret_cards(self):
        """선택된 카드 해석 테스트."""
        print("=== 8. 선택된 카드 해석 ===")
        
        selected_cards = self.test_data.get('selected_cards', [])
        context = self.test_data.get('context', {})
        
        if not selected_cards:
            print("✗ 해석할 카드가 없습니다. 이전 테스트가 실패했을 가능성이 있습니다.")
            self.test_results["카드 해석"] = False
            return
        
        try:
            result = self.service.interpret_cards("test_user", selected_cards, context)
            self._print_test_result("카드 해석", result)
            
            # 성공시 해석 결과 저장
            if result.get('status') == 'success':
                self.test_data['interpretations'] = result.get('interpretations', ["해석1", "해석2", "해석3"])
                
        except Exception as e:
            print(f"✗ 카드 해석 중 예외 발생: {e}")
            self.test_results["카드 해석"] = False

    def test_request_partner_confirmation(self):
        """Partner에게 해석 확인 요청 테스트."""
        print("=== 9. Partner에게 해석 확인 요청 ===")
        
        selected_cards = self.test_data.get('selected_cards', [])
        context = self.test_data.get('context', {})
        interpretations = self.test_data.get('interpretations', ["해석1", "해석2", "해석3"])
        
        if not selected_cards:
            print("✗ 확인 요청할 데이터가 없습니다. 이전 테스트가 실패했을 가능성이 있습니다.")
            self.test_results["Partner 확인 요청"] = False
            return
        
        try:
            result = self.service.request_partner_confirmation(
                user_id="test_user",
                cards=selected_cards,
                context=context,
                interpretations=interpretations,
                partner_info="보호자"
            )
            self._print_test_result("Partner 확인 요청", result)
            
            # 성공시 확인 ID 저장
            if result.get('status') == 'success':
                self.test_data['confirmation_id'] = result.get('confirmation_id', '1000000')
                
        except Exception as e:
            print(f"✗ Partner 확인 요청 중 예외 발생: {e}")
            self.test_results["Partner 확인 요청"] = False

    def test_submit_partner_feedback(self):
        """Partner 피드백 제출 테스트."""
        print("=== 10. Partner 피드백 제출 ===")
        
        confirmation_id = self.test_data.get('confirmation_id', '1000000')
        
        try:
            result = self.service.submit_partner_feedback(confirmation_id, selected_interpretation_index=0)
            self._print_test_result("Partner 피드백 제출", result)
            
        except Exception as e:
            print(f"✗ Partner 피드백 제출 중 예외 발생: {e}")
            self.test_results["Partner 피드백 제출"] = False

    def test_get_recommendation_history_page(self):
        """카드 추천 히스토리 특정 페이지 조회 테스트."""
        print("=== 11. 카드 추천 히스토리 특정 페이지 조회 ===")
        
        context_id = self.test_data.get('context_id', 'test_context')
        
        try:
            result = self.service.get_card_recommendation_history_page(context_id, 1)
            self._print_test_result("히스토리 페이지 조회", result)
            
        except Exception as e:
            print(f"✗ 히스토리 페이지 조회 중 예외 발생: {e}")
            self.test_results["히스토리 페이지 조회"] = False

    def test_get_recommendation_history_summary(self):
        """카드 추천 히스토리 요약 확인 테스트."""
        print("=== 12. 카드 추천 히스토리 요약 확인 ===")
        
        context_id = self.test_data.get('context_id', 'test_context')
        
        try:
            result = self.service.get_card_recommendation_history_summary(context_id)
            self._print_test_result("히스토리 요약 조회", result)
            
        except Exception as e:
            print(f"✗ 히스토리 요약 조회 중 예외 발생: {e}")
            self.test_results["히스토리 요약 조회"] = False

    def run_all_tests(self):
        """모든 테스트를 순차적으로 실행."""
        test_methods = [
            self.test_user_registration,
            self.test_user_authentication,
            self.test_get_user_info,
            self.test_update_user_persona,
            self.test_create_context,
            self.test_get_card_selection_interface,
            self.test_validate_card_selection,
            self.test_interpret_cards,
            self.test_request_partner_confirmation,
            self.test_submit_partner_feedback,
            self.test_get_recommendation_history_page,
            self.test_get_recommendation_history_summary
        ]
        
        # 모든 테스트 실행
        for test_method in test_methods:
            try:
                test_method()
            except Exception as e:
                print(f"✗ 테스트 실행 중 치명적 오류 발생: {e}")
                break
        
        # 최종 결과 요약
        self._print_test_summary()

    def _print_test_summary(self):
        """테스트 실행 결과 요약 출력."""
        print("\n" + "="*50)
        print("테스트 실행 결과 요약")
        print("="*50)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result)
        failed_tests = total_tests - passed_tests
        
        print(f"총 테스트: {total_tests}")
        print(f"성공: {passed_tests}")
        print(f"실패: {failed_tests}")
        print(f"성공률: {(passed_tests/total_tests*100):.1f}%" if total_tests > 0 else "성공률: 0%")
        
        print("\n개별 테스트 결과:")
        for test_name, result in self.test_results.items():
            status = "✓ 성공" if result else "✗ 실패"
            print(f"  {test_name}: {status}")
        
        if failed_tests == 0:
            print("\n모든 테스트가 성공적으로 완료되었습니다!")
        else:
            print(f"\n{failed_tests}개의 테스트가 실패했습니다. 로그를 확인해주세요.")


if __name__ == "__main__":
    try:
        tester = AACServiceTester()
        tester.run_all_tests()
    except Exception as e:
        print(f"테스터 실행 중 치명적 오류 발생: {e}")
        sys.exit(1)