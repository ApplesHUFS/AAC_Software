SERVICE_CONFIG = {
    # OpenAI API 설정
    'openai_model': 'gpt-4o-2024-08-06',
    'openai_temperature': 0.8,
    'interpretation_max_tokens': 400,
    'summary_max_tokens': 200,
    'api_timeout': 15,
    
    # 데이터 파일 경로 (사용자, 피드백, 메모리)
    'users_file_path': 'user_data/users.json',
    'feedback_file_path': 'user_data/feedback.json', 
    'memory_file_path': 'user_data/conversation_memory.json',
    'logs_directory': 'logs/',
    'backup_directory': 'backup/',
    
    # 클러스터 파일 경로 (처리된 데이터 위치)
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
    'offline_db_path': 'user_data/offline_interpretations.json',
    
    # 로깅 설정
    'log_level': 'INFO',
    'enable_detailed_logging': True,
    'log_file_max_size': '10MB',
    'log_retention_days': 30,
}