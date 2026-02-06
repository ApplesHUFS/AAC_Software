"""GPT-4o 기반 카드 적합성 필터

사용자 정보와 컨텍스트를 기반으로 부적절한 카드를 필터링합니다.
LLM의 자연어 이해 능력을 활용하여 키워드 기반 필터링보다
더 정확한 적합성 평가를 수행합니다.
"""

import logging
from typing import Dict, List, Set

from app.config.filter_config import AgeAppropriatenessConfig
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
    """

    def __init__(
        self,
        openai_client: OpenAIClient,
        batch_size: int = 40,
        fallback_config: AgeAppropriatenessConfig | None = None,
    ):
        self._openai = openai_client
        self._batch_size = batch_size
        self._fallback_config = fallback_config or AgeAppropriatenessConfig()

    async def filter_cards(
        self,
        candidates: List[ScoredCard],
        filter_ctx: FilterContext,
    ) -> FilterResult:
        """카드 필터링 실행"""
        if not candidates:
            return FilterResult(appropriate_cards=[])

        # 배치 처리를 위해 카드 이름 추출
        card_names = [self._extract_card_name(c.card.filename) for c in candidates]

        # 프롬프트 생성 및 API 호출
        prompt = self._build_filter_prompt(card_names, filter_ctx)
        response = await self._openai.filter_cards(prompt)

        # 응답이 비어있으면 폴백 사용
        if not response.get("appropriate") and not response.get("inappropriate"):
            logger.warning("LLM 필터 응답 없음, 폴백 필터 사용")
            return self._fallback_filter(candidates, filter_ctx)

        # 결과 적용
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

        return f"""당신은 AAC(보완대체의사소통) 전문가입니다.
다음 카드들이 사용자에게 적합한지 평가해주세요.

## 사용자 정보
- 나이: {user.age}세
- 성별: {user.gender}
- 장애 유형: {user.disability_type}
- 의사소통 특성: {user.communication_characteristics}

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

3. **의사소통 적합성**: {user.disability_type} 사용자가 이해하고 사용할 수 있는가?

## 응답 형식 (JSON)
{{
  "appropriate": ["적합한 카드명1", "적합한 카드명2", ...],
  "inappropriate": [
    {{"name": "부적합한 카드명", "reason": "부적합 이유"}}
  ],
  "highly_relevant": ["상황에 특히 관련된 카드명1", "카드명2"]
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

    def _fallback_filter(
        self,
        candidates: List[ScoredCard],
        filter_ctx: FilterContext,
    ) -> FilterResult:
        """LLM 실패 시 키워드 기반 폴백 필터"""
        age = filter_ctx.user.age

        # 나이대별 부적절 키워드 선택
        if age <= 12:
            inappropriate_keywords = self._fallback_config.child_inappropriate
        elif age <= 17:
            inappropriate_keywords = self._fallback_config.teen_inappropriate
        else:
            inappropriate_keywords = frozenset()

        # 항상 적용되는 부적절 키워드
        all_inappropriate = (
            inappropriate_keywords | self._fallback_config.universal_inappropriate
        )

        appropriate_cards: List[ScoredCard] = []
        inappropriate_list: List[Dict[str, str]] = []

        for c in candidates:
            name = self._extract_card_name(c.card.filename).lower()
            is_inappropriate = any(kw in name for kw in all_inappropriate)

            if is_inappropriate:
                matched_kw = next(
                    (kw for kw in all_inappropriate if kw in name), "unknown"
                )
                inappropriate_list.append(
                    {"name": name, "reason": f"부적절한 키워드 포함: {matched_kw}"}
                )
            else:
                appropriate_cards.append(c)

        return FilterResult(
            appropriate_cards=appropriate_cards,
            inappropriate_cards=inappropriate_list,
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
