DATASET_CONFIG = {
    # 기본 경로 설정
    'images_folder': 'dataset/images',                      # AAC 카드 이미지 폴더 경로
    'persona_json_path': 'dataset/persona.json',            # 페르소나 정의 JSON 파일 경로
    'output_folder': 'dataset/processed',                   # 처리된 데이터 출력 폴더

    # 데이터셋 생성 설정
    'samples_per_persona': 200,                             # 페르소나당 생성할 샘플 수
    'n_clusters': 120,                                       # K-means 클러스터 개수

    # 기존 카드 조합 생성 설정 (legacy - 사용 안함)
    'similarity_threshold': 0.5,                            # 클러스터 간 유사도 임계값
    'card_min_similarity': 0.3,                             # 카드 간 최소 유사도
    'card_count_distribution': [0.35, 0.4, 0.2, 0.05],     # 카드 개수별 확률 분포 [1개, 2개, 3개, 4개]
    'reset_card_usage': True,                               # 카드 사용 횟수 초기화 여부

    # 새로운 페르소나 기반 카드 선택 설정
    'persona_preference_ratio': 0.9,                        # 페르소나 선호 클러스터 사용 비율 (90%)
    'persona_topic_ratio': 0.7,                             # 관심 주제 관련 카드 선택 비율 (70%)
    'topic_similarity_threshold': 0.6,                      # 주제 유사도 임계값
    'complexity_mapping': {                                  # 복잡도별 카드 개수 범위
        'simple': (1, 2),
        'moderate': (1, 3),
        'complex': (2, 4)
    },

    # 클러스터 태깅 설정
    'cluster_medoid_count': 3,                              # 클러스터당 medoid 개수
    'cluster_tag_model': 'gpt-4o-2024-08-06',              # 클러스터 태깅용 모델
    'cluster_tag_temperature': 0.3,                         # 클러스터 태깅 온도

    # 파이프라인 실행 옵션
    'show_sample': True,                                    # 샘플 출력 여부
    'skip_openai': False,                                   # OpenAI API 호출 건너뛰기
    'overwrite_mode': False,                                # 기존 데이터 덮어쓰기 모드
    'filter_confirm': True,                                 # 이미지 필터링 시 확인 요청
    'visualize_clusters': True,                             # 클러스터링 결과 시각화
    'save_interval': 10,                                    # 중간 저장 간격
    'enable_error_recovery': True,                          # 오류 복구 모드 활성화

    # OpenAI API 설정
    'openai_model': 'gpt-4o-2024-08-06',                   # 사용할 OpenAI 모델
    'openai_temperature': 0.8,                             # 생성 온도 (창의성 조절)
    'context_max_tokens': 300,                             # 컨텍스트 생성 최대 토큰
    'interpretation_max_tokens': 400,                       # 해석 생성 최대 토큰
    'request_delay': 1,                                     # API 요청 간 지연 시간 (초)

    # CLIP 인코딩 설정
    'clip_model': 'openai/clip-vit-base-patch32',          # 사용할 CLIP 모델
    'device': 'auto',                                       # 사용할 디바이스 ('auto', 'cuda', 'cpu')

    # 클러스터링 설정
    'clustering_random_state': 42,                          # 클러스터링 랜덤 시드
    'clustering_n_init': 10,                               # K-means 초기화 횟수

    # 페르소나 확장 모드
    'use_persona_based_selection': True,                    # 페르소나 기반 카드 선택 사용 여부
    'enable_cluster_tagging': True,                         # 클러스터 태깅 활성화 여부
    'persona_assignment_batch_size': 50,                    # 페르소나 할당 배치 크기 (LLM 호출 최적화)
}
