"""LLM API 호출 Resilience 모듈

Exponential backoff 재시도, 타임아웃 처리, Fallback 지원
"""

import asyncio
import functools
import logging
from typing import Any, Callable, Optional, TypeVar

from openai import APITimeoutError, RateLimitError

from app.core.exceptions import LLMRateLimitError, LLMServiceError, LLMTimeoutError

logger = logging.getLogger(__name__)

T = TypeVar("T")


def with_retry(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 30.0,
    exponential_base: float = 2.0,
) -> Callable:
    """Exponential backoff 재시도 데코레이터

    Args:
        max_retries: 최대 재시도 횟수
        base_delay: 초기 대기 시간 (초)
        max_delay: 최대 대기 시간 (초)
        exponential_base: 지수 배율
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            last_exception: Optional[Exception] = None

            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)

                except APITimeoutError as e:
                    last_exception = LLMTimeoutError(str(e))
                    logger.warning(
                        f"{func.__name__} 타임아웃 (시도 {attempt + 1}/{max_retries + 1})"
                    )

                except RateLimitError as e:
                    last_exception = LLMRateLimitError(str(e))
                    logger.warning(
                        f"{func.__name__} Rate Limit (시도 {attempt + 1}/{max_retries + 1})"
                    )

                except Exception as e:
                    last_exception = LLMServiceError(str(e))
                    logger.warning(
                        f"{func.__name__} 오류 (시도 {attempt + 1}/{max_retries + 1}): {e}"
                    )

                # 마지막 시도가 아니면 대기
                if attempt < max_retries:
                    delay = min(base_delay * (exponential_base**attempt), max_delay)
                    await asyncio.sleep(delay)

            raise last_exception or LLMServiceError("알 수 없는 오류")

        return wrapper

    return decorator


def with_fallback(fallback_value: T) -> Callable:
    """LLM 실패 시 Fallback 값을 반환하는 데코레이터

    Args:
        fallback_value: 실패 시 반환할 기본값
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            try:
                return await func(*args, **kwargs)

            except (LLMServiceError, LLMTimeoutError, LLMRateLimitError) as e:
                logger.warning(f"{func.__name__} 실패, Fallback 사용: {e}")
                return fallback_value

            except Exception as e:
                logger.warning(f"{func.__name__} 예상치 못한 오류, Fallback 사용: {e}")
                return fallback_value

        return wrapper

    return decorator


def with_timeout(timeout_seconds: float = 30.0) -> Callable:
    """비동기 함수에 타임아웃을 적용하는 데코레이터

    Args:
        timeout_seconds: 타임아웃 시간 (초)
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return await asyncio.wait_for(
                    func(*args, **kwargs),
                    timeout=timeout_seconds,
                )
            except asyncio.TimeoutError:
                raise LLMTimeoutError(
                    f"{func.__name__} {timeout_seconds}초 타임아웃 초과"
                )

        return wrapper

    return decorator


class GracefulDegradation:
    """Graceful Degradation 컨텍스트 관리자

    LLM 호출 실패 시 fallback 함수를 실행합니다.
    """

    def __init__(
        self,
        fallback_fn: Callable[[], T],
        operation_name: str = "LLM 호출",
    ):
        self._fallback_fn = fallback_fn
        self._operation_name = operation_name
        self._degraded = False

    @property
    def is_degraded(self) -> bool:
        """Fallback이 사용되었는지 여부"""
        return self._degraded

    async def execute(self, primary_fn: Callable[[], T]) -> T:
        """Primary 함수 실행, 실패 시 Fallback 사용

        Args:
            primary_fn: 우선 실행할 함수 (보통 LLM 호출)

        Returns:
            Primary 또는 Fallback 결과
        """
        try:
            result = await primary_fn()
            self._degraded = False
            return result

        except (LLMServiceError, LLMTimeoutError, LLMRateLimitError) as e:
            logger.warning(f"{self._operation_name} 실패, Fallback 실행: {e}")
            self._degraded = True
            return self._fallback_fn()

        except Exception as e:
            logger.warning(f"{self._operation_name} 예상치 못한 오류, Fallback 실행: {e}")
            self._degraded = True
            return self._fallback_fn()
