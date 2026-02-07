"""헬스체크 API 엔드포인트"""

from fastapi import APIRouter

from app.config.settings import get_settings
from app.core.response import success_response

router = APIRouter()
settings = get_settings()


@router.get("/health")
async def health_check():
    """헬스체크"""
    return success_response(
        data={
            "status": "healthy",
            "service": "AAC Interpreter Service",
            "version": settings.VERSION,
        },
        message="서비스가 정상 작동 중입니다.",
    )
