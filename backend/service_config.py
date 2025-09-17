"""
AAC Interpreter Service 설정 파일
"""

from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
DATASET_ROOT = PROJECT_ROOT / "dataset"
USER_DATA_ROOT = PROJECT_ROOT / "user_data"

SERVICE_CONFIG = {
    # OpenAI API 설정
    "openai_model": "gpt-4o-2024-08-06",
    "openai_temperature": 0.8,
    "interpretation_max_tokens": 400,
    "summary_max_tokens": 200,
    "api_timeout": 15,
    # 파일 경로
    "images_folder": str(DATASET_ROOT / "images"),
    "users_file_path": str(USER_DATA_ROOT / "users.json"),
    "feedback_file_path": str(USER_DATA_ROOT / "feedback.json"),
    "memory_file_path": str(USER_DATA_ROOT / "conversation_memory.json"),
    "cluster_tags_path": str(DATASET_ROOT / "processed" / "cluster_tags.json"),
    "embeddings_path": str(DATASET_ROOT / "processed" / "embeddings.json"),
    "clustering_results_path": str(
        DATASET_ROOT / "processed" / "clustering_results.json"
    ),
    # 카드 추천 시스템
    "display_cards_total": 20,
    # 카드 추천 알고리즘 설정
    "context_similarity_threshold": 0.25,
    "context_max_clusters": 8,
    "persona_similarity_threshold": 0.3,
    "persona_max_clusters": 8,
    "context_persona_ratio": 0.5,  # 상황:페르소나 = 0.5:0.5
    # 카드 선택 및 해석
    "min_card_selection": 1,
    "max_card_selection": 4,
    "interpretation_count": 3,
    # 시스템 성능
    "max_conversation_history": 50,
    "memory_pattern_limit": 5,
    # 사용자 페르소나 검증
    "required_fields": [
        "age",
        "gender",
        "disability_type",
        "communication_characteristics",
        "interesting_topics",
        "preferred_category_types",
        "password",
    ],
    "valid_genders": ["남성", "여성"],
    "valid_disability_types": ["의사소통장애", "자폐스펙트럼장애", "지적장애"],
    "min_age": 1,
    "max_age": 100,
    "required_cluster_count": 6,
    # 클러스터 유사도 계산
    "similarity_model": "dragonkue/BGE-m3-ko",
    "similarity_threshold": 0.5,
    "device": "auto",
    # 데이터 정리
    "default_cleanup_days": 30,
    "feedback_cleanup_days": 7,
}
