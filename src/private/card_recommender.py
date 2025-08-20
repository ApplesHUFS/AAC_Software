from typing import Dict, List, Optional, Any
import json
import random
from pathlib import Path


class CardRecommender:
    """페르소나 기반 AAC 카드 추천 시스템.
    
    사용자의 preferred_category_types(클러스터 6개)를 기반으로
    개인화된 AAC 카드를 추천하고, 화면 표시용 카드 선택 인터페이스를 제공합니다.
    
    Attributes:
        clustered_files: 클러스터 ID별 카드 파일 리스트
        all_cards: 전체 카드 리스트
        config: 설정 딕셔너리
    """

    def __init__(self, clustering_results_path: str, config: Dict[str, Any]):
        """CardRecommender 초기화.
        
        Args:
            clustering_results_path: 클러스터링 결과 JSON 파일 경로
            config: 설정 딕셔너리
        """
        self.config = config
        self.clustered_files = {}
        self.all_cards = []
        
        # 클러스터링 결과 로드
        if Path(clustering_results_path).exists():
            with open(clustering_results_path, 'r', encoding='utf-8') as f:
                cluster_data = json.load(f)
            self.clustered_files = {int(k): v for k, v in cluster_data['clustered_files'].items()}
            self.all_cards = cluster_data.get('filenames', [])
        else:
            raise FileNotFoundError(f'클러스터링 결과 파일이 필요합니다: {clustering_results_path}')

    def get_card_selection_interface(self, persona: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """화면 표시용 카드 선택 인터페이스 데이터 생성.
        
        preferred_category_types의 6개 클러스터에서 추천 카드를 선택하고,
        나머지는 랜덤으로 채워서 총 20개 카드를 제공합니다.
        
        Args:
            persona: 사용자 페르소나 정보 (preferred_category_types 포함)
            context: 현재 상황 정보
            
        Returns:
            Dict containing:
                - status (str): 'success' 또는 'error'
                - interface_data (Dict): 선택 인터페이스 데이터
                - message (str): 결과 메시지
        """
        total_cards = self.config.get('display_cards_total', 20)
        recommendation_ratio = self.config.get('recommendation_ratio', 0.7)
        num_recommendations = int(total_cards * recommendation_ratio)
        num_random = total_cards - num_recommendations
        
        preferred_clusters = persona.get('preferred_category_types', [])
        
        if not preferred_clusters:
            return {
                'status': 'error',
                'interface_data': {},
                'message': 'preferred_category_types가 설정되지 않았습니다.'
            }
        
        # 선호 클러스터에서 추천 카드 선택
        recommended_cards = self._select_from_preferred_clusters(preferred_clusters, num_recommendations)
        
        # 랜덤 카드 추가
        random_cards = self._select_random_cards(exclude_cards=recommended_cards, num_cards=num_random)
        
        # 전체 선택지 생성 (순서 섞기)
        all_selection_cards = recommended_cards + random_cards
        random.shuffle(all_selection_cards)
        
        return {
            'status': 'success',
            'interface_data': {
                'selection_options': all_selection_cards,
                'context_info': {
                    'time': context.get('time', '알 수 없음'),
                    'place': context.get('place', '알 수 없음'),
                    'interaction_partner': context.get('interaction_partner', '알 수 없음'),
                    'current_activity': context.get('current_activity', '')
                },
                'selection_rules': {
                    'min_cards': self.config.get('min_card_selection', 1),
                    'max_cards': self.config.get('max_card_selection', 4),
                    'total_options': len(all_selection_cards)
                }
            },
            'message': f'카드 선택 인터페이스 생성 완료 (추천: {len(recommended_cards)}, 랜덤: {len(random_cards)})'
        }

    def _select_from_preferred_clusters(self, preferred_clusters: List[int], num_cards: int) -> List[str]:
        """선호 클러스터에서 카드를 골고루 선택.
        
        Args:
            preferred_clusters: 선호 클러스터 ID 리스트 (6개)
            num_cards: 선택할 카드 수
            
        Returns:
            List[str]: 선택된 카드 파일명들
        """
        selected_cards = []
        
        # 각 클러스터에서 순환하면서 카드 선택
        cluster_index = 0
        cards_per_cluster = {cluster_id: 0 for cluster_id in preferred_clusters}
        
        while len(selected_cards) < num_cards and cluster_index < len(preferred_clusters) * 10:  # 무한루프 방지
            cluster_id = preferred_clusters[cluster_index % len(preferred_clusters)]
            cluster_cards = self.clustered_files.get(cluster_id, [])
            
            # 이미 선택된 카드와 중복되지 않는 카드 찾기
            available_cards = [card for card in cluster_cards if card not in selected_cards]
            
            if available_cards:
                selected_card = random.choice(available_cards)
                selected_cards.append(selected_card)
                cards_per_cluster[cluster_id] += 1
            
            cluster_index += 1
        
        return selected_cards

    def _select_random_cards(self, exclude_cards: List[str], num_cards: int) -> List[str]:
        """전체 카드에서 랜덤 선택.
        
        Args:
            exclude_cards: 제외할 카드들
            num_cards: 선택할 카드 수
            
        Returns:
            List[str]: 선택된 랜덤 카드들
        """
        available_cards = [card for card in self.all_cards if card not in exclude_cards]
        
        if len(available_cards) <= num_cards:
            return available_cards
        
        return random.sample(available_cards, num_cards)

    def validate_card_selection(self, selected_cards: List[str], available_options: List[str]) -> Dict[str, Any]:
        """사용자 카드 선택 유효성 검증.
        
        Args:
            selected_cards: 사용자가 선택한 카드들
            available_options: 선택 가능한 카드 옵션들
            
        Returns:
            Dict containing:
                - status (str): 'success' 또는 'error'
                - valid (bool): 유효성 여부
                - message (str): 결과 메시지
        """
        min_cards = self.config.get('min_card_selection', 1)
        max_cards = self.config.get('max_card_selection', 4)
        
        # 선택 카드 수 검증
        if len(selected_cards) < min_cards:
            return {
                'status': 'error',
                'valid': False,
                'message': f'최소 {min_cards}개 이상의 카드를 선택해야 합니다.'
            }
        
        if len(selected_cards) > max_cards:
            return {
                'status': 'error',
                'valid': False,
                'message': f'최대 {max_cards}개까지만 선택할 수 있습니다.'
            }
        
        # 중복 선택 검증
        if len(selected_cards) != len(set(selected_cards)):
            return {
                'status': 'error',
                'valid': False,
                'message': '중복된 카드를 선택할 수 없습니다.'
            }
        
        # 선택 가능한 옵션 내에서 선택했는지 검증
        invalid_cards = [card for card in selected_cards if card not in available_options]
        if invalid_cards:
            return {
                'status': 'error',
                'valid': False,
                'message': f'선택할 수 없는 카드입니다: {", ".join(invalid_cards)}'
            }
        
        return {
            'status': 'success',
            'valid': True,
            'message': f'{len(selected_cards)}개 카드가 성공적으로 선택되었습니다.'
        }