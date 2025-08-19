SERVICE_CONFIG = {
    # OpenAI API 설정
    'openai_model': 'gpt-4o-2024-08-06',
    'openai_temperature': 0.8,
    'interpretation_max_tokens': 400,
    'summary_max_tokens': 200,
    'api_timeout': 15,
    
    # 데이터 파일 경로
    'users_file_path': 'user_data/users.json',
    'feedback_file_path': 'user_data/feedback.json', 
    'memory_file_path': 'user_data/conversation_memory.json',
    
    # 클러스터 파일 경로
    'cluster_tags_path': 'dataset/processed/cluster_tags.json',
    'embeddings_path': 'dataset/processed/embeddings.json', 
    'clustering_results_path': 'dataset/processed/clustering_results.json',
    
    # 네트워크 및 성능 설정
    'network_timeout': 10,
    'max_retry_attempts': 3,
    'request_delay': 1,
    
    # 시스템 설정
    'max_conversation_history': 50,
    'similarity_threshold': 0.7,
}