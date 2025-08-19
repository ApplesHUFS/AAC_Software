from typing import Dict, List, Optional, Any
import random
from .card_recommender import CardRecommender


class CardSelector:
    """카드 선택 인터페이스.
    
    추천된 카드들과 랜덤 카드들을 조합하여 사용자에게 선택 옵션을 제공합니다.
    사용자는 이 중에서 1-4개의 카드를 선택하여 의사소통할 수 있습니다.
    
    Attributes:
        card_recommender: 카드 추천 시스템
        random_pool_size: 랜덤 카드 풀 크기
    """
    
    def __init__(self, card_recommender: CardRecommender, random_pool_size: int = 20):
        """CardSelector 초기화.
        
        Args:
            card_recommender: 카드 추천 시스템 인스턴스
            random_pool_size: 랜덤 카드 풀 크기
        """
        self.card_recommender = card_recommender
        self.random_pool_size = random_pool_size
        
    def generate_selection_options(self, 
                                 persona: Dict[str, Any], 
                                 num_recommendations: int = 8,
                                 total_options: int = 12) -> Dict[str, Any]:
        """카드 선택 옵션 생성.
        
        페르소나 기반 추천 카드와 다양성을 위한 랜덤 카드를 조합하여
        사용자에게 선택 옵션을 제공합니다.
        
        Args:
            persona: 사용자 페르소나 정보
            num_recommendations: 추천 카드 개수 (기본값: 8)
            total_options: 총 선택지 개수 (기본값: 12)
            
        Returns:
            Dict containing:
                - status (str): 'success' 또는 'error'
                - selection_options (List[str]): 선택 가능한 카드들
                - recommended_cards (List[str]): 추천 카드들 (구분용)
                - random_cards (List[str]): 랜덤 카드들 (구분용)
                - message (str): 결과 메시지
        """
        try:
            # 페르소나 기반 카드 추천 요청
            recommend_result = self.card_recommender.recommend_cards(
                persona=persona, 
                num_cards=num_recommendations
            )
            
            if recommend_result['status'] != 'success':
                return {
                    'status': 'error',
                    'selection_options': [],
                    'recommended_cards': [],
                    'random_cards': [],
                    'message': f"카드 추천 실패: {recommend_result.get('message', '알 수 없는 오류')}"
                }
            
            recommended_cards = recommend_result['cards']
            
            # 랜덤 카드 추가
            num_random = total_options - len(recommended_cards)
            random_cards = self._get_random_cards(
                exclude_cards=recommended_cards,
                num_cards=num_random
            )
            
            # 전체 선택지 생성 (순서 섞기)
            all_cards = recommended_cards + random_cards
            random.shuffle(all_cards)
            
            return {
                'status': 'success',
                'selection_options': all_cards,
                'recommended_cards': recommended_cards,
                'random_cards': random_cards,
                'message': f'총 {len(all_cards)}개 카드 선택지 생성 완료 (추천: {len(recommended_cards)}, 랜덤: {len(random_cards)})'
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'selection_options': [],
                'recommended_cards': [],
                'random_cards': [],
                'message': f'카드 선택지 생성 실패: {str(e)}'
            }
    
    def _get_random_cards(self, exclude_cards: List[str], num_cards: int) -> List[str]:
        """랜덤 카드 선택"""
        if not hasattr(self.card_recommender, 'filenames'):
            return []
            
        available_cards = [
            card for card in self.card_recommender.filenames 
            if card not in exclude_cards
        ]
        
        if len(available_cards) < num_cards:
            return available_cards
            
        return random.sample(available_cards, num_cards)
    
    def validate_user_selection(self, 
                              selected_cards: List[str], 
                              available_options: List[str]) -> Dict[str, Any]:
        """
        사용자가 선택한 카드들의 유효성 검증
        
        Args:
            selected_cards: 사용자가 선택한 카드들 (1~4개)
            available_options: 선택 가능했던 카드 옵션들
            
        Returns:
            Dict[str, Any]: {
                'status': str,
                'valid': bool,
                'selected_cards': List[str],
                'message': str
            }
        """
        # 개수 검증 (1~4개)
        if not isinstance(selected_cards, list) or len(selected_cards) < 1 or len(selected_cards) > 4:
            return {
                'status': 'error',
                'valid': False,
                'selected_cards': [],
                'message': '카드는 1개에서 4개까지 선택해야 합니다.'
            }
        
        # 중복 검증
        if len(selected_cards) != len(set(selected_cards)):
            return {
                'status': 'error',
                'valid': False,
                'selected_cards': [],
                'message': '중복된 카드를 선택할 수 없습니다.'
            }
        
        # 유효한 옵션에서 선택했는지 검증
        invalid_cards = [card for card in selected_cards if card not in available_options]
        if invalid_cards:
            return {
                'status': 'error',
                'valid': False,
                'selected_cards': [],
                'message': f'유효하지 않은 카드가 선택되었습니다: {", ".join(invalid_cards)}'
            }
        
        return {
            'status': 'success',
            'valid': True,
            'selected_cards': selected_cards,
            'message': f'{len(selected_cards)}개 카드 선택이 유효합니다.'
        }
    
    def get_selection_interface_data(self, 
                                   persona: Dict[str, Any],
                                   context: Dict[str, Any]) -> Dict[str, Any]:
        """
        카드 선택 인터페이스용 데이터 생성
        
        Args:
            persona: 사용자 페르소나
            context: 현재 상황 정보
            
        Returns:
            Dict[str, Any]: {
                'status': str,
                'interface_data': {
                    'selection_options': List[str],
                    'recommended_cards': List[str],
                    'context_info': Dict[str, Any],
                    'selection_rules': Dict[str, Any]
                },
                'message': str
            }
        """
        # 기본 설정 사용 (complexity 구분 없이)
        settings = {'recommendations': 8, 'total': 12}
        
        # 선택 옵션 생성
        options_result = self.generate_selection_options(
            persona=persona,
            num_recommendations=settings['recommendations'],
            total_options=settings['total']
        )
        
        if options_result['status'] != 'success':
            return {
                'status': 'error',
                'interface_data': {},
                'message': f"인터페이스 데이터 생성 실패: {options_result['message']}"
            }
        
        return {
            'status': 'success',
            'interface_data': {
                'selection_options': options_result['selection_options'],
                'recommended_cards': options_result['recommended_cards'],
                'context_info': {
                    'time': context.get('time', '알 수 없음'),
                    'place': context.get('place', '알 수 없음'),
                    'interaction_partner': context.get('interaction_partner', '알 수 없음'),
                    'current_activity': context.get('current_activity', '')
                },
                'selection_rules': {
                    'min_cards': 1,
                    'max_cards': 4,
                    'total_options': len(options_result['selection_options'])
                }
            },
            'message': f'카드 선택 인터페이스 데이터 생성 완료'
        }