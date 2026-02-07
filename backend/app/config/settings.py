"""
애플리케이션 설정 관리
Pydantic Settings를 사용하여 환경변수와 기본값을 통합 관리
"""

from functools import lru_cache
from pathlib import Path
from typing import List

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


class RecommendationConfig(BaseModel):
    """카드 추천 알고리즘 설정"""

    semantic_weight: float = 0.5  # CLIP 시맨틱 유사도 가중치
    diversity_weight: float = 0.2  # MMR 다양성 가중치
    persona_weight: float = 0.3  # 사용자 선호 가중치
    mmr_lambda: float = 0.6  # 관련성(1.0) vs 다양성(0.0) 균형
    initial_search_multiplier: int = 10  # Stage 1 초기 검색 배수
    diversity_selection_multiplier: int = 4  # Stage 2 MMR 선택 배수
    top_k: int = 20  # 최종 추천 카드 수


class LLMConfig(BaseModel):
    """LLM 관련 설정"""

    model: str = "gpt-4.1"  # 기본 LLM 모델
    filter_model: str = "gpt-4.1-mini"  # 필터용 경량 모델
    temperature: float = 0.8  # 생성 다양성
    enable_filter: bool = True  # LLM 적합성 필터 활성화
    enable_reranker: bool = True  # LLM 재순위화 활성화
    filter_batch_size: int = 40  # 필터 배치 크기
    rerank_batch_size: int = 30  # 재순위화 배치 크기
    filter_temperature: float = 0.3  # 필터링 시 temperature
    rerank_temperature: float = 0.2  # 재순위화 시 temperature
    filter_max_tokens: int = 2000  # 필터 응답 최대 토큰
    rerank_max_tokens: int = 1200  # 재순위화 응답 최대 토큰
    filter_max_retries: int = 3  # 필터 재시도 횟수
    interpretation_max_tokens: int = 400  # 해석 생성 최대 토큰
    summary_max_tokens: int = 200  # 요약 생성 최대 토큰
    api_timeout: int = 15  # API 타임아웃 (초)


class FeedbackConfig(BaseModel):
    """피드백 학습 설정 (Contextual Relevance Feedback)"""

    enable_learning: bool = True  # 피드백 기반 학습 활성화
    min_similarity: float = 0.3  # 유사 피드백 최소 유사도
    decay_days: int = 30  # 피드백 시간 감쇠 (일)
    weight: float = 0.4  # 피드백 쿼리 가중치


class QueryRewriteConfig(BaseModel):
    """쿼리 재작성 설정"""

    enabled: bool = True  # LLM 기반 쿼리 재작성 활성화
    count: int = 3  # 생성할 추가 쿼리 수
    max_tokens: int = 300  # 쿼리 재작성 최대 토큰


class Settings(BaseSettings):
    """애플리케이션 전역 설정"""

    # 버전 정보 (SSOT)
    VERSION: str = "2.0.0"

    # 환경 설정
    environment: str = Field(default="development", alias="ENVIRONMENT")

    # 프로젝트 경로
    project_root: Path = Field(
        default_factory=lambda: Path(__file__).parent.parent.parent.parent
    )

    # OpenAI API 설정
    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")

    # JWT 설정
    jwt_secret_key: str = Field(default="", alias="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    jwt_access_expire_minutes: int = Field(default=30, alias="JWT_ACCESS_EXPIRE_MINUTES")
    jwt_refresh_expire_days: int = Field(default=7, alias="JWT_REFRESH_EXPIRE_DAYS")

    # Rate Limiting 설정
    rate_limit_login: str = Field(default="5/minute", alias="RATE_LIMIT_LOGIN")
    rate_limit_api: str = Field(default="100/minute", alias="RATE_LIMIT_API")

    # 서버 설정
    host: str = "0.0.0.0"
    port: int = 8001
    debug: bool = False

    @property
    def is_production(self) -> bool:
        """프로덕션 환경 여부"""
        return self.environment.lower() == "production"

    @property
    def debug_mode(self) -> bool:
        """디버그 모드 (프로덕션에서는 항상 False)"""
        return False if self.is_production else self.debug

    # 로깅 설정
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    log_format: str = Field(default="console", alias="LOG_FORMAT")

    # CORS 설정 (쉼표로 구분된 문자열)
    allowed_origins_str: str = Field(
        default="http://localhost:3001,http://127.0.0.1:3001",
        alias="ALLOWED_ORIGINS",
    )
    # 프로덕션용 CORS 설정
    allowed_origins_production_str: str = Field(
        default="",
        alias="ALLOWED_ORIGINS_PRODUCTION",
    )

    @property
    def allowed_origins(self) -> List[str]:
        """환경에 따른 CORS 허용 오리진 리스트"""
        if self.is_production:
            origins_str = self.allowed_origins_production_str
            if not origins_str:
                return []  # 프로덕션에서 설정 없으면 빈 리스트 (모두 차단)
        else:
            origins_str = self.allowed_origins_str
        return [origin.strip() for origin in origins_str.split(",") if origin.strip()]

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

    # 데이터 정리
    default_cleanup_days: int = 30
    feedback_cleanup_days: int = 7

    # 설정 그룹
    recommendation: RecommendationConfig = Field(default_factory=RecommendationConfig)
    llm: LLMConfig = Field(default_factory=LLMConfig)
    feedback: FeedbackConfig = Field(default_factory=FeedbackConfig)
    query_rewrite: QueryRewriteConfig = Field(default_factory=QueryRewriteConfig)

    # 하위 호환성 프로퍼티 (기존 코드 지원)
    @property
    def openai_model(self) -> str:
        return self.llm.model

    @property
    def openai_filter_model(self) -> str:
        return self.llm.filter_model

    @property
    def openai_temperature(self) -> float:
        return self.llm.temperature

    @property
    def interpretation_max_tokens(self) -> int:
        return self.llm.interpretation_max_tokens

    @property
    def summary_max_tokens(self) -> int:
        return self.llm.summary_max_tokens

    @property
    def api_timeout(self) -> int:
        return self.llm.api_timeout

    @property
    def semantic_weight(self) -> float:
        return self.recommendation.semantic_weight

    @property
    def diversity_weight(self) -> float:
        return self.recommendation.diversity_weight

    @property
    def persona_weight(self) -> float:
        return self.recommendation.persona_weight

    @property
    def mmr_lambda(self) -> float:
        return self.recommendation.mmr_lambda

    @property
    def initial_search_multiplier(self) -> int:
        return self.recommendation.initial_search_multiplier

    @property
    def diversity_selection_multiplier(self) -> int:
        return self.recommendation.diversity_selection_multiplier

    @property
    def enable_query_rewriting(self) -> bool:
        return self.query_rewrite.enabled

    @property
    def query_rewrite_count(self) -> int:
        return self.query_rewrite.count

    @property
    def query_rewrite_max_tokens(self) -> int:
        return self.query_rewrite.max_tokens

    @property
    def enable_feedback_learning(self) -> bool:
        return self.feedback.enable_learning

    @property
    def feedback_min_similarity(self) -> float:
        return self.feedback.min_similarity

    @property
    def feedback_decay_days(self) -> int:
        return self.feedback.decay_days

    @property
    def feedback_weight(self) -> float:
        return self.feedback.weight

    @property
    def enable_llm_filter(self) -> bool:
        return self.llm.enable_filter

    @property
    def enable_llm_reranker(self) -> bool:
        return self.llm.enable_reranker

    @property
    def filter_batch_size(self) -> int:
        return self.llm.filter_batch_size

    @property
    def rerank_batch_size(self) -> int:
        return self.llm.rerank_batch_size

    @property
    def filter_temperature(self) -> float:
        return self.llm.filter_temperature

    @property
    def rerank_temperature(self) -> float:
        return self.llm.rerank_temperature

    @property
    def filter_max_tokens(self) -> int:
        return self.llm.filter_max_tokens

    @property
    def rerank_max_tokens(self) -> int:
        return self.llm.rerank_max_tokens

    @property
    def filter_max_retries(self) -> int:
        return self.llm.filter_max_retries

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
