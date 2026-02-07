"""OpenAI 클라이언트 기본 클래스

공통 유틸리티 및 재시도 로직 제공
"""

import asyncio
import base64
import logging
from pathlib import Path
from typing import Any, Callable, Optional

from openai import APITimeoutError, OpenAI, RateLimitError

from app.config.settings import Settings
from app.core.exceptions import LLMRateLimitError, LLMServiceError, LLMTimeoutError

logger = logging.getLogger(__name__)

# 재시도 설정 상수
DEFAULT_MAX_RETRIES = 3
DEFAULT_BASE_DELAY = 1.0
EXPONENTIAL_BASE = 2.0


class OpenAIClientBase:
    """OpenAI 클라이언트 기본 클래스"""

    def __init__(self, settings: Settings):
        self._settings = settings
        self._client = OpenAI(api_key=settings.openai_api_key)

    @property
    def client(self) -> OpenAI:
        """OpenAI 클라이언트 인스턴스"""
        return self._client

    @property
    def settings(self) -> Settings:
        """설정 인스턴스"""
        return self._settings

    def encode_image_to_base64(self, image_path: Path) -> str:
        """이미지를 Base64로 인코딩"""
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")

    def get_image_media_type(self, filename: str) -> str:
        """파일 확장자로 미디어 타입 결정"""
        ext = filename.lower().split(".")[-1]
        media_types = {
            "png": "image/png",
            "jpg": "image/jpeg",
            "jpeg": "image/jpeg",
            "gif": "image/gif",
            "webp": "image/webp",
        }
        return media_types.get(ext, "image/png")

    async def retry_with_backoff(
        self,
        operation_name: str,
        api_call: Callable[[], Any],
        max_retries: int = DEFAULT_MAX_RETRIES,
    ) -> Any:
        """Exponential backoff 재시도 헬퍼

        Args:
            operation_name: 로깅용 작업 이름
            api_call: API 호출 람다 함수
            max_retries: 최대 재시도 횟수

        Returns:
            API 응답

        Raises:
            LLMServiceError: 재시도 후에도 실패한 경우
        """
        last_exception: Optional[Exception] = None

        for attempt in range(max_retries):
            try:
                return api_call()

            except APITimeoutError as e:
                last_exception = LLMTimeoutError(str(e))
                logger.warning(
                    f"{operation_name} 타임아웃 (시도 {attempt + 1}/{max_retries})"
                )

            except RateLimitError as e:
                last_exception = LLMRateLimitError(str(e))
                logger.warning(
                    f"{operation_name} Rate Limit (시도 {attempt + 1}/{max_retries})"
                )

            except Exception as e:
                last_exception = LLMServiceError(str(e))
                logger.warning(
                    f"{operation_name} 오류 (시도 {attempt + 1}/{max_retries}): {e}"
                )

            if attempt < max_retries - 1:
                delay = DEFAULT_BASE_DELAY * (EXPONENTIAL_BASE**attempt)
                await asyncio.sleep(delay)

        raise last_exception or LLMServiceError(f"{operation_name} 실패")
