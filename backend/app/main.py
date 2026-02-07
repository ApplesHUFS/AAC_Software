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
from app.core.middleware import RequestIDMiddleware
from app.core.response import error_response

# 설정 싱글톤
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 시작/종료 시 실행되는 로직"""
    print("=" * 50)
    print("AAC Interpreter API Server 시작")
    print(f"버전: {settings.VERSION}")
    print(f"프로젝트 루트: {settings.project_root}")
    print(f"데이터셋 경로: {settings.dataset_root}")
    print(f"사용자 데이터 경로: {settings.user_data_root}")
    print("=" * 50)
    yield
    print("AAC Interpreter API Server 종료")


app = FastAPI(
    title="AAC Interpreter Service API",
    description="개인화된 AAC 카드 해석 시스템 - FastAPI 백엔드",
    version=settings.VERSION,
    lifespan=lifespan,
)

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
        reload=settings.debug,
    )
