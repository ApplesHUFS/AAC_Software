import os
import sys
import json
from typing import Dict, List, Any
from pprint import pprint

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from aac_interpreter_service import AACInterpreterService


class AACServiceTester:
    def __init__(self):
        self.service = AACInterpreterService()

    def run_all_tests(self):
        print("\n=== 1. 새 사용자 등록 및 페르소나 생성 ===")
        persona = {
            "name": "홍길동",
            "age": 22,
            "gender": "남성",
            "disability_type": "지적장애",
            "communication_characteristics": "단순한 단어나 짧은 구문을 선호",
            "interesting_topics": ["음식", "놀이", "가족"],
            "password": "test123"
        }
        res = self.service.register_user("test_user", persona)
        pprint(res)

        print("\n=== 2. 사용자 인증 및 세션 정보 반환 ===")
        res = self.service.authenticate_user("test_user", "test123")
        pprint(res)

        print("\n=== 3. 사용자 정보 조회 ===")
        res = self.service.get_user_info("test_user")
        pprint(res)

        print("\n=== 4. 사용자 페르소나 업데이트 및 필요시 선호 카테고리 재계산 ===")
        res = self.service.update_user_persona("test_user", {
            "interesting_topics": ["스포츠", "영화"]
        })
        pprint(res)

        print("\n=== 5. 사용자 컨텍스트 업데이트 ===")
        res = self.service.update_user_context(
            user_id="test_user",
            place="집",
            interaction_partner="가족",
            current_activity="식사"
        )
        context_id = res.get('context_id', 'test_context')
        pprint(res)

        print("\n=== 6. 카드 선택 인터페이스 생성 ===")
        context = {
            "time": "12시 30분",
            "place": "집",
            "interaction_partner": "가족",
            "current_activity": "식사"
        }
        res = self.service.get_card_selection_interface("test_user", context, context_id)
        interface_data = res.get('interface_data', {})
        all_selection_cards = interface_data.get('selection_options', [])
        selected_cards = all_selection_cards[:2]
        
        pprint(res)

        print("\n=== 7. 사용자 카드 선택 검증 ===")
        all_cards = [f"test_card_{i}_{j}.png" for i in range(10) for j in range(2)]
        res = self.service.validate_card_selection(selected_cards, all_selection_cards)
        pprint(res)

        print("\n=== 8. 선택된 카드 해석 ===")
        res = self.service.interpret_cards("test_user", selected_cards[:2], context)
        pprint(res)

        print("\n=== 9. Partner에게 해석 확인 요청 ===")
        res = self.service.request_partner_confirmation(
            user_id="test_user",
            cards=selected_cards[:2],
            context=context,
            interpretations=["해석1", "해석2", "해석3"],
            partner_info="보호자"
        )
        confirmation_id = res.get('confirmation_id', '1000000')
        pprint(res)

        print("\n=== 10. Partner 피드백 제출 ===")
        res = self.service.submit_partner_feedback(confirmation_id, selected_interpretation_index=0)
        pprint(res)

        print("\n=== 11. 카드 추천 히스토리 특정 페이지 조회 ===")
        res = self.service.get_card_recommendation_history_page(context_id, 1)
        pprint(res)

        print("\n=== 12. 카드 추천 히스토리 요약 확인 ===")
        res = self.service.get_card_recommendation_history_summary(context_id)
        pprint(res)


if __name__ == "__main__":
    tester = AACServiceTester()
    tester.run_all_tests()
