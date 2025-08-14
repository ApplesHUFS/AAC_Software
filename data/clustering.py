import json
import numpy as np
import matplotlib.pyplot as plt
import base64
from pathlib import Path
from typing import Dict, List, Optional, Any
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from openai import OpenAI
from dotenv import load_dotenv


class Clusterer:
    def __init__(self, embeddings_path: Optional[str] = None, embedding_data: Optional[Dict] = None, config: Optional[Dict] = None):
        load_dotenv()

        if embedding_data is not None:
            self.data = embedding_data
        elif embeddings_path:
            self.data = self._load_embeddings(embeddings_path)
        else:
            raise ValueError("Either embeddings_path or embedding_data must be provided")

        self.config = config or {}
        self.filenames = self.data['filenames']
        self.image_embeddings = np.array(self.data['image_embeddings'])
        self.text_embeddings = np.array(self.data['text_embeddings'])
        self.embeddings = (self.image_embeddings + self.text_embeddings) / 2

        self.client = OpenAI()

    def _load_embeddings(self, embeddings_path: str) -> Dict[str, Any]:
        with open(embeddings_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _encode_image(self, image_path: Path) -> str:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def _analyze_cluster_semantics(self, cluster_files: List[str], images_folder: str) -> Dict[str, Any]:
        images_folder = Path(images_folder)
        sample_files = cluster_files[:6] if len(cluster_files) > 6 else cluster_files

        content = [{
            "type": "text",
            "text": "다음 AAC 카드 이미지들을 분석하여 이 클러스터의 의미적 카테고리와 주제를 파악해주세요:"
        }]

        for i, filename in enumerate(sample_files, 1):
            image_path = images_folder / filename
            if image_path.exists():
                base64_image = self._encode_image(image_path)
                content.extend([
                    {
                        "type": "text",
                        "text": f"\n이미지 {i}:"
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{base64_image}",
                            "detail": "high"
                        }
                    }
                ])

        schema = {
            "type": "json_schema",
            "json_schema": {
                "name": "cluster_analysis",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "semantic_category": {
                            "type": "string",
                            "description": "이 클러스터의 주요 의미적 카테고리 (예: 음식, 교통, 감정, 사람, 활동 등)"
                        },
                        "themes": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "이 클러스터에 포함된 세부 주제들",
                            "maxItems": 5
                        },
                        "complexity_level": {
                            "type": "string",
                            "enum": ["basic", "intermediate", "advanced"],
                            "description": "카드들의 개념적 복잡도"
                        },
                        "typical_usage": {
                            "type": "string",
                            "description": "이런 카드들이 일반적으로 어떤 상황에서 사용되는지"
                        }
                    },
                    "required": ["semantic_category", "themes", "complexity_level", "typical_usage"],
                    "additionalProperties": False
                }
            }
        }

        response = self.client.chat.completions.create(
            model="gpt-4o-2024-08-06",
            messages=[{
                "role": "user",
                "content": content
            }],
            response_format=schema,
            temperature=0.3,
            max_tokens=400
        )

        return json.loads(response.choices[0].message.content)

    def perform_clustering(self, n_clusters: int, images_folder: str) -> Dict[str, Any]:
        random_state = self.config.get('clustering_random_state', 42)
        n_init = self.config.get('clustering_n_init', 10)

        kmeans = KMeans(n_clusters=n_clusters, random_state=random_state, n_init=n_init)
        cluster_labels = kmeans.fit_predict(self.embeddings)

        clustered_files: Dict[int, List[str]] = {}
        for i, filename in enumerate(self.filenames):
            cluster_id = int(cluster_labels[i])
            if cluster_id not in clustered_files:
                clustered_files[cluster_id] = []
            clustered_files[cluster_id].append(filename)

        cluster_semantics = {}
        for cluster_id, files in clustered_files.items():
            semantics = self._analyze_cluster_semantics(files, images_folder)
            cluster_semantics[cluster_id] = semantics

        return {
            'cluster_labels': cluster_labels,
            'clustered_files': clustered_files,
            'cluster_semantics': cluster_semantics,
            'n_clusters': n_clusters,
            'kmeans_model': kmeans,
            'embeddings': self.embeddings
        }

    def save_clustering_results(self, results: Dict[str, Any], output_path: str) -> None:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        cluster_data = {
            'cluster_labels': results['cluster_labels'].tolist(),
            'clustered_files': {str(k): v for k, v in results['clustered_files'].items()},
            'cluster_semantics': {str(k): v for k, v in results['cluster_semantics'].items()},
            'n_clusters': results['n_clusters'],
            'filenames': self.filenames
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(cluster_data, f, ensure_ascii=False, indent=2)

    def print_cluster_summary(self, results: Dict[str, Any]) -> None:
        for cluster_id, files in results['clustered_files'].items():
            semantics = results['cluster_semantics'][cluster_id]
            print(f"Cluster {cluster_id}: {len(files)} files")
            print(f"  Category: {semantics['semantic_category']}")
            print(f"  Themes: {', '.join(semantics['themes'])}")
            print(f"  Complexity: {semantics['complexity_level']}")

    def visualize_clusters(self, results: Dict[str, Any], output_folder: str) -> None:
        output_folder = Path(output_folder)
        output_folder.mkdir(parents=True, exist_ok=True)

        embeddings = results['embeddings']
        cluster_labels = results['cluster_labels']

        pca = PCA(n_components=2, random_state=42)
        embeddings_2d = pca.fit_transform(embeddings)

        self._plot_scatter(embeddings_2d, cluster_labels, results, pca, output_folder)
        self._plot_cluster_counts(results, output_folder)

    def _plot_scatter(self, embeddings_2d: np.ndarray, cluster_labels: np.ndarray,
                     results: Dict[str, Any], pca: PCA, output_folder: Path) -> None:
        plt.figure(figsize=(15, 10))
        n_clusters = results['n_clusters']
        colors = plt.cm.tab20(np.linspace(0, 1, n_clusters))

        for i in range(n_clusters):
            cluster_mask = cluster_labels == i
            semantics = results['cluster_semantics'][i]
            category = semantics['semantic_category']

            plt.scatter(embeddings_2d[cluster_mask, 0],
                       embeddings_2d[cluster_mask, 1],
                       c=[colors[i]],
                       label=f'C{i}: {category} ({np.sum(cluster_mask)})',
                       alpha=0.7, s=50)

        plt.title('Semantic Clustering Results', fontsize=14, fontweight='bold')
        plt.xlabel(f'PCA Component 1 ({pca.explained_variance_ratio_[0]:.2%})')
        plt.ylabel(f'PCA Component 2 ({pca.explained_variance_ratio_[1]:.2%})')
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()

        viz_path = output_folder / 'semantic_clusters.png'
        plt.savefig(viz_path, dpi=300, bbox_inches='tight')
        plt.close()

    def _plot_cluster_counts(self, results: Dict[str, Any], output_folder: Path) -> None:
        plt.figure(figsize=(12, 8))
        n_clusters = results['n_clusters']
        cluster_counts = [len(results['clustered_files'][i]) for i in range(n_clusters)]
        categories = [results['cluster_semantics'][i]['semantic_category'] for i in range(n_clusters)]

        colors = plt.cm.Set3(np.linspace(0, 1, n_clusters))
        bars = plt.bar(range(n_clusters), cluster_counts, color=colors)

        for i, bar in enumerate(bars):
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                    f'{int(height)}', ha='center', va='bottom')

        plt.title('Cluster Sizes by Semantic Category', fontsize=14, fontweight='bold')
        plt.xlabel('Cluster ID')
        plt.ylabel('Number of Files')
        plt.xticks(range(n_clusters), [f'C{i}\n{categories[i][:10]}' for i in range(n_clusters)],
                   rotation=45, ha='right')
        plt.grid(True, alpha=0.3, axis='y')
        plt.tight_layout()

        bar_path = output_folder / 'semantic_cluster_counts.png'
        plt.savefig(bar_path, dpi=300, bbox_inches='tight')
        plt.close()

    def cluster_and_save(self, n_clusters: int, images_folder: str, output_folder: str, visualize: bool = True) -> Dict[str, Any]:
        results = self.perform_clustering(n_clusters, images_folder)

        output_folder = Path(output_folder)
        self.save_clustering_results(results, output_folder / 'clustering_results.json')
        self.print_cluster_summary(results)

        if visualize:
            self.visualize_clusters(results, output_folder)

        return results
