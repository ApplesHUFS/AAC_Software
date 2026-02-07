"""카드 필터링 및 재순위화 클라이언트

LLM 기반 카드 적합성 필터링 및 재순위화 기능 제공
"""

import asyncio
import json
import logging
from typing import Any, Dict, Optional

from openai import APITimeoutError, RateLimitError

from app.config.settings import Settings

from .base import DEFAULT_BASE_DELAY, EXPONENTIAL_BASE, OpenAIClientBase

logger = logging.getLogger(__name__)


class CardFilterReranker(OpenAIClientBase):
    """카드 필터링 및 재순위화 클라이언트"""

    def __init__(self, settings: Settings):
        super().__init__(settings)

    async def filter_cards(
        self,
        prompt: str,
        max_retries: Optional[int] = None,
    ) -> Dict[str, Any]:
        """카드 적합성 필터링 (JSON 응답)

        Graceful Degradation: 실패 시 빈 결과 반환 (필터 건너뛰기)
        """
        logger.info("카드 필터 API 호출 시작")
        retries = max_retries or self._settings.filter_max_retries

        for attempt in range(retries):
            try:
                logger.debug("필터 API 시도 %d/%d", attempt + 1, retries)
                response = self._client.responses.create(
                    model=self._settings.openai_filter_model,
                    instructions="당신은 AAC 카드 적합성 평가 전문가입니다. JSON 형식으로 응답해주세요.",
                    input=prompt,
                    max_output_tokens=self._settings.filter_max_tokens,
                    temperature=self._settings.filter_temperature,
                    text={"format": {"type": "json_object"}},
                )

                content = response.output_text or "{}"
                result = json.loads(content)
                logger.info(
                    "카드 필터 API 완료: %d개 적합, %d개 부적합",
                    len(result.get("appropriate", [])),
                    len(result.get("inappropriate", [])),
                )
                return result

            except APITimeoutError:
                logger.warning(f"필터 타임아웃 (시도 {attempt + 1}/{retries})")

            except RateLimitError:
                logger.warning(f"필터 Rate Limit (시도 {attempt + 1}/{retries})")

            except json.JSONDecodeError as e:
                logger.warning(f"필터 JSON 파싱 오류 (시도 {attempt + 1}/{retries}): {e}")

            except Exception as e:
                logger.warning(f"필터 API 오류 (시도 {attempt + 1}/{retries}): {e}")

            if attempt < retries - 1:
                delay = DEFAULT_BASE_DELAY * (EXPONENTIAL_BASE**attempt)
                await asyncio.sleep(delay)

        # Graceful Degradation: 필터 건너뛰기
        logger.warning("필터 API 재시도 실패, Graceful Degradation 적용")
        return {
            "appropriate": [],
            "inappropriate": [],
            "highly_relevant": [],
        }

    async def rerank_cards(
        self,
        prompt: str,
        max_retries: Optional[int] = None,
    ) -> Dict[str, Any]:
        """카드 재순위화 (JSON 응답)

        Graceful Degradation: 실패 시 빈 결과 반환 (재순위화 건너뛰기)
        """
        logger.info("카드 재순위화 API 호출 시작")
        retries = max_retries or self._settings.filter_max_retries

        for attempt in range(retries):
            try:
                logger.debug("재순위화 API 시도 %d/%d", attempt + 1, retries)
                response = self._client.responses.create(
                    model=self._settings.openai_filter_model,
                    instructions="당신은 AAC 카드 순위 최적화 전문가입니다. JSON 형식으로 응답해주세요.",
                    input=prompt,
                    max_output_tokens=self._settings.rerank_max_tokens,
                    temperature=self._settings.rerank_temperature,
                    text={"format": {"type": "json_object"}},
                )

                content = response.output_text or "{}"
                result = json.loads(content)
                logger.info(
                    "카드 재순위화 API 완료: %d개 카드 순위 조정",
                    len(result.get("ranked", [])),
                )
                return result

            except APITimeoutError:
                logger.warning(f"재순위화 타임아웃 (시도 {attempt + 1}/{retries})")

            except RateLimitError:
                logger.warning(f"재순위화 Rate Limit (시도 {attempt + 1}/{retries})")

            except json.JSONDecodeError as e:
                logger.warning(f"재순위화 JSON 파싱 오류 (시도 {attempt + 1}/{retries}): {e}")

            except Exception as e:
                logger.warning(f"재순위화 API 오류 (시도 {attempt + 1}/{retries}): {e}")

            if attempt < retries - 1:
                delay = DEFAULT_BASE_DELAY * (EXPONENTIAL_BASE**attempt)
                await asyncio.sleep(delay)

        # Graceful Degradation: 재순위화 건너뛰기
        logger.warning("재순위화 API 재시도 실패, Graceful Degradation 적용")
        return {"ranked": []}
