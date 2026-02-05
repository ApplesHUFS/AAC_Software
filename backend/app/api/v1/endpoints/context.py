"""컨텍스트 API 엔드포인트"""

from fastapi import APIRouter, HTTPException, status

from app.api.deps import ContextServiceDep
from app.core.response import success_response
from app.schemas.context import CreateContextRequest

router = APIRouter()


@router.post("", status_code=status.HTTP_201_CREATED)
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
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.message,
        )

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
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="컨텍스트를 찾을 수 없습니다.",
        )

    return success_response(
        data=context.to_dict(),
        message="컨텍스트 조회에 성공했습니다.",
    )
