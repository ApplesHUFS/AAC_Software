"""
커스텀 예외 클래스 정의
HTTP 상태 코드와 매핑되는 비즈니스 예외
"""

from typing import Any, Optional


class AppException(Exception):
    """애플리케이션 기본 예외"""

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        data: Optional[Any] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.data = data
        super().__init__(self.message)


class NotFoundException(AppException):
    """리소스를 찾을 수 없음 (404)"""

    def __init__(self, message: str = "요청한 리소스를 찾을 수 없습니다."):
        super().__init__(message, status_code=404)


class ValidationException(AppException):
    """입력 데이터 검증 실패 (400)"""

    def __init__(self, message: str = "입력 데이터가 올바르지 않습니다."):
        super().__init__(message, status_code=400)


class AuthenticationException(AppException):
    """인증 실패 (401)"""

    def __init__(self, message: str = "인증에 실패했습니다."):
        super().__init__(message, status_code=401)


class DuplicateException(AppException):
    """중복 리소스 (409)"""

    def __init__(self, message: str = "이미 존재하는 리소스입니다."):
        super().__init__(message, status_code=409)


class LLMServiceError(AppException):
    """LLM 서비스 일반 오류 (503)"""

    def __init__(self, message: str = "LLM 서비스 오류가 발생했습니다."):
        super().__init__(message, status_code=503)


class LLMTimeoutError(LLMServiceError):
    """LLM 요청 타임아웃 (504)"""

    def __init__(self, message: str = "LLM 요청 시간이 초과되었습니다."):
        super().__init__(message)
        self.status_code = 504


class LLMRateLimitError(LLMServiceError):
    """LLM Rate Limit 초과 (429)"""

    def __init__(self, message: str = "LLM API 요청 한도를 초과했습니다."):
        super().__init__(message)
        self.status_code = 429
