"""카드 관련 스키마"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class CardInfo(BaseModel):
    """카드 정보"""

    id: str
    name: str
    filename: str
    image_path: str = Field(..., alias="imagePath")
    index: int
    selected: bool = False

    class Config:
        populate_by_name = True


class CardRecommendRequest(BaseModel):
    """카드 추천 요청"""

    user_id: str = Field(..., alias="userId")
    context_id: str = Field(..., alias="contextId")

    class Config:
        populate_by_name = True


class SelectionRules(BaseModel):
    """카드 선택 규칙"""

    min_cards: int = Field(..., alias="minCards")
    max_cards: int = Field(..., alias="maxCards")
    total_options: int = Field(..., alias="totalOptions")

    class Config:
        populate_by_name = True


class ContextInfo(BaseModel):
    """컨텍스트 정보"""

    time: str
    place: str
    interaction_partner: str = Field(..., alias="interactionPartner")
    current_activity: str = Field("", alias="currentActivity")

    class Config:
        populate_by_name = True


class PaginationInfo(BaseModel):
    """페이지네이션 정보"""

    current_page: int = Field(..., alias="currentPage")
    total_pages: int = Field(..., alias="totalPages")

    class Config:
        populate_by_name = True


class CardRecommendResponse(BaseModel):
    """카드 추천 응답"""

    cards: List[CardInfo]
    total_cards: int = Field(..., alias="totalCards")
    context_info: ContextInfo = Field(..., alias="contextInfo")
    selection_rules: SelectionRules = Field(..., alias="selectionRules")
    pagination: PaginationInfo

    class Config:
        populate_by_name = True


class CardValidateRequest(BaseModel):
    """카드 선택 검증 요청"""

    selected_cards: List[str] = Field(..., alias="selectedCards")
    all_recommended_cards: List[str] = Field(..., alias="allRecommendedCards")

    class Config:
        populate_by_name = True


class CardValidateResponse(BaseModel):
    """카드 선택 검증 응답"""

    valid: bool
    selected_count: int = Field(..., alias="selectedCount")

    class Config:
        populate_by_name = True


class CardInterpretRequest(BaseModel):
    """카드 해석 요청"""

    user_id: str = Field(..., alias="userId")
    context_id: str = Field(..., alias="contextId")
    selected_cards: List[str] = Field(..., alias="selectedCards")

    class Config:
        populate_by_name = True


class InterpretationOption(BaseModel):
    """해석 옵션"""

    index: int
    text: str
    selected: bool = False


class SelectedCardInfo(BaseModel):
    """선택된 카드 정보"""

    filename: str
    name: str
    image_path: str = Field(..., alias="imagePath")

    class Config:
        populate_by_name = True


class CardInterpretResponse(BaseModel):
    """카드 해석 응답"""

    interpretations: List[InterpretationOption]
    feedback_id: int = Field(..., alias="feedbackId")
    method: str
    selected_cards: List[SelectedCardInfo] = Field(..., alias="selectedCards")

    class Config:
        populate_by_name = True


class HistorySummaryItem(BaseModel):
    """히스토리 요약 항목"""

    page_number: int = Field(..., alias="pageNumber")
    card_count: int = Field(..., alias="cardCount")
    timestamp: str

    class Config:
        populate_by_name = True


class CardHistoryResponse(BaseModel):
    """카드 히스토리 요약 응답"""

    context_id: str = Field(..., alias="contextId")
    total_pages: int = Field(..., alias="totalPages")
    latest_page: int = Field(..., alias="latestPage")
    history_summary: List[HistorySummaryItem] = Field(..., alias="historySummary")

    class Config:
        populate_by_name = True


class CardHistoryPageResponse(BaseModel):
    """카드 히스토리 페이지 응답"""

    cards: List[CardInfo]
    pagination: PaginationInfo
    timestamp: str
    context_id: str = Field(..., alias="contextId")

    class Config:
        populate_by_name = True
