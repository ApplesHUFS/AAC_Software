"""컨텍스트 API 엔드포인트"""

from fastapi import APIRouter

from app.api.deps import ContextServiceDep
from app.core.exceptions import NotFoundException, ValidationException
from app.core.response import success_response
from app.schemas.context import CreateContextRequest

router = APIRouter()


@router.post("", status_code=201)
async def create_context(
    request: CreateContextRequest,
    context_service: ContextServiceDep,
):
    """컨텍스트 생성"""
    result = await context_service.create_context(
        user_id=request.user_id,
        place=request.place,
        interaction_partner=request.interaction_partner,
        current_activity=request.current_activity or "",
    )

    if not result.success:
        raise ValidationException(result.message)

    return success_response(
        data=result.context.to_dict(),
        message=result.message,
    )


@router.get("/{context_id}")
async def get_context(
    context_id: str,
    context_service: ContextServiceDep,
):
    """컨텍스트 조회"""
    context = await context_service.get_context(context_id)

    if not context:
        raise NotFoundException("컨텍스트를 찾을 수 없습니다.")

    return success_response(
        data=context.to_dict(),
        message="컨텍스트 조회에 성공했습니다.",
    )
