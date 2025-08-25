import os
import sys
import json
from typing import Dict, List, Any
from pprint import pprint

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from aac_interpreter_service import AACInterpreterService


class AACServiceTester:
    """AAC 인터프리터 서비스 종합 테스트 클래스"""

    def __init__(self):
        # 실제 서비스 객체 초기화
        self.service = AACInterpreterService()

    def run_all_tests(self):
        print("\n=== 1. 새 사용자 등록 및 페르소나 생성 ===")
        persona = {
            "name": "홍길동",
            "age": 22,
            "gender": "male",
            "disability_type": "지적장애",
            "communication_characteristics": "단순한 단어나 짧은 구문을 선호",
            "interesting_topics": ["음식", "놀이", "가족"],
            "preferred_category": [15, 23, 8],
            "password": "pw123"
        }
        res = self.service.register_user("1", persona)
        pprint(res)

        print("\n=== 2. 사용자 인증 및 세션 정보 반환 ===")
        res = self.service.authenticate_user("1", "pw123")
        pprint(res)

        print("\n=== 3. 사용자 정보 조회 ===")
        res = self.service.get_user_info("1")
        pprint(res)

        print("\n=== 4. 사용자 페르소나 업데이트 및 필요 시 선호 카테고리 재계산 ===")
        res = self.service.update_user_persona("1", {
            "interesting_topics": ["스포츠", "영화"]
        })
        pprint(res)

        print("\n=== 5. 사용자 컨텍스트 업데이트 ===")
        res = self.service.update_user_context(
            user_id="1",
            place="학교",
            interaction_partner="친구",
            current_activity="대화"
        )
        pprint(res)

        print("\n=== 6. 카드 선택 인터페이스 생성 ===")
        context = {
            "time": "5시 10분",
            "place": "카페",
            "interaction_partner": "친구",
            "current_activity": "잡담"
        }
        res = self.service.get_card_selection_interface("1", context, "d227f781-3a25-40b2-929d-4a48922effee")
        pprint(res)

        print("\n=== 7. 사용자 카드 선택 검증 ===")
        res = self.service.validate_card_selection(["2462_사과.png", "2392_가족.png"], ["2024_학교", "2025_공부"])
        pprint(res)

        print("\n=== 8. 선택된 카드 해석 ===")
        res = self.service.interpret_cards("1", ["2462_사과.png", "2392_가족.png"], context)
        pprint(res)

        print("\n=== 9. Partner에게 해석 확인 요청 ===")
        res = self.service.request_partner_confirmation(
            user_id="1",
            cards=["2462_사과.png", "2392_가족.png"],
            context=context,
            interpretations=["해석1", "해석2", "해석3"],
            partner_info="보호자"
        )
        pprint(res)

        print("\n=== 10. Partner 피드백 제출 ===")
        res = self.service.submit_partner_feedback("1000000", selected_interpretation_index=0)
        pprint(res)

        print("\n=== 11. 카드 추천 히스토리 특정 페이지 조 ===")
        res = self.service.get_card_recommendation_history_page("d227f781-3a25-40b2-929d-4a48922effee", 1)
        pprint(res)

        print("\n=== 12. 카드 추천 히스토리 요약 확인 ===")
        res = self.service.get_card_recommendation_history_summary("d227f781-3a25-40b2-929d-4a48922effee")
        pprint(res)

if __name__ == "__main__":
    tester = AACServiceTester()
    tester.run_all_tests()