"""사용자 저장소 인터페이스"""

from abc import ABC, abstractmethod
from typing import Optional

from app.domain.user.entity import User


class UserRepository(ABC):
    """사용자 저장소 추상 클래스"""

    @abstractmethod
    async def find_by_id(self, user_id: str) -> Optional[User]:
        """사용자 ID로 조회"""
        pass

    @abstractmethod
    async def exists(self, user_id: str) -> bool:
        """사용자 존재 여부 확인"""
        pass

    @abstractmethod
    async def save(self, user: User) -> None:
        """사용자 저장"""
        pass

    @abstractmethod
    async def update(self, user: User) -> None:
        """사용자 업데이트"""
        pass
