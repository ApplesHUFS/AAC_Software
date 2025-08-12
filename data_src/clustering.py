import json
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA


class Clusterer:
    def __init__(self, embeddings_path: Optional[str] = None, embedding_data: Optional[Dict] = None):
        if embedding_data is not None:
            self.data = embedding_data
        elif embeddings_path:
            self.data = self._load_embeddings(embeddings_path)
        else:
            raise ValueError("Either embeddings_path or embedding_data must be provided")
        
        self.filenames = self.data['filenames']
        self.image_embeddings = np.array(self.data['image_embeddings'])
        self.text_embeddings = np.array(self.data['text_embeddings'])
        self.embeddings = (self.image_embeddings + self.text_embeddings) / 2
    
    def _load_embeddings(self, embeddings_path: str) -> Dict:
        with open(embeddings_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def perform_clustering(self, n_clusters: int) -> Dict:
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        cluster_labels = kmeans.fit_predict(self.embeddings)
        
        clustered_files = {}
        for i, filename in enumerate(self.filenames):
            cluster_id = int(cluster_labels[i])
            if cluster_id not in clustered_files:
                clustered_files[cluster_id] = []
            clustered_files[cluster_id].append(filename)
        
        return {
            'cluster_labels': cluster_labels,
            'clustered_files': clustered_files,
            'n_clusters': n_clusters,
            'kmeans_model': kmeans,
            'embeddings': self.embeddings
        }
    
    def save_clustering_results(self, results: Dict, output_path: str):
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        cluster_data = {
            'cluster_labels': results['cluster_labels'].tolist(),
            'clustered_files': {str(k): v for k, v in results['clustered_files'].items()},
            'n_clusters': results['n_clusters'],
            'filenames': self.filenames
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(cluster_data, f, ensure_ascii=False, indent=2)
        
        print(f"Clustering results saved to {output_path}")
    
    def print_cluster_summary(self, results: Dict):
        print(f"\nClustering Results:")
        print(f"Total files: {len(self.filenames)}")
        print(f"Number of clusters: {results['n_clusters']}")
        
        for cluster_id, files in results['clustered_files'].items():
            print(f"Cluster {cluster_id}: {len(files)} files")
    
    def visualize_clusters(self, results: Dict, output_folder: str):
        output_folder = Path(output_folder)
        output_folder.mkdir(parents=True, exist_ok=True)
        
        embeddings = results['embeddings']
        cluster_labels = results['cluster_labels']
        
        pca = PCA(n_components=2, random_state=42)
        embeddings_2d = pca.fit_transform(embeddings)
        
        self._plot_scatter(embeddings_2d, cluster_labels, results['n_clusters'], pca, output_folder)
        self._plot_cluster_counts(results, output_folder)
    
    def _plot_scatter(self, embeddings_2d: np.ndarray, cluster_labels: np.ndarray, 
                     n_clusters: int, pca: PCA, output_folder: Path):
        plt.figure(figsize=(15, 8))
        colors = plt.cm.tab10(np.linspace(0, 1, n_clusters))
        
        for i in range(n_clusters):
            cluster_mask = cluster_labels == i
            plt.scatter(embeddings_2d[cluster_mask, 0], 
                       embeddings_2d[cluster_mask, 1], 
                       c=[colors[i]], 
                       label=f'Cluster {i} ({np.sum(cluster_mask)} files)',
                       alpha=0.7, s=50)
        
        plt.title('AAC Card Clustering Results (PCA 2D Visualization)', fontsize=14, fontweight='bold')
        plt.xlabel(f'PCA Component 1 (Explained Variance: {pca.explained_variance_ratio_[0]:.2%})')
        plt.ylabel(f'PCA Component 2 (Explained Variance: {pca.explained_variance_ratio_[1]:.2%})')
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        viz_path = output_folder / 'cluster_visualization.png'
        plt.savefig(viz_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Cluster visualization saved: {viz_path}")
    
    def _plot_cluster_counts(self, results: Dict, output_folder: Path):
        plt.figure(figsize=(10, 6))
        n_clusters = results['n_clusters']
        cluster_counts = [len(results['clustered_files'][i]) for i in range(n_clusters)]
        colors = plt.cm.tab10(np.linspace(0, 1, n_clusters))
        
        bars = plt.bar(range(n_clusters), cluster_counts, color=colors)
        
        for i, bar in enumerate(bars):
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                    f'{int(height)}', ha='center', va='bottom')
        
        plt.title('Number of Files per Cluster', fontsize=14, fontweight='bold')
        plt.xlabel('Cluster ID')
        plt.ylabel('Number of Files')
        plt.xticks(range(n_clusters))
        plt.grid(True, alpha=0.3, axis='y')
        plt.tight_layout()
        
        bar_path = output_folder / 'cluster_counts.png'
        plt.savefig(bar_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Cluster count graph saved: {bar_path}")
    
    def cluster_and_save(self, n_clusters: int, output_folder: str, visualize: bool = True) -> Dict:
        results = self.perform_clustering(n_clusters)
        
        output_folder = Path(output_folder)
        self.save_clustering_results(results, output_folder / 'clustering_results.json')
        self.print_cluster_summary(results)
        
        if visualize:
            self.visualize_clusters(results, output_folder)
        
        return results