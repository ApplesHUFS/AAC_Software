import json
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Dict, List, Optional, Any
from sklearn.preprocessing import normalize
from sklearn.metrics import silhouette_score
from sklearn.decomposition import PCA
from tqdm import tqdm

plt.rcParams['font.family'] = ['DejaVu Sans', 'sans-serif']
plt.rcParams['axes.unicode_minus'] = False


class SphericalKMeans:
    """고차원 임베딩용 Spherical K-means 구현"""
    
    def __init__(self, n_clusters: int, max_iter: int = 100, n_init: int = 10, random_state: int = 42):
        self.n_clusters = n_clusters
        self.max_iter = max_iter
        self.n_init = n_init
        self.random_state = random_state
        self.cluster_centers_ = None
        self.labels_ = None

    def _init_centroids(self, X: np.ndarray) -> np.ndarray:
        """K-means++ 초기화"""
        n_samples, n_features = X.shape
        rng = np.random.RandomState(self.random_state)
        
        centers = np.zeros((self.n_clusters, n_features))
        centers[0] = X[rng.randint(n_samples)]
        centers[0] = centers[0] / np.linalg.norm(centers[0])
        
        for c_id in range(1, self.n_clusters):
            distances = np.array([min([1 - np.dot(x, center) for center in centers[:c_id]]) for x in X])
            probs = distances / distances.sum()
            cumprobs = probs.cumsum()
            idx = np.searchsorted(cumprobs, rng.rand())
            
            centers[c_id] = X[idx]
            centers[c_id] = centers[c_id] / np.linalg.norm(centers[c_id])
            
        return centers

    def _assign_clusters(self, X: np.ndarray, centers: np.ndarray) -> np.ndarray:
        """코사인 유사도로 클러스터 할당"""
        similarities = np.dot(X, centers.T)
        return np.argmax(similarities, axis=1)

    def _update_centers(self, X: np.ndarray, labels: np.ndarray) -> np.ndarray:
        """중심점 업데이트"""
        centers = np.zeros((self.n_clusters, X.shape[1]))
        
        for k in range(self.n_clusters):
            mask = labels == k
            if np.sum(mask) > 0:
                center = np.mean(X[mask], axis=0)
                centers[k] = center / (np.linalg.norm(center) + 1e-10)
            else:
                centers[k] = np.random.randn(X.shape[1])
                centers[k] = centers[k] / np.linalg.norm(centers[k])
                
        return centers

    def fit(self, X: np.ndarray) -> 'SphericalKMeans':
        """Spherical K-means 학습"""
        X_normalized = normalize(X, norm='l2')
        
        best_inertia = np.inf
        best_centers = None
        best_labels = None
        
        for init in range(self.n_init):
            centers = self._init_centroids(X_normalized)
            
            for iteration in range(self.max_iter):
                labels = self._assign_clusters(X_normalized, centers)
                new_centers = self._update_centers(X_normalized, labels)
                
                center_shift = np.max([1 - np.dot(centers[k], new_centers[k]) for k in range(self.n_clusters)])
                centers = new_centers
                
                if center_shift < 1e-4:
                    break
            
            inertia = 0.0
            for k in range(self.n_clusters):
                mask = labels == k
                if np.sum(mask) > 0:
                    similarities = np.dot(X_normalized[mask], centers[k])
                    inertia += np.sum(1 - similarities)
            
            if inertia < best_inertia:
                best_inertia = inertia
                best_centers = centers.copy()
                best_labels = labels.copy()
        
        self.cluster_centers_ = best_centers
        self.labels_ = best_labels
        
        return self


class Clusterer:
    """계층적 Spherical K-means 클러스터러"""
    
    def __init__(self, embeddings_path: str = None, embedding_data: Dict = None, config: Dict = None):
        if embedding_data is not None:
            self.data = embedding_data
        elif embeddings_path:
            with open(embeddings_path, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
        else:
            raise ValueError("embeddings_path 또는 embedding_data 필요")

        self.config = config or {}
        self.filenames = self.data['filenames']

        # 임베딩 융합
        img_embeddings = np.array(self.data['image_embeddings'])
        txt_embeddings = np.array(self.data['text_embeddings'])
        
        img_normalized = normalize(img_embeddings, norm='l2')
        txt_normalized = normalize(txt_embeddings, norm='l2')
        
        img_weight = self.config.get('image_weight', 0.7)
        self.embeddings = img_weight * img_normalized + (1 - img_weight) * txt_normalized
        self.embeddings = normalize(self.embeddings, norm='l2')

    def _find_optimal_clusters(self, X: np.ndarray, min_k: int = 2, max_k: int = 30) -> int:
        """최적 클러스터 수 결정"""
        sample_size = min(len(X), 2000)
        if len(X) > sample_size:
            indices = np.random.choice(len(X), sample_size, replace=False)
            X_sample = X[indices]
        else:
            X_sample = X
        
        best_score = -1
        best_k = min_k
        
        for k in range(min_k, min(max_k, len(X_sample) // 2)):
            try:
                kmeans = SphericalKMeans(n_clusters=k, n_init=3)
                labels = kmeans.fit(X_sample).labels_
                
                if len(np.unique(labels)) > 1:
                    score = silhouette_score(X_sample, labels, metric='cosine')
                    if score > best_score:
                        best_score = score
                        best_k = k
            except:
                continue
        
        return best_k

    def perform_clustering(self, n_clusters: int = None) -> Dict[str, Any]:
        """계층적 클러스터링 수행"""
        # 1단계: 거시적 클러스터링
        macro_k = self._find_optimal_clusters(self.embeddings, min_k=8, max_k=20)
        macro_kmeans = SphericalKMeans(n_clusters=macro_k)
        macro_labels = macro_kmeans.fit(self.embeddings).labels_
        
        # 2단계: 미시적 클러스터링
        final_labels = np.zeros(len(self.embeddings), dtype=int)
        final_cluster_id = 0
        cluster_hierarchy = {}
        
        for macro_id in range(macro_k):
            macro_mask = macro_labels == macro_id
            macro_size = np.sum(macro_mask)
            
            if macro_size < 15:
                final_labels[macro_mask] = final_cluster_id
                cluster_hierarchy[final_cluster_id] = {'macro_id': macro_id, 'size': macro_size}
                final_cluster_id += 1
                continue
            
            macro_embeddings = self.embeddings[macro_mask]
            max_micro_k = min(max(2, macro_size // 15), 8)
            
            if max_micro_k >= 2:
                try:
                    micro_k = self._find_optimal_clusters(macro_embeddings, min_k=2, max_k=max_micro_k)
                    micro_kmeans = SphericalKMeans(n_clusters=micro_k)
                    micro_labels = micro_kmeans.fit(macro_embeddings).labels_
                    
                    for micro_id in range(micro_k):
                        micro_mask = micro_labels == micro_id
                        micro_size = np.sum(micro_mask)
                        
                        if micro_size > 0:
                            global_mask = np.zeros(len(self.embeddings), dtype=bool)
                            global_mask[macro_mask] = micro_mask
                            
                            final_labels[global_mask] = final_cluster_id
                            cluster_hierarchy[final_cluster_id] = {
                                'macro_id': macro_id, 'micro_id': micro_id, 'size': micro_size
                            }
                            final_cluster_id += 1
                except:
                    final_labels[macro_mask] = final_cluster_id
                    cluster_hierarchy[final_cluster_id] = {'macro_id': macro_id, 'size': macro_size}
                    final_cluster_id += 1
            else:
                final_labels[macro_mask] = final_cluster_id
                cluster_hierarchy[final_cluster_id] = {'macro_id': macro_id, 'size': macro_size}
                final_cluster_id += 1
        
        # 결과 구성
        clustered_files = {}
        for i, filename in enumerate(self.filenames):
            cluster_id = int(final_labels[i])
            if cluster_id not in clustered_files:
                clustered_files[cluster_id] = []
            clustered_files[cluster_id].append(filename)
        
        return {
            'cluster_labels': final_labels.tolist(),
            'clustered_files': clustered_files,
            'n_clusters': final_cluster_id,
            'kmeans_model': None,
            'embeddings': self.embeddings,
            'hierarchy_info': {'cluster_hierarchy': cluster_hierarchy}
        }

    def save_clustering_results(self, results: Dict[str, Any], output_path: str) -> None:
        """클러스터링 결과 저장"""
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        cluster_data = {
            'cluster_labels': results['cluster_labels'],
            'clustered_files': {str(k): v for k, v in results['clustered_files'].items()},
            'n_clusters': results['n_clusters'],
            'filenames': self.filenames
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(cluster_data, f, ensure_ascii=False, indent=2)

    def print_cluster_summary(self, results: Dict[str, Any]) -> None:
        """클러스터링 결과 요약"""
        clustered_files = results['clustered_files']
        sizes = [len(files) for files in clustered_files.values()]
        print(f"클러스터 {results['n_clusters']}개 생성, 크기 분포: {min(sizes)}-{max(sizes)}")

    def visualize_clusters(self, results: Dict[str, Any], output_folder: str) -> None:
        """클러스터 시각화"""
        output_folder = Path(output_folder)
        output_folder.mkdir(parents=True, exist_ok=True)

        try:
            pca = PCA(n_components=2)
            embeddings_2d = pca.fit_transform(self.embeddings)
            
            plt.figure(figsize=(12, 8))
            cluster_labels = np.array(results['cluster_labels'])
            n_clusters = results['n_clusters']
            
            colors = plt.cm.tab20(np.linspace(0, 1, min(n_clusters, 20)))
            if n_clusters > 20:
                colors = plt.cm.nipy_spectral(np.linspace(0, 1, n_clusters))
            
            for cluster_id in range(n_clusters):
                mask = cluster_labels == cluster_id
                if np.sum(mask) > 0:
                    plt.scatter(embeddings_2d[mask, 0], embeddings_2d[mask, 1],
                               c=[colors[cluster_id % len(colors)]], alpha=0.7, s=20)
            
            plt.title(f'Clustering Results ({n_clusters} clusters)')
            plt.tight_layout()
            plt.savefig(output_folder / 'cluster_visualization.png', dpi=200, bbox_inches='tight')
            plt.close()
            
        except Exception as e:
            print(f"시각화 오류: {e}")

    def cluster_and_save(self, n_clusters: int, output_folder: str, visualize: bool = True) -> Dict[str, Any]:
        """전체 클러스터링 프로세스"""
        results = self.perform_clustering(n_clusters)
        
        output_folder = Path(output_folder)
        self.save_clustering_results(results, output_folder / 'clustering_results.json')
        self.print_cluster_summary(results)
        
        if visualize:
            self.visualize_clusters(results, output_folder)

        return results