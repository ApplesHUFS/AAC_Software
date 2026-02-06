"""OpenAI API 클라이언트"""

import asyncio
import base64
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from openai import OpenAI

from app.config.settings import Settings

logger = logging.getLogger(__name__)


class OpenAIClient:
    """OpenAI API 통합 클라이언트"""

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
    ) -> List[str]:
        """선택된 카드들을 해석하여 3가지 가능한 의미 생성"""

        # 시스템 프롬프트 구성
        system_prompt = self._build_interpretation_system_prompt(
            user_persona, context, memory_summary
        )

        # 사용자 메시지 구성
        user_content = self._build_interpretation_user_content(card_images)

        try:
            response = self._client.chat.completions.create(
                model=self._settings.openai_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content},
                ],
                max_tokens=self._settings.interpretation_max_tokens,
                temperature=self._settings.openai_temperature,
            )

            content = response.choices[0].message.content or ""
            return self._parse_interpretations(content)

        except Exception as e:
            print(f"OpenAI API 오류: {e}")
            return [
                "해석을 생성할 수 없습니다.",
                "다시 시도해주세요.",
                "오류가 발생했습니다.",
            ]

    def _build_interpretation_system_prompt(
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
## 응답 형식
반드시 아래 형식으로 3가지 해석을 제공해주세요:
1. [첫 번째 해석]
2. [두 번째 해석]
3. [세 번째 해석]

각 해석은 사용자의 의도를 자연스러운 한국어 문장으로 표현해주세요.
상황과 사용자 특성을 고려하여 가장 가능성 높은 순서로 작성해주세요.
"""
        return prompt

    def _build_interpretation_user_content(
        self, card_images: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """해석용 사용자 메시지 구성"""
        content: List[Dict[str, Any]] = [
            {
                "type": "text",
                "text": "다음 AAC 카드들을 선택했습니다. 이 카드들의 조합이 무엇을 의미하는지 3가지 해석을 제공해주세요.",
            }
        ]

        for card in card_images:
            content.append(
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:{card['media_type']};base64,{card['base64']}",
                        "detail": "high",
                    },
                }
            )
            content.append(
                {
                    "type": "text",
                    "text": f"카드 이름: {card['name']}",
                }
            )

        return content

    def _parse_interpretations(self, content: str) -> List[str]:
        """응답에서 해석 추출"""
        lines = content.strip().split("\n")
        interpretations = []

        for line in lines:
            line = line.strip()
            if line and (
                line.startswith("1.")
                or line.startswith("2.")
                or line.startswith("3.")
            ):
                text = line[2:].strip()
                if text:
                    interpretations.append(text)

        # 3개가 안 되면 기본값 추가
        while len(interpretations) < 3:
            interpretations.append("해석을 생성할 수 없습니다.")

        return interpretations[:3]

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

            response = self._client.chat.completions.create(
                model=self._settings.openai_model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=self._settings.summary_max_tokens,
                temperature=0.5,
            )

            return response.choices[0].message.content or ""

        except Exception as e:
            print(f"대화 요약 오류: {e}")
            return ""

    async def filter_cards(
        self,
        prompt: str,
        max_retries: Optional[int] = None,
    ) -> Dict[str, Any]:
        """카드 적합성 필터링 (JSON 응답)

        GPT-4o를 사용하여 카드의 적합성을 평가하고
        부적절한 카드를 필터링합니다.
        """
        retries = max_retries or self._settings.filter_max_retries

        for attempt in range(retries):
            try:
                response = self._client.chat.completions.create(
                    model=self._settings.openai_model,
                    messages=[
                        {
                            "role": "system",
                            "content": "당신은 AAC 카드 적합성 평가 전문가입니다. JSON 형식으로 응답해주세요.",
                        },
                        {"role": "user", "content": prompt},
                    ],
                    max_tokens=self._settings.filter_max_tokens,
                    temperature=self._settings.filter_temperature,
                    response_format={"type": "json_object"},
                )

                content = response.choices[0].message.content or "{}"
                return json.loads(content)

            except json.JSONDecodeError as e:
                logger.warning(f"JSON 파싱 오류 (시도 {attempt + 1}/{retries}): {e}")
                if attempt < retries - 1:
                    await asyncio.sleep(2**attempt)
                continue

            except Exception as e:
                logger.warning(f"필터 API 오류 (시도 {attempt + 1}/{retries}): {e}")
                if attempt < retries - 1:
                    await asyncio.sleep(2**attempt)
                continue

        # 폴백: 필터링 없이 원본 반환
        logger.error("필터 API 재시도 횟수 초과, 폴백 응답 반환")
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

        GPT-4o를 사용하여 카드를 컨텍스트에 맞게 재순위화합니다.
        """
        retries = max_retries or self._settings.filter_max_retries

        for attempt in range(retries):
            try:
                response = self._client.chat.completions.create(
                    model=self._settings.openai_model,
                    messages=[
                        {
                            "role": "system",
                            "content": "당신은 AAC 카드 순위 최적화 전문가입니다. JSON 형식으로 응답해주세요.",
                        },
                        {"role": "user", "content": prompt},
                    ],
                    max_tokens=self._settings.rerank_max_tokens,
                    temperature=self._settings.rerank_temperature,
                    response_format={"type": "json_object"},
                )

                content = response.choices[0].message.content or "{}"
                return json.loads(content)

            except json.JSONDecodeError as e:
                logger.warning(f"JSON 파싱 오류 (시도 {attempt + 1}/{retries}): {e}")
                if attempt < retries - 1:
                    await asyncio.sleep(2**attempt)
                continue

            except Exception as e:
                logger.warning(f"재순위화 API 오류 (시도 {attempt + 1}/{retries}): {e}")
                if attempt < retries - 1:
                    await asyncio.sleep(2**attempt)
                continue

        # 폴백: 빈 순위 반환 (원본 순서 유지)
        logger.error("재순위화 API 재시도 횟수 초과, 폴백 응답 반환")
        return {"ranked": []}
