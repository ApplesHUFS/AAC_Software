from typing import Dict, List, Optional, Any
import json
import random
from pathlib import Path
from .cluster_similarity_calculator import ClusterSimilarityCalculator

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
        self.recommendation_history = {}  # context_id별 추천 히스토리
        self.cluster_calculator = ClusterSimilarityCalculator(
                cluster_tags_path=self.config['cluster_tags_path'],
                config=self.config
            )
        # 클러스터링 결과 로드
        if Path(clustering_results_path).exists():
            with open(clustering_results_path, 'r', encoding='utf-8') as f:
                cluster_data = json.load(f)
            self.clustered_files = {int(k): v for k, v in cluster_data['clustered_files'].items()}
            self.all_cards = cluster_data.get('filenames', [])
        else:
            raise FileNotFoundError(f'클러스터링 결과 파일이 필요합니다: {clustering_results_path}')

    def get_card_selection_interface(self, persona: Dict[str, Any], context: Dict[str, Any], context_id: str) -> Dict[str, Any]:
        """화면 표시용 카드 선택 인터페이스 데이터 생성.

        preferred_category_types의 6개 클러스터에서 추천 카드를 선택하고,
        나머지는 랜덤으로 채워서 총 20개 카드를 제공합니다.

        Args:
            persona: 사용자 페르소나 정보 중 일부 (preferred_category_types)
            context: 현재 상황 정보
            context_id: 현재 상황 정보 ID

        Returns:
            Dict containing:
                - status (str): 'success' 또는 'error'
                - interface_data (Dict): 선택 인터페이스 데이터
                - message (str): 결과 메시지
        """
        total_cards = self.config.get('display_cards_total')
        recommendation_ratio = self.config.get('recommendation_ratio')
        num_recommendations = int(total_cards * recommendation_ratio)
        num_random = total_cards - num_recommendations

        preferred_clusters = persona.get('preferred_category_types')
        current_activity=context.get('current_activity')

        # 히스토리 초기화
        if context_id not in self.recommendation_history:
            self.recommendation_history[context_id] = []

        # current_activity와 관련된 클러스터에서 추천 카드 선택
        recommended_cards = self._select_from_context_clusters(current_activity, num_recommendations)

        # preferred_category_types에서 나머지 추천 카드 선택
        prefer_cards = self._select_from_preferred_clusters(preferred_clusters, num_cards=num_random)

        # 전체 선택지 생성 (순서 섞기)
        all_selection_cards = recommended_cards + prefer_cards
        random.shuffle(all_selection_cards)

        self._add_to_recommendation_history(context_id, all_selection_cards)

        interface_data = {
            'selection_options': all_selection_cards,
            'context_info': {
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

        return {
            'status': 'success',
            'interface_data': interface_data,
            'message': f'카드 선택 인터페이스 생성 완료 (상황 관련: {len(recommended_cards)}, 선호 관련: {len(prefer_cards)})'
        }

    def _select_from_preferred_clusters(self, preferred_clusters: List[int], num_cards: int) -> List[str]:
        """선호 클러스터에서 카드를 골고루 선택.

        Args:
            preferred_clusters: 선호 클러스터 ID 리스트
            num_cards: 선택할 카드 수

        Returns:
            List[str]: 선택된 카드 파일명들
        """
        selected_cards = []
        n_clusters = self.config.get('n_clusters')

        # 각 클러스터에서 순환하면서 카드 선택
        cluster_index = 0
        cards_per_cluster = {cluster_id: 0 for cluster_id in preferred_clusters}

        while len(selected_cards) < num_cards and cluster_index < n_clusters:
            cluster_id = preferred_clusters[cluster_index % len(preferred_clusters)]
            cluster_cards = self.clustered_files.get(cluster_id)

            # 이미 선택된 카드와 중복되지 않는 카드 찾기
            available_cards = [card for card in cluster_cards if card not in selected_cards]

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
        min_cards = self.config.get('min_card_selection')
        max_cards = self.config.get('max_card_selection')

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

    def _add_to_recommendation_history(self, context_id: str, cards: List[str]) -> Dict[str, Any]:
        """카드 추천 히스토리에 추가.

        Args:
            context_id: 컨텍스트 ID
            cards: 추천된 카드 리스트

        Returns:
            Dict containing:
                - status (str): 'success'
                - page_number (int): 추가된 페이지 번호
                - total_pages (int): 총 페이지 수
        """
        from datetime import datetime

        # 추천 결과 추가
        recommendation_entry = {
            'page_number': len(self.recommendation_history[context_id]) + 1,
            'cards': cards,
            'timestamp': datetime.now().isoformat()
        }

        self.recommendation_history[context_id].append(recommendation_entry)

    def get_recommendation_history_page(self, context_id: str, page_number: int) -> Dict[str, Any]:
        """카드 추천 히스토리 특정 페이지 조회.

        Args:
            context_id: 컨텍스트 ID
            page_number: 조회할 페이지 번호 (1-based)

        Returns:
            Dict containing:
                - status (str): 'success' 또는 'error'
                - cards (List[str]): 카드 리스트
                - page_number (int): 현재 페이지 번호
                - total_pages (int): 총 페이지 수
                - timestamp (str): 생성 시간
                - message (str): 결과 메시지
        """
        if context_id not in self.recommendation_history:
            self.recommendation_history[context_id] = []

        history = self.recommendation_history[context_id]

        if not history:
            return {
                'status': 'error',
                'cards': [],
                'page_number': 0,
                'total_pages': 0,
                'timestamp': '',
                'message': f'컨텍스트 {context_id}의 추천 히스토리가 없습니다.'
            }
        
        total_pages = len(history)

        # 페이지 번호 검증
        if page_number < 1 or page_number > total_pages:
            return {
                'status': 'error',
                'cards': [],
                'page_number': 0,
                'total_pages': total_pages,
                'timestamp': '',
                'message': f'유효하지 않은 페이지 번호입니다. (1-{total_pages} 범위)'
            }

        # 페이지 정보
        page_data = history[page_number - 1]
        return {
            'status': 'success',
            'cards': page_data['cards'],
            'page_number': page_number,
            'total_pages': total_pages,
            'timestamp': page_data['timestamp'],
            'message': f'페이지 {page_number}/{total_pages}를 조회했습니다.'
        }

    def get_recommendation_history_summary(self, context_id: str) -> Dict[str, Any]:
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
        if context_id not in self.recommendation_history:
            return {
                'status': 'error',
                'total_pages': 0,
                'latest_page': 0,
                'history_summary': [],
                'message': f'컨텍스트 {context_id}의 추천 히스토리가 없습니다.'
            }

        history = self.recommendation_history[context_id]
        total_pages = len(history)

        # 페이지별 요약 정보
        history_summary = []
        for i, entry in enumerate(history):
            history_summary.append({
                'page_number': i + 1,
                'card_count': len(entry['cards']),
                'timestamp': entry['timestamp']
            })

        return {
            'status': 'success',
            'total_pages': total_pages,
            'latest_page': total_pages,
            'history_summary': history_summary,
            'message': f'컨텍스트 {context_id}의 추천 히스토리 요약 (총 {total_pages}페이지)'
        }
    
    def _select_from_context_clusters(self, current_activity: str, num_cards: int) -> List[str]:
        """
        current_activity와 유사도가 높은 클러스터에서 카드 선택

        Args:
            current_activity: 현재 활동 정보
            num_cards: 뽑을 카드 수
        
            Returns:
                List[str]: 선택된 카드 파일명들
        """
        selected_cards=[]
        if not current_activity:
            return self._select_random_cards([], num_cards)
        
        try:
            context_preferred_clusters = self.cluster_calculator.calculate_preferred_categories(
                interesting_topics=[current_activity],
                similarity_threshold=0.3,  
                max_categories=3
            )

            # 해당 클러스터들에서 카드 선택
            selected_cards = self._select_from_preferred_clusters(
                context_preferred_clusters, 
                num_cards
            )
        
        except Exception as e:
            print(f'context 기반 카드 선택 오류: {e}')
        
        return selected_cards