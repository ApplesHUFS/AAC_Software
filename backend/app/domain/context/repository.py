"""컨텍스트 저장소 인터페이스"""

from abc import ABC, abstractmethod
from typing import Optional

from app.domain.context.entity import Context


class ContextRepository(ABC):
    """컨텍스트 저장소 추상 클래스"""

    @abstractmethod
    async def find_by_id(self, context_id: str) -> Optional[Context]:
        """컨텍스트 ID로 조회"""
        pass

    @abstractmethod
    async def save(self, context: Context) -> None:
        """컨텍스트 저장"""
        pass

    @abstractmethod
    async def delete(self, context_id: str) -> None:
        """컨텍스트 삭제"""
        pass
