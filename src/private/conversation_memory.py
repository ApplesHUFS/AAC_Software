import json
import os
import base64
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path
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
        
        # 이미지 폴더 경로 설정
        self.images_folder = Path(self.config.get('images_folder', 'dataset/images'))
        
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
            # OpenAI 클라이언트 (이미지 분석용)
            self.openai_client = OpenAI()
        except Exception as e:
            raise RuntimeError(f"OpenAI 클라이언트 초기화 실패: {str(e)}. 환경변수 OPENAI_API_KEY를 확인하세요.")
        
        self._load_memory()
    
    def _load_memory(self):
        """메모리 파일에서 데이터 로드"""
        if os.path.exists(self.memory_file_path):
            try:
                with open(self.memory_file_path, 'r', encoding='utf-8') as f:
                    self.memory_data = json.load(f)
            except Exception as e:
                print(f"메모리 파일 로드 실패: {e}")
                self.memory_data = {"user_memories": {}}
    
    def _save_memory(self):
        """메모리 데이터를 파일에 저장"""
        try:
            os.makedirs(os.path.dirname(self.memory_file_path), exist_ok=True)
            with open(self.memory_file_path, 'w', encoding='utf-8') as f:
                json.dump(self.memory_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"메모리 파일 저장 실패: {e}")
    
    def _encode_image(self, image_path: Path) -> str:
        """이미지를 base64로 인코딩"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    def _analyze_card_interpretation_connection(self, 
                                              cards: List[str], 
                                              context: Dict[str, Any],
                                              final_interpretation: str) -> str:
        """카드 이미지와 해석의 연결성을 분석하여 요약 생성.
        
        Args:
            cards: 선택된 카드 파일명 리스트
            context: 상황 정보
            final_interpretation: 최종 선택된 해석
            
        Returns:
            str: 분석된 연결성 요약
        """
        try:
            # 이미지 콘텐츠 준비
            content = [{
                "type": "text",
                "text": f"""다음 AAC 카드 이미지들을 보고, 주어진 상황에서 어떤 시각적 특징이 최종 해석으로 연결되었는지 분석해주세요.

상황 정보:
- 시간: {context.get('time', '알 수 없음')}
- 장소: {context.get('place', '알 수 없음')}
- 대화 상대: {context.get('interaction_partner', '알 수 없음')}
- 현재 활동: {context.get('current_activity', '알 수 없음')}

최종 해석: {final_interpretation}

이미지들:"""
            }]
            
            # 각 카드 이미지 추가
            for i, card_filename in enumerate(cards, 1):
                image_path = self.images_folder / card_filename
                
                if image_path.exists():
                    base64_image = self._encode_image(image_path)
                    content.extend([
                        {"type": "text", "text": f"\n카드 {i}:"},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{base64_image}",
                                "detail": "low"
                            }
                        }
                    ])
                else:
                    content.append({
                        "type": "text", 
                        "text": f"\n카드 {i}: {card_filename} (이미지 파일 없음)"
                    })
            
            content.append({
                "type": "text",
                "text": "\n위 이미지들의 어떤 시각적 요소(객체, 색깔, 행동, 표정 등)가 최종 해석으로 연결되었는지 50자 이내로 분석해주세요."
            })
            
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": content}],
                temperature=0.3,
                max_tokens=100
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"이미지-해석 연결성 분석 실패: {e}")
            # 간단한 fallback
            card_names = [card.replace('.png', '').replace('_', ' ') for card in cards]
            return f"카드 '{', '.join(card_names[:2])}'의 시각적 특징을 통해 '{final_interpretation[:20]}...' 의미 전달"
    
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
        connection_analysis = self._analyze_card_interpretation_connection(cards, context, final_interpretation)
        
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
        """LangChain ConversationSummaryMemory를 사용하여 요약 업데이트"""
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