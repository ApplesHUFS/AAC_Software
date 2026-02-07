"""카드 해석 클라이언트

AAC 카드 해석 및 대화 요약 기능 제공
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional

from openai import APITimeoutError, RateLimitError

from app.config.settings import Settings
from app.core.exceptions import LLMRateLimitError, LLMServiceError, LLMTimeoutError

from .base import DEFAULT_BASE_DELAY, DEFAULT_MAX_RETRIES, EXPONENTIAL_BASE, OpenAIClientBase

logger = logging.getLogger(__name__)


class CardInterpreter(OpenAIClientBase):
    """카드 해석 전문 클라이언트"""

    def __init__(self, settings: Settings):
        super().__init__(settings)

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

        Raises:
            LLMServiceError: 재시도 후에도 실패한 경우
        """
        logger.info("카드 해석 시작: %d개 카드", len(card_images))
        logger.debug(
            "해석 컨텍스트: place=%s, partner=%s",
            context.get("place"),
            context.get("interactionPartner"),
        )

        instructions = self._build_system_prompt(user_persona, context, memory_summary)
        user_content = self._build_user_content(card_images)

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

            if attempt < max_retries - 1:
                delay = DEFAULT_BASE_DELAY * (EXPONENTIAL_BASE**attempt)
                await asyncio.sleep(delay)

        logger.error(f"카드 해석 재시도 실패: {last_exception}")
        raise last_exception or LLMServiceError("카드 해석에 실패했습니다.")

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

    def _build_system_prompt(
        self,
        user_persona: Dict[str, Any],
        context: Dict[str, Any],
        memory_summary: Optional[str],
    ) -> str:
        """해석용 시스템 프롬프트 생성"""
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

    def _build_user_content(
        self, card_images: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """해석용 사용자 메시지 구성"""
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
