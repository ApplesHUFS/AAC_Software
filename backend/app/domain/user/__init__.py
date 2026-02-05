"""User domain module"""

from app.domain.user.entity import User
from app.domain.user.service import UserService

__all__ = ["User", "UserService"]
