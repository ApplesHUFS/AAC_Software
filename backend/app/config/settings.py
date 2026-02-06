"""
애플리케이션 설정 관리
Pydantic Settings를 사용하여 환경변수와 기본값을 통합 관리
"""

from functools import lru_cache
from pathlib import Path
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """애플리케이션 전역 설정"""

    # 프로젝트 경로
    project_root: Path = Field(
        default_factory=lambda: Path(__file__).parent.parent.parent.parent
    )

    # OpenAI API 설정 (Responses API 사용)
    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    openai_model: str = "gpt-4.1"
    openai_filter_model: str = "gpt-4.1-mini"
    openai_temperature: float = 0.8
    interpretation_max_tokens: int = 400
    summary_max_tokens: int = 200
    api_timeout: int = 15

    # 서버 설정
    host: str = "0.0.0.0"
    port: int = 8001
    debug: bool = False

    # CORS 설정 (쉼표로 구분된 문자열)
    allowed_origins_str: str = Field(
        default="http://localhost:3001,http://127.0.0.1:3001",
        alias="ALLOWED_ORIGINS",
    )

    @property
    def allowed_origins(self) -> List[str]:
        """CORS 허용 오리진 리스트"""
        return [origin.strip() for origin in self.allowed_origins_str.split(",") if origin.strip()]

    # 카드 추천 설정
    display_cards_total: int = 20

    # 카드 선택 및 해석
    min_card_selection: int = 1
    max_card_selection: int = 4
    interpretation_count: int = 3

    # 시스템 성능
    max_conversation_history: int = 50
    memory_pattern_limit: int = 5

    # 사용자 검증
    valid_genders: List[str] = ["남성", "여성"]
    valid_disability_types: List[str] = ["의사소통장애", "자폐스펙트럼장애", "지적장애"]
    min_age: int = 1
    max_age: int = 100

    # GPU/CPU 설정
    device: str = "auto"

    # CLIP 추천 시스템 설정
    use_clip_recommendation: bool = True
    clip_model: str = "openai/clip-vit-large-patch14"
    clip_image_weight: float = 0.8  # 이미지-텍스트 임베딩 융합 가중치

    # 추천 점수 가중치 (합계 = 1.0)
    semantic_weight: float = 0.5   # CLIP 시맨틱 유사도
    diversity_weight: float = 0.2  # MMR 다양성
    persona_weight: float = 0.3    # 사용자 선호

    # MMR 파라미터
    mmr_lambda: float = 0.6  # 관련성(1.0) vs 다양성(0.0) 균형

    # LLM 필터 설정
    enable_llm_filter: bool = True
    enable_llm_reranker: bool = True
    filter_batch_size: int = 40
    rerank_batch_size: int = 30
    filter_temperature: float = 0.3
    rerank_temperature: float = 0.2
    filter_max_tokens: int = 2000
    rerank_max_tokens: int = 1200
    filter_max_retries: int = 3

    # 데이터 정리
    default_cleanup_days: int = 30
    feedback_cleanup_days: int = 7

    @property
    def dataset_root(self) -> Path:
        """데이터셋 루트 경로"""
        return self.project_root / "dataset"

    @property
    def user_data_root(self) -> Path:
        """사용자 데이터 루트 경로"""
        return self.project_root / "user_data"

    @property
    def images_folder(self) -> Path:
        """이미지 폴더 경로"""
        return self.dataset_root / "images"

    @property
    def users_file_path(self) -> Path:
        """사용자 데이터 파일 경로"""
        return self.user_data_root / "users.json"

    @property
    def feedback_file_path(self) -> Path:
        """피드백 데이터 파일 경로"""
        return self.user_data_root / "feedback.json"

    @property
    def memory_file_path(self) -> Path:
        """대화 메모리 파일 경로"""
        return self.user_data_root / "conversation_memory.json"

    @property
    def embeddings_path(self) -> Path:
        """CLIP 임베딩 파일 경로"""
        return self.dataset_root / "processed" / "embeddings.json"

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


@lru_cache
def get_settings() -> Settings:
    """설정 싱글톤 반환"""
    return Settings()
