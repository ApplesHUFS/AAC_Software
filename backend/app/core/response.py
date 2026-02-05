"""
표준 API 응답 형식 정의
모든 API 응답은 이 형식을 따름
"""

from datetime import datetime
from typing import Any, Dict, Optional


def success_response(
    data: Any = None,
    message: str = "",
) -> Dict[str, Any]:
    """
    성공 응답 생성

    Args:
        data: 응답 데이터
        message: 성공 메시지

    Returns:
        표준 성공 응답 딕셔너리
    """
    return {
        "success": True,
        "timestamp": datetime.now().isoformat(),
        "data": data if data is not None else {},
        "message": message,
    }


def error_response(
    error: str,
    data: Optional[Any] = None,
) -> Dict[str, Any]:
    """
    에러 응답 생성

    Args:
        error: 에러 메시지
        data: 추가 데이터 (선택)

    Returns:
        표준 에러 응답 딕셔너리
    """
    return {
        "success": False,
        "timestamp": datetime.now().isoformat(),
        "data": data,
        "error": error,
    }
