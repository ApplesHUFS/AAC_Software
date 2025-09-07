"""AAC 클러스터링 시스템 설정"""

DATASET_CONFIG = {
    # 기본 경로
    'images_folder': 'dataset/images',
    'output_folder': 'dataset/processed',

    # 임베딩 설정
    'image_weight': 0.7,  # 이미지 가중치 (나머지는 텍스트)
    'clip_model': 'openai/clip-vit-base-patch32',

    # 계층적 클러스터링 설정
    'macro_min_clusters': 8,     # 대분류 최소 개수
    'macro_max_clusters': 20,    # 대분류 최대 개수
    'min_cluster_size': 15,      # 분할 가능한 최소 크기
    'max_micro_clusters': 8,     # 대분류당 최대 세분화 수

    # 이미지 필터링
    'filter_confirm': True,

    # 파이프라인 옵션
    'visualize_clusters': True,
    'overwrite_mode': False,

    # OpenAI API (태깅용)
    'openai_model': 'gpt-4o-2024-08-06',
    'openai_temperature': 0.3,
    'request_delay': 1,

    # GPU/CPU 설정
    'device': 'auto',

    # 클러스터 태깅
    'cluster_medoid_count': 3,

    # 유사도 모델
    'similarity_model': 'Snowflake/snowflake-arctic-embed-l',

    # 선호 카테고리 할당
    'similarity_threshold': 0.3,
    'required_cluster_count': 6,

    # 레거시 호환성
    'n_clusters': None,  # None이면 자동 결정
}


def validate_config(config: dict) -> bool:
    """설정 유효성 검사"""
    required_keys = ['images_folder', 'output_folder', 'clip_model']
    
    for key in required_keys:
        if key not in config:
            raise ValueError(f"필수 설정 누락: {key}")
    
    return True


if __name__ == "__main__":
    validate_config(DATASET_CONFIG)
    print("5000개 이미지 데이터셋 설정 완료")