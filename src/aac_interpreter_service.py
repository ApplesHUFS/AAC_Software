from typing import Dict, List, Optional, Any

# Public 모듈 - 외부 API 및 사용자 인터페이스
from .public import UserManager, ContextManager, FeedbackManager

# Private 모듈 - 내부 비즈니스 로직 및 데이터 처리  
from .private import (
    ConfigManager,
    CardRecommender, 
    CardInterpreter,
    ConversationSummaryMemory
)


class AACInterpreterService:
    """AAC 카드 해석 시스템의 메인 컨트롤러.
    
    사용자 페르소나 기반 AAC 카드 추천, 해석, 피드백 수집을 통한
    개인화된 의사소통 지원 시스템입니다.
    
    Attributes:
        user_manager: 사용자 관리 컴포넌트
        card_recommender: 카드 추천 및 선택 컴포넌트 (통합)
        card_interpreter: 카드 해석 컴포넌트
        feedback_manager: 피드백 관리 컴포넌트
        context_manager: 상황 정보 관리 컴포넌트
        conversation_memory: 대화 메모리 관리 컴포넌트
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """AACInterpreterService 초기화.
        
        Args:
            config: 선택적 설정 딕셔너리. None이면 기본 설정 사용.
        """
        self.config = config or {}
        self.config_manager = ConfigManager()
        
        # 각 컴포넌트 초기화
        data_paths = self.config_manager.get_data_paths()
        cluster_config = self.config_manager.get_cluster_config()
        
        self.user_manager = UserManager(data_paths['users_file_path'])
        self.feedback_manager = FeedbackManager(data_paths['feedback_file_path'])
        self.context_manager = ContextManager(config)
        self.conversation_memory = ConversationSummaryMemory(
            memory_file_path=data_paths.get('memory_file_path', 'user_data/conversation_memory.json'),
            config=config
        )
        
        # 카드 추천 및 해석 시스템
        self.card_recommender = CardRecommender(
            cluster_tags_path=str(cluster_config['cluster_tags_path']),
            embeddings_path=str(cluster_config['embeddings_path']),
            clustering_results_path=str(cluster_config['clustering_results_path'])
        )
        self.card_interpreter = CardInterpreter(config)
    
    def register_user(self, persona: Dict[str, Any]) -> Dict[str, Any]:
        """새 사용자 등록 및 페르소나 생성.
        
        Args:
            persona: 사용자 페르소나 정보. UserManager.create_user() 참조.
            
        Returns:
            Dict containing user registration result.
        """
        return self.user_manager.create_user(persona)
    
    def authenticate_user(self, user_id: int, password: str) -> Dict[str, Any]:
        """사용자 인증 및 세션 정보 반환.
        
        Args:
            user_id: 사용자 ID
            password: 사용자 비밀번호
            
        Returns:
            Dict containing:
                - status (str): 'success' 또는 'error'
                - authenticated (bool): 인증 성공 여부
                - user_info (Dict): 사용자 페르소나 정보 (인증 성공시)
                'message': str
            }
        """
        auth_result = self.user_manager.authenticate_user(user_id, password)
        
        if auth_result['authenticated']:
            user_info = self.user_manager.get_user(user_id)
            return {
                'status': 'success',
                'authenticated': True,
                'user_info': user_info.get('user'),
                'message': '인증 성공'
            }
        else:
            return {
                'status': 'error',
                'authenticated': False,
                'user_info': None,
                'message': auth_result['message']
            }
    
    def get_user_info(self, user_id: int) -> Dict[str, Any]:
        """
        사용자 정보 조회
        
        Args:
            user_id: 사용자 ID
            
        Returns:
            Dict[str, Any]: {
                'status': str,
                'user': Dict or None,
                'message': str
            }
        """
        return self.user_manager.get_user(user_id)
    
    def get_card_selection_interface(self, user_id: int, context: Dict[str, Any]) -> Dict[str, Any]:
        """카드 선택 인터페이스 데이터 생성.
        
        실제 화면에 표시할 20개 카드 (추천 70% + 랜덤 30%)를 생성합니다.
        사용자는 이 중에서 1-4개 카드를 선택할 수 있습니다.
        
        Args:
            user_id: 사용자 ID
            context: 현재 상황 정보
            
        Returns:
            Dict containing:
                - status (str): 'success' 또는 'error'
                - interface_data (Dict): 선택 인터페이스 데이터
                - message (str): 결과 메시지
        """
        # 사용자 정보 조회
        user_info = self.user_manager.get_user(user_id)
        if user_info['status'] != 'success':
            return {
                'status': 'error',
                'interface_data': {},
                'message': '사용자 정보를 찾을 수 없습니다.'
            }
        
        # 페르소나 정보 준비
        user_data = user_info['user']
        persona = {
            'interesting_topics': user_data.get('interesting_topics', []),
            'preferred_category_types': user_data.get('preferred_category_types', [])
        }
        
        # 카드 선택 인터페이스 데이터 생성 (CardRecommender로 통합)
        return self.card_recommender.get_card_selection_interface(persona, context)
    
    def validate_card_selection(self, selected_cards: List[str], available_options: List[str]) -> Dict[str, Any]:
        """사용자 카드 선택 검증.
        
        Args:
            selected_cards: 선택된 카드들
            available_options: 선택 가능했던 옵션들
            
        Returns:
            Dict containing validation result.
        """
        return self.card_recommender.validate_card_selection(selected_cards, available_options)
    
    def interpret_cards(self, 
                       user_id: int,
                       selected_cards: List[str],
                       context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        선택된 카드들을 해석 (제시된 흐름의 3.4단계)
        
        Args:
            user_id: 사용자 ID
            selected_cards: 선택된 카드 리스트 (1-4개)
            context: 상황 정보 {
                'time': str,
                'place': str,
                'interaction_partner': str,
                'current_activity': str
            }
            
        Returns:
            Dict[str, Any]: {
                'status': str,
                'interpretations': List[str],  # 3개
                'feedback_id': int,
                'method': str,  # 'online' or 'offline'
                'message': str
            }
        """
        # 사용자 정보 조회
        user_info = self.user_manager.get_user(user_id)
        if user_info['status'] != 'success':
            return {
                'status': 'error',
                'interpretations': [],
                'feedback_id': -1,
                'method': 'none',
                'message': '사용자 정보를 찾을 수 없습니다.'
            }
        
        # 컨텍스트 기본값 설정
        if context is None:
            context = {
                'time': '현재',
                'place': '알 수 없음',
                'interaction_partner': '알 수 없음',
                'current_activity': '대화'
            }
        
        # 페르소나 정보 준비
        user_data = user_info['user']
        persona = {
            'age': user_data.get('age', ''),
            'gender': user_data.get('gender', ''),
            'disability_type': user_data.get('disability_type', ''),
            'communication_characteristics': user_data.get('communication_characteristics', ''),
            'interesting_topics': user_data.get('interesting_topics', [])
        }
        
        # 과거 해석 패턴 조회 (대화 메모리에서)
        memory_patterns = self.conversation_memory.get_card_usage_patterns(user_id, selected_cards)
        past_interpretation = ""
        if memory_patterns['patterns']:
            past_interpretation = f"과거 유사한 상황에서의 해석: {', '.join(memory_patterns['patterns'][-2:])}"
        
        # 카드 해석 수행
        interpretation_result = self.card_interpreter.interpret_cards(
            persona=persona,
            context=context,
            cards=selected_cards,
            past_interpretation=past_interpretation
        )
        
        if interpretation_result['status'] in ['success', 'warning']:
            # 피드백 추적을 위해 해석 시도 기록
            feedback_result = self.feedback_manager.record_interpretation_attempt(
                user_id=user_id,
                cards=selected_cards,
                persona=persona,
                context=context,
                interpretations=interpretation_result['interpretations'],
                method=interpretation_result['method']
            )
            
            return {
                'status': interpretation_result['status'],
                'interpretations': interpretation_result['interpretations'],
                'feedback_id': feedback_result['feedback_id'],
                'method': interpretation_result['method'],
                'message': interpretation_result['message']
            }
        else:
            return {
                'status': 'error',
                'interpretations': [],
                'feedback_id': -1,
                'method': 'none',
                'message': interpretation_result['message']
            }
    
    def submit_feedback(self,
                       feedback_id: int,
                       selected_interpretation_index: Optional[int] = None,
                       user_correction: Optional[str] = None) -> Dict[str, Any]:
        """
        partner 피드백 제출 (제시된 흐름의 3.5, 3.6단계)
        
        Args:
            feedback_id: 피드백 ID
            selected_interpretation_index: 선택된 해석 인덱스 (0-2) - top-3 중 선택
            user_correction: 올바른 해석 직접 입력 - 어떤 것도 맞지 않을 때
            
        Returns:
            Dict[str, Any]: {
                'status': str,
                'message': str
            }
        """
        # 입력 유효성 검증: 둘 중 하나는 반드시 있어야 함
        if selected_interpretation_index is None and not user_correction:
            return {
                'status': 'error',
                'message': 'top-3 해석 중 선택하거나 올바른 해석을 직접 입력해야 합니다.'
            }
        
        # selected_interpretation_index 범위 검증 (0-2)
        if selected_interpretation_index is not None:
            if not (0 <= selected_interpretation_index <= 2):
                return {
                    'status': 'error',
                    'message': '해석 인덱스는 0-2 범위여야 합니다.'
                }
        
        # user_correction 유효성 검증
        if user_correction is not None:
            if not user_correction.strip():
                return {
                    'status': 'error',
                    'message': '올바른 해석을 입력해주세요.'
                }
        
        # 피드백 기록
        feedback_result = self.feedback_manager.record_user_feedback(
            feedback_id=feedback_id,
            selected_interpretation_index=selected_interpretation_index,
            user_correction=user_correction.strip() if user_correction else None
        )
        
        if feedback_result['status'] != 'success':
            return feedback_result
        
        # 해석 시도 정보 조회 (ConversationSummaryMemory에 저장하기 위해)
        try:
            # feedback_id를 통해 해석 시도 정보 찾기
            interpretation_attempt = None
            for attempt in self.feedback_manager._data["interpretations"]:
                if attempt["feedback_id"] == feedback_id:
                    interpretation_attempt = attempt
                    break
            
            if interpretation_attempt:
                user_id = interpretation_attempt["user_id"]
                cards = interpretation_attempt["cards"]
                context = interpretation_attempt["context"]
                interpretations = interpretation_attempt["interpretations"]
                
                # 최종 선택된 해석 결정
                final_interpretation = None
                if user_correction:
                    final_interpretation = user_correction
                elif selected_interpretation_index is not None and 0 <= selected_interpretation_index < len(interpretations):
                    final_interpretation = interpretations[selected_interpretation_index]
                
                # ConversationSummaryMemory에 대화 기억 추가 (제시된 흐름의 3.6단계)
                if final_interpretation:
                    memory_result = self.conversation_memory.add_conversation_memory(
                        user_id=user_id,
                        cards=cards,
                        context=context,
                        interpretations=interpretations,
                        selected_interpretation=final_interpretation if not user_correction else None,
                        user_correction=user_correction
                    )
                    
                    return {
                        'status': 'success',
                        'message': f"피드백이 기록되었으며, 대화 메모리가 업데이트되었습니다. {memory_result.get('message', '')}"
                    }
            
            return {
                'status': 'success',
                'message': '피드백이 기록되었습니다.'
            }
            
        except Exception as e:
            return {
                'status': 'warning',
                'message': f'피드백은 기록되었으나 메모리 업데이트 중 오류 발생: {str(e)}'
            }
    
    def request_partner_confirmation(self,
                                   user_id: int,
                                   cards: List[str],
                                   context: Dict[str, Any],
                                   interpretations: List[str],
                                   partner_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Partner에게 해석 확인 요청 (흐름의 3.5단계)
        
        Args:
            user_id: 사용자 ID
            cards: 선택된 카드들
            context: 상황 정보
            interpretations: 생성된 3개 해석
            partner_info: Partner 정보
            
        Returns:
            Dict[str, Any]: 확인 요청 결과
        """
        return self.feedback_manager.request_interpretation_confirmation(
            user_id=user_id,
            cards=cards,
            context=context,
            interpretations=interpretations,
            partner_info=partner_info
        )
    
    def submit_partner_feedback(self,
                              confirmation_id: str,
                              selected_interpretation_index: Optional[int] = None,
                              direct_feedback: Optional[str] = None) -> Dict[str, Any]:
        """
        Partner 피드백 제출 처리
        
        Args:
            confirmation_id: 확인 요청 ID
            selected_interpretation_index: 선택된 해석 인덱스 (0-2)
            direct_feedback: 직접 입력 피드백
            
        Returns:
            Dict[str, Any]: 피드백 처리 결과
        """
        feedback_result = self.feedback_manager.submit_partner_confirmation(
            confirmation_id=confirmation_id,
            selected_interpretation_index=selected_interpretation_index,
            direct_feedback=direct_feedback
        )
        
        if feedback_result['status'] == 'success':
            # Partner 피드백을 기존 피드백 시스템에도 기록
            feedback_data = feedback_result['feedback_result']
            final_interpretation = (
                feedback_data.get('selected_interpretation') or 
                feedback_data.get('direct_feedback')
            )
            
            if final_interpretation:
                # 대화 메모리 업데이트
                self.conversation_memory.add_conversation_memory(
                    user_id=feedback_data['user_id'],
                    cards=feedback_data['cards'],
                    context=feedback_data['context'],
                    interpretations=feedback_data['interpretations'],
                    selected_interpretation=feedback_data.get('selected_interpretation'),
                    user_correction=feedback_data.get('direct_feedback')
                )
        
        return feedback_result
    
    def get_pending_partner_confirmations(self, partner_filter: Optional[str] = None) -> Dict[str, Any]:
        """
        대기 중인 Partner 확인 요청들 조회
        
        Args:
            partner_filter: 특정 Partner로 필터링
            
        Returns:
            Dict[str, Any]: 대기 중인 확인 요청들
        """
        return self.feedback_manager.get_pending_confirmations(partner_filter)
    
    def update_user_context(self, user_id: int, place: str, interaction_partner: str, current_activity: Optional[str] = None) -> Dict[str, Any]:
        """
        사용자 컨텍스트 업데이트
        
        Args:
            user_id: 사용자 ID
            place: 장소 (직접 입력, 필수)
            interaction_partner: 대화 상대 (직접 입력, 필수) 
            current_activity: 현재 활동 (직접 입력, 옵션)
            
        Returns:
            Dict[str, Any]: {
                'status': str,
                'context_id': str,
                'message': str
            }
        """
        try:
            # 사용자 존재 확인
            user_info = self.user_manager.get_user(user_id)
            if user_info['status'] != 'success':
                return {
                    'status': 'error',
                    'context_id': '',
                    'message': '사용자 정보를 찾을 수 없습니다.'
                }
            
            # 컨텍스트 생성 (time은 자동 생성)
            context_result = self.context_manager.create_context(
                place=place,
                interaction_partner=interaction_partner,
                current_activity=current_activity,
                user_id=str(user_id)
            )
            
            if context_result['status'] == 'success':
                return {
                    'status': 'success',
                    'context_id': context_result['context_id'],
                    'message': '사용자 컨텍스트가 성공적으로 업데이트되었습니다.'
                }
            else:
                return {
                    'status': 'error',
                    'message': '컨텍스트 생성 중 오류가 발생했습니다.'
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'message': f'컨텍스트 업데이트 중 오류 발생: {str(e)}'
            }
    
    
    
