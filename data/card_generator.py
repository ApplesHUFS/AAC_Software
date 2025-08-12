import json
import numpy as np
import random
from typing import List, Dict, Tuple, Optional, Set
from tqdm import tqdm
from collections import defaultdict


class CardCombinationGenerator:
    def __init__(self, 
                 embeddings_path: str,
                 clustering_results_path: str,
                 similarity_threshold: float = 0.5,
                 card_min_similarity: float = 0.3):
        self.similarity_threshold = similarity_threshold
        self.card_min_similarity = card_min_similarity
        self._load_data(embeddings_path, clustering_results_path)
        self._initialize_tracking()
        
    def _load_data(self, embeddings_path: str, clustering_results_path: str):
        with open(embeddings_path, 'r', encoding='utf-8') as f:
            embedding_data = json.load(f)
            
        with open(clustering_results_path, 'r', encoding='utf-8') as f:
            cluster_data = json.load(f)
            
        self.filenames = embedding_data['filenames']
        img_embeddings = np.array(embedding_data['image_embeddings'])
        txt_embeddings = np.array(embedding_data['text_embeddings'])
        
        self.embeddings = (img_embeddings + txt_embeddings) / 2
        norms = np.linalg.norm(self.embeddings, axis=1, keepdims=True) + 1e-12
        self.embeddings = self.embeddings / norms
        
        self.cluster_labels = np.array(cluster_data['cluster_labels'])
        self.clustered_files = {int(k): v for k, v in cluster_data['clustered_files'].items()}
        self.n_clusters = cluster_data['n_clusters']
        
        self.filename_to_idx = {fn: i for i, fn in enumerate(self.filenames)}
        self.centroids = self._compute_centroids()
        
    def _compute_centroids(self) -> Dict[int, np.ndarray]:
        centroids = {}
        for cluster_id, files in self.clustered_files.items():
            indices = [self.filename_to_idx[f] for f in files if f in self.filename_to_idx]
            if indices:
                centroid = self.embeddings[indices].mean(axis=0)
                centroids[cluster_id] = centroid / (np.linalg.norm(centroid) + 1e-12)
        return centroids
        
    def _initialize_tracking(self):
        self.card_usage_count = {fn: 0 for fn in self.filenames}
        self.cluster_usage_count = {i: 0 for i in range(self.n_clusters)}
        
    def _calculate_cluster_similarity(self, cluster1: int, cluster2: int) -> float:
        if cluster1 not in self.centroids or cluster2 not in self.centroids:
            return 0.0
        return float(np.dot(self.centroids[cluster1], self.centroids[cluster2]))
    
    def _find_similar_and_dissimilar_clusters(self, base_cluster_id: int) -> Tuple[List[Tuple[int, float]], List[Tuple[int, float]]]:
        if base_cluster_id not in self.centroids:
            return [], []
        
        base_centroid = self.centroids[base_cluster_id]
        similarities = []
        
        for cluster_id, centroid in self.centroids.items():
            if cluster_id == base_cluster_id:
                continue
            sim = float(np.dot(base_centroid, centroid))
            similarities.append((cluster_id, sim))
        
        similarities.sort(key=lambda x: x[1], reverse=True)
        similar_clusters = similarities[:3]
        dissimilar_clusters = [(cid, sim) for cid, sim in similarities if sim < self.similarity_threshold]
        
        return similar_clusters, dissimilar_clusters
    
    def _select_weighted_card(self, candidate_indices: List[int]) -> int:
        if not candidate_indices:
            return random.choice(range(len(self.filenames)))
        
        usage_counts = [self.card_usage_count[self.filenames[idx]] for idx in candidate_indices]
        min_usage = min(usage_counts)
        
        weights = []
        for count in usage_counts:
            if count == min_usage:
                weights.append(10.0)
            elif count == min_usage + 1:
                weights.append(5.0)
            else:
                weights.append(1.0 / (1.0 + (count - min_usage)))
        
        weights = np.array(weights) / np.sum(weights)
        selected_idx = np.random.choice(len(candidate_indices), p=weights)
        return candidate_indices[selected_idx]
    
    def _sample_cards_with_similarity(self, cluster_id: int, selected_cards: List[str], 
                                    count: int, used_files: Set[str],
                                    prefer_similar: bool = True) -> List[str]:
        if cluster_id not in self.clustered_files:
            return []
        
        available_files = [f for f in self.clustered_files[cluster_id] if f not in used_files]
        if not available_files:
            return []
        
        if not selected_cards:
            available_indices = [self.filename_to_idx[f] for f in available_files if f in self.filename_to_idx]
            if not available_indices:
                return []
            
            results = []
            remaining_indices = available_indices.copy()
            for _ in range(min(count, len(remaining_indices))):
                if not remaining_indices:
                    break
                selected_idx = self._select_weighted_card(remaining_indices)
                results.append(self.filenames[selected_idx])
                remaining_indices.remove(selected_idx)
            return results
        
        card_similarities = []
        for candidate in available_files:
            if candidate not in self.filename_to_idx:
                continue
                
            similarities = []
            for selected in selected_cards:
                if selected in self.filename_to_idx:
                    idx1 = self.filename_to_idx[candidate]
                    idx2 = self.filename_to_idx[selected]
                    sim = float(np.dot(self.embeddings[idx1], self.embeddings[idx2]))
                    similarities.append(sim)
            
            avg_sim = np.mean(similarities) if similarities else 0.0
            card_similarities.append((candidate, avg_sim))
        
        if prefer_similar:
            card_similarities.sort(key=lambda x: x[1], reverse=True)
            top_k = min(len(card_similarities), max(3, len(card_similarities) // 2))
            candidates = [card for card, sim in card_similarities[:top_k]]
        else:
            filtered = [(card, sim) for card, sim in card_similarities if sim >= self.card_min_similarity]
            if not filtered:
                filtered = card_similarities
            candidates = [card for card, sim in filtered]
        
        actual_count = min(count, len(candidates))
        if actual_count == 0:
            return []
        
        candidate_indices = [self.filename_to_idx[card] for card in candidates if card in self.filename_to_idx]
        if not candidate_indices:
            return []
            
        results = []
        remaining_indices = candidate_indices.copy()
        for _ in range(min(actual_count, len(remaining_indices))):
            if not remaining_indices:
                break
            selected_idx = self._select_weighted_card(remaining_indices)
            results.append(self.filenames[selected_idx])
            remaining_indices.remove(selected_idx)
            
        return results
    
    def generate_single_combination(self, n_cards: int) -> List[str]:
        if n_cards < 1:
            return []
        
        cluster_weights = np.array([1.0 / (1.0 + self.cluster_usage_count[i]) 
                                   for i in range(self.n_clusters)])
        cluster_weights /= cluster_weights.sum()
        
        base_cluster = np.random.choice(self.n_clusters, p=cluster_weights)
        used_files = set()
        combination = []
        
        # 베이스 클러스터에서 1-3장 또는 요청된 개수만큼 선택
        base_count = min(n_cards, max(1, min(3, n_cards)))
        if n_cards == 1:
            base_count = 1
        elif n_cards == 4:
            base_count = random.randint(1, 2)  # 4장 요청시 베이스에서 1-2장만
        else:
            base_count = random.randint(1, min(3, n_cards))
        
        base_cards = self._sample_cards_with_similarity(
            base_cluster, [], base_count, used_files, prefer_similar=False
        )
        
        for card in base_cards:
            self.card_usage_count[card] += 1
            self.cluster_usage_count[base_cluster] += 1
        
        combination.extend(base_cards)
        used_files.update(base_cards)
        
        if len(combination) >= n_cards:
            return combination[:n_cards]
        
        similar_clusters, dissimilar_clusters = self._find_similar_and_dissimilar_clusters(base_cluster)
        
        # 유사 클러스터에서 추가 선택
        if similar_clusters and random.random() < 0.7 and len(combination) < n_cards:
            similar_cluster, _ = random.choice(similar_clusters)
            remaining_slots = n_cards - len(combination)
            similar_count = min(random.randint(0, min(2, remaining_slots)), remaining_slots)
            
            if similar_count > 0:
                similar_cards = self._sample_cards_with_similarity(
                    similar_cluster, combination, similar_count, used_files, prefer_similar=True
                )
                for card in similar_cards:
                    self.card_usage_count[card] += 1
                    self.cluster_usage_count[similar_cluster] += 1
                combination.extend(similar_cards)
                used_files.update(similar_cards)
        
        # 비유사 클러스터에서 추가 선택
        if dissimilar_clusters and random.random() < 0.5 and len(combination) < n_cards:
            dissimilar_cluster, _ = random.choice(dissimilar_clusters)
            remaining_slots = n_cards - len(combination)
            dissimilar_count = min(1, remaining_slots)
            
            if dissimilar_count > 0:
                dissimilar_cards = self._sample_cards_with_similarity(
                    dissimilar_cluster, combination, dissimilar_count, used_files, prefer_similar=False
                )
                for card in dissimilar_cards:
                    self.card_usage_count[card] += 1
                    self.cluster_usage_count[dissimilar_cluster] += 1
                combination.extend(dissimilar_cards)
                used_files.update(dissimilar_cards)
        
        # 목표 개수에 못 미치면 다른 클러스터에서 추가 선택
        available_clusters = [cid for cid in self.clustered_files.keys() 
                            if cid != base_cluster and 
                            cid not in [c for c, _ in similar_clusters[:1]] and
                            cid not in [c for c, _ in dissimilar_clusters[:1]]]
        
        while len(combination) < n_cards and available_clusters:
            cluster = random.choice(available_clusters)
            available_clusters.remove(cluster)
            remaining_slots = n_cards - len(combination)
            
            extra_cards = self._sample_cards_with_similarity(
                cluster, combination, min(1, remaining_slots), used_files, prefer_similar=False
            )
            for card in extra_cards:
                self.card_usage_count[card] += 1
                self.cluster_usage_count[cluster] += 1
            combination.extend(extra_cards)
            used_files.update(extra_cards)
        
        return combination[:n_cards]
    
    def generate_combinations(self, n_samples: int, reset_usage: bool = True) -> List[List[str]]:
        if reset_usage:
            self._initialize_tracking()
        
        combinations = []
        card_count_distribution = [0.35, 0.35, 0.2, 0.1]
        
        for _ in tqdm(range(n_samples), desc="Generating card combinations"):
            n_cards = np.random.choice([1, 2, 3, 4], p=card_count_distribution)
            combination = self.generate_single_combination(n_cards)
            if combination:
                combinations.append(combination)
        
        self._print_usage_stats()
        return combinations
    
    def _print_usage_stats(self):
        usage_values = list(self.card_usage_count.values())
        if not usage_values:
            return
        
        print(f"\nCard usage statistics:")
        print(f"  Average: {np.mean(usage_values):.1f} times")
        print(f"  Std dev: {np.std(usage_values):.1f}")
        print(f"  Min: {min(usage_values)} times")
        print(f"  Max: {max(usage_values)} times")
        
        unused = sum(1 for v in usage_values if v == 0)
        print(f"  Unused cards: {unused} ({unused/len(usage_values)*100:.1f}%)")
    
    def update_dataset(self, dataset_path: str, output_path: str):
        with open(dataset_path, 'r', encoding='utf-8') as f:
            dataset = json.load(f)
            
        print(f"Updating dataset: {len(dataset)} samples")
        self._initialize_tracking()
        
        combinations = self.generate_combinations(len(dataset), reset_usage=False)
        
        for item, combination in zip(dataset, combinations):
            item['input']['AAC_card_combination'] = combination
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(dataset, f, ensure_ascii=False, indent=2)
            
        print(f"Dataset updated and saved to {output_path}")
        self.print_dataset_stats(dataset)
        self._analyze_diversity_from_combinations(combinations)
    
    def print_dataset_stats(self, dataset: List[Dict]):
        combination_lengths = [len(item['input']['AAC_card_combination']) for item in dataset]
        card_counts = defaultdict(int)
        similarity_scores = []
        
        for item in dataset:
            cards = item['input']['AAC_card_combination']
            for card in cards:
                card_counts[card] += 1
            
            if len(cards) > 1:
                indices = [self.filename_to_idx[card] for card in cards if card in self.filename_to_idx]
                for i in range(len(indices) - 1):
                    sim = float(np.dot(self.embeddings[indices[i]], self.embeddings[indices[i+1]]))
                    similarity_scores.append(sim)
        
        print(f"\nDataset statistics:")
        print(f"Average cards per combination: {np.mean(combination_lengths):.2f}")
        print(f"Card count distribution:")
        for i in range(1, 5):
            count = combination_lengths.count(i)
            print(f"  {i} cards: {count} ({count/len(dataset)*100:.1f}%)")
        
        if similarity_scores:
            print(f"\nSimilarity between consecutive cards:")
            print(f"  Average: {np.mean(similarity_scores):.3f}")
            print(f"  Std dev: {np.std(similarity_scores):.3f}")
        
        if card_counts:
            usage_values = list(card_counts.values())
            print(f"\nCard usage distribution:")
            print(f"  Average usage: {np.mean(usage_values):.1f} times")
            print(f"  Coefficient of variation: {np.std(usage_values)/np.mean(usage_values):.2f}")
    
    def _analyze_diversity_from_combinations(self, combinations: List[List[str]]):
        print("\nAnalyzing combination diversity...")
        
        cluster_diversities = []
        for combination in combinations:
            if len(combination) > 1:
                indices = [self.filename_to_idx[card] for card in combination if card in self.filename_to_idx]
                clusters = [self.cluster_labels[idx] for idx in indices]
                unique_clusters = len(set(clusters))
                diversity = unique_clusters / len(clusters)
                cluster_diversities.append(diversity)
        
        if cluster_diversities:
            print(f"Average cluster diversity: {np.mean(cluster_diversities):.3f}")
            print("  (1.0 = all cards from different clusters)")
    
    def analyze_diversity(self, n_samples: int = 100):
        print("\nAnalyzing combination diversity...")
        combinations = self.generate_combinations(n_samples, reset_usage=True)
        self._analyze_diversity_from_combinations(combinations)