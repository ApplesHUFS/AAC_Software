"""AAC 클러스터링 시스템 설정"""

DATASET_CONFIG = {
    # 기본 경로
    'images_folder': 'dataset/images',
    'output_folder': 'dataset/processed',

    # 임베딩 설정
    'image_weight': 0.6,  # 이미지 가중치 (AAC 카드는 시각적 요소가 중요)
    'clip_model': 'openai/clip-vit-large-patch14',

    # 계층적 클러스터링 설정
    'macro_min_clusters': 20,    # 대분류 최소 개수
    'macro_max_clusters': 100,    # 대분류 최대 개수
    'min_cluster_size': 30,      # 분할 가능한 최소 크기
    'max_micro_clusters': 6,     # 대분류당 최대 세분화 수

    # 이미지 필터링
    'filter_confirm': True,

    # 파이프라인 옵션
    'visualize_clusters': True,
    'overwrite_mode': False,

    # OpenAI API (태깅용)
    'openai_model': 'gpt-4o-2024-08-06',
    'openai_temperature': 0.2,   # 일관된 태깅을 위해 낮게 설정
    'request_delay': 1.0,

    # GPU/CPU 설정
    'device': 'auto',

    # 클러스터 태깅
    'cluster_medoid_count': 5,   # 더 정확한 태깅 위함.

    # 유사도 모델
    'similarity_model': 'Snowflake/snowflake-arctic-embed-l',

    # 선호 카테고리 할당
    'similarity_threshold': 0.45,    # 더 엄격한 유사도 기준
    'required_cluster_count': 6,     # AAC 사용자 관리 가능한 카테고리 수

    # 레거시 호환성
    'n_clusters': None,  # None이면 자동 결정
}


def validate_config(config: dict) -> bool:
    """설정 유효성 검사.
    
    필수 설정 항목들이 모두 존재하는지 확인하고,
    데이터 크기와 하이퍼파라미터 관계의 일관성을 검증합니다.
    
    Args:
        config: 검증할 설정 딕셔너리
        
    Returns:
        bool: 설정이 유효한 경우 True
        
    Raises:
        ValueError: 필수 설정이 누락되거나 값이 부적절한 경우
    """
    required_keys = ['images_folder', 'output_folder', 'clip_model']
    
    for key in required_keys:
        if key not in config:
            raise ValueError(f"필수 설정 누락: {key}")
    
    # 클러스터링 설정 검증
    if config['macro_min_clusters'] >= config['macro_max_clusters']:
        raise ValueError("macro_min_clusters는 macro_max_clusters보다 작아야 합니다")
    
    if config['min_cluster_size'] < 10:
        raise ValueError("min_cluster_size는 통계적 안정성을 위해 10 이상이어야 합니다")
    
    if config['similarity_threshold'] < 0.0 or config['similarity_threshold'] > 1.0:
        raise ValueError("similarity_threshold는 0.0과 1.0 사이 값이어야 합니다")
    
    if config['image_weight'] < 0.0 or config['image_weight'] > 1.0:
        raise ValueError("image_weight는 0.0과 1.0 사이 값이어야 합니다")
    
    return True


if __name__ == "__main__":
    validate_config(DATASET_CONFIG)
    print("4000개 이미지 데이터셋 최적화 설정 완료")