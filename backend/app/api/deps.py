"""의존성 주입 모듈"""

from functools import lru_cache
from typing import Annotated, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.config.settings import Settings, get_settings
from app.core.security import TokenService, get_token_service
from app.domain.user.entity import User
from app.domain.user.service import UserService
from app.domain.context.service import ContextService
from app.domain.card.service import CardService
from app.domain.card.recommender import CardRecommender
from app.domain.feedback.service import FeedbackService
from app.domain.feedback.analyzer import (
    IFeedbackAnalyzer,
    TFIDFFeedbackAnalyzer,
    NoOpFeedbackAnalyzer,
)
from app.domain.feedback.visual_analyzer import (
    IVisualPatternAnalyzer,
    CLIPVisualPatternAnalyzer,
    NoOpVisualPatternAnalyzer,
)
from app.infrastructure.persistence.json_repository import (
    JsonUserRepository,
    JsonCardRepository,
    JsonFeedbackRepository,
)
from app.infrastructure.persistence.memory_repository import (
    InMemoryContextRepository,
    InMemoryCardHistoryRepository,
    InMemoryFeedbackRequestRepository,
)
from app.infrastructure.persistence.combined_repository import CombinedFeedbackRepository
from app.infrastructure.external.openai_client import OpenAIClient
from app.infrastructure.external.clip_client import CLIPEmbeddingClient
from app.domain.card.vector_searcher import FaissVectorIndex, create_vector_index
from app.domain.card.interfaces import IVectorIndex
from app.domain.card.diversity_selector import MMRDiversitySelector


# 설정
SettingsDep = Annotated[Settings, Depends(get_settings)]

# HTTP Bearer 인증 스키마
http_bearer = HTTPBearer(auto_error=False)


# 인증 의존성
async def get_current_user(
    credentials: Annotated[Optional[HTTPAuthorizationCredentials], Depends(http_bearer)],
    token_service: TokenService = Depends(get_token_service),
    user_repo: "JsonUserRepository" = Depends(lambda: get_user_repository()),
) -> User:
    """현재 인증된 사용자 반환

    Raises:
        HTTPException: 401 인증 실패
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="인증 정보가 필요합니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = token_service.verify_token(credentials.credentials)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 토큰입니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = await user_repo.find_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="사용자를 찾을 수 없습니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


async def get_current_user_optional(
    credentials: Annotated[Optional[HTTPAuthorizationCredentials], Depends(http_bearer)],
    token_service: TokenService = Depends(get_token_service),
    user_repo: "JsonUserRepository" = Depends(lambda: get_user_repository()),
) -> Optional[User]:
    """현재 인증된 사용자 반환 (선택적)

    인증이 없어도 None 반환, 예외 발생하지 않음
    """
    if not credentials:
        return None

    user_id = token_service.verify_token(credentials.credentials)
    if not user_id:
        return None

    return await user_repo.find_by_id(user_id)


CurrentUserDep = Annotated[User, Depends(get_current_user)]
CurrentUserOptionalDep = Annotated[Optional[User], Depends(get_current_user_optional)]


# 인프라스트럭처 레이어 - 싱글톤
def get_openai_client() -> OpenAIClient:
    """OpenAI 클라이언트 팩토리

    시각적 패턴 분석기가 활성화되면 해석 시 개인화된 힌트 활용.
    lru_cache 사용하지 않음 (visual_analyzer 종속성 때문)
    """
    settings = get_settings()
    visual_analyzer = None
    if settings.visual_pattern.enabled:
        visual_analyzer = get_visual_pattern_analyzer()
    return OpenAIClient(settings, visual_analyzer)


@lru_cache
def get_clip_client() -> CLIPEmbeddingClient:
    """CLIP 임베딩 클라이언트 싱글톤"""
    settings = get_settings()
    return CLIPEmbeddingClient(settings)


@lru_cache
def get_vector_index() -> IVectorIndex:
    """FAISS 벡터 검색 인덱스 싱글톤"""
    settings = get_settings()
    return create_vector_index(settings)


@lru_cache
def get_diversity_selector() -> MMRDiversitySelector:
    """MMR 다양성 선택기 싱글톤"""
    return MMRDiversitySelector(get_vector_index())


@lru_cache
def get_user_repository() -> JsonUserRepository:
    """사용자 저장소 싱글톤"""
    settings = get_settings()
    return JsonUserRepository(settings.users_file_path)


@lru_cache
def get_context_repository() -> InMemoryContextRepository:
    """컨텍스트 저장소 싱글톤"""
    return InMemoryContextRepository()


@lru_cache
def get_card_repository() -> JsonCardRepository:
    """카드 저장소 싱글톤"""
    settings = get_settings()
    return JsonCardRepository(settings)


@lru_cache
def get_card_history_repository() -> InMemoryCardHistoryRepository:
    """카드 히스토리 저장소 싱글톤"""
    return InMemoryCardHistoryRepository()


@lru_cache
def get_feedback_repository() -> JsonFeedbackRepository:
    """피드백 저장소 싱글톤"""
    settings = get_settings()
    return JsonFeedbackRepository(settings.feedback_file_path)


@lru_cache
def get_feedback_request_repository() -> InMemoryFeedbackRequestRepository:
    """피드백 요청 저장소 싱글톤"""
    return InMemoryFeedbackRequestRepository()


@lru_cache
def get_feedback_analyzer() -> IFeedbackAnalyzer:
    """피드백 분석기 싱글톤

    Contextual Relevance Feedback 알고리즘을 사용하여
    과거 피드백에서 상황-카드 연관 패턴을 학습합니다.
    """
    settings = get_settings()
    feedback_config = settings.feedback

    if feedback_config.enable_learning:
        return TFIDFFeedbackAnalyzer(
            feedback_file_path=settings.feedback_file_path,
            decay_days=feedback_config.decay_days,
            min_similarity=feedback_config.min_similarity,
        )

    return NoOpFeedbackAnalyzer()


@lru_cache
def get_visual_pattern_analyzer() -> IVisualPatternAnalyzer:
    """시각적 패턴 분석기 싱글톤

    CLIP 임베딩 기반 시각적 특징-의미 연결 분석.
    자폐 스펙트럼 장애 등 시각 중심 의사소통 사용자를 위한 개인화 지원.
    """
    settings = get_settings()
    visual_config = settings.visual_pattern

    if visual_config.enabled:
        return CLIPVisualPatternAnalyzer(
            vector_index=get_vector_index(),
            feedback_file_path=settings.feedback_file_path,
            signature_method=visual_config.signature_method,
            similarity_threshold=visual_config.similarity_threshold,
            decay_days=visual_config.recency_decay_days,
        )

    return NoOpVisualPatternAnalyzer()


# 서비스 레이어
def get_user_service(
    settings: SettingsDep,
    user_repo: JsonUserRepository = Depends(get_user_repository),
) -> UserService:
    """사용자 서비스"""
    return UserService(user_repo, settings)


def get_context_service(
    context_repo: InMemoryContextRepository = Depends(get_context_repository),
) -> ContextService:
    """컨텍스트 서비스"""
    return ContextService(context_repo)


def get_card_recommender(
    settings: SettingsDep,
    openai_client: OpenAIClient = Depends(get_openai_client),
    feedback_analyzer: IFeedbackAnalyzer = Depends(get_feedback_analyzer),
) -> CardRecommender:
    """CLIP 기반 카드 추천 엔진 (LLM 필터 + 피드백 학습)"""
    return CardRecommender(settings, openai_client, feedback_analyzer)


def get_card_service(
    settings: SettingsDep,
    recommender: CardRecommender = Depends(get_card_recommender),
    openai_client: OpenAIClient = Depends(get_openai_client),
    history_repo: InMemoryCardHistoryRepository = Depends(get_card_history_repository),
) -> CardService:
    """카드 서비스"""
    return CardService(settings, recommender, openai_client, history_repo)


def get_feedback_service(
    feedback_repo: JsonFeedbackRepository = Depends(get_feedback_repository),
    request_repo: InMemoryFeedbackRequestRepository = Depends(
        get_feedback_request_repository
    ),
    visual_analyzer: IVisualPatternAnalyzer = Depends(get_visual_pattern_analyzer),
) -> FeedbackService:
    """피드백 서비스

    시각적 패턴 분석기가 활성화되면 피드백 저장 시 시각적 서명 계산.
    """
    return FeedbackService(
        CombinedFeedbackRepository(feedback_repo, request_repo),
        visual_analyzer=visual_analyzer,
    )


# 타입 별칭
UserServiceDep = Annotated[UserService, Depends(get_user_service)]
ContextServiceDep = Annotated[ContextService, Depends(get_context_service)]
CardServiceDep = Annotated[CardService, Depends(get_card_service)]
FeedbackServiceDep = Annotated[FeedbackService, Depends(get_feedback_service)]
