"""카드 API 엔드포인트"""

from fastapi import APIRouter

from app.api.deps import CardServiceDep, UserServiceDep, ContextServiceDep, SettingsDep
from app.core.exceptions import NotFoundException, ValidationException
from app.core.response import success_response
from app.schemas.card import (
    CardRecommendRequest,
    CardValidateRequest,
    CardInterpretRequest,
)

router = APIRouter()


@router.post("/recommend")
async def recommend_cards(
    request: CardRecommendRequest,
    card_service: CardServiceDep,
    user_service: UserServiceDep,
    context_service: ContextServiceDep,
):
    """카드 추천"""
    user = await user_service.get_user(request.user_id)
    if not user:
        raise NotFoundException("사용자를 찾을 수 없습니다.")

    context = await context_service.get_context(request.context_id)
    if not context:
        raise NotFoundException("컨텍스트를 찾을 수 없습니다.")

    result = await card_service.recommend_cards(user, context)

    return success_response(
        data={
            "cards": [card.to_dict() for card in result.cards],
            "totalCards": len(result.cards),
            "contextInfo": result.context_info,
            "selectionRules": {
                "minCards": 1,
                "maxCards": 4,
                "totalOptions": len(result.cards),
            },
            "pagination": result.pagination,
        },
        message=result.message,
    )


@router.post("/validate")
async def validate_selection(
    request: CardValidateRequest,
    card_service: CardServiceDep,
):
    """카드 선택 검증"""
    result = card_service.validate_selection(
        selected_cards=request.selected_cards,
        all_recommended_cards=request.all_recommended_cards,
    )

    if not result.valid:
        raise ValidationException(result.message)

    return success_response(
        data={
            "valid": result.valid,
            "selectedCount": result.selected_count,
        },
        message=result.message,
    )


@router.post("/interpret")
async def interpret_cards(
    request: CardInterpretRequest,
    card_service: CardServiceDep,
    user_service: UserServiceDep,
    context_service: ContextServiceDep,
):
    """카드 해석"""
    user = await user_service.get_user(request.user_id)
    if not user:
        raise NotFoundException("사용자를 찾을 수 없습니다.")

    context = await context_service.get_context(request.context_id)
    if not context:
        raise NotFoundException("컨텍스트를 찾을 수 없습니다.")

    result = await card_service.interpret_cards(
        user=user,
        context=context,
        selected_cards=request.selected_cards,
    )

    return success_response(
        data={
            "interpretations": [interp.to_dict() for interp in result.interpretations],
            "feedbackId": result.feedback_id,
            "method": "gpt-4o-vision",
            "selectedCards": result.selected_cards,
        },
        message=result.message,
    )


@router.get("/history/{context_id}")
async def get_history_summary(
    context_id: str,
    card_service: CardServiceDep,
):
    """히스토리 요약 조회"""
    summary = await card_service.get_history_summary(context_id)

    return success_response(
        data=summary,
        message="히스토리 조회에 성공했습니다.",
    )


@router.get("/history/{context_id}/page/{page_number}")
async def get_history_page(
    context_id: str,
    page_number: int,
    card_service: CardServiceDep,
):
    """특정 페이지 히스토리 조회"""
    page_data = await card_service.get_history_page(context_id, page_number)

    if not page_data:
        raise NotFoundException(f"페이지 {page_number}를 찾을 수 없습니다.")

    return success_response(
        data=page_data,
        message="페이지 조회에 성공했습니다.",
    )
