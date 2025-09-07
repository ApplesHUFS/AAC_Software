DATASET_CONFIG = {
    # 기본 경로
    'images_folder': 'dataset/images',
    'output_folder': 'dataset/processed',

    # 클러스터링 설정
    'n_clusters': 64,

    # 이미지 필터링 옵션
    'filter_confirm': True,

    # 파이프라인 옵션
    'visualize_clusters': True,
    'overwrite_mode': False,

    # OpenAI API (클러스터 태깅용)
    'openai_model': 'gpt-4o-2024-08-06',
    'openai_temperature': 0.8,
    'request_delay': 1,

    # GPU/CPU 설정
    'device': 'auto',  # 'auto', 'cuda', 'cpu'

    # CLIP 인코딩
    'clip_model': 'openai/clip-vit-base-patch32',

    # 클러스터링 알고리즘 설정
    'clustering_random_state': 42,
    'clustering_n_init': 10,

    # 클러스터 태깅 설정
    'cluster_medoid_count': 3,

    # 텍스트 유사도 모델 (클러스터 태깅용)
    'similarity_model': 'Snowflake/snowflake-arctic-embed-l',
}