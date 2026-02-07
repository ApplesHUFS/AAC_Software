"""
AAC Interpreter Service - FastAPI 메인 애플리케이션
"""

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.api.v1.router import api_router
from app.config.settings import get_settings
from app.core.exceptions import AppException
from app.core.middleware import RequestIDMiddleware
from app.core.response import error_response
from app.core.rate_limit import limiter, rate_limit_exceeded_handler

logger = logging.getLogger(__name__)

# 설정 싱글톤
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 시작/종료 시 실행되는 로직"""
    logger.info("=" * 50)
    logger.info("AAC Interpreter API Server 시작")
    logger.info("버전: %s", settings.VERSION)
    logger.info("환경: %s", settings.environment)
    logger.info("디버그 모드: %s", settings.debug_mode)
    logger.info("프로젝트 루트: %s", settings.project_root)
    logger.info("=" * 50)

    # 프로덕션 환경 경고
    if settings.is_production:
        if not settings.jwt_secret_key:
            logger.warning("JWT_SECRET_KEY가 설정되지 않았습니다!")
        if not settings.allowed_origins:
            logger.warning("CORS 오리진이 설정되지 않았습니다!")

    yield
    logger.info("AAC Interpreter API Server 종료")


app = FastAPI(
    title="AAC Interpreter Service API",
    description="개인화된 AAC 카드 해석 시스템 - FastAPI 백엔드",
    version=settings.VERSION,
    lifespan=lifespan,
    debug=settings.debug_mode,
)

# Rate Limiter 설정
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

# Request ID 추적 미들웨어 (가장 먼저 등록하여 모든 요청에 적용)
app.add_middleware(RequestIDMiddleware)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept", "X-Request-ID"],
)


# 커스텀 애플리케이션 예외 핸들러
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    """커스텀 애플리케이션 예외 처리"""
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response(error=exc.message),
    )


# HTTPException 핸들러
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """HTTP 예외 처리 - 통일된 응답 형식"""
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response(error=exc.detail),
    )


# 전역 예외 핸들러
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """전역 예외 처리

    프로덕션 환경에서는 상세 오류 메시지를 숨기고,
    서버 로그에만 기록하여 보안 강화
    """
    from app.core.middleware import get_request_id

    request_id = get_request_id() or "unknown"
    logger.exception(
        "Unhandled exception [request_id=%s, path=%s]: %s",
        request_id,
        request.url.path,
        str(exc),
    )

    if settings.is_production:
        error_msg = "서버 내부 오류가 발생했습니다. 잠시 후 다시 시도해주세요."
    else:
        error_msg = f"서버 내부 오류: {str(exc)}"

    return JSONResponse(
        status_code=500,
        content=error_response(error=error_msg),
    )


# API 라우터 등록
app.include_router(api_router, prefix="/api")


# 이미지 서빙
@app.get("/api/images/{filename}")
async def serve_image(filename: str):
    """AAC 카드 이미지 서빙"""
    # Path Traversal 방어: 파일명에서 디렉토리 구분자 차단
    if ".." in filename or "/" in filename or "\\" in filename:
        return JSONResponse(
            status_code=400,
            content=error_response(error="잘못된 파일명입니다"),
        )

    # 경로 정규화 후 기준 디렉토리 내 경로인지 검증
    image_path = (settings.images_folder / filename).resolve()
    base_path = settings.images_folder.resolve()

    if not str(image_path).startswith(str(base_path)):
        return JSONResponse(
            status_code=400,
            content=error_response(error="잘못된 파일명입니다"),
        )

    if not image_path.exists():
        return JSONResponse(
            status_code=404,
            content=error_response(error=f"이미지를 찾을 수 없습니다: {filename}"),
        )

    return FileResponse(image_path)


# 헬스체크 (루트 엔드포인트 겸용)
@app.get("/")
@app.get("/health")
async def health_check():
    """헬스체크 및 API 정보 (/ 와 /health 통합)"""
    return {
        "success": True,
        "data": {
            "status": "healthy",
            "service": "AAC Interpreter Service",
            "version": settings.VERSION,
            "docs": "/docs",
            "redoc": "/redoc",
        },
        "message": "서비스가 정상 작동 중입니다.",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug_mode,
    )
