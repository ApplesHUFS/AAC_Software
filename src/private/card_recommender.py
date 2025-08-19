from typing import Dict, List, Optional, Any
import json
import numpy as np
import random
from pathlib import Path


class CardRecommender:
    """페르소나 기반 AAC 카드 추천 및 선택 시스템.
    
    사용자의 관심 주제(interesting_topics)와 페르소나 정보를 기반으로
    개인화된 AAC 카드를 추천하고, 화면 표시용 카드 선택 인터페이스를 제공합니다.
    클러스터링된 카드 데이터와 CLIP 임베딩을 활용하여 관련성 높은 카드들을 우선 추천합니다.
    
    Attributes:
        cluster_tags: 클러스터 ID별 태그 리스트
        embeddings: 정규화된 카드 임베딩 배열
        clustered_files: 클러스터 ID별 카드 파일 리스트
        filename_to_idx: 카드 파일명 -> 임베딩 인덱스 매핑
    """

    def __init__(self, 
                 cluster_tags_path: Optional[str] = None,
                 embeddings_path: Optional[str] = None,
                 clustering_results_path: Optional[str] = None):
        """CardRecommender 초기화.
        
        Args:
            cluster_tags_path: 클러스터 태그 JSON 파일 경로
            embeddings_path: CLIP 임베딩 JSON 파일 경로  
            clustering_results_path: 클러스터링 결과 JSON 파일 경로
        """
        # 데이터 구조 초기화
        self.cluster_tags = {}          # 클러스터 ID별 태그 리스트
        self.embeddings = None          # 카드 임베딩 배열 (np.ndarray)
        self.clustered_files = {}       # 클러스터 ID별 카드 파일 리스트
        self.filename_to_idx = {}       # 카드 파일명 -> 임베딩 인덱스 매핑
        
        # 클러스터 태그 로드
        if cluster_tags_path and Path(cluster_tags_path).exists():
            with open(cluster_tags_path, 'r', encoding='utf-8') as f:
                cluster_tags_raw = json.load(f)
            self.cluster_tags = {int(k): v for k, v in cluster_tags_raw.items()}
        
        # 임베딩 데이터 로드 및 정규화
        if embeddings_path and Path(embeddings_path).exists():
            with open(embeddings_path, 'r', encoding='utf-8') as f:
                embed_data = json.load(f)
            self.filenames = embed_data['filenames']
            img_embs = np.array(embed_data['image_embeddings'])
            txt_embs = np.array(embed_data['text_embeddings'])
            self.embeddings = (img_embs + txt_embs) / 2
            # L2 정규화 적용
            norms = np.linalg.norm(self.embeddings, axis=1, keepdims=True) + 1e-12
            self.embeddings = self.embeddings / norms
            self.filename_to_idx = {fn: i for i, fn in enumerate(self.filenames)}
        
        # 클러스터링 결과 로드
        if clustering_results_path and Path(clustering_results_path).exists():
            with open(clustering_results_path, 'r', encoding='utf-8') as f:
                cluster_data = json.load(f)
            self.clustered_files = {int(k): v for k, v in cluster_data['clustered_files'].items()}

    def recommend_cards(self, persona: Dict[str, Any], num_cards: int = 4) -> Dict[str, Any]:
        """사용자 페르소나 기반 개인화 카드 추천.
        
        사용자의 interesting_topics를 우선 고려하여 관련 카드들을 추천하고,
        다양성 확보를 위해 여러 클러스터에서 카드를 선택합니다.
        
        Args:
            persona: 사용자 페르소나 정보 (interesting_topics 포함)
            num_cards: 추천할 카드 수
            
        Returns:
            Dict containing:
                - status (str): 'success' 또는 'error'
                - cards (List[str]): 추천된 카드 파일명 리스트
                - clusters_used (List[int]): 사용된 클러스터 ID 리스트
                - message (str): 결과 메시지
        """
        # 필수 클러스터 파일 검증
        if not self.cluster_tags or not self.clustered_files:
            raise FileNotFoundError('클러스터 파일(cluster_tags.json, clustering_results.json)이 필요합니다. data/cluster_tagger.py와 data/clustering.py를 실행하여 생성하세요.')
        
        interesting_topics = persona.get('interesting_topics', [])
        preferred_clusters = persona.get('preferred_category_types', [])
        
        # 카드 수 범위 제한 (1~30개)
        n_cards = max(1, min(num_cards, 30))

        selected_cards = []
        used_clusters = []
        card_usage_count = {fn: 0 for fn in self.filenames}

        def weighted_choice(cards_list):
            """사용 빈도 기반 가중치 선택"""
            if not cards_list:
                return None
            usages = [card_usage_count[c] for c in cards_list]
            min_usage = min(usages)
            weights = [10.0 if u == min_usage else 5.0 if u == min_usage + 1 else 1.0 / (1 + u - min_usage) for u in usages]
            total = sum(weights)
            if total == 0:
                return random.choice(cards_list)
            probs = [w/total for w in weights]
            return random.choices(cards_list, probs)[0]

        # 1) 기본 클러스터 선택 (페르소나 기반 맞춤 추천)
        if preferred_clusters:
            base_cluster = random.choice(preferred_clusters)
        else:
            base_cluster = random.choice(list(self.clustered_files.keys()))
        used_clusters.append(base_cluster)

        # 기본 클러스터에서 카드 선택
        base_cards_pool = [f for f in self.clustered_files.get(base_cluster, []) if f in self.filename_to_idx]
        while base_cards_pool and len(selected_cards) < n_cards:
            c = weighted_choice(base_cards_pool)
            if c:
                selected_cards.append(c)
                card_usage_count[c] += 1
                base_cards_pool.remove(c)

        # 2) 다른 클러스터에서 다양성 확보
        other_clusters = [cid for cid in self.clustered_files.keys() if cid not in used_clusters]
        random.shuffle(other_clusters)
        
        for cid in other_clusters:
            if len(selected_cards) >= n_cards:
                break
            card_pool = [f for f in self.clustered_files[cid] if f in self.filename_to_idx and f not in selected_cards]
            if not card_pool:
                continue
            c = weighted_choice(card_pool)
            if c:
                selected_cards.append(c)
                card_usage_count[c] += 1
                used_clusters.append(cid)

        return {
            'status': 'success',
            'cards': selected_cards[:n_cards],
            'clusters_used': used_clusters,
            'message': f'{len(selected_cards[:n_cards])}개 카드 추천 완료'
        }

    def get_card_selection_interface(self, persona: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """화면 표시용 카드 선택 인터페이스 데이터 생성.
        
        20개 카드 (추천 70% + 랜덤 30%)를 생성하여 사용자가 1-4개를 선택할 수 있도록 합니다.
        
        Args:
            persona: 사용자 페르소나 정보
            context: 현재 상황 정보
            
        Returns:
            Dict containing:
                - status (str): 'success' 또는 'error'
                - interface_data (Dict): 선택 인터페이스 데이터
                - message (str): 결과 메시지
        """
        try:
            # 화면 표시용 설정: 20개 카드 (추천 70% + 랜덤 30%)
            total_display_cards = 20
            num_recommendations = int(total_display_cards * 0.7)  # 14개
            num_random = total_display_cards - num_recommendations  # 6개
            
            # 페르소나 기반 카드 추천
            recommend_result = self.recommend_cards(persona, num_recommendations)
            
            if recommend_result['status'] != 'success':
                return {
                    'status': 'error',
                    'interface_data': {},
                    'message': f"카드 추천 실패: {recommend_result.get('message', '알 수 없는 오류')}"
                }
            
            recommended_cards = recommend_result['cards']
            
            # 랜덤 카드 추가
            random_cards = self._get_random_cards(
                exclude_cards=recommended_cards,
                num_cards=num_random
            )
            
            # 전체 선택지 생성 (순서 섞기)
            all_cards = recommended_cards + random_cards
            random.shuffle(all_cards)
            
            return {
                'status': 'success',
                'interface_data': {
                    'selection_options': all_cards,
                    'recommended_cards': recommended_cards,
                    'random_cards': random_cards,
                    'context_info': {
                        'time': context.get('time', '알 수 없음'),
                        'place': context.get('place', '알 수 없음'),
                        'interaction_partner': context.get('interaction_partner', '알 수 없음'),
                        'current_activity': context.get('current_activity', '')
                    },
                    'selection_rules': {
                        'min_cards': 1,
                        'max_cards': 4,
                        'total_options': len(all_cards)
                    }
                },
                'message': f'카드 선택 인터페이스 생성 완료 (추천: {len(recommended_cards)}, 랜덤: {len(random_cards)})'
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'interface_data': {},
                'message': f'카드 선택 인터페이스 생성 실패: {str(e)}'
            }

    def _get_random_cards(self, exclude_cards: List[str], num_cards: int) -> List[str]:
        """랜덤 카드 선택.
        
        Args:
            exclude_cards: 제외할 카드들 (이미 추천된 카드들)
            num_cards: 선택할 랜덤 카드 수
            
        Returns:
            List[str]: 선택된 랜덤 카드 파일명들
        """
        if not hasattr(self, 'filenames') or not self.filenames:
            return []
            
        available_cards = [
            card for card in self.filenames 
            if card not in exclude_cards and card in self.filename_to_idx
        ]
        
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
        # 선택 카드 수 검증 (1-4개)
        if not selected_cards:
            return {
                'status': 'error',
                'valid': False,
                'message': '최소 1개 이상의 카드를 선택해야 합니다.'
            }
        
        if len(selected_cards) > 4:
            return {
                'status': 'error',
                'valid': False,
                'message': '최대 4개까지만 선택할 수 있습니다.'
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

