import json
import random
from pathlib import Path

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
            sampled_files[cluster_id] = sampled
            
            print(f"클러스터 {cluster_id}: {len(files)}개 중 {n_samples}개 선택")
            for file in sampled:
                print(f"  - {file}")
        
        return sampled_files
    
    def save_sampled_results(self, sampled_files, output_path):
        sampled_data = {
            'sampled_files': {str(k): v for k, v in sampled_files.items()},
            'total_sampled': sum(len(files) for files in sampled_files.values())
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(sampled_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n샘플링 결과 저장: {output_path}")

def sample_clusters(clustering_results_path, samples_per_cluster=3, specific_clusters=None, output_path="sampled_results.json"):
    sampler = ClusterSampler(clustering_results_path)
    sampled = sampler.sample_from_clusters(samples_per_cluster, specific_clusters)
    sampler.save_sampled_results(sampled, output_path)
    return sampled

if __name__ == "__main__":
    sample_clusters("./aac_embeddings/clustering_results.json", samples_per_cluster=3)
    
    # sample_clusters("./aac_embeddings/clustering_results.json", samples_per_cluster=5, specific_clusters=[0, 2, 5])