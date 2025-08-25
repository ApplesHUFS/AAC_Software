from typing import Dict, List, Optional, Any

# Public
from src.public import UserManager, ContextManager, FeedbackManager

# Private
from src.private import (
    CardRecommender,
    CardInterpreter,
    ConversationSummaryMemory,
    ClusterSimilarityCalculator
)

from src.service_config import SERVICE_CONFIG


class AACInterpreterService:
    """AAC 카드 해석 시스템의 메인 컨트롤러.

    사용자 페르소나 기반 AAC 카드 추천, 해석, 피드백 수집을 통한
    개인화된 의사소통 지원 시스템입니다.

    Attributes:
        config: 설정 딕셔너리
        user_manager: 사용자 관리 컴포넌트
        card_recommender: 카드 추천 컴포넌트
        card_interpreter: 카드 해석 컴포넌트
        feedback_manager: 피드백 관리 컴포넌트
        context_manager: 상황 정보 관리 컴포넌트
        conversation_memory: 대화 메모리 관리 컴포넌트
        cluster_calculator: 클러스터 유사도 계산기 (optional)
    """

    def __init__(self, config: Optional[Dict] = None):
        """AACInterpreterService 초기화.

        Args:
            config: 선택적 설정 딕셔너리. None이면 기본 설정 사용.
        """
        self.config = SERVICE_CONFIG

        try:
            # user 관리자 클래스
            self.user_manager = UserManager(
                users_file_path=self.config['users_file_path'],
                config=self.config
            )

            # feedback 관리자 클래스
            self.feedback_manager = FeedbackManager(
                feedback_file_path=self.config['feedback_file_path']
            )

            # context 관리자 클래스
            self.context_manager = ContextManager(config=self.config)

            # ConversationSummaryMemory 클래스
            self.conversation_memory = ConversationSummaryMemory(
                memory_file_path=self.config.get('memory_file_path'),
                config=self.config
            )

            # 카드 추천 시스템
            self.card_recommender = CardRecommender(
                clustering_results_path=str(self.config['clustering_results_path']),
                config=self.config
            )

            # 카드 해석 시스템
            self.card_interpreter = CardInterpreter(config=self.config)

            # 클러스터 유사도 계산기
            self.cluster_calculator = ClusterSimilarityCalculator(
                cluster_tags_path=self.config['cluster_tags_path'],
                config=self.config
            )
        except Exception as e:
            print(f"컴포넌트 초기화 실패: {e}")


    def register_user(self, user_id, persona: Dict[str, Any]) -> Dict[str, Any]:
        """새 사용자 등록 및 페르소나 생성.

        Args:
            persona: 사용자 페르소나 정보. 다음 필드들이 필수:
                - age (int): 사용자 나이 (1-100)
                - gender (str): 성별 ('male' 또는 'female')
                - disability_type (str): 장애 유형
                - communication_characteristics (str): 의사소통 특징
                - interesting_topics (List[str]): 관심 주제 목록
                - password (str): 사용자 비밀번호

        Returns:
            Dict containing:
                - status (str): 'success' 또는 'error'
                - user_id (int): 생성된 사용자 ID (-1 if error)
                - message (str): 결과 메시지
        """

        # interesting_topics 체크
        if 'interesting_topics' not in persona:
            return {
                'status': 'error',
                'user_id': -1,
                'message': 'interesting_topics가 필요합니다.'
            }

        # 딕셔너리 업데이트
        persona.update({
            'preferred_category_types': self._calculate_preferred_categories(persona['interesting_topics'])
        })

        return self.user_manager.create_user(user_id, persona)

    def authenticate_user(self, user_id: str, password: str) -> Dict[str, Any]:
        """사용자 인증 및 세션 정보 반환.

        Args:
            user_id: 사용자 ID
            password: 사용자 비밀번호

        Returns:
            Dict containing:
                - status (str): 'success' 또는 'error'
                - authenticated (bool): 인증 성공 여부
                - user_info (Dict): 사용자 페르소나 정보 (인증 성공시)
                - message (str): 결과 메시지
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
        """사용자 정보 조회.

        Args:
            user_id: 사용자 ID

        Returns:
            Dict containing:
                - status (str): 'success' 또는 'error'
                - user (Dict): 사용자 정보 (성공시)
                - message (str): 결과 메시지
        """
        return self.user_manager.get_user(user_id)

    def update_user_persona(self, user_id: int, persona_updates: Dict[str, Any]) -> Dict[str, Any]:
        """사용자 페르소나 업데이트 및 필요시 선호 카테고리 재계산.

        interesting_topics가 업데이트된 경우 ClusterSimilarityCalculator를 통해
        preferred_category_types를 자동으로 재계산

        Args:
            user_id: 사용자 ID
            persona_updates: 업데이트할 페르소나 필드들
                지원하는 필드:
                - name (str): 사용자 이름
                - age (int): 나이
                - gender (str): 성별
                - disability_type (str): 장애 유형
                - communication_characteristics (str): 의사소통 특징
                - interesting_topics (List[str]): 관심 주제

        Returns:
            Dict containing:
                - status (str): 'success' 또는 'error'
                - updated_fields (List[str]): 업데이트된 필드 목록
                - category_recalculated (bool): 카테고리 재계산 수행 여부
                - message (str): 결과 메시지
        """

        update_result = self.user_manager.update_user_persona(user_id, persona_updates)

        if update_result['status'] != 'success':
            update_result.pop('needs_category_recalculation', None)
            return {
                **update_result,
                'category_recalculated': False
            }

        category_recalculated = False

        # interesting_topics가 업데이트 되었고 클러스터 계산기가 사용 가능한 경우
        if update_result.get('needs_category_recalculation') and self.cluster_calculator:
            try:
                # 업데이트된 사용자 정보
                user_info = self.user_manager.get_user(user_id)
                interesting_topics = user_info['user'].get('interesting_topics')

                # 선호 카테고리 재계산
                preferred_categories = self._calculate_preferred_categories(interesting_topics)

                # 재계산된 카테고리 업데이트
                category_update_result = self.user_manager.update_preferred_categories(
                    user_id, preferred_categories
                )

                if category_update_result['status'] == 'success':
                    category_recalculated = True
                    update_result['message'] += ' 선호 카테고리가 자동으로 재계산되었습니다.'
                else:
                    update_result['message'] += f' 선호 카테고리 재계산 실패: {category_update_result["message"]}'

            except Exception as e:
                update_result['message'] += f' 선호 카테고리 재계산 중 오류 발생: {str(e)}'

        update_result.pop('needs_category_recalculation', None)

        return {
            **update_result,
            'category_recalculated': category_recalculated
        }

    def update_user_context(self, user_id: int, place: str, interaction_partner: str,
                           current_activity: str) -> Dict[str, Any]:
        """사용자 컨텍스트 업데이트.

        Args:
            user_id: 사용자 ID
            place: 장소 (직접 입력, 필수)
            interaction_partner: 대화 상대 (직접 입력, 필수)
            current_activity: 현재 활동 (직접 입력, 옵션)

        Returns:
            Dict containing:
                - status (str): 'success' 또는 'error'
                - context_id (str): 생성된 컨텍스트 ID
                - message (str): 결과 메시지
        """
        # 사용자 존재 확인
        user_info = self.user_manager.get_user(user_id)
        if user_info['status'] != 'success':
            return {
                'status': 'error',
                'context_id': '',
                'message': '사용자 정보를 찾을 수 없습니다.'
            }

        # 컨텍스트 생성
        context_result = self.context_manager.create_context(
            place=place,
            interaction_partner=interaction_partner,
            user_id=str(user_id),
            current_activity=current_activity
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
                'context_id': '',
                'message': context_result['message']
            }

    def get_card_selection_interface(self, user_id: int, context: Dict[str, Any], context_id: str) -> Dict[str, Any]:
        """카드 선택 인터페이스 데이터 생성.

        사용자의 preferred_category_types를 기반으로 추천된 카드들과 랜덤 카드들을
        조합하여 화면에 표시할 20개 카드를 생성합니다.

        Args:
            user_id: 사용자 ID
            context: 현재 상황 정보

        Returns:
            Dict containing:
                - status (str): 'success' 또는 'error'
                - interface_data (Dict): 선택 인터페이스 데이터
                    - 'selection_options': all_selection_cards,
                    - 'context_info': {
                        'time': context.get('time'),
                        'place': context.get('place'),
                        'interaction_partner': context.get('interaction_partner'),
                        'current_activity': context.get('current_activity')
                        },
                        'selection_rules': {
                            'min_cards': self.config.get('min_card_selection'),
                            'max_cards': self.config.get('max_card_selection'),
                            'total_options': len(all_selection_cards)
                        },
                        'total_pages': self.recommendation_history[context_id][-1]['page_number']
                        }
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

        # 카드 선택 인터페이스 데이터 생성
        return self.card_recommender.get_card_selection_interface(persona, context, context_id)

    def validate_card_selection(self, selected_cards: List[str], available_options: List[str]) -> Dict[str, Any]:
        """사용자 카드 선택 검증.

        Args:
            selected_cards: 선택된 카드들
            available_options: 선택 가능했던 옵션들

        Returns:
            Dict containing:
                - status (str): 'success' 또는 'error'
                - valid (bool): 유효성 여부
                - message (str): 결과 메시지
        """
        if self.card_recommender is None:
            return {
                'status': 'error',
                'valid': False,
                'message': '카드 추천 시스템이 초기화되지 않았습니다.'
            }

        return self.card_recommender.validate_card_selection(selected_cards, available_options)

    def interpret_cards(self,
                       user_id: int,
                       selected_cards: List[str],
                       context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """선택된 카드들을 해석.

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
            Dict containing:
                - status (str): 'success' 또는 'error'
                - interpretations (List[str]): 3개 해석 (성공시)
                - feedback_id (int): 피드백 ID
                - method (str): 해석 방법
                - message (str): 결과 메시지
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

        # 페르소나 정보
        user_data = user_info['user']
        persona = {
            'age': user_data.get('age'),
            'gender': user_data.get('gender'),
            'disability_type': user_data.get('disability_type'),
            'communication_characteristics': user_data.get('communication_characteristics'),
            'interesting_topics': user_data.get('interesting_topics')
        }

        # 과거 해석 요약
        conv_summary = self.conversation_memory.get_user_memory_summary(
                user_id
            )

        past_interpretation = conv_summary['summary']

        # 카드 해석 수행
        interpretation_result = self.card_interpreter.interpret_cards(
            persona=persona,
            context=context,
            cards=selected_cards,
            past_interpretation=past_interpretation
        )

        if interpretation_result['status'] == 'success':
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

    def request_partner_confirmation(self,
                                   user_id: int,
                                   cards: List[str],
                                   context: Dict[str, Any],
                                   interpretations: List[str],
                                   partner_info: Dict[str, Any]) -> Dict[str, Any]:
        """Partner에게 해석 확인 요청.

        Args:
            user_id: 사용자 ID
            cards: 선택된 카드들
            context: 상황 정보
            interpretations: 생성된 3개 해석
            partner_info: Partner 정보

        Returns:
            Dict containing 확인 요청 결과
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
        """Partner 피드백 제출 처리.

        Args:
            confirmation_id: 확인 요청 ID
            selected_interpretation_index: 선택된 해석 인덱스 (0-2)
            direct_feedback: 직접 입력 피드백

        Returns:
            Dict containing 피드백 처리 결과
        """
        feedback_result = self.feedback_manager.submit_partner_confirmation(
            confirmation_id=confirmation_id,
            selected_interpretation_index=selected_interpretation_index,
            direct_feedback=direct_feedback
        )

        if feedback_result['status'] == 'success' and self.conversation_memory:
            # Partner 피드백을 대화 메모리에 기록
            try:
                feedback_data = feedback_result['feedback_result']
                final_interpretation = (
                    feedback_data.get('selected_interpretation') or
                    feedback_data.get('direct_feedback')
                )

                if final_interpretation:
                    self.conversation_memory.add_conversation_memory(
                        user_id=feedback_data['user_id'],
                        cards=feedback_data['cards'],
                        context=feedback_data['context'],
                        interpretations=feedback_data['interpretations'],
                        selected_interpretation=feedback_data.get('selected_interpretation'),
                        user_correction=feedback_data.get('direct_feedback')
                    )
            except Exception as e:
                print(f"메모리 업데이트 실패: {e}")
                # 메모리 업데이트 실패는 전체 피드백 처리를 막지 않음

        return feedback_result

    def get_pending_partner_confirmations(self, partner_filter: Optional[str] = None) -> Dict[str, Any]:
        """대기 중인 Partner 확인 요청들 조회.

        Args:
            partner_filter: 특정 Partner로 필터링

        Returns:
            Dict containing 대기 중인 확인 요청들
        """
        return self.feedback_manager.get_pending_confirmations(partner_filter)

    def _cleanup_old_requests(self, max_age_days: int=7)-> Dict[str, Any]:
        """오래된 확인 요청들 정리.

        Args:
            max_age_days: 확인 요청을 보관할 최대 일수

        Returns:
            Dict[str, Any]: 정리 결과
        """
        return self.feedback_manager.cleanup_old_requests(max_age_days)

    def _calculate_preferred_categories(self, interesting_topics: List[str]) -> List[int]:
        """관심 주제를 기반으로 선호 클러스터 계산.

        Args:
            interesting_topics: 사용자의 관심 주제 리스트

        Returns:
            List[int]: 선호 클러스터 ID 리스트 (최대 6개)

        Raises:
            RuntimeError: 클러스터 계산기가 초기화되지 않은 경우
            Exception: 계산 과정에서 오류 발생시
        """

        similarity_threshold = self.config.get('similarity_threshold')
        required_cluster_count = self.config.get('required_cluster_count')

        return self.cluster_calculator.calculate_preferred_categories(
            interesting_topics=interesting_topics,
            similarity_threshold=similarity_threshold,
            max_categories=required_cluster_count
        )

    def get_card_recommendation_history_page(self, context_id: str, page_number: int) -> Dict[str, Any]:
        """카드 추천 히스토리 특정 페이지 조회.

        Args:
            context_id: 컨텍스트 ID
            page_number: 조회할 페이지 번호

        Returns:
            Dict containing:
                - status (str): 'success' 또는 'error'
                - cards (List[str]): 카드 리스트
                - page_number (int): 현재 페이지 번호
                - total_pages (int): 총 페이지 수
                - timestamp (str): 생성 시간
                - message (str): 결과 메시지
        """
        return self.card_recommender.get_recommendation_history_page(context_id, page_number)

    def get_card_recommendation_history_summary(self, context_id: str) -> Dict[str, Any]:
        """카드 추천 히스토리 요약 정보 조회.

        Args:
            context_id: 컨텍스트 ID

        Returns:
            Dict containing:
                - status (str): 'success' 또는 'error'
                - total_pages (int): 총 페이지 수
                - latest_page (int): 최신 페이지 번호
                - history_summary (List[Dict]): 페이지별 요약 정보
                - message (str): 결과 메시지
        """
        if self.card_recommender is None:
            return {
                'status': 'error',
                'total_pages': 0,
                'latest_page': 0,
                'history_summary': [],
                'message': '카드 추천 시스템이 초기화되지 않았습니다.'
            }

        return self.card_recommender.get_recommendation_history_summary(context_id)
