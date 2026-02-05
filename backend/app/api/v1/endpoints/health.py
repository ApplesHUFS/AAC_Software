"""헬스체크 API 엔드포인트"""

from fastapi import APIRouter

from app.core.response import success_response

router = APIRouter()


@router.get("/health")
async def health_check():
    """헬스체크"""
    return success_response(
        data={
            "status": "healthy",
            "service": "AAC Interpreter Service",
            "version": "2.0.0",
        },
        message="서비스가 정상 작동 중입니다.",
    )
