import os
import json
import sys
from typing import Dict, List, Any

# 프로젝트 경로 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from aac_interpreter_service import AACInterpreterService


class AACServiceTester:
    """AAC 인터프리터 서비스 종합 테스트 클래스"""
    
    def __init__(self):
        self.service = AACInterpreterService()
        self.test_users = []
        self.test_contexts = []
        self.test_feedback_ids = []
        
    def run_all_tests(self):
        """모든 테스트 실행"""
        print("=== AAC 인터프리터 서비스 종합 테스트 시작 ===\n")
        
        try:
            self.test_user_registration()
            self.test_user_authentication()
            self.test_context_management()
            self.test_card_recommendation()
            self.test_card_interpretation()
            self.test_feedback_system()
            self.test_partner_confirmation()
            self.test_memory_system()
            
            print("\n=== 모든 테스트 완료 ===")
            print("✓ 전체 시스템 정상 동작 확인")
            
        except Exception as e:
            print(f"\n✗ 테스트 실행 중 오류 발생: {str(e)}")
            raise
    
    def test_user_registration(self):
        """사용자 등록 테스트"""
        print("1. 사용자 등록 테스트")
        
        test_personas = [
            {
                'age': 8,
                'gender': 'male',
                'disability_type': '자폐스펙트럼 장애',
                'communication_characteristics': '단순한 문장 선호, 시각적 단서 필요',
                'interesting_topics': ['동물', '음식', '놀이'],
                'password': 'test123'
            },
            {
                'age': 25,
                'gender': 'female', 
                'disability_type': '의사소통 장애',
                'communication_characteristics': '복잡한 감정 표현 어려움',
                'interesting_topics': ['영화', '책', '여행', '음악'],
                'password': 'user456'
            }
        ]
        
        for i, persona in enumerate(test_personas):
            result = self.service.register_user(persona)
            assert result['status'] == 'success', f"사용자 {i+1} 등록 실패: {result['message']}"
            
            user_id = result['user_id']
            self.test_users.append({'user_id': user_id, 'password': persona['password']})
            
            print(f"  ✓ 사용자 {i+1} 등록 성공 (ID: {user_id})")
        
        print()
    
    def test_user_authentication(self):
        """사용자 인증 테스트"""
        print("2. 사용자 인증 테스트")
        
        for i, user_data in enumerate(self.test_users):
            # 정상 인증
            auth_result = self.service.authenticate_user(
                user_data['user_id'], 
                user_data['password']
            )
            assert auth_result['authenticated'] == True, f"사용자 {i+1} 인증 실패"
            assert 'user_info' in auth_result, "사용자 정보가 반환되지 않음"
            
            # 잘못된 비밀번호 테스트
            wrong_auth = self.service.authenticate_user(
                user_data['user_id'], 
                'wrong_password'
            )
            assert wrong_auth['authenticated'] == False, "잘못된 비밀번호로 인증 성공"
            
            print(f"  ✓ 사용자 {i+1} 인증 테스트 통과")
        
        print()
    
    def test_context_management(self):
        """컨텍스트 관리 테스트"""
        print("3. 컨텍스트 관리 테스트")
        
        test_contexts = [
            {
                'place': '집',
                'interaction_partner': '엄마',
                'current_activity': '저녁 식사'
            },
            {
                'place': '학교',
                'interaction_partner': '선생님',
                'current_activity': '수업 시간'
            }
        ]
        
        for i, (user_data, context_data) in enumerate(zip(self.test_users, test_contexts)):
            context_result = self.service.update_user_context(
                user_data['user_id'],
                context_data['place'],
                context_data['interaction_partner'],
                context_data['current_activity']
            )
            
            assert context_result['status'] == 'success', f"컨텍스트 {i+1} 생성 실패"
            
            context_id = context_result['context_id']
            self.test_contexts.append({
                'context_id': context_id,
                'user_id': user_data['user_id'],
                **context_data
            })
            
            print(f"  ✓ 사용자 {i+1} 컨텍스트 생성 성공 (ID: {context_id})")
        
        print()
    
    def test_card_recommendation(self):
        """카드 추천 테스트"""
        print("4. 카드 추천 시스템 테스트")
        
        for i, (user_data, context_data) in enumerate(zip(self.test_users, self.test_contexts)):
            context = {
                'time': '현재',
                'place': context_data['place'],
                'interaction_partner': context_data['interaction_partner'],
                'current_activity': context_data['current_activity']
            }
            
            interface_result = self.service.get_card_selection_interface(
                user_data['user_id'],
                context
            )
            
            assert interface_result['status'] == 'success', f"카드 인터페이스 {i+1} 생성 실패"
            
            interface_data = interface_result['interface_data']
            assert 'available_cards' in interface_data, "사용 가능한 카드 목록이 없음"
            assert len(interface_data['available_cards']) == 20, "표시 카드 수가 20개가 아님"
            
            # 카드 선택 유효성 검증
            selected_cards = interface_data['available_cards'][:3]  # 처음 3개 선택
            validation_result = self.service.validate_card_selection(
                selected_cards,
                interface_data['available_cards']
            )
            
            assert validation_result['status'] == 'success', f"카드 선택 검증 {i+1} 실패"
            
            print(f"  ✓ 사용자 {i+1} 카드 추천 및 선택 검증 성공")
        
        print()
    
    def test_card_interpretation(self):
        """카드 해석 테스트"""
        print("5. 카드 해석 시스템 테스트")
        
        test_card_selections = [
            ['밥', '물', '좋아요'],
            ['책', '읽다', '행복하다', '집']
        ]
        
        for i, (user_data, context_data, cards) in enumerate(
            zip(self.test_users, self.test_contexts, test_card_selections)
        ):
            context = {
                'time': '현재',
                'place': context_data['place'],
                'interaction_partner': context_data['interaction_partner'],
                'current_activity': context_data['current_activity']
            }
            
            interpretation_result = self.service.interpret_cards(
                user_data['user_id'],
                cards,
                context
            )
            
            assert interpretation_result['status'] == 'success', f"카드 해석 {i+1} 실패"
            assert len(interpretation_result['interpretations']) == 3, "해석 개수가 3개가 아님"
            assert interpretation_result['feedback_id'] > 0, "피드백 ID가 생성되지 않음"
            
            self.test_feedback_ids.append(interpretation_result['feedback_id'])
            
            print(f"  ✓ 사용자 {i+1} 카드 해석 성공")
            print(f"    선택 카드: {', '.join(cards)}")
            print(f"    해석 예시: {interpretation_result['interpretations'][0][:50]}...")
        
        print()
    
    def test_feedback_system(self):
        """피드백 시스템 테스트"""
        print("6. 피드백 시스템 테스트")
        
        # 첫 번째 사용자: 해석 선택 피드백
        feedback_result_1 = self.service.submit_feedback(
            self.test_feedback_ids[0],
            selected_interpretation_index=1  # 두 번째 해석 선택
        )
        
        assert feedback_result_1['status'] == 'success', "해석 선택 피드백 제출 실패"
        print("  ✓ 해석 선택 피드백 제출 성공")
        
        # 두 번째 사용자: 직접 수정 피드백
        feedback_result_2 = self.service.submit_feedback(
            self.test_feedback_ids[1],
            user_correction="저는 집에서 책을 읽고 있어서 정말 행복해요"
        )
        
        assert feedback_result_2['status'] == 'success', "직접 수정 피드백 제출 실패"
        print("  ✓ 직접 수정 피드백 제출 성공")
        
        print()
    
    def test_partner_confirmation(self):
        """파트너 확인 시스템 테스트"""
        print("7. 파트너 확인 시스템 테스트")
        
        # 파트너 확인 요청
        partner_request = self.service.request_partner_confirmation(
            user_id=self.test_users[0]['user_id'],
            cards=['도움', '필요', '지금'],
            context={
                'time': '현재',
                'place': '교실',
                'interaction_partner': '선생님',
                'current_activity': '수업'
            },
            interpretations=['지금 도움이 필요해요', '도움을 요청하고 있어요', '지금 당장 도와주세요'],
            partner_info={'name': '김선생님', 'role': '교사'}
        )
        
        assert partner_request['status'] == 'success', "파트너 확인 요청 실패"
        confirmation_id = partner_request['confirmation_id']
        
        # 대기 중인 확인 요청 조회
        pending_confirmations = self.service.get_pending_partner_confirmations()
        assert pending_confirmations['status'] == 'success', "대기 중인 확인 요청 조회 실패"
        
        # 파트너 피드백 제출
        partner_feedback = self.service.submit_partner_feedback(
            confirmation_id,
            selected_interpretation_index=0
        )
        
        assert partner_feedback['status'] == 'success', "파트너 피드백 제출 실패"
        
        print("  ✓ 파트너 확인 시스템 테스트 완료")
        print()
    
    def test_memory_system(self):
        """메모리 시스템 테스트"""
        print("8. 대화 메모리 시스템 테스트")
        
        # 추가 해석 및 피드백으로 메모리 패턴 생성
        for i, user_data in enumerate(self.test_users):
            # 여러 번의 해석 수행으로 메모리 패턴 축적
            test_sessions = [
                {
                    'cards': ['안녕', '친구'],
                    'context': {'time': '오전', 'place': '놀이터', 'interaction_partner': '친구', 'current_activity': '놀이'}
                },
                {
                    'cards': ['고마워', '도움'],
                    'context': {'time': '오후', 'place': '집', 'interaction_partner': '가족', 'current_activity': '숙제'}
                }
            ]
            
            for j, session in enumerate(test_sessions):
                interpretation_result = self.service.interpret_cards(
                    user_data['user_id'],
                    session['cards'],
                    session['context']
                )
                
                if interpretation_result['status'] == 'success':
                    # 피드백 제출로 메모리에 저장
                    self.service.submit_feedback(
                        interpretation_result['feedback_id'],
                        selected_interpretation_index=0
                    )
                    
            print(f"  ✓ 사용자 {i+1} 메모리 패턴 생성 완료")
        
        print("  ✓ 대화 메모리 시스템 테스트 완료")
        print()
    
    def test_error_handling(self):
        """오류 처리 테스트"""
        print("9. 오류 처리 테스트")
        
        # 존재하지 않는 사용자
        invalid_user_result = self.service.authenticate_user(99999, 'password')
        assert invalid_user_result['authenticated'] == False, "존재하지 않는 사용자 인증이 성공됨"
        
        # 잘못된 카드 선택
        invalid_cards_result = self.service.interpret_cards(
            self.test_users[0]['user_id'],
            [],  # 빈 카드 리스트
            {'time': '현재', 'place': '집', 'interaction_partner': '가족', 'current_activity': '대화'}
        )
        # 빈 카드 리스트는 시스템에서 어떻게 처리하는지에 따라 다름
        
        # 잘못된 피드백 ID
        invalid_feedback_result = self.service.submit_feedback(99999, selected_interpretation_index=0)
        assert invalid_feedback_result['status'] == 'error', "존재하지 않는 피드백 ID로 피드백 제출이 성공됨"
        
        print("  ✓ 오류 처리 테스트 완료")
        print()


def main():
    """메인 테스트 실행 함수"""
    # 환경 설정 확인
    required_paths = [
        'dataset/images',
        'dataset/processed', 
        'user_data'
    ]
    
    print("=== 환경 설정 확인 ===")
    for path in required_paths:
        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)
            print(f"  디렉토리 생성: {path}")
        else:
            print(f"  ✓ 디렉토리 존재: {path}")
    
    # 기본 데이터 파일 생성 (빈 파일로 시작)
    data_files = [
        'user_data/users.json',
        'user_data/feedback.json',
        'user_data/conversation_memory.json',
        'dataset/processed/cluster_tags.json',
        'dataset/processed/embeddings.json',
        'dataset/processed/clustering_results.json'
    ]
    
    for file_path in data_files:
        if not os.path.exists(file_path):
            with open(file_path, 'w', encoding='utf-8') as f:
                if 'clustering_results' in file_path:
                    json.dump({'clusters': {}, 'metadata': {}}, f, ensure_ascii=False, indent=2)
                else:
                    json.dump({}, f, ensure_ascii=False, indent=2)
            print(f"  데이터 파일 생성: {file_path}")
        else:
            print(f"  ✓ 데이터 파일 존재: {file_path}")
    
    print("\n")
    
    # 테스트 실행
    tester = AACServiceTester()
    tester.run_all_tests()


if __name__ == "__main__":
    main()
