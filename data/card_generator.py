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
                 config: Optional[Dict] = None):
        self.config = config or {}
        self._load_data(embeddings_path, clustering_results_path)
        self._initialize_tracking()

    def _load_data(self, embeddings_path: str, clustering_results_path: str) -> None:
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
        self.cluster_semantics = {int(k): v for k, v in cluster_data['cluster_semantics'].items()}
        self.n_clusters = cluster_data['n_clusters']

        self.filename_to_idx = {fn: i for i, fn in enumerate(self.filenames)}

    def _initialize_tracking(self) -> None:
        self.card_usage_count = {fn: 0 for fn in self.filenames}
        self.cluster_usage_count = {i: 0 for i in range(self.n_clusters)}

    def _get_complexity_card_count(self, complexity: str) -> int:
        complexity_mapping = {
            "simple": random.choice([1, 2]),
            "moderate": random.choice([2, 3]),
            "complex": random.choice([3, 4])
        }
        return complexity_mapping.get(complexity, 2)

    def _calculate_cluster_preference_scores(self, persona: Dict) -> Dict[int, float]:
        scores = {}

        for cluster_id, semantics in self.cluster_semantics.items():
            score = 0.0

            # preferred_category_type 매칭
            semantic_category = semantics['semantic_category'].lower()
            for preferred in persona['communication_characteristics']['preferred_category_type']:
                if preferred.lower() in semantic_category or semantic_category in preferred.lower():
                    score += 1.0

            # interesting_topics 매칭
            interesting_topic = persona['communication_characteristics']['interesting_topics'].lower()
            themes = [theme.lower() for theme in semantics['themes']]

            if any(interesting_topic in theme or theme in interesting_topic for theme in themes):
                score += 1.5

            if interesting_topic in semantic_category or semantic_category in interesting_topic:
                score += 1.0

            # complexity_level 매칭
            persona_complexity = persona['communication_characteristics']['selection_complexity']
            cluster_complexity = semantics['complexity_level']

            if (persona_complexity == "simple" and cluster_complexity == "basic") or \
               (persona_complexity == "moderate" and cluster_complexity == "intermediate") or \
               (persona_complexity == "complex" and cluster_complexity == "advanced"):
                score += 0.5

            scores[cluster_id] = max(score, 0.1)  # 최소 점수 보장

        return scores

    def _select_weighted_cluster(self, preference_scores: Dict[int, float], used_clusters: Set[int]) -> int:
        available_clusters = [cid for cid in preference_scores.keys() if cid not in used_clusters]

        if not available_clusters:
            available_clusters = list(preference_scores.keys())

        weights = []
        for cluster_id in available_clusters:
            preference_score = preference_scores[cluster_id]
            usage_penalty = 1.0 / (1.0 + self.cluster_usage_count[cluster_id] * 0.1)
            final_weight = preference_score * usage_penalty
            weights.append(final_weight)

        weights_array = np.array(weights)
        weights_array = weights_array / weights_array.sum()

        selected_idx = np.random.choice(len(available_clusters), p=weights_array)
        return available_clusters[selected_idx]

    def _select_cards_from_cluster(self, cluster_id: int, count: int, used_files: Set[str],
                                 selected_cards: List[str] = None) -> List[str]:
        if cluster_id not in self.clustered_files:
            return []

        available_files = [f for f in self.clustered_files[cluster_id] if f not in used_files]
        if not available_files:
            return []

        if not selected_cards:
            # 첫 번째 클러스터에서 선택
            candidate_indices = [self.filename_to_idx[f] for f in available_files if f in self.filename_to_idx]
            selected_indices = []

            for _ in range(min(count, len(candidate_indices))):
                if not candidate_indices:
                    break

                weights = [1.0 / (1.0 + self.card_usage_count[self.filenames[idx]]) for idx in candidate_indices]
                weights_array = np.array(weights) / np.sum(weights)

                selected_idx_pos = np.random.choice(len(candidate_indices), p=weights_array)
                selected_idx = candidate_indices.pop(selected_idx_pos)
                selected_indices.append(selected_idx)

            return [self.filenames[idx] for idx in selected_indices]

        else:
            # 기존 카드와의 유사도 고려
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

            # 적당한 유사도의 카드들 선택 (너무 비슷하거나 너무 다르지 않게)
            card_similarities.sort(key=lambda x: abs(x[1] - 0.3))  # 0.3 정도의 유사도 선호
            top_candidates = [card for card, _ in card_similarities[:min(10, len(card_similarities))]]

            selected = []
            for _ in range(min(count, len(top_candidates))):
                if not top_candidates:
                    break

                candidate_indices = [self.filename_to_idx[card] for card in top_candidates if card in self.filename_to_idx]
                weights = [1.0 / (1.0 + self.card_usage_count[self.filenames[idx]]) for idx in candidate_indices]

                if weights:
                    weights_array = np.array(weights) / np.sum(weights)
                    selected_idx_pos = np.random.choice(len(candidate_indices), p=weights_array)
                    selected_card = self.filenames[candidate_indices[selected_idx_pos]]
                    selected.append(selected_card)
                    top_candidates.remove(selected_card)

            return selected

    def generate_single_combination(self, persona: Dict) -> List[str]:
        target_count = self._get_complexity_card_count(
            persona['communication_characteristics']['selection_complexity']
        )

        preference_scores = self._calculate_cluster_preference_scores(persona)
        used_clusters: Set[int] = set()
        used_files: Set[str] = set()
        combination = []

        # 첫 번째 클러스터 선택 (선호도 기반)
        primary_cluster = self._select_weighted_cluster(preference_scores, used_clusters)
        used_clusters.add(primary_cluster)

        primary_count = min(target_count, random.randint(1, max(1, target_count - 1)))
        primary_cards = self._select_cards_from_cluster(primary_cluster, primary_count, used_files)

        for card in primary_cards:
            self.card_usage_count[card] += 1
            self.cluster_usage_count[primary_cluster] += 1

        combination.extend(primary_cards)
        used_files.update(primary_cards)

        # 필요한 경우 추가 클러스터에서 선택
        while len(combination) < target_count:
            remaining_count = target_count - len(combination)

            # 선호도가 높은 클러스터 우선 선택
            secondary_cluster = self._select_weighted_cluster(preference_scores, used_clusters)
            used_clusters.add(secondary_cluster)

            secondary_cards = self._select_cards_from_cluster(
                secondary_cluster, remaining_count, used_files, combination
            )

            for card in secondary_cards:
                self.card_usage_count[card] += 1
                self.cluster_usage_count[secondary_cluster] += 1

            combination.extend(secondary_cards)
            used_files.update(secondary_cards)

            if len(used_clusters) >= self.n_clusters:
                break

        return combination[:target_count]

    def generate_combinations(self, dataset: List[Dict]) -> List[List[str]]:
        combinations = []

        for item in tqdm(dataset, desc="Generating persona-based combinations"):
            persona = item['input']['persona']
            combination = self.generate_single_combination(persona)
            combinations.append(combination)

        return combinations

    def update_dataset(self, dataset_path: str, output_path: str) -> None:
        with open(dataset_path, 'r', encoding='utf-8') as f:
            dataset = json.load(f)

        self._initialize_tracking()
        combinations = self.generate_combinations(dataset)

        for item, combination in zip(dataset, combinations):
            item['input']['AAC_card_combination'] = combination

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(dataset, f, ensure_ascii=False, indent=2)

        self.print_dataset_stats(dataset)

    def print_dataset_stats(self, dataset: List[Dict]) -> None:
        combination_lengths = [len(item['input']['AAC_card_combination']) for item in dataset]

        complexity_stats = defaultdict(list)
        for item in dataset:
            complexity = item['input']['persona']['communication_characteristics']['selection_complexity']
            length = len(item['input']['AAC_card_combination'])
            complexity_stats[complexity].append(length)

        print(f"\nDataset Statistics:")
        print(f"Total samples: {len(dataset)}")
        print(f"Average cards per combination: {np.mean(combination_lengths):.2f}")

        print(f"\nComplexity-based distribution:")
        for complexity, lengths in complexity_stats.items():
            print(f"  {complexity}: avg {np.mean(lengths):.1f} cards, samples: {len(lengths)}")

        # 클러스터 사용 통계
        cluster_usage = list(self.cluster_usage_count.values())
        print(f"\nCluster usage:")
        print(f"  Average: {np.mean(cluster_usage):.1f}")
        print(f"  Min-Max: {min(cluster_usage)}-{max(cluster_usage)}")

        # 카드 사용 통계
        card_usage = list(self.card_usage_count.values())
        unused_cards = sum(1 for count in card_usage if count == 0)
        print(f"\nCard usage:")
        print(f"  Average: {np.mean(card_usage):.1f}")
        print(f"  Unused cards: {unused_cards} ({unused_cards/len(card_usage)*100:.1f}%)")
