import json
import os
from typing import Dict, List, Optional, Any
from datetime import datetime
from openai import OpenAI
from langchain.memory import ConversationSummaryMemory as LangChainConversationSummaryMemory
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage


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
        langchain_enabled: LangChain 사용 가능 여부
        openai_client: OpenAI API 클라이언트
        openai_enabled: OpenAI API 사용 가능 여부
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
            "user_memories": {},  # user_id별 메모리
            "global_patterns": {}  # 전역 패턴
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
            self.langchain_enabled = True
        except Exception:
            self.llm = None
            self.langchain_enabled = False
        
        # OpenAI 클라이언트 초기화 (fallback용)
        try:
            self.openai_client = OpenAI()
            self.openai_enabled = True
        except Exception:
            self.openai_client = None
            self.openai_enabled = False
        
        self._load_memory()
    
    def _load_memory(self):
        """메모리 파일에서 데이터 로드"""
        if os.path.exists(self.memory_file_path):
            try:
                with open(self.memory_file_path, 'r', encoding='utf-8') as f:
                    self.memory_data = json.load(f)
            except Exception as e:
                print(f"메모리 파일 로드 실패: {e}")
                self.memory_data = {
                    "user_memories": {},
                    "global_patterns": {}
                }
    
    def _save_memory(self):
        """메모리 데이터를 파일에 저장"""
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
                - summary_updated (bool): 요약 업데이트 여부
                - message (str): 결과 메시지
                'summary': str,
                'memory_updated': bool,
                'message': str
            }
        """
        user_id_str = str(user_id)
        
        # 사용자별 메모리 초기화
        if user_id_str not in self.memory_data["user_memories"]:
            self.memory_data["user_memories"][user_id_str] = {
                "conversation_history": [],
                "card_interpretation_patterns": {},
                "context_patterns": {},
                "summary": ""
            }
        
        # 대화 기록 추가
        conversation_entry = {
            "timestamp": datetime.now().isoformat(),
            "cards": cards,
            "context": context,
            "interpretations": interpretations,
            "selected_interpretation": selected_interpretation,
            "user_correction": user_correction
        }
        
        self.memory_data["user_memories"][user_id_str]["conversation_history"].append(conversation_entry)
        
        # 카드-해석 패턴 업데이트
        self._update_card_patterns(user_id_str, cards, selected_interpretation or user_correction)
        
        # 컨텍스트 패턴 업데이트
        self._update_context_patterns(user_id_str, context, cards)
        
        # 요약 생성 또는 업데이트
        summary_result = self._generate_or_update_summary(user_id_str)
        
        # 메모리 저장
        self._save_memory()
        
        return {
            'status': 'success',
            'summary': summary_result['summary'],
            'memory_updated': True,
            'message': f'사용자 {user_id}의 대화 메모리가 업데이트되었습니다.'
        }
    
    def _update_card_patterns(self, user_id_str: str, cards: List[str], final_interpretation: Optional[str]):
        """카드 조합과 해석 간의 패턴 업데이트"""
        if not final_interpretation:
            return
            
        user_memory = self.memory_data["user_memories"][user_id_str]
        patterns = user_memory["card_interpretation_patterns"]
        
        # 카드 조합을 키로 사용
        card_key = ",".join(sorted(cards))
        
        if card_key not in patterns:
            patterns[card_key] = {
                "cards": cards,
                "interpretations": [],
                "frequency": 0
            }
        
        patterns[card_key]["interpretations"].append(final_interpretation)
        patterns[card_key]["frequency"] += 1
    
    def _update_context_patterns(self, user_id_str: str, context: Dict[str, Any], cards: List[str]):
        """컨텍스트와 카드 사용 패턴 업데이트"""
        user_memory = self.memory_data["user_memories"][user_id_str]
        patterns = user_memory["context_patterns"]
        
        # 컨텍스트 키 생성
        context_key = f"{context.get('place', '')}-{context.get('current_activity', '')}"
        
        if context_key not in patterns:
            patterns[context_key] = {
                "context": context,
                "used_cards": [],
                "frequency": 0
            }
        
        patterns[context_key]["used_cards"].extend(cards)
        patterns[context_key]["frequency"] += 1
    
    def _generate_or_update_summary(self, user_id_str: str) -> Dict[str, Any]:
        """사용자의 대화 기록을 LangChain ConversationSummaryMemory로 요약"""
        user_memory = self.memory_data["user_memories"][user_id_str]
        conversation_history = user_memory["conversation_history"]
        
        if len(conversation_history) == 0:
            user_memory["summary"] = "아직 대화 기록이 없습니다."
            return {"summary": "아직 대화 기록이 없습니다."}
        
        # LangChain ConversationSummaryMemory 사용
        if self.langchain_enabled and self.llm:
            try:
                # LangChain ConversationSummaryMemory 생성
                langchain_memory = LangChainConversationSummaryMemory(
                    llm=self.llm,
                    return_messages=False
                )
                
                # 대화 기록을 LangChain 메시지 형태로 변환
                messages = []
                for conv in conversation_history[-10:]:  # 최근 10개 대화만
                    cards_str = ", ".join(conv["cards"])
                    context_str = f"{conv['context'].get('place', '?')}에서 {conv['context'].get('current_activity', '?')} 중"
                    selected = conv.get("selected_interpretation") or conv.get("user_correction") or "선택되지 않음"
                    
                    # 사용자 메시지 (카드 선택)
                    user_msg = f"상황: {context_str}, 선택한 카드: {cards_str}"
                    messages.append(HumanMessage(content=user_msg))
                    
                    # AI 메시지 (해석 결과)
                    ai_msg = f"해석 결과: {', '.join(conv['interpretations'][:2])}. 최종 선택: {selected}"
                    messages.append(AIMessage(content=ai_msg))
                
                # 기존 요약이 있으면 반영
                existing_summary = user_memory.get("summary", "")
                if existing_summary and existing_summary != "아직 대화 기록이 없습니다.":
                    langchain_memory.buffer = existing_summary
                
                # 새로운 대화들을 메모리에 추가하고 요약 생성
                for i in range(0, len(messages), 2):
                    if i + 1 < len(messages):
                        langchain_memory.save_context(
                            {"input": messages[i].content},
                            {"output": messages[i + 1].content}
                        )
                
                # 생성된 요약 가져오기
                new_summary = langchain_memory.buffer
                user_memory["summary"] = new_summary
                
                return {"summary": new_summary}
                
            except Exception as e:
                print(f"LangChain 요약 생성 실패: {e}")
                return self._fallback_openai_summary(user_memory, conversation_history)
        
        return self._fallback_openai_summary(user_memory, conversation_history)
    
    def _fallback_openai_summary(self, user_memory: Dict, conversation_history: List[Dict]) -> Dict[str, Any]:
        """LangChain 실패 시 OpenAI client로 요약 생성"""
        if not self.openai_enabled:
            raise RuntimeError("대화 메모리 생성 실패: OpenAI API가 필요합니다. 환경변수 OPENAI_API_KEY를 확인하세요.")
        
        try:
            recent_conversations = conversation_history[-10:]
            existing_summary = user_memory.get("summary", "")
            
            prompt = self._create_summary_prompt(recent_conversations, existing_summary)
            
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system", 
                        "content": "당신은 AAC 사용자의 대화 패턴을 분석하고 요약하는 전문가입니다."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            new_summary = response.choices[0].message.content.strip()
            user_memory["summary"] = new_summary
            
            return {"summary": new_summary}
            
        except Exception as e:
            raise RuntimeError(f"대화 메모리 생성 실패: {str(e)}")
    
    def _create_summary_prompt(self, conversations: List[Dict], existing_summary: str) -> str:
        """요약 생성을 위한 프롬프트 작성"""
        prompt = f"""
다음은 AAC 사용자의 최근 대화 기록입니다:

기존 요약:
{existing_summary if existing_summary else "없음"}

최근 대화 기록:
"""
        
        for i, conv in enumerate(conversations, 1):
            cards_str = ", ".join(conv["cards"])
            context_str = f"{conv['context'].get('place', '?')}에서 {conv['context'].get('current_activity', '?')} 중"
            selected = conv.get("selected_interpretation") or conv.get("user_correction") or "선택되지 않음"
            
            prompt += f"""
대화 {i}:
- 카드: {cards_str}
- 상황: {context_str}
- 최종 해석: {selected}
"""

        prompt += """
위 정보를 바탕으로 다음 내용을 포함하여 사용자의 AAC 사용 패턴을 요약해주세요:

1. 자주 사용하는 카드들과 그 맥락
2. 선호하는 해석 스타일이나 패턴
3. 특정 상황에서의 의사소통 특징
4. 시간에 따른 변화나 학습 패턴

요약은 200자 이내로 간결하게 작성해주세요.
"""
        
        return prompt
    
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
                - patterns_count (int): 학습된 패턴 수
        """
        user_id_str = str(user_id)
        
        if user_id_str not in self.memory_data["user_memories"]:
            return {
                'status': 'success',
                'summary': '아직 대화 기록이 없습니다.',
                'conversation_count': 0,
                'patterns_count': 0
            }
        
        user_memory = self.memory_data["user_memories"][user_id_str]
        
        return {
            'status': 'success',
            'summary': user_memory.get("summary", "요약이 생성되지 않았습니다."),
            'conversation_count': len(user_memory["conversation_history"]),
            'patterns_count': len(user_memory["card_interpretation_patterns"])
        }
    
    def get_card_usage_patterns(self, user_id: int, card_combination: List[str]) -> Dict[str, Any]:
        """특정 카드 조합의 과거 사용 패턴 조회.
        
        사용자가 해당 카드 조합을 과거에 어떤 의미로 사용했는지 패턴을 조회하여
        카드 해석 시 참고할 수 있도록 합니다.
        
        Args:
            user_id: 사용자 ID
            card_combination: 조회할 카드 파일명 리스트
            
        Returns:
            Dict containing:
                - status (str): 'success'
                - patterns (List[str]): 과거 해석 패턴들
                - frequency (int): 사용 빈도 (있는 경우)
                - suggestions (List[str]): 최근 3개 해석 제안
        """
        user_id_str = str(user_id)
        
        if user_id_str not in self.memory_data["user_memories"]:
            return {
                'status': 'success',
                'patterns': [],
                'suggestions': []
            }
        
        patterns = self.memory_data["user_memories"][user_id_str]["card_interpretation_patterns"]
        card_key = ",".join(sorted(card_combination))
        
        if card_key in patterns:
            pattern_data = patterns[card_key]
            return {
                'status': 'success',
                'patterns': pattern_data["interpretations"],
                'frequency': pattern_data["frequency"],
                'suggestions': pattern_data["interpretations"][-3:]  # 최근 3개 해석
            }
        
        return {
            'status': 'success',
            'patterns': [],
            'suggestions': []
        }
    
