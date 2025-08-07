import torch
from PIL import Image
from transformers import AutoProcessor, AutoModel
import os
import tqdm
import json
from sklearn.cluster import KMeans
import numpy as np
from pathlib import Path

class AACCLIPEncoder:
    def __init__(self, model_name="openai/clip-vit-base-patch32"):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"device: {self.device}")

        self.model = AutoModel.from_pretrained(
            model_name,
            torch_dtype=torch.bfloat16,
            attn_implementation="sdpa"
        ).to(self.device)

        self.processor = AutoProcessor.from_pretrained(model_name)

    def encode_single(self, image_path, text):
        image = Image.open(image_path).convert("RGB")

        inputs = self.processor(
            text=[text],
            images=image,
            return_tensors="pt",
            padding=True
        ).to(self.device)

        with torch.no_grad():
            outputs = self.model(**inputs)

            image_embedding = outputs.image_embeds / outputs.image_embeds.norm(dim=-1, keepdim=True)
            text_embedding = outputs.text_embeds / outputs.text_embeds.norm(dim=-1, keepdim=True)

            return image_embedding.cpu().numpy().flatten(), text_embedding.cpu().numpy().flatten()
    
    def encode_folder(self, folder_path):
        filenames = []
        image_embeddings = []
        text_embeddings = []

        for filename in tqdm(os.listdir(folder_path), desc="폴더 내 파일 처리"):
            file_path = os.path.join(folder_path, filename)
            file_ext = Path(filename).suffix.lower()

            if file_ext == '.png' and os.path.isfile(file_path):
                text = Path(filename).stem.split('_', 1)[-1] if '_' in Path(filename).stem else Path(filename).stem

                img_emb, txt_emb = self.encode_single(file_path, text)
                
                if img_emb is not None and txt_emb is not None:
                    filenames.append(filename)
                    image_embeddings.append(img_emb)
                    text_embeddings.append(txt_emb)
        
        image_embeddings = np.array(image_embeddings)
        text_embeddings = np.array(text_embeddings)

        print(f"총 {len(filenames)}개의 파일 인코딩 완료")
        return filenames, image_embeddings, text_embeddings
    
    def save_embeddings(self, filenames, image_embeddings, text_embeddings, output_folder):
        Path(output_folder).mkdir(parents=True, exist_ok=True)

        embedding_data = {
            'filenames': filenames,
            'image_embeddings': image_embeddings.tolist(),
            'text_embeddings': text_embeddings.tolist()
        }

        json_path = os.path.join(output_folder, 'aac_embeddings.json')
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(embedding_data, f, ensure_ascii=False, indent=2)

class AACClusterer:
    def __init__(self, embeddings_path=None, embedding_data=None):
        if embedding_data is not None:
            self.data = embedding_data
        elif embeddings_path:
            self.data = self.load_embeddings(embeddings_path)
        
        self.filenames = self.data['filenames']
        self.image_embeddings = np.array(self.data['image_embeddings'])
        self.text_embeddings = np.array(self.data['text_embeddings'])

    def load_embeddings(self, embeddings_path):
        with open(embeddings_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def find_optimal_clusters(self, embeddings, max_clusters=70):
        inertias = []
        k_range = range(1, min(max_clusters + 1, len(embeddings)))

        for k in tqdm(k_range, desc="클러스터 수 결정"):
            kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
            kmeans.fit(embeddings)
            inertias.append(kmeans.inertia_)

        return list(k_range), inertias
    
    def detect_elbow_point(self, k_range, inertias):
        if len(inertias) < 3:
            return min(3, max(k_range))
        
        k_norm = np.array(k_range) / max(k_range)
        inertia_norm = np.array(inertias) / max(inertias)

        difference = []
        for i, (k, inertia) in enumerate(zip(k_norm, inertia_norm)):
            line_y = 1 - k
            diff = abs(inertia - line_y)
            difference.append(diff)
        
        elbow_idx = np.argmax(difference)
        return k_range[elbow_idx]
        
    def perform_clustering(self, n_clusters=None):
        embeddings = (self.image_embeddings + self.text_embeddings) / 2
    
        if n_clusters is None:
            k_range, inertias = self.find_optimal_clusters(embeddings)
            n_clusters = self.detect_elbow_point(k_range, inertias)
            print(f"자동 선택한 클러스터 수: {n_clusters}")

        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        cluster_labels = kmeans.fit_predict(embeddings)

        clustered_files = {}
        for i, filename in enumerate(self.filenames):
            cluster_id = cluster_labels[i]
            if cluster_id not in clustered_files:
                clustered_files[cluster_id] = []
            clustered_files[cluster_id].append(filename)

        results = {
            'cluster_labels': cluster_labels,
            'clustered_files': clustered_files,
            'n_clusters': n_clusters,
            'kmeans_model': kmeans
        }

        return results

    def print_cluster_results(self, results):
        print(f"\n=== AAC 카드 클러스터링 결과 ===")
        print(f"임베딩 타입: {results['embedding_type']}")
        print(f"총 파일 수: {len(self.filenames)}")
        print(f"클러스터 수: {results['n_clusters']}")
        
        for cluster_id, files in results['clustered_files'].items():
            print(f"\n클러스터 {cluster_id} ({len(files)}개 파일):")
            for filename in files:
                print(f"  - {filename}")


def run_aac_clustering_pipeline(
    aac_folder_path, 
    output_folder='./aac_embeddings',
    n_clusters=None
):
    """
    AAC 카드 클러스터링 전체 파이프라인 실행
    
    Args:
        aac_folder_path: AAC 카드 이미지들이 있는 폴더 경로
        output_folder: 임베딩 결과를 저장할 폴더
        n_clusters: 클러스터 수 (None이면 자동 결정)
        embedding_type: 사용할 임베딩 타입 ('image', 'text', 'combined')
    
    Returns:
        클러스터링 결과 딕셔너리
    """
        
    print("\nCLIP 인코딩 중...")
    encoder = AACCLIPEncoder()
    filenames, image_embeddings, text_embeddings = encoder.encode_folder(aac_folder_path)
    
    if len(filenames) == 0:
        print("처리할 이미지 파일이 없습니다.")
        return None
    
    print("\n임베딩 데이터 저장 중...")
    encoder.save_embeddings(filenames, image_embeddings, text_embeddings, output_folder)
    
    print("\nK-means 클러스터링 수행 중...")
    embedding_data = {
        'filenames': filenames,
        'image_embeddings': image_embeddings.tolist(),
        'text_embeddings': text_embeddings.tolist()
    }
    
    clusterer = AACClusterer(embedding_data=embedding_data)
    results = clusterer.perform_clustering(n_clusters=n_clusters)
    
    clusterer.print_cluster_results(results)
    
    print("\n=== 클러스터링 완료 ===")
    return results

if __name__ == "__main__":
    aac_cards_path = "data/images"
    
    results = run_aac_clustering_pipeline(
        aac_folder_path=aac_cards_path,
        output_folder="./aac_embeddings",
        n_clusters=None
    )
    
    # 저장된 임베딩으로 나중에 다시 클러스터링하고 싶다면:
    # clusterer = AACClusterer(embeddings_path='./aac_embeddings/aac_embeddings.json')
    # new_results = clusterer.perform_clustering('text', n_clusters=3)