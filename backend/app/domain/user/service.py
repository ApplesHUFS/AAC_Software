"""사용자 서비스"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.config.settings import Settings
from app.domain.user.entity import User
from app.domain.user.repository import UserRepository
from app.infrastructure.external.embedding_client import EmbeddingClient


@dataclass
class RegisterResult:
    """회원가입 결과"""

    success: bool
    user_id: Optional[str]
    message: str


@dataclass
class AuthResult:
    """인증 결과"""

    authenticated: bool
    user_info: Optional[Dict[str, Any]]
    message: str


@dataclass
class GetUserResult:
    """사용자 조회 결과"""

    success: bool
    user: Optional[Dict[str, Any]]
    message: str


@dataclass
class UpdateResult:
    """업데이트 결과"""

    success: bool
    updated_fields: List[str]
    category_recalculated: bool
    message: str


class UserService:
    """사용자 관련 비즈니스 로직"""

    def __init__(
        self,
        repository: UserRepository,
        embedding_client: EmbeddingClient,
        settings: Settings,
    ):
        self._repo = repository
        self._embedding = embedding_client
        self._settings = settings

    async def register_user(
        self,
        user_id: str,
        name: str,
        age: int,
        gender: str,
        disability_type: str,
        communication_characteristics: str,
        interesting_topics: List[str],
        password: str,
    ) -> RegisterResult:
        """새 사용자 등록"""
        # 중복 검사
        if await self._repo.exists(user_id):
            return RegisterResult(
                success=False,
                user_id=user_id,
                message=f"사용자 ID '{user_id}'가 이미 존재합니다.",
            )

        # 검증
        validation_error = self._validate_persona(
            age, gender, disability_type, interesting_topics
        )
        if validation_error:
            return RegisterResult(
                success=False, user_id=user_id, message=validation_error
            )

        # 선호 카테고리 계산
        preferred_categories = await self._embedding.calculate_preferred_categories(
            interesting_topics,
            self._settings.similarity_threshold,
            self._settings.required_cluster_count,
        )

        # 사용자 생성
        user = User(
            user_id=user_id,
            name=name,
            age=age,
            gender=gender,
            disability_type=disability_type,
            communication_characteristics=communication_characteristics,
            interesting_topics=interesting_topics,
            preferred_category_types=preferred_categories,
            password_hash=User.hash_password(password),
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        await self._repo.save(user)

        return RegisterResult(
            success=True,
            user_id=user_id,
            message=f"사용자 '{user_id}'({name})가 성공적으로 생성되었습니다.",
        )

    async def authenticate_user(self, user_id: str, password: str) -> AuthResult:
        """사용자 인증"""
        user = await self._repo.find_by_id(user_id)

        if not user:
            return AuthResult(
                authenticated=False,
                user_info=None,
                message="사용자를 찾을 수 없습니다.",
            )

        if not user.verify_password(password):
            return AuthResult(
                authenticated=False,
                user_info=None,
                message="비밀번호가 일치하지 않습니다.",
            )

        return AuthResult(
            authenticated=True,
            user_info=user.to_response_dict(),
            message="로그인에 성공했습니다.",
        )

    async def get_user_info(self, user_id: str) -> GetUserResult:
        """사용자 정보 조회"""
        user = await self._repo.find_by_id(user_id)

        if not user:
            return GetUserResult(
                success=False,
                user=None,
                message="사용자를 찾을 수 없습니다.",
            )

        return GetUserResult(
            success=True,
            user=user.to_response_dict(),
            message="프로필 조회에 성공했습니다.",
        )

    async def get_user(self, user_id: str) -> Optional[User]:
        """사용자 엔티티 조회"""
        return await self._repo.find_by_id(user_id)

    async def update_user_persona(
        self, user_id: str, updates: Dict[str, Any]
    ) -> UpdateResult:
        """사용자 페르소나 업데이트"""
        user = await self._repo.find_by_id(user_id)

        if not user:
            return UpdateResult(
                success=False,
                updated_fields=[],
                category_recalculated=False,
                message="사용자를 찾을 수 없습니다.",
            )

        updated_fields: List[str] = []
        category_recalculated = False

        # 필드 매핑 (camelCase -> snake_case)
        field_mapping = {
            "name": "name",
            "age": "age",
            "gender": "gender",
            "disabilityType": "disability_type",
            "disability_type": "disability_type",
            "communicationCharacteristics": "communication_characteristics",
            "communication_characteristics": "communication_characteristics",
            "interestingTopics": "interesting_topics",
            "interesting_topics": "interesting_topics",
        }

        for key, value in updates.items():
            field_name = field_mapping.get(key)
            if field_name and hasattr(user, field_name):
                setattr(user, field_name, value)
                updated_fields.append(key)

        # 관심 주제가 변경된 경우 선호 카테고리 재계산
        if "interestingTopics" in updates or "interesting_topics" in updates:
            user.preferred_category_types = (
                await self._embedding.calculate_preferred_categories(
                    user.interesting_topics,
                    self._settings.similarity_threshold,
                    self._settings.required_cluster_count,
                )
            )
            category_recalculated = True

        user.updated_at = datetime.now()
        await self._repo.update(user)

        return UpdateResult(
            success=True,
            updated_fields=updated_fields,
            category_recalculated=category_recalculated,
            message="프로필이 성공적으로 업데이트되었습니다.",
        )

    def _validate_persona(
        self,
        age: int,
        gender: str,
        disability_type: str,
        interesting_topics: List[str],
    ) -> Optional[str]:
        """페르소나 검증"""
        if age < self._settings.min_age or age > self._settings.max_age:
            return f"나이는 {self._settings.min_age}세부터 {self._settings.max_age}세까지 입력 가능합니다."

        if gender not in self._settings.valid_genders:
            return f"성별은 {', '.join(self._settings.valid_genders)} 중에서 선택해주세요."

        if disability_type not in self._settings.valid_disability_types:
            return f"장애 유형은 {', '.join(self._settings.valid_disability_types)} 중에서 선택해주세요."

        if not interesting_topics:
            return "관심 주제는 최소 1개 이상 입력해주세요."

        if len(interesting_topics) > 10:
            return "관심 주제는 최대 10개까지 입력 가능합니다."

        return None
