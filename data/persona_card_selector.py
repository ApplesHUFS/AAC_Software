import json
import numpy as np
import random
from typing import List, Dict, Any, Optional, Set
from pathlib import Path
from collections import defaultdict


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
        self.clustered_files = {int(k): v for k, v in cluster_data['clustered_files'].items()}
        self.filename_to_idx = {fn: i for i, fn in enumerate(self.filenames)}

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
        if '_' not in stem:
            return ""
        return stem.split('_', 1)[1].lower()

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

    def _sample_from_clusters(self, cluster_ids: List[int], count: int,
                             used_cards: Set[str],
                             persona_topics: Optional[List[str]] = None) -> List[str]:
        if not cluster_ids:
            return []

        available_cards = []
        for cluster_id in cluster_ids:
            if cluster_id in self.clustered_files:
                cluster_cards = [card for card in self.clustered_files[cluster_id]
                               if card not in used_cards]
                available_cards.extend(cluster_cards)

        if not available_cards:
            return []

        if persona_topics:
            topic_related = self._find_topic_related_cards(persona_topics, cluster_ids)
            topic_related = [card for card in topic_related if card not in used_cards]

            if topic_related:
                topic_ratio = self.config.get('persona_topic_ratio', 0.7)
                topic_count = min(int(count * topic_ratio), len(topic_related))

                selected_cards = []
                for _ in range(topic_count):
                    if not topic_related:
                        break
                    card = self._select_weighted_card(topic_related)
                    selected_cards.append(card)
                    topic_related.remove(card)
                    available_cards = [c for c in available_cards if c != card]

                remaining_count = count - len(selected_cards)
                for _ in range(remaining_count):
                    if not available_cards:
                        break
                    card = self._select_weighted_card(available_cards)
                    selected_cards.append(card)
                    available_cards.remove(card)

                return selected_cards

        selected_cards = []
        for _ in range(min(count, len(available_cards))):
            if not available_cards:
                break
            card = self._select_weighted_card(available_cards)
            selected_cards.append(card)
            available_cards.remove(card)

        return selected_cards

    def generate_persona_combination(self, persona: Dict[str, Any]) -> List[str]:
        complexity = persona.get('selection_complexity', 'moderate')
        preferred_clusters = persona.get('preferred_category_types', [])
        interesting_topics = persona.get('interesting_topics', [])

        min_cards, max_cards = self._get_complexity_range(complexity)
        n_cards = random.randint(min_cards, max_cards)

        combination = []
        used_cards = set()

        persona_preference_ratio = self.config.get('persona_preference_ratio', 0.9)
        use_persona_preference = random.random() < persona_preference_ratio

        if use_persona_preference and preferred_clusters:
            preferred_count = min(n_cards, max(1, int(n_cards * 0.8)))

            preferred_cards = self._sample_from_clusters(
                preferred_clusters, preferred_count, used_cards, interesting_topics
            )

            for card in preferred_cards:
                self.card_usage_count[card] += 1
                for cluster_id, files in self.clustered_files.items():
                    if card in files:
                        self.cluster_usage_count[cluster_id] += 1
                        break

            combination.extend(preferred_cards)
            used_cards.update(preferred_cards)

        remaining_count = n_cards - len(combination)
        if remaining_count > 0:
            all_clusters = list(self.clustered_files.keys())
            available_clusters = [cid for cid in all_clusters if cid not in preferred_clusters]

            if not available_clusters:
                available_clusters = all_clusters

            other_cards = self._sample_from_clusters(
                available_clusters, remaining_count, used_cards
            )

            for card in other_cards:
                self.card_usage_count[card] += 1
                for cluster_id, files in self.clustered_files.items():
                    if card in files:
                        self.cluster_usage_count[cluster_id] += 1
                        break

            combination.extend(other_cards)

        return combination[:n_cards]

    def generate_combinations_for_personas(self, personas: List[Dict[str, Any]],
                                         samples_per_persona: int) -> List[List[str]]:
        self._initialize_tracking()
        all_combinations = []

        for persona in personas:
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

        persona_dict = {p['id']: p['persona'] for p in personas}

        print(f"Generating persona-based card combinations for {len(dataset)} samples...")

        for item in dataset:
            persona_id = item['input']['persona']['age']  # This needs proper persona matching
            persona_data = None

            for p in personas:
                if (p['persona']['age'] == item['input']['persona']['age'] and
                    p['persona']['gender'] == item['input']['persona']['gender'] and
                    p['persona']['disability_type'] == item['input']['persona']['disability_type']):
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
