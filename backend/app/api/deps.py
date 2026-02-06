"""의존성 주입 모듈"""

from functools import lru_cache
from typing import Annotated

from fastapi import Depends

from app.config.settings import Settings, get_settings
from app.domain.user.service import UserService
from app.domain.context.service import ContextService
from app.domain.card.service import CardService
from app.domain.card.recommender import CardRecommender
from app.domain.feedback.service import FeedbackService
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
from app.infrastructure.external.openai_client import OpenAIClient
from app.infrastructure.external.clip_client import CLIPEmbeddingClient
from app.domain.card.vector_searcher import FaissVectorIndex, create_vector_index
from app.domain.card.interfaces import IVectorIndex
from app.domain.card.diversity_selector import MMRDiversitySelector


# 설정
SettingsDep = Annotated[Settings, Depends(get_settings)]


# 인프라스트럭처 레이어 - 싱글톤
@lru_cache
def get_openai_client() -> OpenAIClient:
    """OpenAI 클라이언트 싱글톤"""
    settings = get_settings()
    return OpenAIClient(settings)


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
) -> CardRecommender:
    """CLIP 기반 카드 추천 엔진 (LLM 필터 포함)"""
    return CardRecommender(settings, openai_client)


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
) -> FeedbackService:
    """피드백 서비스"""

    class CombinedFeedbackRepository:
        def __init__(self, feedback_repo, request_repo):
            self._feedback = feedback_repo
            self._request = request_repo

        async def save_request(self, request):
            await self._request.save_request(request)

        async def find_request(self, confirmation_id):
            return await self._request.find_request(confirmation_id)

        async def save_feedback(self, feedback):
            return await self._feedback.save_feedback(feedback)

        async def delete_request(self, confirmation_id):
            await self._request.delete_request(confirmation_id)

        async def get_next_feedback_id(self):
            return await self._feedback.get_next_feedback_id()

    return FeedbackService(CombinedFeedbackRepository(feedback_repo, request_repo))


# 타입 별칭
UserServiceDep = Annotated[UserService, Depends(get_user_service)]
ContextServiceDep = Annotated[ContextService, Depends(get_context_service)]
CardServiceDep = Annotated[CardService, Depends(get_card_service)]
FeedbackServiceDep = Annotated[FeedbackService, Depends(get_feedback_service)]
