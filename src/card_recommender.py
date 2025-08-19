from typing import Dict, List, Optional, Any
import json
import numpy as np
import random
from pathlib import Path


class CardRecommender:
    """페르소나 기반 AAC 카드 추천 시스템.
    
    사용자의 관심 주제(interesting_topics)와 페르소나 정보를 기반으로
    개인화된 AAC 카드를 추천합니다. 클러스터링된 카드 데이터와 
    CLIP 임베딩을 활용하여 관련성 높은 카드들을 우선 추천합니다.
    
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
            num_cards: 추천할 카드 수 (기본값: 4)
            
        Returns:
            Dict containing:
                - status (str): 'success' 또는 'error'
                - recommended_cards (List[str]): 추천된 카드 파일명 리스트
                - recommendation_reasons (List[str]): 추천 이유
                - message (str): 결과 메시지
        - 추천 카드 간 중복 최소화, 카드 사용 빈도에 따른 가중치 부여
        - 반환되는 카드 수는 요청에 준함 (1-4장)
        """
        # 의도: 필수 클러스터 파일 검증 (완벽한 추천을 위해 필수)
        if not self.cluster_tags or not self.clustered_files:
            raise FileNotFoundError('클러스터 파일(cluster_tags.json, clustering_results.json)이 필요합니다. data/cluster_tagger.py와 data/clustering.py를 실행하여 생성하세요. 완벽한 시스템을 위해 필수 파일입니다.')
        interesting_topics = persona.get('interesting_topics', [])
        preferred_clusters = persona.get('preferred_category_types', [])
        complexity = persona.get('selection_complexity', 'moderate')
        min_cards, max_cards = {
            'simple': (1, 2),
            'moderate': (1, 3),
            'complex': (2, 4)
        }.get(complexity, (1, 3))
        n_cards = max(min(num_cards, max_cards), min_cards)

        selected_cards = []
        used_clusters = []
        card_usage_count = {fn: 0 for fn in self.filenames}

        def weighted_choice(cards_list):
            usages = [card_usage_count[c] for c in cards_list]
            min_usage = min(usages)
            weights = [10.0 if u == min_usage else 5.0 if u == min_usage + 1 else 1.0 / (1 + u - min_usage) for u in usages]
            total = sum(weights)
            probs = [w/total for w in weights]
            return random.choices(cards_list, probs)[0]

        # 의도: 기본 클러스터 선택 (워크플로우 3.2단계 - 페르소나 기반 맞춤 추천)
        if preferred_clusters:
            base_cluster = random.choice(preferred_clusters)  # 사용자 선호 클러스터 우선 사용
        else:
            base_cluster = random.choice(list(self.clustered_files.keys()))  # 선호도 없으면 랜덤 선택
        used_clusters.append(base_cluster)

        base_cards_pool = [f for f in self.clustered_files.get(base_cluster, []) if f in self.filename_to_idx]
        # 중복 없이 가중치 선택
        while base_cards_pool and len(selected_cards) < n_cards:
            c = weighted_choice(base_cards_pool)
            selected_cards.append(c)
            card_usage_count[c] += 1
            base_cards_pool.remove(c)

        # 2) 비슷한 클러스터에서 카드 추가(다양성 확보)
        # (간단하게 다른 클러스터 랜덤 선택)
        other_clusters = [cid for cid in self.clustered_files.keys() if cid not in used_clusters]
        random.shuffle(other_clusters)
        for cid in other_clusters:
            if len(selected_cards) >= n_cards:
                break
            card_pool = [f for f in self.clustered_files[cid] if f in self.filename_to_idx and f not in selected_cards]
            if not card_pool:
                continue
            c = weighted_choice(card_pool)
            selected_cards.append(c)
            card_usage_count[c] +=1
            used_clusters.append(cid)

        return {
            'status': 'success',
            'cards': selected_cards[:n_cards],
            'clusters_used': used_clusters,
            'message': f'{len(selected_cards[:n_cards])}개 카드 추천 완료'
        }

