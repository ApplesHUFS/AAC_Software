import json
import numpy as np
import base64
import torch
from pathlib import Path
from typing import Dict, List, Any, Optional
from openai import OpenAI
from dotenv import load_dotenv
from sklearn.metrics import pairwise_distances
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
import time


class ClusterTagger:
    def __init__(self, embeddings_path: str, clustering_results_path: str,
                 images_folder: str, config: Optional[Dict] = None):
        load_dotenv()

        self.config = config or {}
        self.images_folder = Path(images_folder)
        self.client = OpenAI()

        device_setting = self.config.get('device', 'auto')
        if device_setting == 'auto':
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device_setting

        similarity_model_name = self.config.get('similarity_model', 'jhgan/ko-sroberta-multitask')
        self.similarity_model = SentenceTransformer(similarity_model_name, device=self.device)
        print(f"Similarity model '{similarity_model_name}' loaded on: {self.device}")

        self._load_data(embeddings_path, clustering_results_path)

    def _load_data(self, embeddings_path: str, clustering_results_path: str) -> None:
        with open(embeddings_path, 'r', encoding='utf-8') as f:
            embedding_data = json.load(f)

        with open(clustering_results_path, 'r', encoding='utf-8') as f:
            cluster_data = json.load(f)

        self.filenames = embedding_data['filenames']
        img_embeddings = np.array(embedding_data['image_embeddings'])
        txt_embeddings = np.array(embedding_data['text_embeddings'])
        self.embeddings = (img_embeddings + txt_embeddings) / 2

        self.cluster_labels = np.array(cluster_data['cluster_labels'])
        self.clustered_files = {int(k): v for k, v in cluster_data['clustered_files'].items()}
        self.filename_to_idx = {fn: i for i, fn in enumerate(self.filenames)}

    def _find_top_medoids(self, cluster_id: int, top_k: int = 3) -> List[str]:
        if cluster_id not in self.clustered_files:
            return []

        cluster_files = self.clustered_files[cluster_id]
        cluster_indices = [self.filename_to_idx[f] for f in cluster_files if f in self.filename_to_idx]

        if len(cluster_indices) <= top_k:
            return cluster_files

        cluster_embeddings = self.embeddings[cluster_indices]
        distances = pairwise_distances(cluster_embeddings)
        distance_sums = distances.sum(axis=1)

        top_medoid_indices = distance_sums.argsort()[:top_k]
        return [cluster_files[i] for i in top_medoid_indices]

    def _encode_image(self, image_path: Path) -> str:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def _extract_keyword(self, filename: str) -> str:
        stem = Path(filename).stem
        return stem.split('_', 1)[1] if '_' in stem else ""

    def _tag_cluster_with_llm(self, medoid_files: List[str]) -> List[str]:
        if not medoid_files:
            return []

        content = [{
            "type": "text",
            "text": "다음 AAC 카드 이미지들을 보고, 이들이 공통적으로 나타내는 주제나 카테고리를 파악해주세요. "
                   "각 이미지의 키워드도 함께 고려하여 최대 3개의 핵심 주제를 한국어로 제시해주세요.\n\n"
        }]

        for i, filename in enumerate(medoid_files, 1):
            image_path = self.images_folder / filename
            if not image_path.exists():
                continue

            keyword = self._extract_keyword(filename)
            base64_image = self._encode_image(image_path)

            content.extend([
                {
                    "type": "text",
                    "text": f"이미지 {i} (키워드: {keyword}):"
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{base64_image}",
                        "detail": "low"
                    }
                }
            ])

        content.append({
            "type": "text",
            "text": "\n위 이미지들의 공통 주제를 최대 3개의 한국어 단어나 짧은 구문으로 제시해주세요. "
                   "JSON 형식으로 응답해주세요."
        })

        schema = {
            "type": "json_schema",
            "json_schema": {
                "name": "cluster_tagging",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "topics": {
                            "type": "array",
                            "description": "클러스터의 주요 주제들",
                            "items": {"type": "string"},
                            "maxItems": 3
                        }
                    },
                    "required": ["topics"],
                    "additionalProperties": False
                }
            }
        }

        try:
            response = self.client.chat.completions.create(
                model=self.config.get('openai_model', 'gpt-4o-2024-08-06'),
                messages=[{"role": "user", "content": content}],
                response_format=schema,
                temperature=0.3,
                max_tokens=200
            )

            result = json.loads(response.choices[0].message.content)
            return result.get("topics", [])

        except Exception as e:
            print(f"Error tagging cluster: {e}")
            return []

    def tag_all_clusters(self) -> Dict[int, List[str]]:
        cluster_tags = {}
        delay = self.config.get('request_delay', 1)

        for cluster_id in tqdm(self.clustered_files.keys(), desc="Tagging clusters"):
            medoid_files = self._find_top_medoids(cluster_id, self.config.get('cluster_medoid_count', 3))
            if not medoid_files:
                continue

            tags = self._tag_cluster_with_llm(medoid_files)
            cluster_tags[cluster_id] = tags

            if delay > 0:
                time.sleep(delay)

        return cluster_tags

    def save_cluster_tags(self, cluster_tags: Dict[int, List[str]], output_path: str) -> None:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump({str(k): v for k, v in cluster_tags.items()},
                     f, ensure_ascii=False, indent=2)

        print(f"Cluster tags saved to {output_path}")

    def compute_topic_similarity(self, topic1: str, topic2: str) -> float:
        try:
            embeddings = self.similarity_model.encode([topic1, topic2], convert_to_tensor=True)
            similarity = torch.nn.functional.cosine_similarity(embeddings[0:1], embeddings[1:2]).item()
            return max(0.0, min(1.0, (similarity + 1) / 2))
        except Exception as e:
            print(f"Error computing similarity between '{topic1}' and '{topic2}': {e}")
            return 0.0

    def compute_topic_similarities_batch(self, topics1: List[str], topics2: List[str]) -> np.ndarray:
        try:
            if not topics1 or not topics2:
                return np.zeros((len(topics1), len(topics2)))

            embeddings1 = self.similarity_model.encode(topics1, convert_to_tensor=True)
            embeddings2 = self.similarity_model.encode(topics2, convert_to_tensor=True)

            similarities = torch.mm(embeddings1, embeddings2.T)
            similarities = (similarities + 1) / 2  # -1~1을 0~1로 변환

            return torch.clamp(similarities, 0.0, 1.0).cpu().numpy()
        except Exception as e:
            print(f"Error computing batch similarities: {e}")
            return np.zeros((len(topics1), len(topics2)))

    def assign_preferred_categories(self, cluster_tags: Dict[int, List[str]],
                                   personas: List[Dict],
                                   similarity_threshold: float = 0.75) -> List[Dict]:

        for persona in tqdm(personas, desc="Assigning preferred categories"):
            interesting_topics = persona['persona']['interesting_topics']
            preferred_categories = []

            if not interesting_topics or not cluster_tags:
                persona['persona']['preferred_category_types'] = preferred_categories
                continue

            all_cluster_topics = []
            cluster_topic_mapping = []

            for cluster_id, cluster_topics in cluster_tags.items():
                for topic in cluster_topics:
                    all_cluster_topics.append(topic)
                    cluster_topic_mapping.append(cluster_id)

            if not all_cluster_topics:
                persona['persona']['preferred_category_types'] = preferred_categories
                continue

            similarities = self.compute_topic_similarities_batch(interesting_topics, all_cluster_topics)

            cluster_max_similarities = {}
            for i, cluster_id in enumerate(cluster_topic_mapping):
                max_sim = similarities[:, i].max()
                if cluster_id not in cluster_max_similarities or max_sim > cluster_max_similarities[cluster_id]:
                    cluster_max_similarities[cluster_id] = max_sim

            candidates = [(cluster_id, sim) for cluster_id, sim in cluster_max_similarities.items()
                         if sim >= similarity_threshold]

            candidates.sort(key=lambda x: x[1], reverse=True)
            preferred_categories = [cluster_id for cluster_id, _ in candidates[:8]]

            persona['persona']['preferred_category_types'] = preferred_categories

            if preferred_categories:
                print(f"Persona {persona['persona']['age']}/{persona['persona']['gender']}: "
                      f"{len(preferred_categories)} preferred categories (max sim: {candidates[0][1]:.3f})")

        return personas
