"""OpenAI Responses API 클라이언트

Responses API를 사용하여 텍스트 생성, 이미지 분석, JSON 출력을 처리합니다.
Resilience: 재시도(exponential backoff) 및 Graceful Degradation 지원
"""

import asyncio
import base64
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from openai import APITimeoutError, OpenAI, RateLimitError

from app.config.settings import Settings
from app.core.exceptions import LLMRateLimitError, LLMServiceError, LLMTimeoutError

logger = logging.getLogger(__name__)

# 재시도 설정 상수
DEFAULT_MAX_RETRIES = 3
DEFAULT_BASE_DELAY = 1.0
EXPONENTIAL_BASE = 2.0


class OpenAIClient:
    """OpenAI Responses API 통합 클라이언트"""

    def __init__(self, settings: Settings):
        self._settings = settings
        self._client = OpenAI(api_key=settings.openai_api_key)

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

    async def interpret_cards(
        self,
        card_images: List[Dict[str, Any]],
        user_persona: Dict[str, Any],
        context: Dict[str, Any],
        memory_summary: Optional[str] = None,
        max_retries: int = DEFAULT_MAX_RETRIES,
    ) -> List[str]:
        """선택된 카드들을 해석하여 3가지 가능한 의미 생성

        카드 해석은 잘못된 해석이 위험하므로 Fallback 없이 명확한 에러를 반환합니다.
        재시도 로직만 적용됩니다.

        Raises:
            LLMServiceError: 재시도 후에도 실패한 경우
        """
        logger.info("카드 해석 시작: %d개 카드", len(card_images))
        logger.debug(
            "해석 컨텍스트: place=%s, partner=%s",
            context.get("place"), context.get("interactionPartner")
        )

        instructions = self._build_interpretation_system_prompt(
            user_persona, context, memory_summary
        )
        user_content = self._build_interpretation_user_content(card_images)

        interpretation_schema = {
            "type": "json_schema",
            "name": "card_interpretations",
            "strict": True,
            "schema": {
                "type": "object",
                "properties": {
                    "interpretations": {
                        "type": "array",
                        "description": "3가지 해석 문장 목록",
                        "items": {"type": "string"},
                    }
                },
                "required": ["interpretations"],
                "additionalProperties": False,
            },
        }

        last_exception: Optional[Exception] = None

        for attempt in range(max_retries):
            try:
                logger.info(
                    f"카드 해석 API 호출 (시도 {attempt + 1}/{max_retries}), "
                    f"model: {self._settings.openai_model}"
                )

                response = self._client.responses.create(
                    model=self._settings.openai_model,
                    instructions=instructions,
                    input=user_content,
                    max_output_tokens=self._settings.interpretation_max_tokens,
                    temperature=self._settings.openai_temperature,
                    text={"format": interpretation_schema},
                )

                content = response.output_text or "{}"
                logger.info(f"API Response (structured): {content[:500]}")

                result = json.loads(content)
                interpretations = result.get("interpretations", [])

                while len(interpretations) < 3:
                    interpretations.append("해석을 생성할 수 없습니다.")

                logger.info("카드 해석 완료: %d개 해석 생성", len(interpretations))
                return interpretations[:3]

            except APITimeoutError as e:
                last_exception = LLMTimeoutError(str(e))
                logger.warning(f"카드 해석 타임아웃 (시도 {attempt + 1}/{max_retries})")

            except RateLimitError as e:
                last_exception = LLMRateLimitError(str(e))
                logger.warning(f"카드 해석 Rate Limit (시도 {attempt + 1}/{max_retries})")

            except json.JSONDecodeError as e:
                last_exception = LLMServiceError(f"JSON 파싱 오류: {e}")
                logger.warning(f"카드 해석 JSON 오류 (시도 {attempt + 1}/{max_retries})")

            except Exception as e:
                last_exception = LLMServiceError(str(e))
                logger.warning(f"카드 해석 오류 (시도 {attempt + 1}/{max_retries}): {e}")

            # 마지막 시도가 아니면 대기
            if attempt < max_retries - 1:
                delay = DEFAULT_BASE_DELAY * (EXPONENTIAL_BASE**attempt)
                await asyncio.sleep(delay)

        # 재시도 실패 - 명확한 에러 반환 (Fallback 금지)
        logger.error(f"카드 해석 재시도 실패: {last_exception}")
        raise last_exception or LLMServiceError("카드 해석에 실패했습니다.")

    async def _retry_with_backoff(
        self,
        operation_name: str,
        api_call: Any,
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

    def _build_interpretation_system_prompt(
        self,
        user_persona: Dict[str, Any],
        context: Dict[str, Any],
        memory_summary: Optional[str],
    ) -> str:
        """해석용 시스템 프롬프트 생성 (Structured Outputs용)"""
        prompt = f"""당신은 AAC(보완대체의사소통) 카드 해석 전문가입니다.
사용자가 선택한 카드들을 보고 3가지 가능한 의미를 추론해주세요.

## 사용자 정보
- 이름: {user_persona.get('name', '알 수 없음')}
- 나이: {user_persona.get('age', '알 수 없음')}세
- 성별: {user_persona.get('gender', '알 수 없음')}
- 장애 유형: {user_persona.get('disabilityType', '알 수 없음')}
- 의사소통 특성: {user_persona.get('communicationCharacteristics', '알 수 없음')}
- 관심 주제: {', '.join(user_persona.get('interestingTopics', []))}

## 현재 상황
- 시간: {context.get('time', '알 수 없음')}
- 장소: {context.get('place', '알 수 없음')}
- 대화 상대: {context.get('interactionPartner', '알 수 없음')}
- 현재 활동: {context.get('currentActivity', '없음')}
"""

        if memory_summary:
            prompt += f"\n## 과거 대화 패턴\n{memory_summary}\n"

        prompt += """
## 응답 지침
정확히 3개의 해석을 제공해주세요:
- 각 해석은 사용자의 의도를 자연스러운 한국어 문장으로 표현
- 상황과 사용자 특성을 고려하여 가장 가능성 높은 순서로 작성
- 짧고 명확한 문장으로 표현 (한 문장 또는 두 문장 이내)
"""
        return prompt

    def _build_interpretation_user_content(
        self, card_images: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """해석용 사용자 메시지 구성 (Responses API 형식)"""
        content: List[Dict[str, Any]] = [
            {
                "type": "input_text",
                "text": "다음 AAC 카드들을 선택했습니다. 이 카드들의 조합이 무엇을 의미하는지 3가지 해석을 제공해주세요.",
            }
        ]

        for card in card_images:
            content.append(
                {
                    "type": "input_image",
                    "image_url": f"data:{card['media_type']};base64,{card['base64']}",
                }
            )
            content.append(
                {
                    "type": "input_text",
                    "text": f"카드 이름: {card['name']}",
                }
            )

        return [{"role": "user", "content": content}]

    async def summarize_conversation(
        self,
        conversation_history: List[Dict[str, Any]],
    ) -> str:
        """대화 히스토리 요약"""
        if not conversation_history:
            return ""

        try:
            prompt = "다음 AAC 대화 기록을 간단히 요약해주세요:\n\n"
            for item in conversation_history[-10:]:
                prompt += f"- 카드: {item.get('cards', [])}\n"
                prompt += f"  해석: {item.get('interpretation', '')}\n"

            response = self._client.responses.create(
                model=self._settings.openai_model,
                input=prompt,
                max_output_tokens=self._settings.summary_max_tokens,
                temperature=0.5,
            )

            return response.output_text or ""

        except Exception as e:
            logger.error(f"대화 요약 오류: {e}")
            return ""

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

    async def rewrite_query(
        self,
        place: str,
        partner: str,
        activity: str,
        count: int = 3,
        context_hints: Optional[List[str]] = None,
    ) -> List[str]:
        """검색 쿼리 확장 (JSON 응답)

        원본 컨텍스트를 여러 검색 쿼리로 확장하여
        더 다양한 카드 후보를 확보합니다.

        Args:
            place: 장소
            partner: 대화 상대
            activity: 현재 활동
            count: 생성할 쿼리 수
            context_hints: 과거 피드백에서 추출된 컨텍스트 힌트

        Returns:
            확장된 쿼리 목록
        """
        logger.info(
            "쿼리 재작성 시작: place=%s, partner=%s, activity=%s",
            place, partner, activity
        )

        # 피드백 기반 컨텍스트 힌트 섹션
        hints_section = ""
        if context_hints:
            hints_section = f"""
## 과거 유사 상황 (피드백 기반)
다음은 과거에 비슷한 상황에서 사용된 표현입니다. 이를 참고하여 쿼리를 확장하세요:
{', '.join(context_hints)}
"""

        prompt = f"""AAC 카드 검색을 위해 쿼리를 확장해주세요.

## 원본 컨텍스트
- 장소: {place or '없음'}
- 대화 상대: {partner or '없음'}
- 현재 활동: {activity or '없음'}
{hints_section}
## 요청
위 상황에서 필요한 AAC 카드를 찾기 위한 검색 쿼리 {count}개를 생성하세요.
각 쿼리는 서로 다른 관점에서 작성:
1. 동의어/유사어를 사용한 표현
2. 관련 활동이나 행동을 확장한 표현
3. 감정이나 요구 표현을 추가한 표현

## 응답 형식 (JSON)
{{"queries": ["쿼리1 상황에서 사용하는 의사소통 카드", "쿼리2 상황에서 사용하는 의사소통 카드", "쿼리3 상황에서 사용하는 의사소통 카드"]}}"""

        try:
            response = self._client.responses.create(
                model=self._settings.openai_filter_model,
                instructions="AAC 카드 검색 쿼리 확장 전문가입니다. JSON 형식으로 응답해주세요.",
                input=prompt,
                max_output_tokens=self._settings.query_rewrite_max_tokens,
                temperature=0.7,
                text={"format": {"type": "json_object"}},
            )

            content = response.output_text or "{}"
            result = json.loads(content)
            queries = result.get("queries", [])

            if queries:
                logger.info(f"쿼리 재작성 완료: {len(queries)}개 생성")
                return queries[:count]

        except json.JSONDecodeError as e:
            logger.warning(f"쿼리 재작성 JSON 파싱 오류: {e}")

        except Exception as e:
            logger.warning(f"쿼리 재작성 API 오류: {e}")

        return []
