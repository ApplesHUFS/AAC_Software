import unittest
import os
import tempfile
from unittest.mock import Mock, patch, MagicMock
from src.conversation_memory import ConversationSummaryMemory


class TestConversationSummaryMemory(unittest.TestCase):
    
    def setUp(self):
        """테스트 초기화"""
        # 임시 파일을 사용하여 테스트 격리
        self.test_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        self.test_file.close()
        
        # OpenAI를 모킹하여 API 호출 없이 테스트
        self.config = {
            'openai_model': 'gpt-4o-2024-08-06',
            'openai_temperature': 0.7,
            'summary_max_tokens': 200
        }
        
        with patch('src.conversation_memory.ChatOpenAI'), \
             patch('src.conversation_memory.OpenAI'):
            self.memory = ConversationSummaryMemory(
                memory_file_path=self.test_file.name,
                config=self.config
            )
    
    def tearDown(self):
        """테스트 정리"""
        if os.path.exists(self.test_file.name):
            os.unlink(self.test_file.name)
    
    def test_add_conversation_memory_basic(self):
        """기본 대화 메모리 추가 테스트"""
        user_id = 1
        cards = ['card1.png', 'card2.png']
        context = {
            'time': '오후 3시',
            'place': '집',
            'interaction_partner': '엄마',
            'current_activity': '간식 먹기'
        }
        interpretations = ['배고파요', '간식을 주세요', '같이 먹어요']
        selected_interpretation = '간식을 주세요'
        
        result = self.memory.add_conversation_memory(
            user_id=user_id,
            cards=cards,
            context=context,
            interpretations=interpretations,
            selected_interpretation=selected_interpretation
        )
        
        self.assertEqual(result['status'], 'success')
        self.assertTrue(result['memory_updated'])
        self.assertIn('업데이트', result['message'])
    
    def test_get_user_memory_summary_empty(self):
        """빈 사용자 메모리 요약 조회 테스트"""
        result = self.memory.get_user_memory_summary(999)
        
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['conversation_count'], 0)
        self.assertEqual(result['patterns_count'], 0)
        self.assertIn('대화 기록이 없습니다', result['summary'])
    
    def test_get_card_usage_patterns_empty(self):
        """빈 카드 사용 패턴 조회 테스트"""
        result = self.memory.get_card_usage_patterns(999, ['card1.png'])
        
        self.assertEqual(result['status'], 'success')
        self.assertEqual(len(result['patterns']), 0)
        self.assertEqual(len(result['suggestions']), 0)
    
    def test_clear_user_memory(self):
        """사용자 메모리 삭제 테스트"""
        user_id = 1
        
        # 먼저 메모리 추가
        self.memory.add_conversation_memory(
            user_id=user_id,
            cards=['card1.png'],
            context={
                'time': '오후 3시',
                'place': '집',
                'interaction_partner': '엄마',
                'current_activity': '간식 먹기'
            },
            interpretations=['배고파요'],
            selected_interpretation='배고파요'
        )
        
        # 메모리 삭제
        result = self.memory.clear_user_memory(user_id)
        
        self.assertEqual(result['status'], 'success')
        self.assertIn('삭제되었습니다', result['message'])
        
        # 삭제 확인
        summary_result = self.memory.get_user_memory_summary(user_id)
        self.assertEqual(summary_result['conversation_count'], 0)
    
    @patch('src.conversation_memory.LangChainConversationSummaryMemory')
    def test_generate_summary_with_langchain(self, mock_langchain_memory):
        """LangChain을 사용한 요약 생성 테스트"""
        # Mock LangChain ConversationSummaryMemory
        mock_instance = Mock()
        mock_instance.buffer = "사용자가 주로 음식 관련 카드를 사용하여 간식을 요청하는 패턴을 보임"
        mock_langchain_memory.return_value = mock_instance
        
        # Enable langchain
        self.memory.langchain_enabled = True
        self.memory.llm = Mock()
        
        user_id = 1
        cards = ['food.png', 'want.png']
        context = {
            'time': '오후 3시',
            'place': '집',
            'interaction_partner': '엄마',
            'current_activity': '간식 시간'
        }
        interpretations = ['간식 주세요', '배고파요', '먹고 싶어요']
        
        result = self.memory.add_conversation_memory(
            user_id=user_id,
            cards=cards,
            context=context,
            interpretations=interpretations,
            selected_interpretation='간식 주세요'
        )
        
        self.assertEqual(result['status'], 'success')
        self.assertIn('간식', result['summary'])
    
    def test_create_simple_summary(self):
        """간단한 통계 기반 요약 생성 테스트"""
        # Disable LangChain and OpenAI
        self.memory.langchain_enabled = False
        self.memory.openai_enabled = False
        
        user_id = 1
        
        # 여러 대화 추가
        conversations = [
            (['food.png'], '간식 주세요'),
            (['food.png', 'drink.png'], '물과 간식 주세요'),
            (['play.png'], '놀고 싶어요')
        ]
        
        for cards, interpretation in conversations:
            self.memory.add_conversation_memory(
                user_id=user_id,
                cards=cards,
                context={
                    'time': '오후 3시',
                    'place': '집',
                    'interaction_partner': '엄마',
                    'current_activity': '일상'
                },
                interpretations=[interpretation],
                selected_interpretation=interpretation
            )
        
        summary_result = self.memory.get_user_memory_summary(user_id)
        
        self.assertEqual(summary_result['status'], 'success')
        self.assertEqual(summary_result['conversation_count'], 3)
        self.assertIn('총 3회 대화', summary_result['summary'])
        self.assertIn('food.png', summary_result['summary'])
    
    def test_card_interpretation_patterns(self):
        """카드 해석 패턴 학습 테스트"""
        user_id = 1
        cards = ['food.png', 'want.png']
        
        # 같은 카드 조합으로 여러 번 대화
        interpretations_list = [
            '간식 주세요',
            '배고파요',
            '먹고 싶어요'
        ]
        
        for interpretation in interpretations_list:
            self.memory.add_conversation_memory(
                user_id=user_id,
                cards=cards,
                context={
                    'time': '오후 3시',
                    'place': '집',
                    'interaction_partner': '엄마',
                    'current_activity': '간식 시간'
                },
                interpretations=[interpretation],
                selected_interpretation=interpretation
            )
        
        # 패턴 조회
        patterns_result = self.memory.get_card_usage_patterns(user_id, cards)
        
        self.assertEqual(patterns_result['status'], 'success')
        self.assertEqual(len(patterns_result['patterns']), 3)
        self.assertEqual(patterns_result['frequency'], 3)
        self.assertIn('간식 주세요', patterns_result['patterns'])
    
    def test_memory_persistence(self):
        """메모리 지속성 테스트 (파일 저장/로드)"""
        user_id = 1
        cards = ['test.png']
        context = {
            'time': '오후 3시',
            'place': '집',
            'interaction_partner': '엄마',
            'current_activity': '테스트'
        }
        interpretations = ['테스트입니다']
        
        # 메모리 추가
        self.memory.add_conversation_memory(
            user_id=user_id,
            cards=cards,
            context=context,
            interpretations=interpretations,
            selected_interpretation='테스트입니다'
        )
        
        # 새로운 인스턴스 생성하여 로드 테스트
        with patch('src.conversation_memory.ChatOpenAI'), \
             patch('src.conversation_memory.OpenAI'):
            new_memory = ConversationSummaryMemory(
                memory_file_path=self.test_file.name,
                config=self.config
            )
        
        # 로드된 데이터 확인
        summary_result = new_memory.get_user_memory_summary(user_id)
        self.assertGreater(summary_result['conversation_count'], 0)


if __name__ == '__main__':
    unittest.main()