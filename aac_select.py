import json
import random

class ClusterSampler:
    def __init__(self, clustering_results_path):
        with open(clustering_results_path, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
        
        self.clustered_files = {int(k): v for k, v in self.data['clustered_files'].items()}
    
    def sample_from_clusters(self, samples_per_cluster=3, specific_clusters=None):
        sampled_files = {}
        
        clusters_to_sample = specific_clusters or list(self.clustered_files.keys())
        
        for cluster_id in clusters_to_sample:
            if cluster_id not in self.clustered_files:
                print(f"클러스터 {cluster_id}가 존재하지 않습니다.")
                continue
                
            files = self.clustered_files[cluster_id]
            n_samples = min(samples_per_cluster, len(files))
            
            sampled = random.sample(files, n_samples)
            sampled_files[cluster_id] = sampled             # [0, 2, 5] -> {0: [...], 2: [...], 5: [...]}
            
            print(f"클러스터 {cluster_id}: {len(files)}개 중 {n_samples}개 선택")
            for file in sampled:
                print(f"  - {file}")
        
        return sampled_files

if __name__ == "__main__":
    sampler = ClusterSampler(clustering_results_path="./aac_embeddings/clustering_results.json")
    sampled = sampler.sample_from_clusters(samples_per_cluster=5, specific_clusters=[0, 2, 5])
    print(sampled)