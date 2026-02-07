"""Rate Limiting 모듈

slowapi를 활용한 API 요청 제한 구현
"""

from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.core.response import error_response

# Rate Limit 상수 (데코레이터에서 사용)
RATE_LIMIT_LOGIN = "5/minute"
RATE_LIMIT_API = "100/minute"

# 클라이언트 IP 기반 Rate Limiting
limiter = Limiter(key_func=get_remote_address)


def get_limiter() -> Limiter:
    """Rate Limiter 인스턴스 반환"""
    return limiter


def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    """Rate Limit 초과 시 응답 핸들러"""
    return JSONResponse(
        status_code=429,
        content=error_response(
            error="요청이 너무 많습니다. 잠시 후 다시 시도해주세요.",
        ),
        headers={"Retry-After": str(exc.detail)},
    )
