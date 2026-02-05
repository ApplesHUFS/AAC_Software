"""컨텍스트 서비스"""

from dataclasses import dataclass
from typing import Optional

from app.domain.context.entity import Context
from app.domain.context.repository import ContextRepository


@dataclass
class CreateContextResult:
    """컨텍스트 생성 결과"""

    success: bool
    context: Optional[Context]
    message: str


class ContextService:
    """컨텍스트 관련 비즈니스 로직"""

    def __init__(self, repository: ContextRepository):
        self._repo = repository

    async def create_context(
        self,
        user_id: str,
        place: str,
        interaction_partner: str,
        current_activity: str = "",
    ) -> CreateContextResult:
        """새 컨텍스트 생성"""
        context = Context(
            context_id=Context.generate_id(),
            user_id=user_id,
            time=Context.get_current_time(),
            place=place,
            interaction_partner=interaction_partner,
            current_activity=current_activity or "",
        )

        await self._repo.save(context)

        return CreateContextResult(
            success=True,
            context=context,
            message="대화 상황이 성공적으로 생성되었습니다.",
        )

    async def get_context(self, context_id: str) -> Optional[Context]:
        """컨텍스트 조회"""
        return await self._repo.find_by_id(context_id)
