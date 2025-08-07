import requests
import torch
from PIL import Image
from transformers import AutoProcessor, AutoModel
import os
import pickle
import json
from sklearn.cluster import KMeans
import numpy as np
from pathlib import Path

class AACCLIPEncoder:
    def __init__(self,model_name="openai/clip-vit-base-patch32"):
        #CLIP 인코더 초기화
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"device: {self.device}")

        #CLIP 모델과 프로세서 로드
        self.model = AutoModel.from_pretrained(
            model_name,
            torch_dtype=torch.bfloat16,
            attn_implementation="sdpa"
        ).to(self.device)

        self.processor = AutoProcessor.from_pretrained(model_name)

    def encode_single(self, image_path, text):
        try:
            #이미지 로드
            image = Image.open(image_path).convert("RGB")

            #입력 전처리
            inputs = self.processor(
                text=[text],
                images=image,
                return_tensors="pt",
                padding=True
            ).to(self.device)

            #모델 추론
            with torch.no_grad():
                outputs = self.model(**inputs)

                #임베딩 정규화
                image_embedding = outputs.image_embeds / outputs.image_embeds.norm(dim=-1, keepdim=True)
                text_embedding = outputs.text_embdes / outputs.text_embeds.norm(dim=-1, keepdim=True)

                return image_embedding.cpu().numpy().flatten(), text_embedding.cpu().numpy().flatten()
        except Exception as e:
            print(f"인코딩 실패 {image_path}: {e}")
            return None, None
    
    def encode_folder(self, folder_path):
        #폴더 내 모든 파일 인코딩
        valid_extensions = ['.jpg','.jpeg','.png','.bmp','.gif','.tiff']

        filenames = []
        image_embeddings = []
        text_embeddings = []

        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            file_ext = Path(filename).suffix.lower

            if file_ext in valid_extensions and os.path.isfile(file_path):
                print(f"처리 중: {filename}")

                text = Path(filename).stem

                img_emb, txt_emb = self.encode_single(file_path, text)
                
                if img_emb is not None and txt_emb is not None:
                    filenames.append(filename)
                    image_embeddings.append(img_emb)
                    text_embeddings.append(txt_emb)
        
        #numpy 배열로 반환
        image_embeddings = np.array(image_embeddings)
        text_embeddings = np.array(text_embeddings)

        print(f"총 {len(filenames)}개의 파일 인코딩 완료")
        return filenames, image_embeddings, text_embeddings
    
    def save_embeddings(self, filenames, image_embeddings, text_embeddings, output_folder):
        #임베딩을 파일로 저장
        Path(output_folder).mkdir(parents=True, exist_ok=True)

        #데이터 구조 생성
        embedding_data= {
            'filenames':filenames,
            'image_embeddings':image_embeddings.tolist(),
            'text_embeddings':text_embeddings.tolist()
        }

        #json 형식으로 저장
        json_path = os.path.join(output_folder, 'acc_embeddings.json')
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(embedding_data, f, ensure_ascii=False, indent=2)


class AACClusterer:
    def __init__(self, embeddings_path=None, embedding_data=None):
        #클러스터링 클래스 초기화
        if embedding_data is not None:
            self.data = embedding_data
        elif embeddings_path:
            self.data = self.load_embeddings(embeddings_path)
        else:
            raise ValueError("임베딩 데이터 또는 파일 경로가 필요합니다.")
        
        self.filenames = self.data['filenames']
        self.image_embeddings = np.array(self.data['image_embeddings'])
        self.text_embeddings = np.array(self.data['text_embeddings'])

    def load_embeddings(self, embeddings_path):
        #저장된 임베딩 파일 로드
        if embeddings_path.endswith('.json'):
            with open(embeddings_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            raise ValueError("지원되는 형식: .json")
    
    def find_optimal_clusters(self, embeddings, max_clusters=70):
        inertias = []
        k_range = range(1, min(max_clusters + 1, len(embeddings)))

        for k in k_range:
            kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
            kmeans.fit(embeddings)
            inertias.append(kmeans.inertia_)

        return list(k_range), inertias
    
    def detect_elbow_point(self, k_range, inertias):
        if len(inertias) < 3:
            return min(3, max(k_range))
        
        #정규화
        k_norm = np.array(k_range) / max(k_range)
        inertia_norm = np.array(inertias)/ max(inertias)

        difference = []
        for i, (k,inertia) in enumerate(zip(k_norm, inertia_norm)):
            line_y = 1-k
            diff = abs(inertia - line_y)
            difference.append(diff)
        
        elbow_idx = np.argmax(difference)
        return k_range[elbow_idx]
        
    def perform_clustering(self, embedding_type='combined', n_clusters=None):

        #임베딩 타입 선택
        if embedding_type == 'image':
            embeddings = self.images_embeddings
        elif embedding_type == 'text':
            embeddings = self.text_embeddings
        elif embedding_type == 'combined':
            embeddings = (self.images_embeddings + self.text_embeddings) / 2
        else:
            raise ValueError("임베딩 타입은 'image', 'text', combined' 중 하나여야 합니다.")
    
        #클러스터 수 자동 결정
        if n_clusters is None:
            k_range, inertias = self.find_optimal_clusters(embeddings)

            n_clusters = self.detect_elbow_point(k_range, inertias)
            print(f"자동 선택한 클러스터 수: {n_clusters}")

        #k-means 클러스터링
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        cluster_labels = kmeans.fit_predict(embeddings)

        #클러스터별 파일 그룹화
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
            'embedding_type': embedding_type,
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
    n_clusters=None,
    embedding_type='combined'
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
    
    print("=== AAC 카드 CLIP 클러스터링 파이프라인 시작 ===")
    
    # 1단계: CLIP으로 이미지/텍스트 인코딩
    print("\n1단계: CLIP 인코딩 중...")
    encoder = AACCLIPEncoder()
    filenames, image_embeddings, text_embeddings = encoder.encode_folder(aac_folder_path)
    
    if len(filenames) == 0:
        print("처리할 이미지 파일이 없습니다.")
        return None
    
    # 2단계: 임베딩 데이터 저장
    print("\n2단계: 임베딩 데이터 저장 중...")
    encoder.save_embeddings(filenames, image_embeddings, text_embeddings, output_folder)
    
    # 3단계: K-means 클러스터링
    print("\n3단계: K-means 클러스터링 수행 중...")
    embedding_data = {
        'filenames': filenames,
        'image_embeddings': image_embeddings.tolist(),
        'text_embeddings': text_embeddings.tolist()
    }
    
    clusterer = AACClusterer(embeddings_data=embedding_data)
    results = clusterer.perform_clustering(embedding_type=embedding_type, n_clusters=n_clusters)
    
    # 4단계: 결과 출력
    clusterer.print_cluster_results(results)
    
    print("\n=== 클러스터링 완료 ===")
    return results

# 사용 예시
if __name__ == "__main__":
    # AAC 카드 폴더 경로 설정
    aac_cards_path = "path/to/your/aac_cards"  # 실제 경로로 변경하세요
    
    # 파이프라인 실행
    results = run_aac_clustering_pipeline(
        aac_folder_path=aac_cards_path,
        output_folder="./aac_embeddings",
        n_clusters=5,  # 원하는 클러스터 수
        embedding_type='combined'  # 'image', 'text', 'combined' 중 선택
    )
    
    # 저장된 임베딩으로 나중에 다시 클러스터링하고 싶다면:
    # clusterer = AACClusterer('./aac_embeddings/aac_embeddings.pkl')
    # new_results = clusterer.perform_clustering('text', n_clusters=3)
