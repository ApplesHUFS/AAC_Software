"""
AAC Interpreter Service - FastAPI 메인 애플리케이션
"""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse

from app.api.v1.router import api_router
from app.config.settings import get_settings
from app.core.response import error_response


@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 시작/종료 시 실행되는 로직"""
    settings = get_settings()
    print("=" * 50)
    print("AAC Interpreter API Server 시작")
    print(f"프로젝트 루트: {settings.project_root}")
    print(f"데이터셋 경로: {settings.dataset_root}")
    print(f"사용자 데이터 경로: {settings.user_data_root}")
    print("=" * 50)
    yield
    print("AAC Interpreter API Server 종료")


app = FastAPI(
    title="AAC Interpreter Service API",
    description="개인화된 AAC 카드 해석 시스템 - FastAPI 백엔드",
    version="2.0.0",
    lifespan=lifespan,
)

# CORS 설정
settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
    """전역 예외 처리"""
    return JSONResponse(
        status_code=500,
        content=error_response(error=f"서버 내부 오류: {str(exc)}"),
    )


# API 라우터 등록
app.include_router(api_router, prefix="/api")


# 이미지 서빙
@app.get("/api/images/{filename}")
async def serve_image(filename: str):
    """AAC 카드 이미지 서빙"""
    settings = get_settings()
    image_path = settings.images_folder / filename

    if not image_path.exists():
        return JSONResponse(
            status_code=404,
            content=error_response(error=f"이미지를 찾을 수 없습니다: {filename}"),
        )

    return FileResponse(image_path)


# 루트 엔드포인트
@app.get("/")
async def root():
    """API 정보"""
    return {
        "success": True,
        "data": {
            "service": "AAC Interpreter Service",
            "version": "2.0.0",
            "docs": "/docs",
            "redoc": "/redoc",
        },
        "message": "AAC Interpreter API에 오신 것을 환영합니다.",
    }


# 헬스체크 (루트 레벨)
@app.get("/health")
async def health_check():
    """헬스체크"""
    return {
        "success": True,
        "data": {
            "status": "healthy",
            "service": "AAC Interpreter Service",
            "version": "2.0.0",
        },
        "message": "서비스가 정상 작동 중입니다.",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )
