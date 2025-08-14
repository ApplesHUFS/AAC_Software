import json
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Dict, List, Optional, Any
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import pairwise_distances

class MetaClusterer:
    """기존 클러스터링 결과를 불러와서 메타 클러스터링만 수행하는 클래스"""

    def __init__(self, clustering_results_path: str, embeddings_path: str, config: Optional[Dict] = None):
        self.config = config or {}

        # 1차 클러스터링 결과 로드
        self.clustering_result = self._load_clustering_results(clustering_results_path)

        # 임베딩 데이터 로드
        self.embedding_data = self._load_embeddings(embeddings_path)
        self.filenames = self.embedding_data['filenames']
        self.image_embeddings = np.array(self.embedding_data['image_embeddings'])
        self.text_embeddings = np.array(self.embedding_data['text_embeddings'])
        self.embeddings = (self.image_embeddings + self.text_embeddings) / 2

        print(f"✅ Loaded clustering results: {len(self.clustering_result['clustered_files'])} clusters")
        print(f"✅ Loaded embeddings: {len(self.filenames)} files")

    def _load_clustering_results(self, clustering_results_path: str) -> Dict[str, Any]:
        """1차 클러스터링 결과 JSON 파일 로드"""
        with open(clustering_results_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _load_embeddings(self, embeddings_path: str) -> Dict[str, Any]:
        """임베딩 데이터 JSON 파일 로드"""
        with open(embeddings_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def find_medoid(self, cluster_embeddings: np.ndarray) -> int:
        """클러스터 내에서 medoid(중앙값) 인덱스를 찾는 함수"""
        if len(cluster_embeddings) == 1:
            return 0

        # 클러스터 내 모든 점들 간의 거리 계산
        distances = pairwise_distances(cluster_embeddings)

        # 각 점에서 다른 모든 점까지의 거리 합 계산
        distance_sums = distances.sum(axis=1)

        # 거리 합이 최소인 점이 medoid
        medoid_idx = distance_sums.argmin()

        return medoid_idx

    def perform_meta_clustering(self, meta_n_clusters: int) -> Dict[str, Any]:
        """1차 클러스터링 결과를 바탕으로 medoid 기반 메타 클러스터링 수행"""

        # 클러스터 레이블 배열 재구성
        cluster_labels = np.array(self.clustering_result['cluster_labels'])
        n_clusters = self.clustering_result['n_clusters']

        # 각 클러스터의 medoid 찾기
        medoids = []
        medoid_info = []

        for i in range(n_clusters):
            cluster_mask = cluster_labels == i
            cluster_embeddings = self.embeddings[cluster_mask]
            cluster_filenames = [self.filenames[j] for j, mask in enumerate(cluster_mask) if mask]

            if len(cluster_embeddings) == 0:
                continue

            # 클러스터 내에서 medoid 찾기
            medoid_idx = self.find_medoid(cluster_embeddings)
            medoid_embedding = cluster_embeddings[medoid_idx]
            medoid_filename = cluster_filenames[medoid_idx]

            medoids.append(medoid_embedding)
            medoid_info.append({
                'original_cluster_id': i,
                'cluster_size': len(cluster_embeddings),
                'medoid_embedding': medoid_embedding,
                'medoid_filename': medoid_filename,
                'all_filenames': cluster_filenames
            })

        # medoid들을 이용해 메타 클러스터링 수행
        if len(medoids) == 0:
            raise ValueError("No valid clusters found for meta clustering")

        medoids_array = np.array(medoids)

        # 메타 클러스터 수가 medoid 수보다 크면 조정
        actual_meta_clusters = min(meta_n_clusters, len(medoids))

        meta_kmeans = KMeans(
            n_clusters=actual_meta_clusters,
            random_state=self.config.get('clustering_random_state', 42),
            n_init=self.config.get('clustering_n_init', 10)
        )
        meta_labels = meta_kmeans.fit_predict(medoids_array)

        # 메타 클러스터별로 1차 클러스터들 그룹화
        meta_clustered_groups: Dict[int, List[int]] = {}
        for i, meta_label in enumerate(meta_labels):
            meta_label = int(meta_label)
            if meta_label not in meta_clustered_groups:
                meta_clustered_groups[meta_label] = []
            meta_clustered_groups[meta_label].append(medoid_info[i]['original_cluster_id'])

        # 1차 클러스터 ID → 메타 클러스터 ID 매핑
        cluster_to_meta_mapping = {}
        for meta_id, cluster_ids in meta_clustered_groups.items():
            for cluster_id in cluster_ids:
                cluster_to_meta_mapping[cluster_id] = meta_id

        return {
            'meta_cluster_labels': meta_labels,
            'meta_clustered_groups': meta_clustered_groups,
            'meta_n_clusters': actual_meta_clusters,
            'medoid_info': medoid_info,
            'cluster_to_meta_mapping': cluster_to_meta_mapping,
            'meta_kmeans_model': meta_kmeans,
            'medoids_embeddings': medoids_array
        }

    def save_meta_clustering_results(self, meta_clustering_result: Dict[str, Any], output_path: str) -> None:
        """메타 클러스터링 결과를 JSON 파일로 저장"""
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        # JSON 직렬화 가능한 형태로 변환
        save_data = {
            'meta_cluster_labels': meta_clustering_result['meta_cluster_labels'].tolist(),
            'meta_clustered_groups': {str(k): v for k, v in meta_clustering_result['meta_clustered_groups'].items()},
            'meta_n_clusters': meta_clustering_result['meta_n_clusters'],
            'cluster_to_meta_mapping': {str(k): v for k, v in meta_clustering_result['cluster_to_meta_mapping'].items()},
            'medoid_info': [
                {
                    'original_cluster_id': info['original_cluster_id'],
                    'cluster_size': info['cluster_size'],
                    'medoid_filename': info['medoid_filename'],
                    'all_filenames': info['all_filenames']
                }
                for info in meta_clustering_result['medoid_info']
            ]
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, ensure_ascii=False, indent=2)

        print(f"Meta clustering results saved to {output_path}")

    def print_meta_cluster_summary(self, meta_clustering_result: Dict[str, Any]) -> None:
        """메타 클러스터링 결과 요약 출력"""
        print(f"\n=== Meta Clustering Results ===")
        print(f"Number of meta clusters: {meta_clustering_result['meta_n_clusters']}")

        for meta_id, cluster_ids in meta_clustering_result['meta_clustered_groups'].items():
            total_files = sum(
                info['cluster_size']
                for info in meta_clustering_result['medoid_info']
                if info['original_cluster_id'] in cluster_ids
            )
            medoid_files = [
                info['medoid_filename']
                for info in meta_clustering_result['medoid_info']
                if info['original_cluster_id'] in cluster_ids
            ]

            print(f"\nMeta Cluster {meta_id}: {len(cluster_ids)} original clusters, {total_files} total files")
            print(f"  - Original cluster IDs: {cluster_ids}")
            print(f"  - Representative medoids: {medoid_files[:3]}{'...' if len(medoid_files) > 3 else ''}")

    def visualize_meta_clusters(self, meta_clustering_result: Dict[str, Any], output_folder: str) -> None:
        """메타 클러스터 시각화"""
        output_folder = Path(output_folder)
        output_folder.mkdir(parents=True, exist_ok=True)

        # 1차 클러스터를 메타 클러스터 색상으로 시각화
        cluster_labels = np.array(self.clustering_result['cluster_labels'])
        cluster_to_meta = meta_clustering_result['cluster_to_meta_mapping']

        # 각 데이터 포인트의 메타 클러스터 레이블 생성
        meta_labels_for_points = np.array([
            cluster_to_meta.get(cluster_labels[i], -1)
            for i in range(len(cluster_labels))
        ])

        # PCA로 2D 변환
        pca = PCA(n_components=2, random_state=42)
        embeddings_2d = pca.fit_transform(self.embeddings)

        # 메타 클러스터별 시각화
        plt.figure(figsize=(15, 8))
        meta_n_clusters = meta_clustering_result['meta_n_clusters']
        colors = plt.cm.Set3(np.linspace(0, 1, meta_n_clusters))

        for meta_id in range(meta_n_clusters):
            mask = meta_labels_for_points == meta_id
            if np.any(mask):
                plt.scatter(embeddings_2d[mask, 0], embeddings_2d[mask, 1],
                           c=[colors[meta_id]],
                           label=f'Meta Cluster {meta_id} ({np.sum(mask)} files)',
                           alpha=0.7, s=30)

        # Medoid 위치 강조 표시
        medoids_2d = pca.transform(meta_clustering_result['medoids_embeddings'])
        plt.scatter(medoids_2d[:, 0], medoids_2d[:, 1],
                   c='red', marker='x', s=200, linewidths=3,
                   label='Medoids')

        plt.title('Meta Clustering Results (PCA 2D Visualization)', fontsize=14, fontweight='bold')
        plt.xlabel(f'PCA Component 1 (Explained Variance: {pca.explained_variance_ratio_[0]:.2%})')
        plt.ylabel(f'PCA Component 2 (Explained Variance: {pca.explained_variance_ratio_[1]:.2%})')
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()

        viz_path = output_folder / 'meta_cluster_visualization.png'
        plt.savefig(viz_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Meta cluster visualization saved: {viz_path}")

        # 메타 클러스터별 크기 막대 그래프
        plt.figure(figsize=(10, 6))
        meta_cluster_sizes = []

        for meta_id in range(meta_n_clusters):
            size = sum(
                info['cluster_size']
                for info in meta_clustering_result['medoid_info']
                if cluster_to_meta.get(info['original_cluster_id']) == meta_id
            )
            meta_cluster_sizes.append(size)

        bars = plt.bar(range(meta_n_clusters), meta_cluster_sizes, color=colors)

        for i, bar in enumerate(bars):
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                    f'{int(height)}', ha='center', va='bottom')

        plt.title('Number of Files per Meta Cluster', fontsize=14, fontweight='bold')
        plt.xlabel('Meta Cluster ID')
        plt.ylabel('Number of Files')
        plt.xticks(range(meta_n_clusters))
        plt.grid(True, alpha=0.3, axis='y')
        plt.tight_layout()

        bar_path = output_folder / 'meta_cluster_counts.png'
        plt.savefig(bar_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Meta cluster count graph saved: {bar_path}")

    def run_meta_clustering(self, meta_n_clusters: int, output_folder: str, visualize: bool = True) -> Dict[str, Any]:
        """메타 클러스터링 실행 및 결과 저장"""

        print(f"Starting meta clustering with {meta_n_clusters} clusters...")

        # 메타 클러스터링 수행
        meta_clustering_result = self.perform_meta_clustering(meta_n_clusters)

        output_folder = Path(output_folder)

        # 메타 클러스터링 결과 저장
        self.save_meta_clustering_results(meta_clustering_result, output_folder / 'new_meta_clustering_result.json')
        self.print_meta_cluster_summary(meta_clustering_result)

        # 메타 클러스터링 시각화
        if visualize:
            self.visualize_meta_clusters(meta_clustering_result, output_folder)

        return meta_clustering_result


# 실행 코드
if __name__ == "__main__":
    # 파일 경로 설정
    clustering_results_path = "/home/ellt/Workspace/AAC_Software/dataset/processed/clustering_results.json"
    embeddings_path = "/home/ellt/Workspace/AAC_Software/dataset/processed/embeddings.json"
    output_folder = "/home/ellt/Workspace/AAC_Software/dataset/processed"

    try:
        # 메타 클러스터러 초기화
        meta_clusterer = MetaClusterer(
            clustering_results_path=clustering_results_path,
            embeddings_path=embeddings_path
        )

        # 메타 클러스터링 실행
        meta_clustering_result = meta_clusterer.run_meta_clustering(
            meta_n_clusters=32,  # 메타 클러스터 개수
            output_folder=output_folder,
            visualize=True
        )

        print("✅ Meta clustering completed successfully!")

    except FileNotFoundError as e:
        print(f"❌ File not found: {e}")
        print("Please check if the file paths are correct.")
    except Exception as e:
        print(f"❌ Error during meta clustering: {e}")
