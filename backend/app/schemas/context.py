"""컨텍스트 관련 스키마"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class CreateContextRequest(BaseModel):
    """컨텍스트 생성 요청"""

    user_id: str = Field(..., alias="userId")
    place: str = Field(..., min_length=1)
    interaction_partner: str = Field(..., alias="interactionPartner", min_length=1)
    current_activity: Optional[str] = Field(None, alias="currentActivity")

    class Config:
        populate_by_name = True


class ContextResponse(BaseModel):
    """컨텍스트 응답"""

    context_id: str = Field(..., alias="contextId")
    user_id: str = Field(..., alias="userId")
    time: str
    place: str
    interaction_partner: str = Field(..., alias="interactionPartner")
    current_activity: str = Field("", alias="currentActivity")
    created_at: Optional[datetime] = Field(None, alias="createdAt")

    class Config:
        populate_by_name = True
