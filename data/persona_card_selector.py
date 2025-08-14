import json
import numpy as np
import random
from typing import List, Dict, Any, Optional, Set, Tuple
from pathlib import Path
from collections import defaultdict
from tqdm import tqdm


class PersonaCardSelector:
    def __init__(self, embeddings_path: str, clustering_results_path: str,
                 cluster_tags_path: str, config: Optional[Dict] = None):
        self.config = config or {}
        self._load_data(embeddings_path, clustering_results_path, cluster_tags_path)
        self._initialize_tracking()

    def _load_data(self, embeddings_path: str, clustering_results_path: str,
                   cluster_tags_path: str) -> None:
        with open(embeddings_path, 'r', encoding='utf-8') as f:
            embedding_data = json.load(f)

        with open(clustering_results_path, 'r', encoding='utf-8') as f:
            cluster_data = json.load(f)

        with open(cluster_tags_path, 'r', encoding='utf-8') as f:
            self.cluster_tags = {int(k): v for k, v in json.load(f).items()}

        self.filenames = embedding_data['filenames']
        img_embeddings = np.array(embedding_data['image_embeddings'])
        txt_embeddings = np.array(embedding_data['text_embeddings'])
        self.embeddings = (img_embeddings + txt_embeddings) / 2

        norms = np.linalg.norm(self.embeddings, axis=1, keepdims=True) + 1e-12
        self.embeddings = self.embeddings / norms

        self.clustered_files = {int(k): v for k, v in cluster_data['clustered_files'].items()}
        self.filename_to_idx = {fn: i for i, fn in enumerate(self.filenames)}
        self.centroids = self._compute_centroids()

    def _compute_centroids(self) -> Dict[int, np.ndarray]:
        centroids = {}
        for cluster_id, files in tqdm(self.clustered_files.items(), desc="Computing centroids"):
            indices = [self.filename_to_idx[f] for f in files if f in self.filename_to_idx]
            if indices:
                centroid = self.embeddings[indices].mean(axis=0)
                centroids[cluster_id] = centroid / (np.linalg.norm(centroid) + 1e-12)
        return centroids

    def _initialize_tracking(self) -> None:
        self.card_usage_count = {fn: 0 for fn in self.filenames}
        self.cluster_usage_count = {i: 0 for i in self.clustered_files.keys()}

    def _get_complexity_range(self, complexity: str) -> tuple:
        complexity_mapping = {
            'simple': (1, 2),
            'moderate': (1, 3),
            'complex': (2, 4)
        }
        return complexity_mapping.get(complexity, (1, 3))

    def _extract_keyword(self, filename: str) -> str:
        stem = Path(filename).stem
        return stem.split('_', 1)[1].lower() if '_' in stem else ""

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

        similarity_threshold = self.config.get('similarity_threshold', 0.5)
        similar_clusters = similarities[:3]
        dissimilar_clusters = [(cid, sim) for cid, sim in similarities if sim < similarity_threshold]

        return similar_clusters, dissimilar_clusters

    def _find_topic_related_cards(self, interesting_topics: List[str],
                                 cluster_ids: List[int]) -> List[str]:
        related_cards = []
        interesting_topics_lower = [topic.lower() for topic in interesting_topics]

        for cluster_id in cluster_ids:
            if cluster_id not in self.clustered_files:
                continue

            for filename in self.clustered_files[cluster_id]:
                keyword = self._extract_keyword(filename)
                if any(topic in keyword or keyword in topic
                      for topic in interesting_topics_lower):
                    related_cards.append(filename)

        return related_cards

    def _select_weighted_card(self, candidates: List[str]) -> str:
        if not candidates:
            return random.choice(self.filenames)

        usage_counts = [self.card_usage_count[card] for card in candidates]
        min_usage = min(usage_counts)

        weights = []
        for count in usage_counts:
            if count == min_usage:
                weights.append(10.0)
            elif count == min_usage + 1:
                weights.append(5.0)
            else:
                weights.append(1.0 / (1.0 + (count - min_usage)))

        weights_array = np.array(weights) / np.sum(weights)
        selected_idx = np.random.choice(len(candidates), p=weights_array)
        return candidates[selected_idx]

    def _compute_similarity_batch(self, candidate_indices: List[int], selected_indices: List[int]) -> np.ndarray:
        if not selected_indices:
            return np.zeros(len(candidate_indices))

        candidate_embeddings = self.embeddings[candidate_indices]
        selected_embeddings = self.embeddings[selected_indices]

        similarities = np.dot(candidate_embeddings, selected_embeddings.T)
        return similarities.mean(axis=1)

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
                selected_idx = self._select_weighted_card([self.filenames[idx] for idx in remaining_indices])
                results.append(selected_idx)
                selected_file_idx = self.filename_to_idx[selected_idx]
                remaining_indices.remove(selected_file_idx)
            return results

        candidate_indices = [self.filename_to_idx[f] for f in available_files if f in self.filename_to_idx]
        selected_indices = [self.filename_to_idx[f] for f in selected_cards if f in self.filename_to_idx]

        if not candidate_indices or not selected_indices:
            return []

        similarities = self._compute_similarity_batch(candidate_indices, selected_indices)

        card_similarities = list(zip(available_files, similarities))

        if prefer_similar:
            card_similarities.sort(key=lambda x: x[1], reverse=True)
            top_k = min(len(card_similarities), max(3, len(card_similarities) // 2))
            candidates = [card for card, _ in card_similarities[:top_k]]
        else:
            card_min_similarity = self.config.get('card_min_similarity', 0.3)
            filtered = [(card, sim) for card, sim in card_similarities if sim >= card_min_similarity]
            if not filtered:
                filtered = card_similarities
            candidates = [card for card, _ in filtered]

        actual_count = min(count, len(candidates))
        if actual_count == 0:
            return []

        results = []
        remaining_candidates = candidates.copy()
        for _ in range(min(actual_count, len(remaining_candidates))):
            if not remaining_candidates:
                break
            selected_card = self._select_weighted_card(remaining_candidates)
            results.append(selected_card)
            remaining_candidates.remove(selected_card)

        return results

    def generate_persona_combination(self, persona: Dict[str, Any]) -> List[str]:
        complexity = persona.get('selection_complexity', 'moderate')
        preferred_clusters = persona.get('preferred_category_types', [])

        min_cards, max_cards = self._get_complexity_range(complexity)
        n_cards = random.randint(min_cards, max_cards)

        combination = []
        used_cards = set()

        persona_preference_ratio = self.config.get('persona_preference_ratio', 0.9)
        use_persona_preference = random.random() < persona_preference_ratio

        if use_persona_preference and preferred_clusters:
            base_cluster = random.choice(preferred_clusters)
        else:
            base_cluster = random.choice(list(self.clustered_files.keys()))

        base_count = min(n_cards, max(1, min(3, n_cards)))
        if n_cards == 1:
            base_count = 1
        elif n_cards == 4:
            base_count = random.randint(1, 2)
        else:
            base_count = random.randint(1, min(3, n_cards))

        base_cards = self._sample_cards_with_similarity(
            base_cluster, [], base_count, used_cards, prefer_similar=False
        )

        for card in base_cards:
            self.card_usage_count[card] += 1
            self.cluster_usage_count[base_cluster] += 1

        combination.extend(base_cards)
        used_cards.update(base_cards)

        if len(combination) >= n_cards:
            return combination[:n_cards]

        similar_clusters, dissimilar_clusters = self._find_similar_and_dissimilar_clusters(base_cluster)

        if similar_clusters and random.random() < 0.7 and len(combination) < n_cards:
            similar_cluster, _ = random.choice(similar_clusters)
            remaining_slots = n_cards - len(combination)
            similar_count = min(random.randint(0, min(2, remaining_slots)), remaining_slots)

            if similar_count > 0:
                similar_cards = self._sample_cards_with_similarity(
                    similar_cluster, combination, similar_count, used_cards, prefer_similar=True
                )
                for card in similar_cards:
                    self.card_usage_count[card] += 1
                    self.cluster_usage_count[similar_cluster] += 1
                combination.extend(similar_cards)
                used_cards.update(similar_cards)

        if dissimilar_clusters and random.random() < 0.5 and len(combination) < n_cards:
            dissimilar_cluster, _ = random.choice(dissimilar_clusters)
            remaining_slots = n_cards - len(combination)
            dissimilar_count = min(1, remaining_slots)

            if dissimilar_count > 0:
                dissimilar_cards = self._sample_cards_with_similarity(
                    dissimilar_cluster, combination, dissimilar_count, used_cards, prefer_similar=False
                )
                for card in dissimilar_cards:
                    self.card_usage_count[card] += 1
                    self.cluster_usage_count[dissimilar_cluster] += 1
                combination.extend(dissimilar_cards)
                used_cards.update(dissimilar_cards)

        available_clusters = [cid for cid in self.clustered_files.keys()
                            if cid != base_cluster and
                            cid not in [c for c, _ in similar_clusters[:1]] and
                            cid not in [c for c, _ in dissimilar_clusters[:1]]]

        while len(combination) < n_cards and available_clusters:
            cluster = random.choice(available_clusters)
            available_clusters.remove(cluster)
            remaining_slots = n_cards - len(combination)

            extra_cards = self._sample_cards_with_similarity(
                cluster, combination, min(1, remaining_slots), used_cards, prefer_similar=False
            )
            for card in extra_cards:
                self.card_usage_count[card] += 1
                self.cluster_usage_count[cluster] += 1
            combination.extend(extra_cards)
            used_cards.update(extra_cards)

        return combination[:n_cards]

    def generate_combinations_for_personas(self, personas: List[Dict[str, Any]],
                                         samples_per_persona: int) -> List[List[str]]:
        self._initialize_tracking()
        all_combinations = []

        for persona in tqdm(personas, desc="Generating combinations for personas"):
            persona_data = persona['persona']
            for _ in range(samples_per_persona):
                combination = self.generate_persona_combination(persona_data)
                if combination:
                    all_combinations.append(combination)

        return all_combinations

    def update_dataset_with_personas(self, dataset_path: str, output_path: str,
                                    personas_path: str) -> None:
        with open(dataset_path, 'r', encoding='utf-8') as f:
            dataset = json.load(f)

        with open(personas_path, 'r', encoding='utf-8') as f:
            personas = json.load(f)

        print(f"Generating persona-based card combinations for {len(dataset)} samples...")

        for item in tqdm(dataset, desc="Updating dataset with personas"):
            item_persona = item['input']['persona']
            persona_data = None

            for p in personas:
                if (p['persona']['age'] == item_persona['age'] and
                    p['persona']['gender'] == item_persona['gender'] and
                    p['persona']['disability_type'] == item_persona['disability_type']):
                    persona_data = p['persona']
                    break

            if persona_data:
                combination = self.generate_persona_combination(persona_data)
                item['input']['AAC_card_combination'] = combination
            else:
                print(f"Warning: No matching persona found for item {item.get('id', 'unknown')}")

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(dataset, f, ensure_ascii=False, indent=2)

        print(f"Dataset updated with persona-based combinations: {output_path}")
        self._print_statistics()

    def _print_statistics(self) -> None:
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
