"""Request ID 추적 미들웨어

모든 요청에 고유 request_id를 부여하여 로깅 및 디버깅 지원
"""

import uuid
from contextvars import ContextVar
from typing import Optional

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

# 현재 요청의 request_id를 저장하는 context variable
request_id_var: ContextVar[Optional[str]] = ContextVar("request_id", default=None)


def get_request_id() -> Optional[str]:
    """현재 컨텍스트의 request_id 반환"""
    return request_id_var.get()


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Request ID 추적 미들웨어

    - 클라이언트가 X-Request-ID 헤더를 보내면 해당 값 사용
    - 없으면 UUID4로 새 request_id 생성
    - 응답 헤더에 X-Request-ID 추가
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        # 클라이언트 제공 request_id 또는 새로 생성
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())

        # context variable에 저장
        token = request_id_var.set(request_id)

        try:
            response = await call_next(request)
            response.headers["X-Request-ID"] = request_id
            return response
        finally:
            request_id_var.reset(token)
