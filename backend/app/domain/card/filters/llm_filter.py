"""GPT-4o 기반 카드 적합성 필터

사용자 정보와 컨텍스트를 기반으로 부적절한 카드를 필터링합니다.
LLM의 자연어 이해 능력을 활용하여 의미론적 적합성 평가를 수행합니다.

설계 원칙:
- 키워드 기반 fallback 없이 LLM 전용 필터링
- LLM 실패 시 명시적 오류 반환 (잘못된 fallback 방지)
"""

import logging
from typing import Dict, List, Set

from app.core.exceptions import LLMFilterError
from app.domain.card.filters.base import (
    FilterContext,
    FilterResult,
    ICardFilter,
)
from app.domain.card.interfaces import ScoredCard
from app.infrastructure.external.openai_client import OpenAIClient

logger = logging.getLogger(__name__)


class LLMCardFilter(ICardFilter):
    """GPT-4o 기반 카드 적합성 필터

    카드 목록과 사용자 정보를 GPT-4o에 전달하여
    각 카드의 적합성을 평가받습니다.

    키워드 기반 fallback 없이 LLM 응답에만 의존.
    LLM 실패 시 명시적 오류 반환.
    """

    def __init__(
        self,
        openai_client: OpenAIClient,
        batch_size: int = 40,
    ):
        self._openai = openai_client
        self._batch_size = batch_size

    async def filter_cards(
        self,
        candidates: List[ScoredCard],
        filter_ctx: FilterContext,
    ) -> FilterResult:
        """카드 필터링 실행

        Raises:
            LLMFilterError: LLM 응답이 비어있을 때 (키워드 fallback 대신 명시적 오류)
        """
        if not candidates:
            return FilterResult(appropriate_cards=[])

        card_names = [self._extract_card_name(c.card.filename) for c in candidates]

        prompt = self._build_filter_prompt(card_names, filter_ctx)
        response = await self._openai.filter_cards(prompt)

        # 응답이 비어있으면 명시적 오류 발생 (키워드 fallback 제거)
        if not response.get("appropriate") and not response.get("inappropriate"):
            logger.error("LLM 필터 응답 비어있음 - 오류 발생")
            raise LLMFilterError(
                "LLM 필터가 유효한 응답을 반환하지 않았습니다. 다시 시도해주세요."
            )

        return self._apply_filter_result(candidates, response)

    def _build_filter_prompt(
        self,
        card_names: List[str],
        filter_ctx: FilterContext,
    ) -> str:
        """필터링 프롬프트 생성"""
        user = filter_ctx.user
        context = filter_ctx.context

        # 카드 목록 (최대 batch_size개)
        card_list = "\n".join(
            f"- {name}" for name in card_names[: self._batch_size]
        )

        # 관심 주제 포맷팅
        topics_str = ", ".join(user.interesting_topics) if user.interesting_topics else "없음"

        return f"""당신은 AAC(보완대체의사소통) 전문가입니다.
다음 카드들이 사용자에게 적합한지 평가해주세요.

## 사용자 정보
- 나이: {user.age}세
- 성별: {user.gender}
- 장애 유형: {user.disability_type}
- 의사소통 특성: {user.communication_characteristics}
- 관심 주제: {topics_str}

## 현재 상황
- 장소: {context.place}
- 대화 상대: {context.interaction_partner}
- 현재 활동: {context.current_activity}

## 평가할 카드 목록
{card_list}

## 평가 기준
1. **나이 적합성**: {user.age}세에게 적절한 카드인가?
   - 성인 관계(연애, 결혼, 신혼부부 등)는 아동에게 부적절
   - 영아 돌봄(기저귀 갈기 등)은 학령기 아동에게 부적절
   - 폭력적/선정적 내용은 모든 아동에게 부적절

2. **상황 관련성**: 현재 상황({context.place}에서 {context.current_activity})과 관련있는가?
   - 완전히 무관한 카드는 우선순위 낮춤

3. **관심 주제 관련성**: 사용자의 관심 주제({topics_str})와 관련된 카드인가?
   - 관심 주제 관련 카드는 현재 상황과 직접 관련 없어도 **적합으로 분류**
   - 사용자가 좋아하는 주제이므로 의사소통 동기 부여에 도움됨

4. **의사소통 적합성**: {user.disability_type} 사용자가 이해하고 사용할 수 있는가?

## 응답 형식 (JSON)
{{
  "appropriate": ["적합한 카드명1", "적합한 카드명2", ...],
  "inappropriate": [
    {{"name": "부적합한 카드명", "reason": "부적합 이유"}}
  ],
  "highly_relevant": ["상황 또는 관심 주제에 특히 관련된 카드명1", "카드명2"]
}}

적합/부적합을 명확히 구분하여 빠짐없이 분류해주세요."""

    def _apply_filter_result(
        self,
        candidates: List[ScoredCard],
        response: Dict,
    ) -> FilterResult:
        """API 응답을 FilterResult로 변환"""
        appropriate_names: Set[str] = set(response.get("appropriate", []))
        highly_relevant_names: Set[str] = set(response.get("highly_relevant", []))

        # 카드명으로 인덱싱
        name_to_card: Dict[str, ScoredCard] = {}
        for c in candidates:
            name = self._extract_card_name(c.card.filename)
            name_to_card[name] = c

        # 적합한 카드 필터링
        appropriate_cards: List[ScoredCard] = []
        for name in appropriate_names:
            if name in name_to_card:
                card = name_to_card[name]
                # highly_relevant 카드에 점수 보너스
                if name in highly_relevant_names:
                    card.semantic_score += 0.1
                appropriate_cards.append(card)

        # 원래 순서대로 정렬 (semantic_score 유지)
        original_order = {
            self._extract_card_name(c.card.filename): i
            for i, c in enumerate(candidates)
        }
        appropriate_cards.sort(
            key=lambda c: original_order.get(
                self._extract_card_name(c.card.filename), float("inf")
            )
        )

        return FilterResult(
            appropriate_cards=appropriate_cards,
            inappropriate_cards=response.get("inappropriate", []),
            highly_relevant_cards=list(highly_relevant_names),
        )

    def _extract_card_name(self, filename: str) -> str:
        """파일명에서 카드 이름 추출

        예: '36892_기저귀를 갈다.png' -> '기저귀를 갈다'
        """
        name = filename.rsplit(".", 1)[0]  # 확장자 제거
        if "_" in name:
            return name.split("_", 1)[1]
        return name

    def get_filter_name(self) -> str:
        return "LLMCardFilter"
