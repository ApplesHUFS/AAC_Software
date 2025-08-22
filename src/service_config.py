"""
AAC Interpreter Service 설정 파일

이 파일은 AAC 카드 해석 시스템의 모든 설정값을 정의합니다.
각 설정값은 시스템의 특정 기능과 연결되어 있으며,
잘못된 설정은 시스템 오류를 발생시킬 수 있습니다.

주의사항:
- 모든 파일 경로는 실제 존재하는 경로여야 합니다
- OpenAI API 키는 환경변수 OPENAI_API_KEY로 설정되어야 합니다
- 클러스터 관련 파일들이 없으면 해당 기능이 비활성화됩니다
"""

SERVICE_CONFIG = {
    # ===== OpenAI API 설정 =====
    # GPT-4 Vision 모델을 사용하여 AAC 카드 이미지 해석
    'openai_model': 'gpt-4o-2024-08-06',
    'openai_temperature': 0.8,  # 창의적 해석을 위한 높은 온도
    'interpretation_max_tokens': 400,  # 해석당 최대 토큰 수
    'summary_max_tokens': 200,   # 메모리 요약용 최대 토큰 수
    'api_timeout': 15,           # API 호출 타임아웃 (초)

    # ===== 파일 경로 설정 =====
    # AAC 카드 이미지 폴더 - PNG 파일들이 저장된 위치
    'images_folder': 'dataset/images',

    # 사용자 및 시스템 데이터 파일 경로
    'users_file_path': 'user_data/users.json',
    'feedback_file_path': 'user_data/feedback.json',
    'memory_file_path': 'user_data/conversation_memory.json',

    # 클러스터링 및 AI 모델 데이터 파일 경로
    # 이 파일들이 없으면 관련 기능이 비활성화됩니다
    'cluster_tags_path': 'dataset/processed/cluster_tags.json',
    'embeddings_path': 'dataset/processed/embeddings.json',
    'clustering_results_path': 'dataset/processed/clustering_results.json',

    # ===== 카드 추천 시스템 설정 =====
    'display_cards_total': 20,         # 화면에 표시할 총 카드 수 (고정값)
    'recommendation_ratio': 0.7,       # 추천 카드 비율 (70% 추천, 30% 랜덤)
    'cluster_count': 6,                # 전체 클러스터 수

    # ===== 카드 선택 및 해석 설정 =====
    'min_card_selection': 1,           # 최소 선택 카드 수
    'max_card_selection': 4,           # 최대 선택 카드 수
    'interpretation_count': 3,         # 생성할 해석 수 (고정값)

    # ===== 시스템 성능 및 제한 설정 =====
    'max_conversation_history': 50,    # 최대 대화 기록 수 (메모리 관리)
    'memory_pattern_limit': 5,         # 메모리 패턴 조회 제한

    # ===== 사용자 페르소나 검증 설정 =====
    # 이 값들은 사용자 등록시 엄격하게 검증됩니다
    'valid_genders': ['male', 'female'],
    'valid_disability_types': [
        '의사소통장애',
        '자폐스펙트럼장애',
        '지적장애'
    ],
    'min_age': 1,                      # 최소 연령
    'max_age': 100,                    # 최대 연령
    'required_cluster_count': 6,       # preferred_category_types에 필요한 클러스터 수 (고정값)

    # ===== 클러스터 유사도 계산 설정 =====
    # 한국어 문장 임베딩 모델 - 관심사와 클러스터 태그 간 유사도 계산
    'similarity_model': 'jhgan/ko-sroberta-multitask',
    'similarity_threshold': 0.3,       # 클러스터 유사도 임계값 (0.0-1.0)
    'device': 'auto',                  # 연산 디바이스 ('auto', 'cpu', 'cuda')

    # ===== 데이터 정리 설정 =====
    'default_cleanup_days': 30,        # 기본 데이터 정리 주기 (일)
    'feedback_cleanup_days': 7,        # 피드백 요청 정리 주기 (일)
}

# ===== 설정 검증 함수 =====
def validate_config(config: dict) -> tuple[bool, list[str]]:
    """
    설정값 유효성 검증

    Args:
        config: 검증할 설정 딕셔너리

    Returns:
        tuple: (검증 성공 여부, 오류 메시지 리스트)
    """
    errors = []

    # 필수 설정값 검증
    required_keys = [
        'openai_model', 'images_folder', 'users_file_path',
        'display_cards_total', 'min_card_selection', 'max_card_selection',
        'interpretation_count', 'required_cluster_count'
    ]

    for key in required_keys:
        if key not in config:
            errors.append(f"필수 설정 '{key}'가 누락되었습니다.")

    # 숫자 범위 검증
    if config.get('min_age', 1) >= config.get('max_age', 100):
        errors.append("min_age는 max_age보다 작아야 합니다.")

    if config.get('min_card_selection', 1) > config.get('max_card_selection', 4):
        errors.append("min_card_selection은 max_card_selection보다 작거나 같아야 합니다.")

    if config.get('similarity_threshold', 0.3) < 0 or config.get('similarity_threshold', 0.3) > 1:
        errors.append("similarity_threshold는 0.0과 1.0 사이여야 합니다.")

    # 비율 검증
    if config.get('recommendation_ratio', 0.7) < 0 or config.get('recommendation_ratio', 0.7) > 1:
        errors.append("recommendation_ratio는 0.0과 1.0 사이여야 합니다.")

    # 고정값 검증
    if config.get('interpretation_count', 3) != 3:
        errors.append("interpretation_count는 3이어야 합니다.")

    if config.get('required_cluster_count', 6) != 6:
        errors.append("required_cluster_count는 6이어야 합니다.")

    if config.get('display_cards_total', 20) != 20:
        errors.append("display_cards_total은 20이어야 합니다.")

    # 리스트 설정 검증
    valid_genders = config.get('valid_genders', [])
    if not isinstance(valid_genders, list) or len(valid_genders) == 0:
        errors.append("valid_genders는 비어있지 않은 리스트여야 합니다.")

    valid_disability_types = config.get('valid_disability_types', [])
    if not isinstance(valid_disability_types, list) or len(valid_disability_types) == 0:
        errors.append("valid_disability_types는 비어있지 않은 리스트여야 합니다.")

    return len(errors) == 0, errors


def get_critical_files(config: dict) -> list[str]:
    """
    시스템 동작에 중요한 파일 경로 목록 반환

    Args:
        config: 설정 딕셔너리

    Returns:
        list: 중요한 파일 경로 리스트
    """
    return [
        config.get('images_folder', 'dataset/images'),
        config.get('cluster_tags_path', 'dataset/processed/cluster_tags.json'),
        config.get('clustering_results_path', 'dataset/processed/clustering_results.json')
    ]


def get_optional_files(config: dict) -> list[str]:
    """
    선택적 파일 경로 목록 반환 (없어도 시스템 동작 가능)

    Args:
        config: 설정 딕셔너리

    Returns:
        list: 선택적 파일 경로 리스트
    """
    return [
        config.get('embeddings_path', 'dataset/processed/embeddings.json')
    ]


# 설정 검증 실행
if __name__ == "__main__":
    import os

    print("=== AAC Service Configuration 검증 ===")

    # 설정값 검증
    is_valid, validation_errors = validate_config(SERVICE_CONFIG)

    if not is_valid:
        print("✗ 설정 검증 실패:")
        for error in validation_errors:
            print(f"  - {error}")
    else:
        print("✓ 설정 검증 성공")

    # 파일 존재 여부 확인
    print("\n=== 파일 존재 여부 확인 ===")

    critical_files = get_critical_files(SERVICE_CONFIG)
    optional_files = get_optional_files(SERVICE_CONFIG)

    print("중요한 파일들:")
    for file_path in critical_files:
        if os.path.exists(file_path):
            print(f"  ✓ {file_path}")
        else:
            print(f"  ✗ {file_path} (시스템 기능 제한됨)")

    print("\n선택적 파일들:")
    for file_path in optional_files:
        if os.path.exists(file_path):
            print(f"  ✓ {file_path}")
        else:
            print(f"  - {file_path} (없음)")

    # 환경 변수 확인
    print("\n=== 환경 변수 확인 ===")
    if os.getenv('OPENAI_API_KEY'):
        print("  ✓ OPENAI_API_KEY 설정됨")
    else:
        print("  ✗ OPENAI_API_KEY 설정되지 않음 (카드 해석 기능 비활성화)")
