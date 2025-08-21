DATASET_CONFIG = {
    # 기본 경로
    'images_folder': 'dataset/images',
    'persona_json_path': 'dataset/persona.json',
    'output_folder': 'dataset/processed',

    # 데이터셋 설정
    'samples_per_persona': 200,
    'n_clusters': 64,

    # 페르소나 기반 카드 선택
    'persona_preference_ratio': 0.9,
    'persona_topic_ratio': 0.7,
    'topic_similarity_threshold': 0.75,
    'similarity_threshold': 0.5,
    'card_min_similarity': 0.3,

    # 클러스터 태깅
    'cluster_medoid_count': 3,

    # 파이프라인 옵션
    'show_sample': True,
    'skip_openai': False,
    'overwrite_mode': False,
    'filter_confirm': True,
    'visualize_clusters': True,
    'save_interval': 10,
    'enable_error_recovery': True,

    # OpenAI API
    'openai_model': 'gpt-4o-2024-08-06',
    'openai_temperature': 0.8,
    'context_max_tokens': 300,
    'interpretation_max_tokens': 400,
    'request_delay': 1,

    # GPU/CPU 설정
    'device': 'auto',  # 'auto', 'cuda', 'cpu'

    # CLIP 인코딩
    'clip_model': 'openai/clip-vit-base-patch32',

    # 클러스터링
    'clustering_random_state': 42,
    'clustering_n_init': 10,

    # 텍스트 유사도 모델
    'similarity_model': 'Snowflake/snowflake-arctic-embed-l',
}
