"""공통 상수 API 엔드포인트"""

from fastapi import APIRouter

from app.config.settings import get_settings

router = APIRouter()
settings = get_settings()


@router.get("/constants")
async def get_constants():
    """프론트엔드에서 사용할 공통 상수 제공"""
    return {
        "minCardSelection": settings.min_card_selection,
        "maxCardSelection": settings.max_card_selection,
        "genderOptions": settings.valid_genders,
        "disabilityTypes": settings.valid_disability_types,
    }
