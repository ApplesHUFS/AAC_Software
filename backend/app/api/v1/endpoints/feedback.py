"""피드백 API 엔드포인트"""

from fastapi import APIRouter, HTTPException, status

from app.api.deps import FeedbackServiceDep
from app.core.response import success_response
from app.schemas.feedback import FeedbackRequestBody, FeedbackSubmitRequest

router = APIRouter()


@router.post("/request")
async def request_feedback(
    request: FeedbackRequestBody,
    feedback_service: FeedbackServiceDep,
):
    """피드백 요청"""
    result = await feedback_service.request_feedback(
        user_id=request.user_id,
        cards=request.cards,
        context=request.context.model_dump(by_alias=True),
        interpretations=request.interpretations,
        partner_info=request.partner_info,
    )

    return success_response(
        data={
            "confirmationId": result.confirmation_id,
            "confirmationRequest": result.confirmation_request,
        },
        message=result.message,
    )


@router.post("/submit")
async def submit_feedback(
    request: FeedbackSubmitRequest,
    feedback_service: FeedbackServiceDep,
):
    """피드백 제출"""
    result = await feedback_service.submit_feedback(
        confirmation_id=request.confirmation_id,
        selected_index=request.selected_interpretation_index,
        direct_feedback=request.direct_feedback,
    )

    if not result.success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.message,
        )

    return success_response(
        data={
            "feedbackResult": result.feedback.to_dict(),
        },
        message=result.message,
    )
