SERVICE_CONFIG = {
    # OpenAI API 설정
    'openai_model': 'gpt-4o-2024-08-06',
    'openai_temperature': 0.8,
    'interpretation_max_tokens': 400,
    'summary_max_tokens': 200,
    'api_timeout': 15,

    # 이미지 폴더 경로
    'images_folder': 'dataset/images',

    # 데이터 파일 경로
    'users_file_path': 'user_data/users.json',
    'feedback_file_path': 'user_data/feedback.json',
    'memory_file_path': 'user_data/conversation_memory.json',

    # 클러스터 파일 경로 (전처리된 데이터)
    'cluster_tags_path': 'dataset/processed/cluster_tags.json',
    'embeddings_path': 'dataset/processed/embeddings.json',
    'clustering_results_path': 'dataset/processed/clustering_results.json',

    # 카드 추천 설정
    'display_cards_total': 20,         # 화면에 표시할 총 카드 수
    'recommendation_ratio': 0.7,       # 추천 카드 비율 (70%)
    'cluster_count': 6,                # 사용할 클러스터 수

    # 카드 선택 설정
    'min_card_selection': 1,           # 최소 선택 카드 수
    'max_card_selection': 4,           # 최대 선택 카드 수

    # 해석 설정
    'interpretation_count': 3,         # 생성할 해석 수

    # 시스템 설정
    'max_conversation_history': 50,    # 최대 대화 기록 수
    'memory_pattern_limit': 5,         # 메모리 패턴 조회 제한

    # 사용자 페르소나 검증
    'valid_genders': ['male', 'female'],
    'valid_disability_types': ['의사소통 장애', '자폐스펙트럼 장애', '지적 장애'],
    'min_age': 1,
    'max_age': 100,
    'required_cluster_count': 6,       # preferred_category_types에 필요한 클러스터 수

    # 클러스터 유사도 계산 설정
    'similarity_model': 'jhgan/ko-sroberta-multitask',  # 한국어 문장 임베딩 모델
    'similarity_threshold': 0.3,       # 클러스터 유사도 임계값
    'device': 'auto',                  # 연산 디바이스 (auto, cpu, cuda)
}
