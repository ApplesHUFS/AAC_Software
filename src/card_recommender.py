from typing import Dict, List, Optional, Any
import json
import numpy as np
import random
from pathlib import Path

class CardRecommender:
    """페르소나 기반 카드 추천 시스템"""

    def __init__(self, 
                 cluster_tags_path: Optional[str] = None,
                 embeddings_path: Optional[str] = None,
                 clustering_results_path: Optional[str] = None):
        # 설정과 데이터를 로드하여 내부 변수 초기화
        self.cluster_tags = {}          # 클러스터 ID별 태그 리스트
        self.embeddings = None          # 카드 임베딩 배열 (np.ndarray)
        self.clustered_files = {}       # 클러스터 ID별 카드 파일 리스트
        self.filename_to_idx = {}       # 카드 파일명 -> 임베딩 인덱스 매핑
        
        # 클러스터 태그 읽기
        if cluster_tags_path and Path(cluster_tags_path).exists():
            with open(cluster_tags_path, 'r', encoding='utf-8') as f:
                cluster_tags_raw = json.load(f)
            self.cluster_tags = {int(k): v for k, v in cluster_tags_raw.items()}
        
        # 임베딩 및 클러스터링 결과 읽기
        if embeddings_path and Path(embeddings_path).exists():
            with open(embeddings_path, 'r', encoding='utf-8') as f:
                embed_data = json.load(f)
            self.filenames = embed_data['filenames']
            img_embs = np.array(embed_data['image_embeddings'])
            txt_embs = np.array(embed_data['text_embeddings'])
            self.embeddings = (img_embs + txt_embs) / 2
            # 정규화
            norms = np.linalg.norm(self.embeddings, axis=1, keepdims=True) + 1e-12
            self.embeddings = self.embeddings / norms
            self.filename_to_idx = {fn: i for i, fn in enumerate(self.filenames)}
        
        if clustering_results_path and Path(clustering_results_path).exists():
            with open(clustering_results_path, 'r', encoding='utf-8') as f:
                cluster_data = json.load(f)
            self.clustered_files = {int(k): v for k, v in cluster_data['clustered_files'].items()}

    def recommend_cards(self, persona: Dict[str, Any], num_cards: int = 4) -> Dict[str, Any]:
        """
        사용자 페르소나 기반으로 카드 추천 생성
        
        전략 요약:
        - 선호 클러스터 기반 초기 카드 선택
        - 클러스터 간 유사도 이용해 다양성 확보 (비슷한/서로 다른 클러스터 혼합)
        - 추천 카드 간 중복 최소화, 카드 사용 빈도에 따른 가중치 부여
        - 반환되는 카드 수는 요청에 준함 (1-4장)
        """
        if not self.cluster_tags or not self.clustered_files:
            return {
                'status': 'error',
                'cards': [],
                'clusters_used': [],
                'message': '클러스터 태그 또는 클러스터링 데이터가 없습니다.'
            }
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

        # 1) 기본 클러스터에서 카드 샘플링
        if preferred_clusters:
            base_cluster = random.choice(preferred_clusters)
        else:
            base_cluster = random.choice(list(self.clustered_files.keys()))
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

    def get_cluster_info(self, cluster_id: int) -> Dict[str, Any]:
        """
        특정 클러스터 정보 조회 (태그, 포함 파일수, 대표태그 등 간략 정보)
        """
        if cluster_id not in self.clustered_files:
            return {
                'status': 'error',
                'cluster_info': None,
                'message': f'클러스터 ID {cluster_id} 없음'
            }
        files = self.clustered_files[cluster_id]
        tags = self.cluster_tags.get(cluster_id, [])
        info = {
            'cluster_id': cluster_id,
            'num_files': len(files),
            'tags': tags,
            'sample_files': files[:5]
        }
        return {
            'status': 'success',
            'cluster_info': info,
            'message': '클러스터 정보 조회 성공'
        }

    def get_all_clusters_info(self) -> Dict[str, Any]:
        """
        전체 클러스터들의 기본 정보 리스트 반환
        """
        clusters_list = []
        for cid, files in self.clustered_files.items():
            tags = self.cluster_tags.get(cid, [])
            clusters_list.append({
                'cluster_id': cid,
                'num_files': len(files),
                'tags': tags,
                'sample_files': files[:5]
            })
        return {
            'status': 'success',
            'clusters': clusters_list,
            'total_count': len(clusters_list)
        }
