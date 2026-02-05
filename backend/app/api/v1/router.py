"""API v1 라우터 통합"""

from fastapi import APIRouter

from app.api.v1.endpoints import auth, context, cards, feedback, health

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(context.router, prefix="/context", tags=["Context"])
api_router.include_router(cards.router, prefix="/cards", tags=["Cards"])
api_router.include_router(feedback.router, prefix="/feedback", tags=["Feedback"])
api_router.include_router(health.router, tags=["Health"])
