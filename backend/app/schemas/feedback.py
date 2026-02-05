"""피드백 관련 스키마"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ContextSummary(BaseModel):
    """컨텍스트 요약"""

    time: str = ""
    place: str = ""
    interaction_partner: str = Field("", alias="interactionPartner")
    current_activity: str = Field("", alias="currentActivity")

    class Config:
        populate_by_name = True


class FeedbackRequestBody(BaseModel):
    """피드백 요청 본문"""

    user_id: str = Field(..., alias="userId")
    cards: List[str]
    context: ContextSummary
    interpretations: List[str]
    partner_info: str = Field(..., alias="partnerInfo")

    class Config:
        populate_by_name = True


class InterpretationOptionInfo(BaseModel):
    """해석 옵션 정보"""

    index: int
    interpretation: str


class ConfirmationRequest(BaseModel):
    """확인 요청 정보"""

    confirmation_id: str = Field(..., alias="confirmationId")
    user_context: ContextSummary = Field(..., alias="userContext")
    selected_cards: List[str] = Field(..., alias="selectedCards")
    interpretation_options: List[InterpretationOptionInfo] = Field(
        ..., alias="interpretationOptions"
    )
    partner: str

    class Config:
        populate_by_name = True


class FeedbackRequestResponse(BaseModel):
    """피드백 요청 응답"""

    confirmation_id: str = Field(..., alias="confirmationId")
    confirmation_request: ConfirmationRequest = Field(..., alias="confirmationRequest")

    class Config:
        populate_by_name = True


class FeedbackSubmitRequest(BaseModel):
    """피드백 제출 요청"""

    confirmation_id: str = Field(..., alias="confirmationId")
    selected_interpretation_index: Optional[int] = Field(
        None, alias="selectedInterpretationIndex"
    )
    direct_feedback: Optional[str] = Field(None, alias="directFeedback")

    class Config:
        populate_by_name = True


class FeedbackResult(BaseModel):
    """피드백 결과"""

    feedback_type: str = Field(..., alias="feedbackType")
    selected_index: Optional[int] = Field(None, alias="selectedIndex")
    selected_interpretation: Optional[str] = Field(None, alias="selectedInterpretation")
    direct_feedback: Optional[str] = Field(None, alias="directFeedback")
    confirmation_id: str = Field(..., alias="confirmationId")
    user_id: str = Field(..., alias="userId")
    cards: List[str]
    context: Dict[str, Any]
    interpretations: List[str]
    partner_info: str = Field(..., alias="partnerInfo")
    confirmed_at: str = Field(..., alias="confirmedAt")

    class Config:
        populate_by_name = True


class FeedbackSubmitResponse(BaseModel):
    """피드백 제출 응답"""

    feedback_result: FeedbackResult = Field(..., alias="feedbackResult")

    class Config:
        populate_by_name = True
