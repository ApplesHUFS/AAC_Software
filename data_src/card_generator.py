import json
import numpy as np
import random
from typing import List, Dict, Tuple, Optional
from sklearn.metrics.pairwise import cosine_similarity
from tqdm import tqdm
from collections import defaultdict


class CardCombinationGenerator:
    def __init__(self, 
                 embeddings_path: str,
                 clustering_results_path: str,
                 similarity_range: Tuple[float, float] = (0.15, 0.85)):
        self.similarity_range = similarity_range
        self._load_data(embeddings_path, clustering_results_path)
        self._initialize_tracking()
        
    def _load_data(self, embeddings_path: str, clustering_results_path: str):
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
        self.similarity_matrix = cosine_similarity(self.embeddings)
        
    def _initialize_tracking(self):
        self.card_usage_count = {fn: 0 for fn in self.filenames}
        self.cluster_usage_count = {i: 0 for i in range(self.n_clusters)}
        
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
    
    def _select_initial_card(self) -> Tuple[str, int]:
        cluster_weights = np.array([1.0 / (1.0 + self.cluster_usage_count[i]) 
                                   for i in range(self.n_clusters)])
        cluster_weights /= cluster_weights.sum()
        
        cluster_id = np.random.choice(self.n_clusters, p=cluster_weights)
        cluster_indices = np.where(self.cluster_labels == cluster_id)[0].tolist()
        
        idx = self._select_weighted_card(cluster_indices)
        
        self.card_usage_count[self.filenames[idx]] += 1
        self.cluster_usage_count[cluster_id] += 1
        
        return self.filenames[idx], idx
    
    def _select_next_card(self, selected_indices: List[int], 
                         similarity_range: Optional[Tuple[float, float]] = None) -> Optional[Tuple[str, int]]:
        if similarity_range is None:
            similarity_range = self.similarity_range
            
        last_idx = selected_indices[-1]
        similarities = self.similarity_matrix[last_idx]
        
        min_sim, max_sim = similarity_range
        candidates = [i for i, sim in enumerate(similarities) 
                     if i not in selected_indices and min_sim <= sim <= max_sim]
        
        if not candidates:
            expanded_min = max(0, min_sim - 0.05)
            expanded_max = min(1, max_sim + 0.05)
            candidates = [i for i, sim in enumerate(similarities) 
                         if i not in selected_indices and expanded_min <= sim <= expanded_max]
        
        if not candidates:
            return None
        
        selected_idx = self._select_weighted_card(candidates)
        
        self.card_usage_count[self.filenames[selected_idx]] += 1
        cluster_id = self.cluster_labels[selected_idx]
        self.cluster_usage_count[cluster_id] += 1
        
        return self.filenames[selected_idx], selected_idx
    
    def generate_single_combination(self, n_cards: int) -> List[str]:
        selected_cards = []
        selected_indices = []
        
        card, idx = self._select_initial_card()
        selected_cards.append(card)
        selected_indices.append(idx)
        
        for _ in range(n_cards - 1):
            range_variation = random.uniform(-0.1, 0.1)
            adjusted_range = (
                max(0, self.similarity_range[0] + range_variation),
                min(1, self.similarity_range[1] + range_variation)
            )
            
            result = self._select_next_card(selected_indices, adjusted_range)
            if result is None:
                break
                
            card, idx = result
            selected_cards.append(card)
            selected_indices.append(idx)
        
        return selected_cards
    
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
                    sim = self.similarity_matrix[indices[i], indices[i+1]]
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
    
    def analyze_diversity(self, n_samples: int = 100):
        print("\nAnalyzing combination diversity...")
        combinations = self.generate_combinations(n_samples, reset_usage=True)
        
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