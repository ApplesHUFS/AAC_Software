import json
import numpy as np
import random
from typing import List, Dict, Tuple
from sklearn.metrics.pairwise import cosine_similarity
from tqdm import tqdm

class AACCardCombinationGenerator:
    def __init__(self, 
                 embeddings_path: str,
                 clustering_results_path: str,
                 dataset_path: str,
                 similarity_range: Tuple[float, float] = (0.3, 0.7)):
        self.similarity_range = similarity_range
        self.dataset_path = dataset_path
        
        self.load_data(embeddings_path, clustering_results_path)
        self.calculate_centroids()
        self.precompute_similarities()
        
        self.card_usage_count = {fn: 0 for fn in self.filenames}
        self.cluster_usage_count = {i: 0 for i in range(self.n_clusters)}
        
    def load_data(self, embeddings_path: str, clustering_results_path: str):
        with open(embeddings_path, 'r', encoding='utf-8') as f:
            embedding_data = json.load(f)
            
        with open(clustering_results_path, 'r', encoding='utf-8') as f:
            cluster_data = json.load(f)
            
        self.filenames = embedding_data['filenames']
        self.embeddings = (np.array(embedding_data['image_embeddings']) + 
                          np.array(embedding_data['text_embeddings'])) / 2
        
        self.cluster_labels = np.array(cluster_data['cluster_labels'])
        self.clustered_files = {int(k): v for k, v in cluster_data['clustered_files'].items()}
        self.n_clusters = cluster_data['n_clusters']
        
        self.filename_to_idx = {fn: i for i, fn in enumerate(self.filenames)}
        
    def calculate_centroids(self):
        self.centroids = np.zeros((self.n_clusters, self.embeddings.shape[1]))
        
        for cluster_id in range(self.n_clusters):
            cluster_mask = self.cluster_labels == cluster_id
            cluster_embeddings = self.embeddings[cluster_mask]
            
            if len(cluster_embeddings) > 0:
                self.centroids[cluster_id] = np.mean(cluster_embeddings, axis=0)
                
    def precompute_similarities(self):
        print("유사도 매트릭스 계산 중...")
        self.similarity_matrix = cosine_similarity(self.embeddings)
        
    def select_initial_card(self) -> Tuple[str, int]:
        cluster_weights = []
        for i in range(self.n_clusters):
            weight = 1.0 / (1.0 + self.cluster_usage_count[i])
            cluster_weights.append(weight)
        
        cluster_weights = np.array(cluster_weights)
        cluster_weights = cluster_weights / cluster_weights.sum()
        
        cluster_id = np.random.choice(self.n_clusters, p=cluster_weights)
        
        cluster_mask = self.cluster_labels == cluster_id
        cluster_indices = np.where(cluster_mask)[0]
                
        idx = self._select_least_used_card(cluster_indices)
        
        self.card_usage_count[self.filenames[idx]] += 1
        self.cluster_usage_count[cluster_id] += 1
        
        return self.filenames[idx], idx
    
    def _select_least_used_card(self, candidate_indices) -> int:
        if isinstance(candidate_indices, np.ndarray):
            candidate_indices = candidate_indices.tolist()
        
        usage_counts = [self.card_usage_count[self.filenames[idx]] 
                       for idx in candidate_indices]
        
        min_usage = min(usage_counts)
        weights = []
        for count in usage_counts:
            if count == min_usage:
                weights.append(10.0)
            elif count == min_usage + 1:
                weights.append(5.0)
            else:
                weights.append(1.0 / (1.0 + (count - min_usage)))
        
        weights = np.array(weights)
        weights = weights / weights.sum()
        
        selected_idx = np.random.choice(len(candidate_indices), p=weights)
        return candidate_indices[selected_idx]
    
    def select_next_card(self, 
                        selected_indices: List[int],
                        similarity_range: Tuple[float, float] = None) -> Tuple[str, int]:
        if similarity_range is None:
            similarity_range = self.similarity_range
            
        last_idx = selected_indices[-1]
        
        similarities = self.similarity_matrix[last_idx]
        
        min_sim, max_sim = similarity_range
        candidates = []
        
        for i, sim in enumerate(similarities):
            if i in selected_indices:
                continue
                
            if min_sim <= sim <= max_sim:
                candidates.append(i)
        
        if not candidates:
            expanded_min = max(0, min_sim - 0.05)
            expanded_max = min(1, max_sim + 0.05)
            
            for i, sim in enumerate(similarities):
                if i in selected_indices:
                    continue
                if expanded_min <= sim <= expanded_max:
                    candidates.append(i)
                
        selected_idx = self._select_least_used_card(candidates)
        
        self.card_usage_count[self.filenames[selected_idx]] += 1
        cluster_id = self.cluster_labels[selected_idx]
        self.cluster_usage_count[cluster_id] += 1
        
        return self.filenames[selected_idx], selected_idx
    
    def generate_single_combination(self, n_cards: int) -> List[str]:
        selected_cards = []
        selected_indices = []
        
        card, idx = self.select_initial_card()
        selected_cards.append(card)
        selected_indices.append(idx)
        
        for _ in range(n_cards - 1):
            range_variation = random.uniform(-0.1, 0.1)
            adjusted_range = (
                max(0, self.similarity_range[0] + range_variation),
                min(1, self.similarity_range[1] + range_variation)
            )
            
            card, idx = self.select_next_card(selected_indices, adjusted_range)
            
            if card is None:
                break
                
            selected_cards.append(card)
            selected_indices.append(idx)
        
        return selected_cards
    
    def generate_card_combinations(self, n_samples: int = 200, reset_usage: bool = True) -> List[List[str]]:
        if reset_usage:
            self.card_usage_count = {fn: 0 for fn in self.filenames}
            self.cluster_usage_count = {i: 0 for i in range(self.n_clusters)}
        
        combinations = []
        
        card_count_distribution = [0.2, 0.4, 0.3, 0.1]
        
        for _ in tqdm(range(n_samples), desc="카드 조합 생성"):
            n_cards = np.random.choice([1, 2, 3, 4], p=card_count_distribution)
            combination = self.generate_single_combination(n_cards)
            
            if combination:
                combinations.append(combination)
        
        self._print_usage_statistics()
        
        return combinations
    
    def _print_usage_statistics(self):
        usage_values = list(self.card_usage_count.values())
        if usage_values:
            print(f"\n카드 사용 분포:")
            print(f"  평균: {np.mean(usage_values):.1f}회")
            print(f"  표준편차: {np.std(usage_values):.1f}")
            print(f"  최소: {min(usage_values)}회")
            print(f"  최대: {max(usage_values)}회")
            
            unused = sum(1 for v in usage_values if v == 0)
            print(f"  미사용 카드: {unused}개 ({unused/len(usage_values)*100:.1f}%)")
    
    def update_dataset(self, output_path: str = None):
        if output_path is None:
            output_path = self.dataset_path
            
        with open(self.dataset_path, 'r', encoding='utf-8') as f:
            dataset = json.load(f)
            
        print(f"데이터셋 업데이트 시작: {len(dataset)}개 샘플")
        
        self.card_usage_count = {fn: 0 for fn in self.filenames}
        self.cluster_usage_count = {i: 0 for i in range(self.n_clusters)}
        
        combinations = self.generate_card_combinations(len(dataset), reset_usage=False)
        
        for item, combination in zip(dataset, combinations):
            item['input']['AAC_card_combination'] = combination
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(dataset, f, ensure_ascii=False, indent=2)
            
        print(f"데이터셋 업데이트 완료: {output_path}")
        
        self.print_statistics(dataset)
    
    def print_statistics(self, dataset: List[Dict]):
        card_counts = {}
        combination_lengths = []
        similarity_scores = []
        
        for item in dataset:
            cards = item['input']['AAC_card_combination']
            combination_lengths.append(len(cards))
            
            if len(cards) > 1:
                indices = [self.filename_to_idx[card] for card in cards]
                for i in range(len(indices) - 1):
                    sim = self.similarity_matrix[indices[i], indices[i+1]]
                    similarity_scores.append(sim)
            
            for card in cards:
                card_counts[card] = card_counts.get(card, 0) + 1
        
        print("\n=== 카드 조합 통계 ===")
        print(f"평균 카드 수: {np.mean(combination_lengths):.2f}")
        print(f"카드 수 분포:")
        for i in range(1, 5):
            count = combination_lengths.count(i)
            print(f"  {i}개: {count} ({count/len(dataset)*100:.1f}%)")
        
        if similarity_scores:
            print(f"\n연속 카드 간 유사도:")
            print(f"  평균: {np.mean(similarity_scores):.3f}")
            print(f"  표준편차: {np.std(similarity_scores):.3f}")
            print(f"  최소: {np.min(similarity_scores):.3f}")
            print(f"  최대: {np.max(similarity_scores):.3f}")
        
        usage_values = list(card_counts.values())
        print(f"\n카드 사용 균등성:")
        print(f"  평균 사용: {np.mean(usage_values):.1f}회")
        print(f"  표준편차: {np.std(usage_values):.1f}")
        print(f"  최소 사용: {min(usage_values)}회")
        print(f"  최대 사용: {max(usage_values)}회")
        print(f"  변동계수: {np.std(usage_values)/np.mean(usage_values):.2f} (낮을수록 균등)")
        
        print(f"\n가장 많이 사용된 카드 Top 10:")
        sorted_cards = sorted(card_counts.items(), key=lambda x: x[1], reverse=True)
        for card, count in sorted_cards[:10]:
            word = card.split('_', 1)[-1].replace('.png', '')
            print(f"  {word}: {count}회")
            
        print(f"\n가장 적게 사용된 카드 Top 10:")
        for card, count in sorted_cards[-10:]:
            word = card.split('_', 1)[-1].replace('.png', '')
            print(f"  {word}: {count}회")
    
    def analyze_combination_diversity(self, n_samples: int = 100):
        """생성된 조합의 다양성 분석"""
        print("\n=== 조합 다양성 분석 ===")
        combinations = self.generate_card_combinations(n_samples, reset_usage=True)
        
        cluster_diversities = []
        
        for combination in tqdm(combinations, desc="다양성 분석"):
            if len(combination) > 1:
                indices = [self.filename_to_idx[card] for card in combination]
                clusters = [self.cluster_labels[idx] for idx in indices]
                unique_clusters = len(set(clusters))
                diversity = unique_clusters / len(clusters)
                cluster_diversities.append(diversity)
        
        if cluster_diversities:
            print(f"평균 클러스터 다양성: {np.mean(cluster_diversities):.3f}")
            print(f"  (1.0 = 모든 카드가 다른 클러스터)")


if __name__ == "__main__":
    generator = AACCardCombinationGenerator(
        embeddings_path="./aac_embeddings/aac_embeddings.json",
        clustering_results_path="./aac_embeddings/clustering_results.json",
        dataset_path="data/aac_dataset.json",
        similarity_range=(0.15, 0.85)
    )
    
    print("조합 다양성 테스트...")
    generator.analyze_combination_diversity(n_samples=100)
    
    print("\n데이터셋 업데이트 시작...")
    generator.update_dataset(output_path="data/aac_dataset_with_cards.json")