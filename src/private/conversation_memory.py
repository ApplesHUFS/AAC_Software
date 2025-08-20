import json
import os
from typing import Dict, List, Optional, Any
from datetime import datetime
from langchain.memory import ConversationSummaryMemory as LangChainConversationSummaryMemory
from langchain_openai import ChatOpenAI
from .llm import LLMFactory


class ConversationSummaryMemory:
    """대화 요약 메모리 관리 시스템.
    
    LangChain의 ConversationSummaryMemory를 활용하여 카드 해석과 컨텍스트의 
    연결성을 학습하고 요약하여 저장합니다. 향후 카드 해석 시 과거 패턴을 
    참조하여 더 정확한 해석을 제공할 수 있도록 돕습니다.
    
    Attributes:
        memory_file_path: 메모리 데이터 저장 파일 경로
        config: 설정 딕셔너리
        memory_data: 사용자별 메모리 데이터
        llm: LangChain ChatOpenAI 모델
        llm_factory: OpenAI API 통합 관리 팩토리
    """
    
    def __init__(self, memory_file_path: Optional[str] = None, config: Optional[Dict] = None):
        """ConversationSummaryMemory 초기화.
        
        Args:
            memory_file_path: 메모리 파일 저장 경로. None이면 기본값 사용.
            config: 설정 딕셔너리. None이면 기본값 사용.
        """
        self.memory_file_path = memory_file_path or "user_data/conversation_memory.json"
        self.config = config or {}
        self.memory_data = {
            "user_memories": {}  # user_id별 메모리
        }
        
        # LangChain ChatOpenAI 모델 초기화
        self.model = self.config.get('openai_model', 'gpt-4o-2024-08-06')
        self.temperature = self.config.get('openai_temperature', 0.8)
        self.max_tokens = self.config.get('summary_max_tokens', 200)
        
        try:
            self.llm = ChatOpenAI(
                model=self.model,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            # LLMFactory 초기화 (이미지 분석용)
            llm_config = {
                'openai_model': self.model,
                'openai_temperature': 0.3,  # 분석용으로 낮은 온도
                'interpretation_max_tokens': 100,
                'api_timeout': self.config.get('api_timeout', 15),
                'images_folder': self.config.get('images_folder', 'dataset/images')
            }
            self.llm_factory = LLMFactory(llm_config)
            
        except Exception as e:
            raise RuntimeError(f"OpenAI 클라이언트 초기화 실패: {str(e)}. 환경변수 OPENAI_API_KEY를 확인하세요.")
        
        self._load_memory()
    
    def _load_memory(self):
        """메모리 파일에서 데이터 로드."""
        if os.path.exists(self.memory_file_path):
            try:
                with open(self.memory_file_path, 'r', encoding='utf-8') as f:
                    self.memory_data = json.load(f)
            except Exception as e:
                print(f"메모리 파일 로드 실패: {e}")
                self.memory_data = {"user_memories": {}}
    
    def _save_memory(self):
        """메모리 데이터를 파일에 저장."""
        try:
            os.makedirs(os.path.dirname(self.memory_file_path), exist_ok=True)
            with open(self.memory_file_path, 'w', encoding='utf-8') as f:
                json.dump(self.memory_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"메모리 파일 저장 실패: {e}")
    
    def add_conversation_memory(self, 
                              user_id: int, 
                              cards: List[str], 
                              context: Dict[str, Any],
                              interpretations: List[str],
                              selected_interpretation: Optional[str] = None,
                              user_correction: Optional[str] = None) -> Dict[str, Any]:
        """새로운 대화 기억을 추가하고 요약.
        
        카드 조합과 컨텍스트, 최종 해석의 연관성을 학습하여 메모리에 저장합니다.
        LangChain의 ConversationSummaryMemory를 사용하여 요약을 생성합니다.
        
        Args:
            user_id: 사용자 ID
            cards: 사용된 AAC 카드 파일명 리스트
            context: 상황 정보 (time, place, interaction_partner, current_activity)
            interpretations: 생성된 3개 해석 리스트
            selected_interpretation: Partner가 선택한 올바른 해석
            user_correction: Partner가 직접 입력한 올바른 해석
        
        Returns:
            Dict containing:
                - status (str): 'success' 또는 'error'
                - summary (str): 업데이트된 요약
                - memory_updated (bool): 메모리 업데이트 여부
                - message (str): 결과 메시지
        """
        user_id_str = str(user_id)
        
        # 사용자별 메모리 초기화
        if user_id_str not in self.memory_data["user_memories"]:
            self.memory_data["user_memories"][user_id_str] = {
                "conversation_history": [],
                "summary": ""
            }
        
        # 최종 해석 결정
        final_interpretation = selected_interpretation or user_correction
        if not final_interpretation:
            return {
                'status': 'error',
                'summary': '',
                'memory_updated': False,
                'message': '최종 해석이 제공되지 않았습니다.'
            }
        
        # 대화 기록 추가
        conversation_entry = {
            "timestamp": datetime.now().isoformat(),
            "cards": cards,
            "context": context,
            "interpretations": interpretations,
            "final_interpretation": final_interpretation
        }
        
        self.memory_data["user_memories"][user_id_str]["conversation_history"].append(conversation_entry)
        
        # 카드-해석 연결성 분석
        try:
            connection_analysis = self.llm_factory.analyze_card_interpretation_connection(
                cards, context, final_interpretation
            )
        except Exception as e:
            # 간단한 fallback
            card_names = [card.replace('.png', '').replace('_', ' ') for card in cards]
            connection_analysis = f"카드 '{', '.join(card_names[:2])}'의 시각적 특징을 통해 '{final_interpretation[:20]}...' 의미 전달"
        
        # LangChain ConversationSummaryMemory를 사용한 요약 생성
        summary_result = self._update_summary_with_langchain(user_id_str, connection_analysis)
        
        # 메모리 저장
        self._save_memory()
        
        return {
            'status': 'success',
            'summary': summary_result,
            'memory_updated': True,
            'message': f'사용자 {user_id}의 대화 메모리가 업데이트되었습니다.'
        }
    
    def _update_summary_with_langchain(self, user_id_str: str, connection_analysis: str) -> str:
        """LangChain ConversationSummaryMemory를 사용하여 요약 업데이트.
        
        Args:
            user_id_str: 사용자 ID 문자열
            connection_analysis: 카드-해석 연결성 분석 결과
            
        Returns:
            str: 업데이트된 요약
        """
        user_memory = self.memory_data["user_memories"][user_id_str]
        conversation_history = user_memory["conversation_history"]
        
        if len(conversation_history) == 0:
            user_memory["summary"] = "아직 대화 기록이 없습니다."
            return "아직 대화 기록이 없습니다."
        
        try:
            # LangChain ConversationSummaryMemory 생성
            langchain_memory = LangChainConversationSummaryMemory(
                llm=self.llm,
                return_messages=False
            )
            
            # 기존 요약이 있으면 반영
            existing_summary = user_memory.get("summary", "")
            if existing_summary and existing_summary != "아직 대화 기록이 없습니다.":
                langchain_memory.buffer = existing_summary
            
            # 최근 대화 기록을 LangChain 형태로 변환하여 추가
            recent_conv = conversation_history[-1]  # 가장 최근 대화만
            cards_str = ", ".join([card.replace('.png', '').replace('_', ' ') for card in recent_conv["cards"]])
            context_str = f"{recent_conv['context'].get('place', '?')}에서 {recent_conv['context'].get('current_activity', '?')} 중"
            
            # 사용자 메시지 (카드 선택과 상황)
            user_input = f"상황: {context_str}, 선택한 카드: {cards_str}"
            
            # AI 메시지 (분석된 연결성)
            ai_output = f"카드-해석 연결성: {connection_analysis}. 최종 해석: {recent_conv['final_interpretation']}"
            
            # 메모리에 저장하고 요약 업데이트
            langchain_memory.save_context(
                {"input": user_input},
                {"output": ai_output}
            )
            
            # 생성된 요약 가져오기
            new_summary = langchain_memory.buffer
            user_memory["summary"] = new_summary
            
            return new_summary
            
        except Exception as e:
            print(f"LangChain 요약 생성 실패: {e}")
            # 간단한 fallback 요약
            fallback_summary = f"총 {len(conversation_history)}회 대화. 최근: {connection_analysis}"
            user_memory["summary"] = fallback_summary
            return fallback_summary
    
    def get_user_memory_summary(self, user_id: int) -> Dict[str, Any]:
        """사용자의 대화 메모리 요약 조회.
        
        카드 해석 시 참고할 수 있도록 사용자의 과거 대화 패턴을 요약하여 반환합니다.
        
        Args:
            user_id: 사용자 ID
            
        Returns:
            Dict containing:
                - status (str): 'success'
                - summary (str): 대화 패턴 요약
                - conversation_count (int): 대화 횟수
        """
        user_id_str = str(user_id)
        
        if user_id_str not in self.memory_data["user_memories"]:
            return {
                'status': 'success',
                'summary': '아직 대화 기록이 없습니다.',
                'conversation_count': 0
            }
        
        user_memory = self.memory_data["user_memories"][user_id_str]
        
        return {
            'status': 'success',
            'summary': user_memory.get("summary", "요약이 생성되지 않았습니다."),
            'conversation_count': len(user_memory["conversation_history"])
        }
    
    def get_recent_patterns(self, user_id: int, limit: int = 5) -> Dict[str, Any]:
        """최근 카드 사용 패턴 조회.
        
        카드 해석 시 참고할 수 있도록 최근 사용된 카드들과 해석을 반환합니다.
        
        Args:
            user_id: 사용자 ID
            limit: 조회할 최근 기록 수
            
        Returns:
            Dict containing:
                - status (str): 'success'
                - recent_patterns (List[str]): 최근 패턴 요약들
                - suggestions (str): 해석 참고 정보
        """
        user_id_str = str(user_id)
        
        if user_id_str not in self.memory_data["user_memories"]:
            return {
                'status': 'success',
                'recent_patterns': [],
                'suggestions': '과거 사용 패턴이 없습니다.'
            }
        
        conversation_history = self.memory_data["user_memories"][user_id_str]["conversation_history"]
        recent_conversations = conversation_history[-limit:] if conversation_history else []
        
        patterns = []
        for conv in recent_conversations:
            cards_str = ", ".join([card.replace('.png', '').replace('_', ' ') for card in conv["cards"]])
            pattern = f"카드 '{cards_str}' → '{conv['final_interpretation'][:30]}...'"
            patterns.append(pattern)
        
        suggestions = ""
        if patterns:
            suggestions = f"최근 {len(patterns)}회 대화에서 주로 사용된 패턴들을 참고하여 해석하세요."
        else:
            suggestions = "과거 사용 패턴이 없어 페르소나 정보를 중심으로 해석하세요."
        
        return {
            'status': 'success',
            'recent_patterns': patterns,
            'suggestions': suggestions
        }