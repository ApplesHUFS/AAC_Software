# 랜덤으로 클러스터 중 하나를 선택해 카드 조합 만들기
import random
import json


def load_json_files(reclustering_path, aac_dataset_path):
    with open(reclustering_path, 'r', encoding='utf-8') as f:
        reclustering_data = json.load(f)
        
    with open(aac_dataset_path, 'r', encoding='utf-8') as f:
        aac_dataset = json.load(f)
    return reclustering_data, aac_dataset


def extract_clusters(reclustering_data):
    return reclustering_data.get('clustered_files', {})

def generate_card_combination(clusters, num_cards):
    # clusters의 key값(id)을 뽑아와 랜덤으로 하나의 클러스터를 선택 후, 해당 클러스터안의 이미지들을 가져온다.
    cluster_ids = list(clusters.keys())
    selected_cluster_id = random.choice(cluster_ids)
    selected_cluster_cards = clusters[selected_cluster_id]
    
    #num_cards만큼 해당 클러스터에서 카드를 뽑는데, 카드 개수와 클러스터 안의 카드 개수 중 min 값을 선택해 카드 개수로 지정
    num_cards_select = min(num_cards, len(selected_cluster_cards))
    selected_cards = random.sample(selected_cluster_cards, num_cards_select)
    
    return selected_cards #num_cards_to_select만큼 선택된 이미지가 return 됨.

# 메인 함수
def generate_aac_card_combinations(reclustering_path="", aac_dataset_path="smj/AAC_Software/data/aac_dataset.json"):
    print("1. JSON 파일 로딩")
    reclustering_data, aac_dataset = load_json_files(reclustering_path, aac_dataset_path)
    
    if reclustering_data is None or aac_dataset is None:
        return None
    
    print("2. 클러스터 정보 추출")
    clusters = extract_clusters(reclustering_data)
    
    print("4. 카드 조합 생성 시작")
    # 각 페르소나별로 처리 (200개씩 묶어서 처리)
    for persona_idx in range(24):  # 24개 페르소나
        start_idx = persona_idx * 200
        end_idx = start_idx + 200
        
        print(f"페르소나 {persona_idx + 1} 처리 중... (데이터 {start_idx + 1} ~ {end_idx})")
        
        # 카드 개수별로 50개씩 데이터 인덱스 생성
        card_counts = [1] * 50 + [2] * 50 + [3] * 50 + [4] * 50  # [1,1,1...1, 2,2,2...2, 3,3,3...3, 4,4,4...4]
        random.shuffle(card_counts)  # 카드 개수 순서를 랜덤하게 섞음
        
        # 현재 페르소나의 200개 데이터에 카드 조합 할당
        for i, data_idx in enumerate(range(start_idx, end_idx)):
            data = aac_dataset[data_idx]
            data_id = data['id']
            
            # 해당 데이터에 할당될 카드 개수
            num_cards = card_counts[i]
            
            # 랜덤하게 카드 조합 생성
            card_combination = generate_card_combination(clusters, num_cards)
            
            # AAC_card_combination에 하나의 카드 조합만 저장
            data['input']['AAC_card_combination'] = card_combination
    
    print("5. 카드 조합 생성 완료")
    return aac_dataset

def save_updated_dataset(aac_dataset, output_path="aac_dataset_combination.json"):
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(aac_dataset, f, ensure_ascii=False, indent=2)
        print(f"업데이트된 데이터셋이 {output_path}에 저장되었습니다.")
    except Exception as e:
        print(f"파일 저장 오류: {e}")

if __name__ == "__main__":
    # 카드 조합 생성
    updated_dataset = generate_aac_card_combinations(
        reclustering_path="",
        aac_dataset_path="smj/AAC_Software/data/aac_dataset.json"
    )
    
    if updated_dataset:
        # 결과 저장
        save_updated_dataset(updated_dataset, "aac_dataset_combination.json")