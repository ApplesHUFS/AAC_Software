"""공통 스키마 정의"""

from datetime import datetime
from typing import Any, Generic, Optional, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    """표준 API 응답 형식"""

    success: bool
    timestamp: datetime = Field(default_factory=datetime.now)
    data: Optional[T] = None
    message: str = ""
    error: Optional[str] = None


class PaginationInfo(BaseModel):
    """페이지네이션 정보"""

    current_page: int = Field(..., alias="currentPage")
    total_pages: int = Field(..., alias="totalPages")

    class Config:
        populate_by_name = True
